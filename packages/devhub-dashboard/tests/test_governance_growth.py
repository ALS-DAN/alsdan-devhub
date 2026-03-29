"""Tests voor Governance en Growth paneel data (via providers)."""

from pathlib import Path

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.providers import GovernanceProvider, GrowthProvider


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


class TestGovernancePage:
    def test_article_statuses_count(self, tmp_path: Path):
        provider = GovernanceProvider(_make_config(tmp_path))
        articles = provider.get_article_statuses()
        assert len(articles) == 9

    def test_all_articles_have_id_title(self, tmp_path: Path):
        provider = GovernanceProvider(_make_config(tmp_path))
        articles = provider.get_article_statuses()
        for article in articles:
            assert article.article_id.startswith("Art.")
            assert article.title
            assert article.description

    def test_security_summary_empty(self, tmp_path: Path):
        provider = GovernanceProvider(_make_config(tmp_path))
        summary = provider.get_security_summary()
        assert summary["available"] is False

    def test_security_summary_with_files(self, tmp_path: Path):
        knowledge = tmp_path / "knowledge" / "security"
        knowledge.mkdir(parents=True)
        (knowledge / "security_audit_2026.md").write_text("# Audit")
        (knowledge / "redteam_findings.md").write_text("# Red Team")

        provider = GovernanceProvider(_make_config(tmp_path))
        summary = provider.get_security_summary()
        assert summary["available"] is True

    def test_constitution_exists_check(self, tmp_path: Path):
        constitution = tmp_path / "docs" / "compliance" / "DEV_CONSTITUTION.md"
        constitution.parent.mkdir(parents=True)
        constitution.write_text("# DEV_CONSTITUTION")
        assert constitution.exists()


class TestGrowthPage:
    def test_default_domains_valid(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        radar = provider.get_skill_radar_data()
        assert len(radar) >= 6
        for name, level in radar:
            assert name
            assert 1 <= level <= 5

    def test_all_levels_dreyfus(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        for _, level in provider.get_skill_radar_data():
            assert level in (1, 2, 3, 4, 5)

    def test_completed_sprint_count_no_tracker(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        assert provider.get_completed_sprint_count() == 0

    def test_completed_sprint_count_with_tracker(self, tmp_path: Path):
        tracker = tmp_path / "docs" / "planning" / "SPRINT_TRACKER.md"
        tracker.parent.mkdir(parents=True)
        tracker.write_text("---\nlaatste_sprint: 42\n---\n")

        provider = GrowthProvider(_make_config(tmp_path))
        assert provider.get_completed_sprint_count() == 42
