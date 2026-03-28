"""
KnowledgeScanner — Pre-task knowledge scan voor agents.

Leest agent knowledge profile uit KnowledgeConfig, queryt KnowledgeStore
per domein, vergelijkt met min_grade vereisten. Best-effort: blokkeert
de taak NIET, annoteert output met lacunes.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from devhub_core.contracts.curator_contracts import KnowledgeDomain
from devhub_core.contracts.research_contracts import ResearchDepth, ResearchRequest
from devhub_core.contracts.scanner_contracts import (
    DomainScanStatus,
    KnowledgeScanResult,
    grade_gte,
)

if TYPE_CHECKING:
    from devhub_core.contracts.research_contracts import ResearchQueue
    from devhub_core.research.knowledge_config import (
        DomainConfig,
        KnowledgeConfig,
    )
    from devhub_core.research.knowledge_store import KnowledgeStore


class KnowledgeScanner:
    """Pre-task knowledge scan voor agents.

    Leest agent knowledge profile, queryt vectorstore per domein,
    vergelijkt met min_grade vereisten en RQ-dekking.
    """

    def __init__(
        self,
        config: KnowledgeConfig,
        store: KnowledgeStore,
        queue: ResearchQueue | None = None,
    ) -> None:
        self._config = config
        self._store = store
        self._queue = queue

    def scan_agent(self, agent_name: str) -> KnowledgeScanResult:
        """Voer knowledge scan uit voor een agent.

        1. Zoek AgentKnowledgeProfile op
        2. Per required domein: query store, check grade, check RQ-dekking
        3. Genereer ResearchRequests voor gaps
        4. Submit naar queue indien beschikbaar
        """
        profile = self._config.get_agent_profile(agent_name)
        if profile is None:
            return KnowledgeScanResult(
                agent_name=agent_name,
                scan_timestamp=datetime.now(tz=UTC).isoformat(),
            )

        statuses: list[DomainScanStatus] = []
        all_requests: list[ResearchRequest] = []

        for domain_name, required_grade in profile.domains:
            domain_config = self._config.get_domain(domain_name)
            if domain_config is None:
                continue

            status = self._scan_domain(domain_name, required_grade, domain_config)
            statuses.append(status)

            if not status.sufficient:
                requests = self._generate_gap_requests(agent_name, status, domain_config)
                all_requests.extend(requests)

        # Submit naar queue
        if self._queue is not None and all_requests:
            for req in all_requests:
                self._queue.submit(req)

        overall = all(s.sufficient for s in statuses)

        return KnowledgeScanResult(
            agent_name=agent_name,
            domain_statuses=tuple(statuses),
            overall_sufficient=overall,
            generated_requests=tuple(all_requests),
            scan_timestamp=datetime.now(tz=UTC).isoformat(),
        )

    def _scan_domain(
        self,
        domain_name: str,
        required_grade: str,
        domain_config: DomainConfig,
    ) -> DomainScanStatus:
        """Scan een domein tegen vereisten."""
        try:
            kd = KnowledgeDomain(domain_name)
        except ValueError:
            return DomainScanStatus(
                domain=domain_name,
                required_grade=required_grade,
                actual_articles=0,
                sufficient=False,
            )

        articles = self._store.list_by_domain(kd)
        actual_articles = len(articles)

        # Bepaal beste grade
        best_grade = "SPECULATIVE"
        if articles:
            grade_order = {"SPECULATIVE": 0, "BRONZE": 1, "SILVER": 2, "GOLD": 3}
            for article in articles:
                if grade_order.get(article.grade, 0) > grade_order.get(best_grade, 0):
                    best_grade = article.grade

        # Check RQ-dekking
        article_rq_tags = set()
        for article in articles:
            article_rq_tags.update(article.rq_tags)

        rq_coverage = tuple((rq, rq in article_rq_tags) for rq in domain_config.rq_focus)

        # Voldoende = grade OK EN alle RQs gedekt
        grade_ok = grade_gte(best_grade, required_grade)
        rq_ok = all(covered for _, covered in rq_coverage) if rq_coverage else True
        sufficient = grade_ok and rq_ok and actual_articles > 0

        return DomainScanStatus(
            domain=domain_name,
            required_grade=required_grade,
            actual_articles=actual_articles,
            actual_best_grade=best_grade,
            rq_coverage=rq_coverage,
            sufficient=sufficient,
        )

    def _generate_gap_requests(
        self,
        agent_name: str,
        status: DomainScanStatus,
        domain_config: DomainConfig,
    ) -> list[ResearchRequest]:
        """Genereer ResearchRequests voor ontbrekende RQ-dekking."""
        requests: list[ResearchRequest] = []
        ts = datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")

        # Zoek seed questions voor ontbrekende RQs
        seed_by_rq: dict[str, str] = {}
        for sq in domain_config.seed_questions:
            if sq.rq_tag not in seed_by_rq:
                seed_by_rq[sq.rq_tag] = sq.question

        for rq in status.missing_rqs:
            question = seed_by_rq.get(
                rq,
                f"Wat is de huidige stand van kennis over {status.domain} ({rq})?",
            )
            requests.append(
                ResearchRequest(
                    request_id=f"SCAN-{agent_name}-{status.domain}-{rq}-{ts}",
                    requesting_agent=f"scanner-{agent_name}",
                    question=question,
                    domain=status.domain,
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=f"Auto-generated by KnowledgeScanner for {agent_name}",
                    rq_tags=(rq,),
                )
            )

        return requests
