"""
KnowledgeCurator — Kwaliteitspoort voor de kennispipeline.

Drie verantwoordelijkheden:
1. Ingest-validatie: kwaliteitspoort voor kennis de vectorstore ingaat
2. Freshness monitoring: detecteert verouderde kennis
3. Health audit: 4-dimensie gezondheidsrapport van de kennisbank
"""

from __future__ import annotations

from datetime import UTC, datetime

from devhub_core.contracts.curator_contracts import (
    CurationFinding,
    CurationReport,
    CurationVerdict,
    KnowledgeArticle,
    KnowledgeDomain,
    KnowledgeHealthReport,
    Observation,
    ObservationType,
)
from devhub_core.contracts.research_contracts import (
    ResearchDepth,
    ResearchQueue,
    ResearchRequest,
)


# Default freshness drempels per domein (in maanden)
DEFAULT_FRESHNESS_THRESHOLDS: dict[KnowledgeDomain, int] = {
    KnowledgeDomain.AI_ENGINEERING: 3,
    KnowledgeDomain.CLAUDE_SPECIFIC: 6,
    KnowledgeDomain.PYTHON_ARCHITECTURE: 12,
    KnowledgeDomain.DEVELOPMENT_METHODOLOGY: 12,
}

# Default health audit drempels
DEFAULT_MAX_SPECULATIVE_PCT = 60.0
DEFAULT_MAX_STALE_PCT = 20.0
DEFAULT_MAX_SINGLE_SOURCE_PCT = 70.0

# Grading validatie
GOLD_MIN_VERIFICATION_PCT = 80.0
SILVER_MIN_VERIFICATION_PCT = 50.0


class KnowledgeCurator:
    """Kwaliteitspoort tussen researcher en vectorstore.

    Audits knowledge, never modifies it. Reports findings.
    """

    def __init__(
        self,
        research_queue: ResearchQueue | None = None,
        freshness_thresholds: dict[KnowledgeDomain, int] | None = None,
    ) -> None:
        self._research_queue = research_queue
        self._freshness_thresholds = freshness_thresholds or DEFAULT_FRESHNESS_THRESHOLDS

    def validate_article(self, article: KnowledgeArticle) -> CurationReport:
        """Valideer een kennisartikel voor ingestie.

        Checks:
        - Bronvermelding aanwezig
        - Gradering onderbouwd (GOLD vereist verification_pct >= 80)
        - Content minimale kwaliteit
        """
        findings: list[CurationFinding] = []

        # Check: bronvermelding
        if not article.sources:
            findings.append(
                CurationFinding(
                    severity="ERROR",
                    category="sources",
                    description="Geen bronvermelding — Art. 5 vereist bronverwijzing",
                    article_id=article.article_id,
                )
            )

        # Check: gradering onderbouwing
        if article.grade == "GOLD" and article.verification_pct < GOLD_MIN_VERIFICATION_PCT:
            findings.append(
                CurationFinding(
                    severity="CRITICAL",
                    category="grade",
                    description=(
                        f"GOLD gradering vereist verification_pct >= {GOLD_MIN_VERIFICATION_PCT}%, "
                        f"maar is {article.verification_pct}%"
                    ),
                    article_id=article.article_id,
                )
            )
        elif article.grade == "SILVER" and article.verification_pct < SILVER_MIN_VERIFICATION_PCT:
            findings.append(
                CurationFinding(
                    severity="ERROR",
                    category="grade",
                    description=(
                        f"SILVER gradering vereist verification_pct "
                        f">= {SILVER_MIN_VERIFICATION_PCT}%, "
                        f"maar is {article.verification_pct}%"
                    ),
                    article_id=article.article_id,
                )
            )

        # Check: content minimale kwaliteit
        if len(article.content) < 50:
            findings.append(
                CurationFinding(
                    severity="WARNING",
                    category="content",
                    description=(
                        f"Content is kort ({len(article.content)} chars) " f"— mogelijk onvolledig"
                    ),
                    article_id=article.article_id,
                )
            )

        # Check: datum aanwezig
        if not article.date:
            findings.append(
                CurationFinding(
                    severity="WARNING",
                    category="freshness",
                    description="Geen datum opgegeven — freshness monitoring niet mogelijk",
                    article_id=article.article_id,
                )
            )

        # Determine verdict
        verdict = CurationVerdict.APPROVED
        if any(f.severity == "CRITICAL" for f in findings):
            verdict = CurationVerdict.REJECTED
        elif any(f.severity == "ERROR" for f in findings):
            verdict = CurationVerdict.NEEDS_REVISION

        return CurationReport(
            article_id=article.article_id,
            findings=tuple(findings),
            verdict=verdict,
        )

    def check_freshness(
        self,
        articles: list[KnowledgeArticle],
        reference_date: datetime | None = None,
    ) -> list[Observation]:
        """Scan artikelen op veroudering en genereer observaties.

        Genereert ook ResearchRequests voor hervalidatie als een queue beschikbaar is.
        """
        if reference_date is None:
            reference_date = datetime.now(tz=UTC)

        observations: list[Observation] = []
        obs_counter = 0

        for article in articles:
            if not article.date:
                continue

            try:
                article_date = datetime.fromisoformat(article.date)
                if article_date.tzinfo is None:
                    article_date = article_date.replace(tzinfo=UTC)
            except ValueError:
                continue

            threshold_months = self._freshness_thresholds.get(article.domain, 12)
            age_days = (reference_date - article_date).days
            threshold_days = threshold_months * 30

            if age_days > threshold_days:
                obs_counter += 1
                observations.append(
                    Observation(
                        observation_id=f"FRESH-{obs_counter:04d}",
                        observation_type=ObservationType.FRESHNESS_ALERT,
                        source_agent="knowledge-curator",
                        severity="WARNING",
                        payload=(
                            f"Artikel '{article.title}' ({article.article_id}) is "
                            f"{age_days} dagen oud (drempel: {threshold_days} dagen voor "
                            f"{article.domain.value})"
                        ),
                        timestamp=reference_date.isoformat(),
                    )
                )

                # Genereer ResearchRequest voor hervalidatie
                if self._research_queue is not None:
                    request = ResearchRequest(
                        request_id=f"REVALIDATE-{article.article_id}",
                        requesting_agent="knowledge-curator",
                        question=f"Hervalideer: {article.title} — is deze kennis nog actueel?",
                        domain=article.domain.value,
                        depth=ResearchDepth.QUICK,
                        priority=7,
                        context=f"Oorspronkelijke gradering: {article.grade}, "
                        f"leeftijd: {age_days} dagen",
                    )
                    self._research_queue.submit(request)

        return observations

    def audit_health(
        self,
        articles: list[KnowledgeArticle],
        reference_date: datetime | None = None,
    ) -> KnowledgeHealthReport:
        """4-dimensie health audit van de kennisbank.

        Dimensies:
        1. Gradering-distributie (penalty als >60% SPECULATIVE)
        2. Freshness (penalty als >20% over drempel)
        3. Source-ratio (penalty als >70% single-source)
        4. Domein-dekking (penalty voor lege domeinen)
        """
        if reference_date is None:
            reference_date = datetime.now(tz=UTC)

        findings: list[CurationFinding] = []

        if not articles:
            return KnowledgeHealthReport(
                overall_score=0.0,
                findings=(
                    CurationFinding(
                        severity="WARNING",
                        category="content",
                        description="Kennisbank is leeg",
                    ),
                ),
                timestamp=reference_date.isoformat(),
            )

        total = len(articles)

        # Dimensie 1: Gradering-distributie
        grading_dist: dict[str, int] = {"GOLD": 0, "SILVER": 0, "BRONZE": 0, "SPECULATIVE": 0}
        for a in articles:
            grading_dist[a.grade] = grading_dist.get(a.grade, 0) + 1

        speculative_pct = (grading_dist["SPECULATIVE"] / total) * 100
        grading_score = max(0.0, 100.0 - max(0.0, speculative_pct - DEFAULT_MAX_SPECULATIVE_PCT))
        if speculative_pct > DEFAULT_MAX_SPECULATIVE_PCT:
            findings.append(
                CurationFinding(
                    severity="WARNING",
                    category="grade",
                    description=(
                        f"{speculative_pct:.0f}% SPECULATIVE artikelen "
                        f"(drempel: {DEFAULT_MAX_SPECULATIVE_PCT}%)"
                    ),
                )
            )

        # Dimensie 2: Freshness
        stale_count = 0
        for a in articles:
            if not a.date:
                stale_count += 1
                continue
            try:
                article_date = datetime.fromisoformat(a.date)
                if article_date.tzinfo is None:
                    article_date = article_date.replace(tzinfo=UTC)
                threshold = self._freshness_thresholds.get(a.domain, 12) * 30
                if (reference_date - article_date).days > threshold:
                    stale_count += 1
            except ValueError:
                stale_count += 1

        stale_pct = (stale_count / total) * 100
        freshness_score = max(0.0, 100.0 - max(0.0, stale_pct - DEFAULT_MAX_STALE_PCT) * 2)
        if stale_pct > DEFAULT_MAX_STALE_PCT:
            findings.append(
                CurationFinding(
                    severity="WARNING",
                    category="freshness",
                    description=(
                        f"{stale_pct:.0f}% verouderde artikelen "
                        f"(drempel: {DEFAULT_MAX_STALE_PCT}%)"
                    ),
                )
            )

        # Dimensie 3: Source-ratio
        single_source = sum(1 for a in articles if len(a.sources) <= 1)
        single_source_pct = (single_source / total) * 100
        source_score = max(0.0, 100.0 - max(0.0, single_source_pct - DEFAULT_MAX_SINGLE_SOURCE_PCT))
        if single_source_pct > DEFAULT_MAX_SINGLE_SOURCE_PCT:
            findings.append(
                CurationFinding(
                    severity="WARNING",
                    category="sources",
                    description=(
                        f"{single_source_pct:.0f}% artikelen met ≤1 bron "
                        f"(drempel: {DEFAULT_MAX_SINGLE_SOURCE_PCT}%)"
                    ),
                )
            )

        # Dimensie 4: Domein-dekking
        domain_coverage: dict[str, int] = {d.value: 0 for d in KnowledgeDomain}
        for a in articles:
            domain_coverage[a.domain.value] = domain_coverage.get(a.domain.value, 0) + 1

        empty_domains = [d for d, c in domain_coverage.items() if c == 0]
        coverage_score = 100.0 - (len(empty_domains) / len(KnowledgeDomain)) * 100
        if empty_domains:
            findings.append(
                CurationFinding(
                    severity="INFO",
                    category="scope",
                    description=f"Lege domeinen: {', '.join(empty_domains)}",
                )
            )

        # Gewogen score
        overall = (
            grading_score * 0.25
            + freshness_score * 0.30
            + source_score * 0.20
            + coverage_score * 0.25
        )

        return KnowledgeHealthReport(
            grading_distribution=grading_dist,
            freshness_score=freshness_score,
            source_ratio_score=source_score,
            domain_coverage=domain_coverage,
            overall_score=round(overall, 1),
            findings=tuple(findings),
            timestamp=reference_date.isoformat(),
        )
