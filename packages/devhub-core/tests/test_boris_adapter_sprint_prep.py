"""Tests voor F6 BorisAdapter sprint-prep methods."""

from pathlib import Path

import pytest

from devhub_core.adapters.boris_adapter import BorisAdapter


@pytest.fixture
def boris_path(tmp_path):
    """Minimal BORIS structuur voor sprint-prep."""
    # Venv
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "python").write_text("#!/bin/sh\n")
    (tmp_path / ".venv" / "bin" / "python").chmod(0o755)
    (tmp_path / "mkdocs.yml").write_text("nav: []\n")

    # CLAUDE.md
    (tmp_path / "CLAUDE.md").write_text("# BORIS hot cache\n## Actieve Sprint\nPRE-3\n")

    # OVERDRACHT.md
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "OVERDRACHT.md").write_text("# Overdracht\nVersie: 2.4.0\n")

    # HEALTH_STATUS.md
    (tmp_path / "HEALTH_STATUS.md").write_text(
        "# BORIS System Status\nOverall: ✅ Gezond\n| Tests | ✅ | 2229 passed |\n"
    )

    # Decisions
    (tmp_path / "memory" / "context").mkdir(parents=True)
    (tmp_path / "memory" / "context" / "decisions.md").write_text(
        "# Beslissingen\n## #27 OPEN\nMENTOR.DEV scope\n## #28 CLOSED\nKlaar\n"
    )

    # ADR files
    adr_dir = tmp_path / "docs" / "architecture"
    adr_dir.mkdir(parents=True)
    (adr_dir / "ADR-001-node-arch.md").write_text("# ADR-001\nNode Architecture\n")
    (adr_dir / "ADR-002-contracts.md").write_text("# ADR-002\nContracts\n")
    (adr_dir / "README.md").write_text("# ADR Index\n")

    # Health reports
    health_dir = tmp_path / "docs" / "health"
    health_dir.mkdir(parents=True)
    (health_dir / "health-report-2026-03-22.md").write_text("# Report 22\nAll good\n")
    (health_dir / "health-report-2026-03-23.md").write_text("# Report 23\nLatest\n")

    # Inbox
    inbox_dir = tmp_path / "docs" / "planning" / "inbox"
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "SPRINT_INTAKE_PRE3.md").write_text("# PRE-3 intake\n")
    (inbox_dir / "IDEA_FOO.md").write_text("# Foo idea\n")

    # Sprint docs
    sprint_dir = tmp_path / "docs" / "planning" / "sprints"
    sprint_dir.mkdir(parents=True)
    (sprint_dir / "SPRINT_PRE3.md").write_text("# Sprint PRE-3\n")

    return tmp_path


@pytest.fixture
def adapter(boris_path):
    return BorisAdapter(str(boris_path))


class TestReadHealthStatus:
    def test_reads_health_status(self, adapter):
        content = adapter.read_health_status()
        assert content is not None
        assert "Gezond" in content

    def test_missing_health_status(self, adapter, boris_path):
        (boris_path / "HEALTH_STATUS.md").unlink()
        assert adapter.read_health_status() is None


class TestReadDecisions:
    def test_reads_decisions(self, adapter):
        content = adapter.read_decisions()
        assert content is not None
        assert "#27" in content

    def test_missing_decisions(self, adapter, boris_path):
        (boris_path / "memory" / "context" / "decisions.md").unlink()
        assert adapter.read_decisions() is None


class TestListAdrFiles:
    def test_lists_adrs(self, adapter):
        adrs = adapter.list_adr_files()
        assert len(adrs) == 2
        assert "ADR-001-node-arch.md" in adrs
        assert "ADR-002-contracts.md" in adrs
        # README.md should NOT be in the list
        assert "README.md" not in adrs

    def test_sorted(self, adapter):
        adrs = adapter.list_adr_files()
        assert adrs == sorted(adrs)

    def test_no_adr_dir(self, tmp_path):
        (tmp_path / "dummy").write_text("")
        a = BorisAdapter(str(tmp_path))
        assert a.list_adr_files() == []


class TestReadAdr:
    def test_reads_adr(self, adapter):
        content = adapter.read_adr("ADR-001-node-arch.md")
        assert content is not None
        assert "Node Architecture" in content

    def test_missing_adr(self, adapter):
        assert adapter.read_adr("ADR-999-nonexistent.md") is None


class TestListHealthReports:
    def test_lists_reports(self, adapter):
        reports = adapter.list_health_reports()
        assert len(reports) == 2
        # Newest first
        assert reports[0] == "health-report-2026-03-23.md"

    def test_no_health_dir(self, tmp_path):
        (tmp_path / "dummy").write_text("")
        a = BorisAdapter(str(tmp_path))
        assert a.list_health_reports() == []


class TestReadHealthReport:
    def test_reads_report(self, adapter):
        content = adapter.read_health_report("health-report-2026-03-23.md")
        assert content is not None
        assert "Latest" in content

    def test_missing_report(self, adapter):
        assert adapter.read_health_report("health-report-1999-01-01.md") is None


class TestGetSprintPrepContext:
    def test_full_context(self, adapter):
        ctx = adapter.get_sprint_prep_context()

        assert ctx["health_status"] is not None
        assert "Gezond" in ctx["health_status"]

        assert ctx["health_report_latest"] is not None
        assert "Latest" in ctx["health_report_latest"]

        assert ctx["developer_profile"]["phase"] == "ORIËNTEREN"
        assert ctx["developer_profile"]["signal"] == "STAGNATIE"

        assert ctx["claude_md"] is not None
        assert ctx["overdracht"] is not None
        assert ctx["decisions"] is not None

        assert len(ctx["inbox"]) == 2
        assert len(ctx["sprint_docs"]) == 1
        assert len(ctx["adr_files"]) == 2

    def test_context_without_health_report(self, adapter, boris_path):
        import shutil
        shutil.rmtree(boris_path / "docs" / "health")
        ctx = adapter.get_sprint_prep_context()
        assert ctx["health_report_latest"] is None

    def test_context_keys_complete(self, adapter):
        ctx = adapter.get_sprint_prep_context()
        expected_keys = {
            "health_status", "health_report_latest", "developer_profile",
            "claude_md", "overdracht", "decisions", "inbox",
            "sprint_docs", "adr_files",
        }
        assert set(ctx.keys()) == expected_keys
