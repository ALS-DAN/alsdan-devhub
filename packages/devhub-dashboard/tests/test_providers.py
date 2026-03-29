"""Tests voor data providers — HealthProvider en PlanningProvider."""

from pathlib import Path

from devhub_core.contracts.node_interface import HealthStatus

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.providers import HealthProvider, PlanningProvider


def _make_config(tmp_path: Path) -> DashboardConfig:
    """Helper: maak config met tmp_path als devhub_root."""
    return DashboardConfig(devhub_root=tmp_path)


class TestHealthProvider:
    def test_get_health_report_empty_root(self, tmp_path: Path):
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        assert report.node_id == "devhub"
        assert len(report.checks) >= 1

    def test_get_health_report_with_packages(self, tmp_path: Path):
        # Maak package directories
        for name in ["devhub-core", "devhub-storage"]:
            pkg = tmp_path / "packages" / name
            pkg.mkdir(parents=True)
            (pkg / "pyproject.toml").write_text("[project]\nname = 'test'")

        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()

        # Check packages dimensie
        pkg_check = next(c for c in report.checks if c.dimension == "packages")
        assert "2" in pkg_check.summary

    def test_count_test_files(self, tmp_path: Path):
        tests_dir = tmp_path / "packages" / "pkg" / "tests"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_foo.py").write_text("def test_x(): pass")
        (tests_dir / "test_bar.py").write_text("def test_y(): pass")
        (tests_dir / "conftest.py").write_text("")  # Niet meegeteld

        provider = HealthProvider(_make_config(tmp_path))
        assert provider._count_test_files() == 2

    def test_healthy_when_tests_exist(self, tmp_path: Path):
        tests_dir = tmp_path / "packages" / "pkg" / "tests"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_one.py").write_text("def test(): pass")

        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        test_check = next(c for c in report.checks if c.dimension == "tests")
        assert test_check.status == HealthStatus.HEALTHY


class TestPlanningProvider:
    def test_get_sprint_info_no_tracker(self, tmp_path: Path):
        provider = PlanningProvider(_make_config(tmp_path))
        info = provider.get_sprint_info()
        assert info.nummer == 0
        assert info.status == "IDLE"

    def test_get_sprint_info_with_tracker(self, tmp_path: Path):
        tracker = tmp_path / "docs" / "planning" / "SPRINT_TRACKER.md"
        tracker.parent.mkdir(parents=True)
        tracker.write_text(
            "---\n"
            "laatste_sprint: 42\n"
            "test_baseline: 1424\n"
            "---\n"
            "\n"
            "Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 3 ✅ → Fase 4 🔄 → Fase 5 🔲\n"
        )

        provider = PlanningProvider(_make_config(tmp_path))
        info = provider.get_sprint_info()
        assert info.nummer == 42
        assert info.test_baseline == 1424

    def test_get_inbox_items_empty(self, tmp_path: Path):
        provider = PlanningProvider(_make_config(tmp_path))
        items = provider.get_inbox_items()
        assert items == []

    def test_get_inbox_items_with_intakes(self, tmp_path: Path):
        inbox = tmp_path / "docs" / "planning" / "inbox"
        inbox.mkdir(parents=True)

        (inbox / "SPRINT_INTAKE_FOO_2026-03-28.md").write_text(
            "---\nstatus: INBOX\nnode: devhub\nsprint_type: FEAT\n---\n# Foo"
        )
        (inbox / "SPRINT_INTAKE_BAR_2026-03-28.md").write_text(
            "---\nstatus: DONE\nnode: devhub\nsprint_type: CHORE\n---\n# Bar"
        )
        (inbox / "IDEA_SOMETHING.md").write_text("# Not an intake")

        provider = PlanningProvider(_make_config(tmp_path))
        items = provider.get_inbox_items()
        assert len(items) == 1
        assert items[0].filename == "SPRINT_INTAKE_FOO_2026-03-28.md"
        assert items[0].node == "devhub"
        assert items[0].sprint_type == "FEAT"

    def test_get_fase_progress(self, tmp_path: Path):
        tracker = tmp_path / "docs" / "planning" / "SPRINT_TRACKER.md"
        tracker.parent.mkdir(parents=True)
        tracker.write_text(
            "Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 3 ✅ → Fase 4 🔄 → Fase 5 🔲\n"
        )

        provider = PlanningProvider(_make_config(tmp_path))
        progress = provider.get_fase_progress()
        assert len(progress) == 6
        assert progress[0] == ("Fase 0", True)
        assert progress[4] == ("Fase 4", True)  # 🔄 = actief = True
        assert progress[5] == ("Fase 5", False)

    def test_parse_intake_frontmatter_defaults(self, tmp_path: Path):
        inbox = tmp_path / "docs" / "planning" / "inbox"
        inbox.mkdir(parents=True)
        (inbox / "SPRINT_INTAKE_TEST_2026-01-01.md").write_text("---\nstatus: INBOX\n---\n# Test")

        provider = PlanningProvider(_make_config(tmp_path))
        items = provider.get_inbox_items()
        assert len(items) == 1
        assert items[0].node == "devhub"  # default
        assert items[0].sprint_type == "FEAT"  # default
