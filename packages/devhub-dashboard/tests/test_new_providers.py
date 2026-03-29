"""Tests voor GovernanceProvider, GrowthProvider, CachedProvider, HealthProvider 7-dim."""

import json
import time
from pathlib import Path

from devhub_core.contracts.node_interface import HealthStatus

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.providers import (
    CachedProvider,
    ComplianceScore,
    GovernanceProvider,
    GrowthProvider,
    HealthProvider,
)


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


def _setup_full_structure(tmp_path: Path) -> None:
    """Maak een volledige project-structuur voor tests."""
    # CLAUDE.md
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (tmp_path / ".claude" / "CLAUDE.md").write_text("# DevHub")

    # Packages
    for name in ["devhub-core", "devhub-storage"]:
        pkg = tmp_path / "packages" / name
        pkg.mkdir(parents=True)
        (pkg / "pyproject.toml").write_text(f'[project]\nname = "{name}"')

    # NodeInterface ABC
    ni_dir = tmp_path / "packages" / "devhub-core" / "devhub_core" / "contracts"
    ni_dir.mkdir(parents=True)
    (ni_dir / "node_interface.py").write_text("class NodeInterface: pass")

    # Test bestanden
    tests_dir = tmp_path / "packages" / "devhub-core" / "tests"
    tests_dir.mkdir(parents=True)
    for i in range(3):
        (tests_dir / f"test_{i}.py").write_text("def test(): pass")

    # Config
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "nodes.yml").write_text("nodes: []")

    # Knowledge
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "article1.md").write_text("# Article\nGrading: SILVER")
    (knowledge_dir / "article2.md").write_text("# No grading here")

    # Sprint tracker
    tracker = tmp_path / "docs" / "planning" / "SPRINT_TRACKER.md"
    tracker.parent.mkdir(parents=True)
    tracker.write_text(
        "---\nlaatste_sprint: 43\ntest_baseline: 1489\n"
        "laatst_bijgewerkt: 2026-03-28\n---\n"
        "Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 3 ✅ → Fase 4 🔄 → Fase 5 🔲\n"
    )

    # Docs directories
    (tmp_path / "docs" / "compliance").mkdir(parents=True)
    (tmp_path / "docs" / "compliance" / "DEV_CONSTITUTION.md").write_text("# Constitution")
    (tmp_path / "docs" / "golden-paths").mkdir(parents=True)

    # Inbox
    inbox = tmp_path / "docs" / "planning" / "inbox"
    inbox.mkdir(parents=True)


# ---------------------------------------------------------------------------
# CachedProvider
# ---------------------------------------------------------------------------


class TestCachedProvider:
    def test_cache_returns_same_value(self):
        provider = CachedProvider()
        provider.__init_cache__(ttl=10.0)
        call_count = 0

        def loader():
            nonlocal call_count
            call_count += 1
            return "result"

        v1 = provider._get_cached("key", loader)
        v2 = provider._get_cached("key", loader)
        assert v1 == v2 == "result"
        assert call_count == 1  # Loader called only once

    def test_cache_invalidate(self):
        provider = CachedProvider()
        provider.__init_cache__(ttl=10.0)
        call_count = 0

        def loader():
            nonlocal call_count
            call_count += 1
            return call_count

        provider._get_cached("key", loader)
        provider.invalidate_cache()
        v2 = provider._get_cached("key", loader)
        assert v2 == 2

    def test_cache_ttl_expiry(self):
        provider = CachedProvider()
        provider.__init_cache__(ttl=0.01)  # 10ms TTL
        call_count = 0

        def loader():
            nonlocal call_count
            call_count += 1
            return call_count

        provider._get_cached("key", loader)
        time.sleep(0.02)
        v2 = provider._get_cached("key", loader)
        assert v2 == 2


# ---------------------------------------------------------------------------
# HealthProvider 7-dim
# ---------------------------------------------------------------------------


class TestHealthProvider7Dim:
    def test_seven_dimensions(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        assert len(report.checks) == 7

    def test_dimension_names(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        dims = {c.dimension for c in report.checks}
        assert dims == {
            "tests",
            "packages",
            "dependencies",
            "architecture",
            "knowledge_health",
            "security",
            "sprint_hygiene",
        }

    def test_tests_dimension_healthy(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        test_check = next(c for c in report.checks if c.dimension == "tests")
        assert test_check.status == HealthStatus.HEALTHY

    def test_architecture_healthy_with_full_structure(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        arch_check = next(c for c in report.checks if c.dimension == "architecture")
        assert arch_check.status == HealthStatus.HEALTHY

    def test_knowledge_health_with_partial_grading(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        kh_check = next(c for c in report.checks if c.dimension == "knowledge_health")
        # 1/2 articles graded = 50% < 70% threshold
        assert kh_check.status == HealthStatus.ATTENTION

    def test_sprint_hygiene_healthy(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        sh_check = next(c for c in report.checks if c.dimension == "sprint_hygiene")
        assert sh_check.status == HealthStatus.HEALTHY

    def test_security_no_audit(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        sec_check = next(c for c in report.checks if c.dimension == "security")
        # Geen security bestanden in knowledge/
        assert sec_check.status == HealthStatus.ATTENTION

    def test_security_with_audit(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        (tmp_path / "knowledge" / "security_audit.md").write_text("# Audit")
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        sec_check = next(c for c in report.checks if c.dimension == "security")
        assert sec_check.status == HealthStatus.HEALTHY

    def test_get_knowledge_metrics(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        count, freshness = provider.get_knowledge_metrics()
        assert count == 2
        assert 0.0 < freshness < 1.0

    def test_caching_works(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        r1 = provider.get_health_report()
        r2 = provider.get_health_report()
        # Timestamps differ but checks should be same cached list
        assert len(r1.checks) == len(r2.checks)


# ---------------------------------------------------------------------------
# GovernanceProvider
# ---------------------------------------------------------------------------


class TestGovernanceProvider:
    def test_compliance_score_full_structure(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = GovernanceProvider(_make_config(tmp_path))
        score = provider.get_compliance_score()
        assert isinstance(score, ComplianceScore)
        assert score.total == 9
        assert score.active > 0

    def test_compliance_percentage(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = GovernanceProvider(_make_config(tmp_path))
        score = provider.get_compliance_score()
        assert 0 <= score.percentage <= 100

    def test_article_statuses_count(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = GovernanceProvider(_make_config(tmp_path))
        articles = provider.get_article_statuses()
        assert len(articles) == 9

    def test_article_with_claude_md(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = GovernanceProvider(_make_config(tmp_path))
        articles = provider.get_article_statuses()
        art1 = next(a for a in articles if a.article_id == "Art. 1")
        assert art1.status == "active"

    def test_article_without_golden_paths(self, tmp_path: Path):
        """Art. 7 checks golden-paths/ existence."""
        config = _make_config(tmp_path)
        # Geen golden-paths directory
        provider = GovernanceProvider(config)
        articles = provider.get_article_statuses()
        art7 = next(a for a in articles if a.article_id == "Art. 7")
        assert art7.status == "attention"

    def test_security_summary_no_data(self, tmp_path: Path):
        provider = GovernanceProvider(_make_config(tmp_path))
        summary = provider.get_security_summary()
        assert summary["available"] is False

    def test_security_summary_with_data(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        (tmp_path / "knowledge" / "redteam_report.json").write_text(
            json.dumps({"audit_id": "test", "asi_coverage": {"ASI01": "MITIGATED"}})
        )
        provider = GovernanceProvider(_make_config(tmp_path))
        summary = provider.get_security_summary()
        assert summary["available"] is True
        assert summary["report_count"] >= 1

    def test_asi_coverage_defaults(self, tmp_path: Path):
        provider = GovernanceProvider(_make_config(tmp_path))
        coverage = provider.get_asi_coverage()
        assert len(coverage) == 10
        assert all(v == "NOT_ASSESSED" for v in coverage.values())


# ---------------------------------------------------------------------------
# GrowthProvider
# ---------------------------------------------------------------------------


class TestGrowthProvider:
    def test_default_skill_radar(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        radar = provider.get_skill_radar_data()
        assert len(radar) == 8  # Default domains
        assert radar[0][0] == "Python"
        assert radar[0][1] == 2

    def test_skill_radar_from_json(self, tmp_path: Path):
        growth_dir = tmp_path / "data" / "growth"
        growth_dir.mkdir(parents=True)
        (growth_dir / "skill_radar_2026.json").write_text(
            json.dumps(
                {
                    "domains": [
                        {"name": "Python", "level": 3},
                        {"name": "Testing", "level": 2},
                    ]
                }
            )
        )
        provider = GrowthProvider(_make_config(tmp_path))
        radar = provider.get_skill_radar_data()
        assert len(radar) == 2
        assert radar[0] == ("Python", 3)

    def test_skill_radar_from_yaml(self, tmp_path: Path):
        radar_dir = tmp_path / "knowledge" / "skill_radar"
        radar_dir.mkdir(parents=True)
        (radar_dir / "SKILL_RADAR_PROFILE_2026-03-26.yaml").write_text(
            "domains:\n" "  - name: 'Python'\n" "    level: 3\n" "  - name: 'AI'\n" "    level: 2\n"
        )
        provider = GrowthProvider(_make_config(tmp_path))
        radar = provider.get_skill_radar_data()
        assert len(radar) == 2
        assert radar[0] == ("Python", 3)

    def test_challenges_empty(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        assert provider.get_challenges() == []

    def test_challenges_from_json(self, tmp_path: Path):
        challenges_dir = tmp_path / "data" / "challenges"
        challenges_dir.mkdir(parents=True)
        (challenges_dir / "challenge_1.json").write_text(
            json.dumps(
                {
                    "challenge_id": "c1",
                    "domain": "Python",
                    "status": "PROPOSED",
                }
            )
        )
        provider = GrowthProvider(_make_config(tmp_path))
        challenges = provider.get_challenges()
        assert len(challenges) == 1
        assert challenges[0]["challenge_id"] == "c1"

    def test_recommendations_empty(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        assert provider.get_recommendations() == []

    def test_t_shape(self, tmp_path: Path):
        provider = GrowthProvider(_make_config(tmp_path))
        broad, deep = provider.get_t_shape()
        # Defaults: Python(2), AI(2), Testing(2), Docs(2), PM(2) = level 2+
        assert len(broad) >= 5
        assert len(deep) == 0  # No level 3+ in defaults

    def test_t_shape_with_deep(self, tmp_path: Path):
        growth_dir = tmp_path / "data" / "growth"
        growth_dir.mkdir(parents=True)
        (growth_dir / "skill_radar.json").write_text(
            json.dumps(
                {
                    "domains": [
                        {"name": "Python", "level": 3},
                        {"name": "Testing", "level": 2},
                        {"name": "Rust", "level": 1},
                    ]
                }
            )
        )
        provider = GrowthProvider(_make_config(tmp_path))
        broad, deep = provider.get_t_shape()
        assert "Python" in broad
        assert "Testing" in broad
        assert "Python" in deep
        assert "Testing" not in deep

    def test_completed_sprint_count(self, tmp_path: Path):
        _setup_full_structure(tmp_path)
        provider = GrowthProvider(_make_config(tmp_path))
        assert provider.get_completed_sprint_count() == 43


# ---------------------------------------------------------------------------
# HealthSnapshot backward compatibility
# ---------------------------------------------------------------------------


class TestHealthSnapshotBackwardCompat:
    def test_old_snapshot_loads_with_new_fields(self, tmp_path: Path):
        from devhub_dashboard.data.history import HealthSnapshot

        old_data = {
            "timestamp": "2026-03-28T12:00:00",
            "overall": "healthy",
            "dimensions_checked": 2,
            "p1_count": 0,
            "p2_count": 0,
            "test_files": 50,
            "packages": 4,
        }
        snapshot = HealthSnapshot.from_dict(old_data)
        assert snapshot.knowledge_items == 0
        assert snapshot.knowledge_freshness == 0.0
        assert snapshot.dependency_issues == 0
        assert snapshot.sprint_hygiene_score == 1.0

    def test_new_snapshot_roundtrip(self, tmp_path: Path):
        from devhub_dashboard.data.history import HealthSnapshot

        snapshot = HealthSnapshot(
            timestamp="2026-03-29T10:00:00",
            overall="healthy",
            dimensions_checked=7,
            p1_count=0,
            p2_count=1,
            test_files=142,
            packages=5,
            knowledge_items=10,
            knowledge_freshness=0.7,
            dependency_issues=2,
            sprint_hygiene_score=0.9,
        )
        data = snapshot.to_dict()
        restored = HealthSnapshot.from_dict(data)
        assert restored == snapshot
        assert restored.knowledge_items == 10
        assert restored.sprint_hygiene_score == 0.9
