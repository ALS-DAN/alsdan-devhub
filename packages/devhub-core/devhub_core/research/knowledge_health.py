"""
KnowledgeHealthChecker — Knowledge Health dimensie voor devhub-health skill.

Combineert domein-dekking, RQ-dekking, grading-distributie en freshness
tot een overall knowledge health score.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import TYPE_CHECKING

from devhub_core.contracts.curator_contracts import KnowledgeDomain

if TYPE_CHECKING:
    from devhub_core.research.knowledge_config import DomainConfig, KnowledgeConfig
    from devhub_core.research.knowledge_store import KnowledgeStore


@dataclass(frozen=True)
class KnowledgeHealthDimension:
    """Knowledge health rapport voor de health skill."""

    domain_coverage: tuple[tuple[str, int], ...] = ()  # (("ai_engineering", 8), ...)
    rq_coverage: tuple[tuple[str, float], ...] = ()  # (("ai_engineering", 83.3), ...)
    grading_distribution: tuple[tuple[str, int], ...] = ()  # (("GOLD", 2), ...)
    stale_domains: tuple[str, ...] = ()
    overall_score: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.overall_score <= 100.0:
            raise ValueError(f"overall_score must be between 0 and 100, got {self.overall_score}")


class KnowledgeHealthChecker:
    """Produceert knowledge health data voor de health skill.

    Combineert:
    - Domein-dekking: artikelen per domein
    - RQ-dekking: percentage RQs gedekt per domein
    - Grading-distributie: GOLD/SILVER/BRONZE/SPECULATIVE counts
    - Freshness: domeinen voorbij hun freshness_months drempel
    """

    def __init__(
        self,
        config: KnowledgeConfig,
        store: KnowledgeStore,
    ) -> None:
        self._config = config
        self._store = store

    def check(self) -> KnowledgeHealthDimension:
        """Voer volledige knowledge health check uit."""
        domain_coverage: list[tuple[str, int]] = []
        rq_coverage: list[tuple[str, float]] = []
        grade_counts: dict[str, int] = {
            "GOLD": 0,
            "SILVER": 0,
            "BRONZE": 0,
            "SPECULATIVE": 0,
        }
        stale: list[str] = []
        now = datetime.now(tz=UTC)

        for domain_config in self._config.domains:
            try:
                kd = KnowledgeDomain(domain_config.name)
            except ValueError:
                continue

            articles = self._store.list_by_domain(kd)
            domain_coverage.append((domain_config.name, len(articles)))

            # RQ-dekking
            article_rqs = set()
            for a in articles:
                article_rqs.update(a.rq_tags)

            if domain_config.rq_focus:
                covered = sum(1 for rq in domain_config.rq_focus if rq in article_rqs)
                pct = (covered / len(domain_config.rq_focus)) * 100.0
            else:
                pct = 100.0
            rq_coverage.append((domain_config.name, pct))

            # Grading
            for a in articles:
                if a.grade in grade_counts:
                    grade_counts[a.grade] += 1

            # Freshness
            if self._check_stale(domain_config, articles, now):
                stale.append(domain_config.name)

        # Overall score: gewogen gemiddelde
        score = self._calculate_score(domain_coverage, rq_coverage, grade_counts, stale)

        return KnowledgeHealthDimension(
            domain_coverage=tuple(domain_coverage),
            rq_coverage=tuple(rq_coverage),
            grading_distribution=tuple(grade_counts.items()),
            stale_domains=tuple(stale),
            overall_score=score,
        )

    def _check_stale(
        self,
        domain_config: DomainConfig,
        articles: list,
        now: datetime,
    ) -> bool:
        """Check of een domein verouderde artikelen heeft."""
        if not articles:
            return False

        freshness_days = domain_config.freshness_months * 30
        for article in articles:
            if article.date:
                try:
                    article_date = datetime.fromisoformat(article.date).replace(tzinfo=UTC)
                    age_days = (now - article_date).days
                    if age_days > freshness_days:
                        return True
                except (ValueError, TypeError):
                    continue
        return False

    def _calculate_score(
        self,
        domain_coverage: list[tuple[str, int]],
        rq_coverage: list[tuple[str, float]],
        grade_counts: dict[str, int],
        stale: list[str],
    ) -> float:
        """Bereken overall score (0-100).

        Gewichten:
        - 30% domein-dekking (domeinen met >= 1 artikel)
        - 30% RQ-dekking (gemiddelde RQ%)
        - 25% grading-kwaliteit (% SILVER+GOLD van totaal)
        - 15% freshness (% niet-stale domeinen)
        """
        total_domains = len(domain_coverage)
        if total_domains == 0:
            return 0.0

        # Domein-dekking: % domeinen met minstens 1 artikel
        domains_with_articles = sum(1 for _, count in domain_coverage if count > 0)
        domain_score = (domains_with_articles / total_domains) * 100.0

        # RQ-dekking: gemiddeld percentage
        rq_score = sum(pct for _, pct in rq_coverage) / total_domains

        # Grading: % SILVER+GOLD
        total_articles = sum(grade_counts.values())
        if total_articles > 0:
            quality = grade_counts.get("GOLD", 0) + grade_counts.get("SILVER", 0)
            grade_score = (quality / total_articles) * 100.0
        else:
            grade_score = 0.0

        # Freshness: % niet-stale domeinen
        domains_with_content = sum(1 for _, c in domain_coverage if c > 0)
        if domains_with_content > 0:
            fresh_score = ((domains_with_content - len(stale)) / domains_with_content) * 100.0
        else:
            fresh_score = 100.0

        return min(
            100.0,
            max(
                0.0,
                (domain_score * 0.30 + rq_score * 0.30 + grade_score * 0.25 + fresh_score * 0.15),
            ),
        )
