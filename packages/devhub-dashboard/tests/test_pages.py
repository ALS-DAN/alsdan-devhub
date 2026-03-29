"""Tests voor dashboard pagina's — health, planning, knowledge data-integratie."""

from pathlib import Path

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.providers import HealthProvider, PlanningProvider


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


def _setup_project_structure(tmp_path: Path) -> None:
    """Maak een minimale project-structuur voor tests."""
    # Packages
    for name in ["devhub-core", "devhub-storage", "devhub-dashboard"]:
        pkg = tmp_path / "packages" / name
        pkg.mkdir(parents=True)
        (pkg / "pyproject.toml").write_text(f"[project]\nname = '{name}'")

    # Test bestanden
    tests_dir = tmp_path / "packages" / "devhub-core" / "tests"
    tests_dir.mkdir(parents=True)
    for i in range(5):
        (tests_dir / f"test_{i}.py").write_text("def test(): pass")

    # Sprint tracker
    tracker = tmp_path / "docs" / "planning" / "SPRINT_TRACKER.md"
    tracker.parent.mkdir(parents=True)
    tracker.write_text(
        "---\n"
        "laatste_sprint: 43\n"
        "test_baseline: 1448\n"
        "---\n"
        "\n"
        "Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 3 ✅ → Fase 4 🔄 → Fase 5 🔲\n"
    )

    # Inbox
    inbox = tmp_path / "docs" / "planning" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "SPRINT_INTAKE_TEST_2026-03-28.md").write_text(
        "---\nstatus: INBOX\nnode: devhub\nsprint_type: FEAT\n---\n"
    )

    # Knowledge
    knowledge = tmp_path / "knowledge" / "ai_engineering"
    knowledge.mkdir(parents=True)
    (knowledge / "intro.md").write_text("# AI Engineering\nGrading: SILVER")
    (knowledge / "patterns.md").write_text("# Patterns\nGrading: BRONZE")
    retro = tmp_path / "knowledge" / "retrospectives"
    retro.mkdir(parents=True)
    (retro / "retro_1.md").write_text("# Retro\nGrading: GOLD")


class TestHealthPageData:
    def test_health_report_with_structure(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        report = provider.get_health_report()
        assert len(report.checks) >= 2  # tests + packages

    def test_package_count_correct(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        assert provider._count_packages() == 3

    def test_test_files_count(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        provider = HealthProvider(_make_config(tmp_path))
        assert provider._count_test_files() == 5


class TestPlanningPageData:
    def test_sprint_info_from_structure(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        provider = PlanningProvider(_make_config(tmp_path))
        info = provider.get_sprint_info()
        assert info.nummer == 43
        assert info.test_baseline == 1448

    def test_inbox_from_structure(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        provider = PlanningProvider(_make_config(tmp_path))
        items = provider.get_inbox_items()
        assert len(items) == 1

    def test_fase_progress_from_structure(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        provider = PlanningProvider(_make_config(tmp_path))
        progress = provider.get_fase_progress()
        assert len(progress) == 6
        # Fase 4 is actief (🔄)
        assert progress[4][1] is True


class TestKnowledgePageData:
    def test_knowledge_files_found(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        config = _make_config(tmp_path)
        knowledge_dir = config.devhub_root / "knowledge"
        files = list(knowledge_dir.rglob("*.md"))
        assert len(files) == 3

    def test_subdirectories_found(self, tmp_path: Path):
        _setup_project_structure(tmp_path)
        config = _make_config(tmp_path)
        knowledge_dir = config.devhub_root / "knowledge"
        dirs = [d for d in knowledge_dir.iterdir() if d.is_dir()]
        assert len(dirs) == 2  # ai_engineering + retrospectives
