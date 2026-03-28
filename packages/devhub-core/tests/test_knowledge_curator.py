"""Tests voor KnowledgeCurator agent — 18 tests."""

from __future__ import annotations

from datetime import UTC, datetime

from devhub_core.agents.knowledge_curator import (
    GOLD_MIN_VERIFICATION_PCT,
    KnowledgeCurator,
)
from devhub_core.contracts.curator_contracts import (
    CurationVerdict,
    KnowledgeArticle,
    KnowledgeDomain,
    ObservationType,
)
from devhub_core.research.in_memory_queue import InMemoryResearchQueue


# Fixed reference date for deterministic tests
REF_DATE = datetime(2026, 3, 27, tzinfo=UTC)


def _make_article(**overrides) -> KnowledgeArticle:
    """Helper voor een valide KnowledgeArticle."""
    defaults = {
        "article_id": "ART-001",
        "title": "Test Article",
        "content": (
            "Dit is een test artikel met voldoende content "
            "voor alle validatie checks in de curator."
        ),
        "domain": KnowledgeDomain.AI_ENGINEERING,
        "grade": "SILVER",
        "sources": ("https://example.com", "https://docs.python.org"),
        "verification_pct": 60.0,
        "date": "2026-03-01",
    }
    defaults.update(overrides)
    return KnowledgeArticle(**defaults)


# --- validate_article tests ---


class TestValidateArticle:
    def test_validate_article_approved(self) -> None:
        """Artikel met alle checks passed krijgt APPROVED."""
        curator = KnowledgeCurator()
        article = _make_article()
        report = curator.validate_article(article)
        assert report.verdict == CurationVerdict.APPROVED
        assert report.is_approved is True
        assert len(report.findings) == 0

    def test_validate_article_no_sources(self) -> None:
        """Artikel zonder bronnen krijgt ERROR finding."""
        curator = KnowledgeCurator()
        article = _make_article(sources=())
        report = curator.validate_article(article)
        assert report.verdict == CurationVerdict.NEEDS_REVISION
        assert any(f.category == "sources" and f.severity == "ERROR" for f in report.findings)

    def test_validate_article_gold_low_verification(self) -> None:
        """GOLD met lage verification_pct wordt REJECTED (CRITICAL)."""
        curator = KnowledgeCurator()
        article = _make_article(grade="GOLD", verification_pct=50.0)
        report = curator.validate_article(article)
        assert report.verdict == CurationVerdict.REJECTED
        assert any(f.severity == "CRITICAL" and f.category == "grade" for f in report.findings)

    def test_validate_article_gold_high_verification_approved(self) -> None:
        """GOLD met hoge verification_pct is APPROVED."""
        curator = KnowledgeCurator()
        article = _make_article(grade="GOLD", verification_pct=GOLD_MIN_VERIFICATION_PCT)
        report = curator.validate_article(article)
        assert report.verdict == CurationVerdict.APPROVED

    def test_validate_article_silver_low_verification(self) -> None:
        """SILVER met lage verification_pct krijgt ERROR -> NEEDS_REVISION."""
        curator = KnowledgeCurator()
        article = _make_article(grade="SILVER", verification_pct=30.0)
        report = curator.validate_article(article)
        assert report.verdict == CurationVerdict.NEEDS_REVISION
        assert any(f.severity == "ERROR" and f.category == "grade" for f in report.findings)

    def test_validate_article_short_content(self) -> None:
        """Korte content krijgt WARNING."""
        curator = KnowledgeCurator()
        article = _make_article(content="Kort.")
        report = curator.validate_article(article)
        assert any(f.category == "content" and f.severity == "WARNING" for f in report.findings)
        # WARNING alone should not block approval
        assert report.verdict == CurationVerdict.APPROVED

    def test_validate_article_no_date(self) -> None:
        """Artikel zonder datum krijgt WARNING."""
        curator = KnowledgeCurator()
        article = _make_article(date="")
        report = curator.validate_article(article)
        assert any(f.category == "freshness" and f.severity == "WARNING" for f in report.findings)

    def test_validate_article_multiple_findings(self) -> None:
        """Artikel met meerdere problemen genereert meerdere findings."""
        curator = KnowledgeCurator()
        article = _make_article(
            sources=(),
            date="",
            content="Kort.",
        )
        report = curator.validate_article(article)
        assert len(report.findings) >= 3
        categories = {f.category for f in report.findings}
        assert "sources" in categories
        assert "freshness" in categories
        assert "content" in categories


# --- check_freshness tests ---


class TestCheckFreshness:
    def test_check_freshness_stale_article(self) -> None:
        """Artikel ouder dan drempel genereert FRESHNESS_ALERT."""
        curator = KnowledgeCurator()
        # AI_ENGINEERING drempel = 3 maanden = 90 dagen
        # Artikel van 6 maanden geleden is stale
        article = _make_article(date="2025-09-01")
        observations = curator.check_freshness([article], reference_date=REF_DATE)
        assert len(observations) == 1
        assert observations[0].observation_type == ObservationType.FRESHNESS_ALERT
        assert observations[0].severity == "WARNING"

    def test_check_freshness_fresh_article(self) -> None:
        """Vers artikel genereert geen observaties."""
        curator = KnowledgeCurator()
        article = _make_article(date="2026-03-20")
        observations = curator.check_freshness([article], reference_date=REF_DATE)
        assert len(observations) == 0

    def test_check_freshness_generates_research_request(self) -> None:
        """Stale artikel met queue genereert ResearchRequest."""
        queue = InMemoryResearchQueue()
        curator = KnowledgeCurator(research_queue=queue)
        article = _make_article(date="2025-06-01")
        curator.check_freshness([article], reference_date=REF_DATE)
        pending = queue.pending()
        assert len(pending) == 1
        assert pending[0].request_id == "REVALIDATE-ART-001"
        assert pending[0].requesting_agent == "knowledge-curator"

    def test_check_freshness_no_date_skipped(self) -> None:
        """Artikel zonder datum wordt overgeslagen."""
        curator = KnowledgeCurator()
        article = _make_article(date="")
        observations = curator.check_freshness([article], reference_date=REF_DATE)
        assert len(observations) == 0

    def test_check_freshness_domain_thresholds(self) -> None:
        """Verschillende domeinen hebben verschillende drempels."""
        curator = KnowledgeCurator()
        # PYTHON_ARCHITECTURE drempel = 12 maanden
        # Artikel van 6 maanden geleden is NIET stale voor python_architecture
        article = _make_article(
            domain=KnowledgeDomain.PYTHON_ARCHITECTURE,
            date="2025-09-27",
        )
        observations = curator.check_freshness([article], reference_date=REF_DATE)
        assert len(observations) == 0

        # Maar wel stale voor AI_ENGINEERING (drempel 3 maanden)
        article_ai = _make_article(
            domain=KnowledgeDomain.AI_ENGINEERING,
            date="2025-09-27",
        )
        observations_ai = curator.check_freshness([article_ai], reference_date=REF_DATE)
        assert len(observations_ai) == 1


# --- audit_health tests ---


class TestAuditHealth:
    def test_audit_health_balanced(self) -> None:
        """Gebalanceerde kennisbank scoort hoog."""
        articles = [
            _make_article(
                article_id=f"ART-{i}",
                domain=domain,
                grade="SILVER",
                sources=("src1", "src2"),
                date="2026-03-01",
            )
            for i, domain in enumerate(KnowledgeDomain, start=1)
        ]
        # Maak eerste GOLD met hoge verificatie
        articles[0] = _make_article(
            article_id="ART-1",
            domain=KnowledgeDomain.AI_ENGINEERING,
            grade="GOLD",
            verification_pct=90.0,
            sources=("src1", "src2"),
            date="2026-03-01",
        )
        curator = KnowledgeCurator()
        report = curator.audit_health(articles, reference_date=REF_DATE)
        assert report.overall_score >= 80.0
        assert report.freshness_score == 100.0
        # All domains covered
        for domain in KnowledgeDomain:
            assert report.domain_coverage[domain.value] >= 1

    def test_audit_health_speculative_heavy(self) -> None:
        """Kennisbank met veel SPECULATIVE scoort lager op grading."""
        articles = [
            _make_article(
                article_id=f"ART-{i}",
                grade="SPECULATIVE",
                date="2026-03-01",
                sources=("src1", "src2"),
            )
            for i in range(10)
        ]
        curator = KnowledgeCurator()
        report = curator.audit_health(articles, reference_date=REF_DATE)
        assert report.grading_distribution["SPECULATIVE"] == 10
        assert any(f.category == "grade" for f in report.findings)

    def test_audit_health_stale_heavy(self) -> None:
        """Kennisbank met veel verouderde artikelen scoort lager op freshness."""
        articles = [
            _make_article(
                article_id=f"ART-{i}",
                date="2024-01-01",  # Very old
                sources=("src1", "src2"),
            )
            for i in range(10)
        ]
        curator = KnowledgeCurator()
        report = curator.audit_health(articles, reference_date=REF_DATE)
        assert report.freshness_score < 100.0
        assert any(f.category == "freshness" for f in report.findings)

    def test_audit_health_single_source_heavy(self) -> None:
        """Kennisbank met veel single-source artikelen scoort lager."""
        articles = [
            _make_article(
                article_id=f"ART-{i}",
                sources=("only-one",),
                date="2026-03-01",
            )
            for i in range(10)
        ]
        curator = KnowledgeCurator()
        report = curator.audit_health(articles, reference_date=REF_DATE)
        assert report.source_ratio_score < 100.0
        assert any(f.category == "sources" for f in report.findings)

    def test_audit_health_empty_domains(self) -> None:
        """Alleen artikelen in 1 domein genereert scope finding."""
        articles = [
            _make_article(
                article_id=f"ART-{i}",
                domain=KnowledgeDomain.AI_ENGINEERING,
                date="2026-03-01",
                sources=("src1", "src2"),
            )
            for i in range(4)
        ]
        curator = KnowledgeCurator()
        report = curator.audit_health(articles, reference_date=REF_DATE)
        empty = [d for d, c in report.domain_coverage.items() if c == 0]
        assert len(empty) == 15  # 16 domeinen - 1 gevuld = 15 leeg
        assert any(f.category == "scope" for f in report.findings)

    def test_audit_health_empty_list(self) -> None:
        """Lege kennisbank retourneert score 0 met finding."""
        curator = KnowledgeCurator()
        report = curator.audit_health([], reference_date=REF_DATE)
        assert report.overall_score == 0.0
        assert len(report.findings) == 1
        assert report.findings[0].description == "Kennisbank is leeg"
