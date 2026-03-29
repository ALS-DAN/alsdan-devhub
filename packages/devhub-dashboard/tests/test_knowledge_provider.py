"""Tests voor KnowledgeProvider — caching, filtering, coverage, freshness."""

from pathlib import Path

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


def _setup_knowledge(tmp_path: Path) -> None:
    """Maak een realistische knowledge-structuur."""
    k = tmp_path / "knowledge"
    k.mkdir()

    # Root files (Formaat A — header+frontmatter)
    (k / "RESEARCH_AGENT_TEAMS.md").write_text(
        "# Research: Agent Teams SPIKE\n"
        "---\n"
        "sprint: 38\n"
        "kennisgradering: SILVER\n"
        "datum: 2026-03-28\n"
        "bron: SPRINT_INTAKE_AGENT_TEAMS\n"
        "---\n\n"
        "## Samenvatting\n\nDeze SPIKE onderzocht agent teams.\n"
    )
    (k / "RESEARCH_N8N.md").write_text(
        "# Research: n8n Event Scheduler\n"
        "---\n"
        "sprint: 40\n"
        "kennisgradering: GOLD\n"
        "datum: 2026-03-28\n"
        "---\n\n"
        "## Samenvatting\n\nn8n als externe scheduler.\n"
    )

    # Retrospectives (Formaat B — standaard frontmatter)
    retro = k / "retrospectives"
    retro.mkdir()
    (retro / "RETRO_DASHBOARD.md").write_text(
        "---\n"
        "title: Retrospective Dashboard NiceGUI\n"
        "domain: retrospectives\n"
        "grade: SILVER\n"
        "date: 2026-03-28\n"
        "author: devhub-sprint\n"
        "sprint: Dashboard NiceGUI\n"
        "---\n\n"
        "# Retrospective\n\nDashboard sprint was succesvol.\n"
    )
    (retro / "RETRO_OLD.md").write_text(
        "---\n"
        "title: Oude Retro\n"
        "domain: retrospectives\n"
        "grade: BRONZE\n"
        "date: 2025-01-01\n"
        "author: devhub-sprint\n"
        "---\n\n"
        "# Oude Retro\n\nDit is een oud artikel.\n"
    )


class TestGetArticles:
    """Artikelen ophalen en filteren."""

    def test_get_all_articles(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        articles = provider.get_articles()
        assert len(articles) == 4

    def test_filter_by_domain(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        articles = provider.get_articles(domain="retrospectives")
        assert len(articles) == 2
        assert all(a.domain == "retrospectives" for a in articles)

    def test_filter_by_grade(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        articles = provider.get_articles(grade="SILVER")
        assert len(articles) == 2
        assert all(a.grade == "SILVER" for a in articles)

    def test_filter_by_grade_case_insensitive(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        articles = provider.get_articles(grade="silver")
        assert len(articles) == 2

    def test_sort_by_date_desc(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        articles = provider.get_articles(sort_by="date_desc")
        dates = [a.date for a in articles if a.date]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_grade_desc(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        articles = provider.get_articles(sort_by="grade_desc")
        assert articles[0].grade == "GOLD"

    def test_empty_knowledge_dir(self, tmp_path: Path) -> None:
        (tmp_path / "knowledge").mkdir()
        provider = KnowledgeProvider(_make_config(tmp_path))
        assert provider.get_articles() == []

    def test_no_knowledge_dir(self, tmp_path: Path) -> None:
        provider = KnowledgeProvider(_make_config(tmp_path))
        assert provider.get_articles() == []


class TestGetArticle:
    """Enkel artikel ophalen."""

    def test_get_existing_article(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        article = provider.get_article("RESEARCH_AGENT_TEAMS")
        assert article is not None
        assert "Agent Teams" in article.title

    def test_get_subdirectory_article(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        article = provider.get_article("retrospectives/RETRO_DASHBOARD")
        assert article is not None
        assert "Dashboard" in article.title

    def test_get_nonexistent_article(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        assert provider.get_article("DOES_NOT_EXIST") is None


class TestDomainCoverage:
    """Domein-dekkingsmatrix."""

    def test_coverage_returns_all_domains(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        coverage = provider.get_domain_coverage()
        domains = {c.domain for c in coverage}
        assert "retrospectives" in domains
        assert "general" in domains

    def test_coverage_article_count(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        coverage = provider.get_domain_coverage()
        retro = next(c for c in coverage if c.domain == "retrospectives")
        assert retro.article_count == 2

    def test_coverage_grade_distribution(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        coverage = provider.get_domain_coverage()
        retro = next(c for c in coverage if c.domain == "retrospectives")
        assert retro.grade_distribution.get("SILVER", 0) == 1
        assert retro.grade_distribution.get("BRONZE", 0) == 1

    def test_coverage_score_between_0_and_1(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        for c in provider.get_domain_coverage():
            assert 0.0 <= c.coverage_score <= 1.0


class TestFreshnessSummary:
    """Freshness samenvatting."""

    def test_freshness_total(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        summary = provider.get_freshness_summary()
        assert summary.total_articles == 4

    def test_freshness_categories(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        summary = provider.get_freshness_summary()
        assert summary.fresh_count + summary.aging_count + summary.stale_count == 4

    def test_freshness_score_between_0_and_1(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        summary = provider.get_freshness_summary()
        assert 0.0 <= summary.freshness_score <= 1.0

    def test_empty_freshness(self, tmp_path: Path) -> None:
        (tmp_path / "knowledge").mkdir()
        provider = KnowledgeProvider(_make_config(tmp_path))
        summary = provider.get_freshness_summary()
        assert summary.total_articles == 0
        assert summary.freshness_score == 0.0


class TestGradingDistribution:
    """Grading verdeling."""

    def test_distribution_counts(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        dist = provider.get_grading_distribution()
        assert dist["GOLD"] == 1
        assert dist["SILVER"] == 2
        assert dist["BRONZE"] == 1


class TestSearch:
    """Keyword zoeken."""

    def test_search_by_title(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        results = provider.search("Agent Teams")
        assert len(results) >= 1
        assert any("Agent Teams" in r.title for r in results)

    def test_search_by_domain(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        results = provider.search("retrospectives")
        assert len(results) >= 2

    def test_search_empty_query(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        assert provider.search("") == []

    def test_search_short_query(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        assert provider.search("a") == []

    def test_search_no_results(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        assert provider.search("zzznonexistent") == []


class TestGetDomains:
    """Unieke domeinen."""

    def test_domains_list(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        domains = provider.get_domains()
        assert "retrospectives" in domains
        assert "general" in domains


class TestCaching:
    """CachedProvider caching gedrag."""

    def test_cache_returns_same_result(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        r1 = provider.get_articles()
        r2 = provider.get_articles()
        assert len(r1) == len(r2)

    def test_invalidate_cache(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        provider.get_articles()
        provider.invalidate_cache()
        # Should re-scan after invalidation
        articles = provider.get_articles()
        assert len(articles) == 4
