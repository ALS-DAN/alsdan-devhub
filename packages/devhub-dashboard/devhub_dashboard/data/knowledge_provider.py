"""Knowledge Provider — data-laag voor het Knowledge paneel.

Scant knowledge/ directory, parsed frontmatter, cached resultaten.
Volgt het CachedProvider pattern uit providers.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.article_parser import KnowledgeArticleParser, ParsedArticle
from devhub_dashboard.data.providers import CachedProvider


@dataclass(frozen=True)
class DomainCoverage:
    """Dekking van een kennisdomein."""

    domain: str
    ring: str  # "core" | "agent" | "project"
    article_count: int
    grade_distribution: dict[str, int]
    avg_freshness_days: float
    coverage_score: float  # 0.0-1.0
    has_gap: bool  # True als core-domein met 0 artikelen


@dataclass(frozen=True)
class FreshnessSummary:
    """Samenvatting freshness over hele kennisbank."""

    total_articles: int
    fresh_count: int  # <30 dagen
    aging_count: int  # 30-90 dagen
    stale_count: int  # >90 dagen
    avg_freshness_days: float
    freshness_score: float  # 0.0-1.0 (hoger = verser)


class KnowledgeProvider(CachedProvider):
    """Data provider voor het Knowledge paneel. Scant knowledge/ directory."""

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self._parser = KnowledgeArticleParser()
        self.__init_cache__()

    @property
    def _knowledge_root(self) -> Path:
        return self._config.devhub_root / "knowledge"

    def get_articles(
        self,
        *,
        domain: str | None = None,
        ring: str | None = None,
        grade: str | None = None,
        max_freshness_days: int | None = None,
        sort_by: str = "date_desc",
    ) -> list[ParsedArticle]:
        """Gefilterde en gesorteerde artikellijst."""
        articles = list(self._get_all_articles().values())

        if domain:
            articles = [a for a in articles if a.domain == domain]
        if ring:
            articles = [a for a in articles if a.ring == ring]
        if grade:
            articles = [a for a in articles if a.grade == grade.upper()]
        if max_freshness_days is not None:
            articles = [a for a in articles if a.freshness_days <= max_freshness_days]

        return self._sort_articles(articles, sort_by)

    def get_article(self, article_id: str) -> ParsedArticle | None:
        """Eén artikel ophalen op basis van article_id (relatief pad zonder .md)."""
        return self._get_all_articles().get(article_id)

    def get_domain_coverage(self) -> list[DomainCoverage]:
        """Dekkingsmatrix: per domein artikelen, grades, freshness."""
        return self._get_cached("domain_coverage", self._compute_coverage)

    def get_freshness_summary(self) -> FreshnessSummary:
        """Totaal freshness overzicht voor KPI cards."""
        return self._get_cached("freshness_summary", self._compute_freshness)

    def get_grading_distribution(self) -> dict[str, int]:
        """Grading verdeling over alle artikelen."""
        articles = self._get_all_articles().values()
        dist: dict[str, int] = {"GOLD": 0, "SILVER": 0, "BRONZE": 0, "SPECULATIVE": 0}
        for a in articles:
            if a.grade in dist:
                dist[a.grade] += 1
            else:
                dist.setdefault(a.grade, 0)
                dist[a.grade] += 1
        return dist

    def get_domains(self) -> list[str]:
        """Unieke domeinen in de kennisbank."""
        articles = self._get_all_articles().values()
        return sorted({a.domain for a in articles})

    def search(self, query: str) -> list[ParsedArticle]:
        """Keyword-based zoeken in titel, domein en summary."""
        if not query or len(query) < 2:
            return []
        q = query.lower()
        articles = self._get_all_articles().values()
        results = [
            a
            for a in articles
            if q in a.title.lower() or q in a.domain.lower() or q in a.summary.lower()
        ]
        return sorted(results, key=lambda a: a.freshness_days)

    def _get_all_articles(self) -> dict[str, ParsedArticle]:
        """Alle artikelen, gecached."""
        return self._get_cached("all_articles", self._scan_all)

    def _scan_all(self) -> dict[str, ParsedArticle]:
        """Scan alle .md bestanden in knowledge/."""
        root = self._knowledge_root
        if not root.exists():
            return {}

        articles: dict[str, ParsedArticle] = {}
        for md_file in sorted(root.rglob("*.md")):
            parsed = self._parser.parse(md_file, knowledge_root=root)
            if parsed:
                articles[parsed.article_id] = parsed
        return articles

    def _sort_articles(self, articles: list[ParsedArticle], sort_by: str) -> list[ParsedArticle]:
        """Sorteer artikelen op basis van sort_by parameter."""
        if sort_by == "date_desc":
            return sorted(articles, key=lambda a: a.date, reverse=True)
        if sort_by == "date_asc":
            return sorted(articles, key=lambda a: a.date)
        if sort_by == "grade_desc":
            grade_order = {"GOLD": 0, "SILVER": 1, "BRONZE": 2, "SPECULATIVE": 3}
            return sorted(articles, key=lambda a: grade_order.get(a.grade, 4))
        if sort_by == "grade_asc":
            grade_order = {"GOLD": 0, "SILVER": 1, "BRONZE": 2, "SPECULATIVE": 3}
            return sorted(articles, key=lambda a: grade_order.get(a.grade, 4), reverse=True)
        if sort_by == "freshness":
            return sorted(articles, key=lambda a: a.freshness_days)
        if sort_by == "domain":
            return sorted(articles, key=lambda a: a.domain)
        return articles

    def _compute_coverage(self) -> list[DomainCoverage]:
        """Bereken dekking per domein."""
        articles = self._get_all_articles().values()

        # Groepeer per domein
        domain_groups: dict[str, list[ParsedArticle]] = {}
        for a in articles:
            domain_groups.setdefault(a.domain, []).append(a)

        coverage: list[DomainCoverage] = []
        for domain, arts in sorted(domain_groups.items()):
            grade_dist: dict[str, int] = {}
            total_freshness = 0.0
            ring = arts[0].ring if arts else "project"

            for a in arts:
                grade_dist[a.grade] = grade_dist.get(a.grade, 0) + 1
                total_freshness += a.freshness_days

            avg_fresh = total_freshness / len(arts) if arts else 9999.0

            # Coverage score: combinatie van count, grade en freshness
            count_score = min(len(arts) / 5.0, 1.0)  # max bij 5 artikelen
            gold_silver = grade_dist.get("GOLD", 0) + grade_dist.get("SILVER", 0)
            grade_score = gold_silver / len(arts) if arts else 0.0
            fresh_score = max(0.0, 1.0 - (avg_fresh / 180.0))
            score = round((count_score * 0.4 + grade_score * 0.3 + fresh_score * 0.3), 2)

            coverage.append(
                DomainCoverage(
                    domain=domain,
                    ring=ring,
                    article_count=len(arts),
                    grade_distribution=grade_dist,
                    avg_freshness_days=round(avg_fresh, 1),
                    coverage_score=score,
                    has_gap=ring == "core" and len(arts) == 0,
                )
            )

        return coverage

    def _compute_freshness(self) -> FreshnessSummary:
        """Bereken freshness samenvatting."""
        articles = list(self._get_all_articles().values())
        if not articles:
            return FreshnessSummary(
                total_articles=0,
                fresh_count=0,
                aging_count=0,
                stale_count=0,
                avg_freshness_days=0.0,
                freshness_score=0.0,
            )

        fresh = sum(1 for a in articles if a.freshness_days < 30)
        aging = sum(1 for a in articles if 30 <= a.freshness_days < 90)
        stale = sum(1 for a in articles if a.freshness_days >= 90)
        total_days = sum(a.freshness_days for a in articles)
        avg = total_days / len(articles)

        # Score: percentage vers + half aging
        score = (fresh + aging * 0.5) / len(articles)

        return FreshnessSummary(
            total_articles=len(articles),
            fresh_count=fresh,
            aging_count=aging,
            stale_count=stale,
            avg_freshness_days=round(avg, 1),
            freshness_score=round(score, 2),
        )
