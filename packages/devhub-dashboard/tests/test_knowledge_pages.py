"""Tests voor Knowledge en Research pagina's — data-laag verificatie."""

from pathlib import Path

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider
from devhub_dashboard.data.research_queue import (
    RequestStatus,
    ResearchQueueManager,
)


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


def _setup_knowledge(tmp_path: Path) -> None:
    """Maak een realistische knowledge-structuur."""
    k = tmp_path / "knowledge"
    k.mkdir()

    (k / "RESEARCH_TEST.md").write_text(
        "# Research: Test\n"
        "---\n"
        "kennisgradering: SILVER\n"
        "datum: 2026-03-28\n"
        "---\n\n"
        "## Samenvatting\n\nTest content.\n"
    )

    retro = k / "retrospectives"
    retro.mkdir()
    (retro / "RETRO_TEST.md").write_text(
        "---\n"
        "title: Test Retro\n"
        "domain: retrospectives\n"
        "grade: GOLD\n"
        "date: 2026-03-28\n"
        "author: test\n"
        "---\n\nRetro content.\n"
    )


class TestKnowledgePageData:
    """Test dat de knowledge pagina correcte data krijgt."""

    def test_knowledge_provider_integrates_with_config(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        config = _make_config(tmp_path)
        provider = KnowledgeProvider(config)

        articles = provider.get_articles()
        assert len(articles) == 2

    def test_freshness_summary_for_kpi(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        summary = provider.get_freshness_summary()
        assert summary.total_articles == 2

    def test_grading_for_kpi(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        grading = provider.get_grading_distribution()
        assert grading["GOLD"] == 1
        assert grading["SILVER"] == 1

    def test_domain_coverage_for_matrix(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        coverage = provider.get_domain_coverage()
        assert len(coverage) >= 1

    def test_article_detail_lookup(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        article = provider.get_article("RESEARCH_TEST")
        assert article is not None
        assert article.grade == "SILVER"

    def test_article_detail_subdirectory(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        article = provider.get_article("retrospectives/RETRO_TEST")
        assert article is not None
        assert article.grade == "GOLD"


class TestResearchPageData:
    """Test dat de research pagina correcte data krijgt met v2 velden."""

    def test_create_v2_request(self, tmp_path: Path) -> None:
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(
            topic="Test Research",
            domain="ai_engineering",
            depth="DEEP",
        )
        assert item.item_id
        assert item.status == "pending"

    def test_v2_fields_persist_after_update(self, tmp_path: Path) -> None:
        import json

        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Persist", domain="ai")

        # Simuleer v2 velden schrijven (zoals het formulier doet)
        item_path = mgr._dir / f"{item.item_id}.json"
        data = json.loads(item_path.read_text(encoding="utf-8"))
        data["background"] = "Motivatie tekst"
        data["research_questions"] = ["RQ1: Hoe?", "RQ2: Waarom?"]
        data["scope_in"] = "Python"
        data["scope_out"] = "JavaScript"
        data["expected_grade"] = "SILVER"
        item_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Herlees en verifieer
        loaded = mgr.get_item(item.item_id)
        assert loaded is not None
        assert loaded.background == "Motivatie tekst"
        assert len(loaded.research_questions) == 2
        assert loaded.scope_in == "Python"
        assert loaded.expected_grade == "SILVER"

    def test_research_detail_data(self, tmp_path: Path) -> None:
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Detail", domain="ai")

        # Simuleer status-flow
        mgr.update_status(item.item_id, RequestStatus.APPROVED)
        mgr.update_status(item.item_id, RequestStatus.IN_PROGRESS)

        loaded = mgr.get_item(item.item_id)
        assert loaded is not None
        assert loaded.status == "in_progress"
        assert len(loaded.status_history) == 2

    def test_review_status_flow(self, tmp_path: Path) -> None:
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Review", domain="ai")

        mgr.update_status(item.item_id, RequestStatus.APPROVED)
        mgr.update_status(item.item_id, RequestStatus.IN_PROGRESS)
        mgr.update_status(item.item_id, RequestStatus.REVIEW)

        loaded = mgr.get_item(item.item_id)
        assert loaded is not None
        assert loaded.status == "review"


class TestOverviewKnowledgeKPI:
    """Test dat overview pagina knowledge data kan ophalen."""

    def test_overview_with_knowledge_provider(self, tmp_path: Path) -> None:
        _setup_knowledge(tmp_path)
        provider = KnowledgeProvider(_make_config(tmp_path))
        freshness = provider.get_freshness_summary()
        assert freshness.total_articles > 0
        assert 0.0 <= freshness.freshness_score <= 1.0

    def test_overview_without_knowledge(self, tmp_path: Path) -> None:
        """Overview moet werken zonder knowledge_provider."""
        provider = KnowledgeProvider(_make_config(tmp_path))
        freshness = provider.get_freshness_summary()
        assert freshness.total_articles == 0
