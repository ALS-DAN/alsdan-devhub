"""
ConfigDrivenBootstrap — Ring 1 auto-bootstrap uit knowledge.yml seed questions.

Leest seed questions uit config, genereert BRONZE-level seed artikelen,
valideert via curator, en produceert audit rapport.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from devhub_core.contracts.curator_contracts import KnowledgeArticle, KnowledgeDomain
from devhub_core.contracts.research_contracts import ResearchDepth, ResearchRequest
from devhub_core.contracts.scanner_contracts import (
    BootstrapAuditReport,
    BootstrapDomainReport,
)

if TYPE_CHECKING:
    from devhub_core.research.bootstrap import BootstrapPipeline
    from devhub_core.research.knowledge_config import DomainConfig, KnowledgeConfig
    from devhub_core.research.knowledge_store import KnowledgeStore


class ConfigDrivenBootstrap:
    """Ring 1 auto-bootstrap vanuit knowledge.yml seed questions.

    Leest seed questions uit config, genereert BRONZE-level artikelen,
    valideert via curator/pipeline, slaat op in vectorstore.
    """

    def __init__(
        self,
        config: KnowledgeConfig,
        pipeline: BootstrapPipeline,
        store: KnowledgeStore,
    ) -> None:
        self._config = config
        self._pipeline = pipeline
        self._store = store

    def get_seed_requests(self) -> dict[str, list[ResearchRequest]]:
        """Genereer ResearchRequests uit config seed questions.

        Alleen voor domeinen in bootstrap_domains() (core ring met
        auto_bootstrap=True en bootstrap_priority > 0).
        """
        result: dict[str, list[ResearchRequest]] = {}

        for domain_config in self._config.bootstrap_domains():
            requests: list[ResearchRequest] = []
            for i, sq in enumerate(domain_config.seed_questions, 1):
                requests.append(
                    ResearchRequest(
                        request_id=f"CBOOT-{domain_config.name}-{i:03d}",
                        requesting_agent="config-bootstrap",
                        question=sq.question,
                        domain=domain_config.name,
                        depth=ResearchDepth.STANDARD,
                        priority=domain_config.bootstrap_priority,
                        context=f"Auto-bootstrap Ring 1: {domain_config.description}",
                        rq_tags=(sq.rq_tag,),
                    )
                )
            if requests:
                result[domain_config.name] = requests

        return result

    def run_bootstrap(self) -> BootstrapAuditReport:
        """Voer Ring 1 bootstrap uit.

        1. Haal bootstrap domeinen op
        2. Per domein: maak seed artikelen van seed questions
        3. Valideer via pipeline (curator)
        4. Audit coverage
        """
        domain_reports: list[BootstrapDomainReport] = []
        total_articles = 0
        ts = datetime.now(tz=UTC).isoformat()

        for domain_config in self._config.bootstrap_domains():
            articles = self._create_seed_articles(domain_config)
            if not articles:
                continue

            # Valideer en sla op via pipeline
            report = self._pipeline.run_seed(articles)
            articles_created = report.approved

            # Check RQ-dekking na bootstrap
            rq_coverage = self._check_rq_coverage(domain_config)

            covered = sum(1 for _, c in rq_coverage if c)
            total_rqs = len(rq_coverage)
            pct = (covered / total_rqs * 100.0) if total_rqs > 0 else 100.0

            domain_reports.append(
                BootstrapDomainReport(
                    domain=domain_config.name,
                    articles_created=articles_created,
                    rq_coverage=rq_coverage,
                    coverage_pct=pct,
                )
            )
            total_articles += articles_created

        total_domains = len(domain_reports)
        overall_pct = (
            sum(dr.coverage_pct for dr in domain_reports) / total_domains
            if total_domains > 0
            else 0.0
        )

        return BootstrapAuditReport(
            domain_reports=tuple(domain_reports),
            total_articles=total_articles,
            total_domains=total_domains,
            overall_coverage_pct=overall_pct,
            timestamp=ts,
        )

    def audit_coverage(self) -> BootstrapAuditReport:
        """Check post-bootstrap coverage zonder nieuwe artikelen te maken."""
        domain_reports: list[BootstrapDomainReport] = []
        total_articles = 0
        ts = datetime.now(tz=UTC).isoformat()

        for domain_config in self._config.bootstrap_domains():
            try:
                kd = KnowledgeDomain(domain_config.name)
            except ValueError:
                continue

            articles = self._store.list_by_domain(kd)
            rq_coverage = self._check_rq_coverage(domain_config)

            covered = sum(1 for _, c in rq_coverage if c)
            total_rqs = len(rq_coverage)
            pct = (covered / total_rqs * 100.0) if total_rqs > 0 else 100.0

            domain_reports.append(
                BootstrapDomainReport(
                    domain=domain_config.name,
                    articles_created=len(articles),
                    rq_coverage=rq_coverage,
                    coverage_pct=pct,
                )
            )
            total_articles += len(articles)

        total_domains = len(domain_reports)
        overall_pct = (
            sum(dr.coverage_pct for dr in domain_reports) / total_domains
            if total_domains > 0
            else 0.0
        )

        return BootstrapAuditReport(
            domain_reports=tuple(domain_reports),
            total_articles=total_articles,
            total_domains=total_domains,
            overall_coverage_pct=overall_pct,
            timestamp=ts,
        )

    def format_report(self, audit: BootstrapAuditReport) -> str:
        """Formatteer menselijk leesbaar rapport."""
        lines = [
            f"Bootstrap Audit — {audit.total_domains} domeinen, "
            f"{audit.total_articles} artikelen"
        ]
        for dr in audit.domain_reports:
            rq_detail = ", ".join(f"{rq}: {'ok' if c else 'ONTBREEKT'}" for rq, c in dr.rq_coverage)
            lines.append(
                f"  {dr.domain}: {dr.articles_created} artikelen, "
                f"dekking {dr.coverage_pct:.0f}% ({rq_detail})"
            )
        lines.append(f"Totale dekking: {audit.overall_coverage_pct:.0f}%")
        return "\n".join(lines)

    def _create_seed_articles(self, domain_config: DomainConfig) -> list[KnowledgeArticle]:
        """Maak BRONZE seed artikelen van seed questions."""
        articles: list[KnowledgeArticle] = []
        try:
            kd = KnowledgeDomain(domain_config.name)
        except ValueError:
            return articles

        for i, sq in enumerate(domain_config.seed_questions, 1):
            articles.append(
                KnowledgeArticle(
                    article_id=f"CBOOT-{domain_config.name}-{i:03d}",
                    title=sq.question,
                    content=(
                        f"Seed artikel voor {domain_config.name} ({sq.rq_tag}). "
                        f"Vraag: {sq.question} "
                        f"Dit is een BRONZE-niveau basis-artikel voor auto-bootstrap. "
                        f"Verrijking via researcher agent vereist voor hogere grading."
                    ),
                    domain=kd,
                    grade="BRONZE",
                    sources=("config-bootstrap",),
                    verification_pct=0.0,
                    date=datetime.now(tz=UTC).strftime("%Y-%m-%d"),
                    author="config-bootstrap",
                    rq_tags=(sq.rq_tag,),
                    domain_ring=domain_config.ring,
                )
            )
        return articles

    def _check_rq_coverage(self, domain_config: DomainConfig) -> tuple[tuple[str, bool], ...]:
        """Check RQ-dekking voor een domein."""
        try:
            kd = KnowledgeDomain(domain_config.name)
        except ValueError:
            return tuple((rq, False) for rq in domain_config.rq_focus)

        articles = self._store.list_by_domain(kd)
        article_rqs = set()
        for a in articles:
            article_rqs.update(a.rq_tags)

        return tuple((rq, rq in article_rqs) for rq in domain_config.rq_focus)
