"""Tests voor BorisAdapter uitbreidingen — sprint, governance, file reads."""

from devhub_core.adapters.boris_adapter import BorisAdapter


class TestBorisAdapterFileReads:
    """Test read_file en afgeleide methoden."""

    def test_read_file_existing(self, tmp_path):
        (tmp_path / "test.md").write_text("# Hello")
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.read_file("test.md") == "# Hello"

    def test_read_file_nonexistent(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.read_file("nonexistent.md") is None

    def test_read_claude_md(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("# BORIS\n\nActieve Sprint: PRE-3")
        adapter = BorisAdapter(str(tmp_path))
        content = adapter.read_claude_md()
        assert "PRE-3" in content

    def test_read_overdracht(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "OVERDRACHT.md").write_text("# Overdracht\n\nLaatste sprint: X")
        adapter = BorisAdapter(str(tmp_path))
        content = adapter.read_overdracht()
        assert "Overdracht" in content

    def test_read_cowork_brief(self, tmp_path):
        docs_dir = tmp_path / "docs" / "planning"
        docs_dir.mkdir(parents=True)
        (docs_dir / "COWORK_BRIEF.md").write_text("# Brief\n\nSprint Queue: ...")
        adapter = BorisAdapter(str(tmp_path))
        content = adapter.read_cowork_brief()
        assert "Sprint Queue" in content

    def test_read_goals(self, tmp_path):
        docs_dir = tmp_path / "docs" / "planning"
        docs_dir.mkdir(parents=True)
        (docs_dir / "GOALS.md").write_text("# Goals\n\n1. Ship pilot")
        adapter = BorisAdapter(str(tmp_path))
        content = adapter.read_goals()
        assert "Ship pilot" in content

    def test_read_backlog(self, tmp_path):
        docs_dir = tmp_path / "docs" / "planning"
        docs_dir.mkdir(parents=True)
        (docs_dir / "IDEEEN_BACKLOG.md").write_text("# Backlog\n\n| ID | Status |")
        adapter = BorisAdapter(str(tmp_path))
        content = adapter.read_backlog()
        assert "Backlog" in content


class TestBorisAdapterSprintDocs:
    """Test sprint-doc reads."""

    def test_list_sprint_docs_empty(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.list_sprint_docs() == []

    def test_list_sprint_docs(self, tmp_path):
        sprint_dir = tmp_path / "docs" / "planning" / "sprints"
        sprint_dir.mkdir(parents=True)
        (sprint_dir / "SPRINT_PRE3.md").write_text("# PRE-3")
        (sprint_dir / "SPRINT_AUTH.md").write_text("# AUTH")
        (sprint_dir / "README.md").write_text("# Not a sprint")

        adapter = BorisAdapter(str(tmp_path))
        docs = adapter.list_sprint_docs()
        assert "SPRINT_PRE3.md" in docs
        assert "SPRINT_AUTH.md" in docs
        assert "README.md" not in docs

    def test_read_sprint_doc(self, tmp_path):
        sprint_dir = tmp_path / "docs" / "planning" / "sprints"
        sprint_dir.mkdir(parents=True)
        (sprint_dir / "SPRINT_PRE3.md").write_text("# Sprint PRE-3\n\nScope: MkDocs")

        adapter = BorisAdapter(str(tmp_path))
        content = adapter.read_sprint_doc("SPRINT_PRE3.md")
        assert "MkDocs" in content

    def test_read_sprint_doc_nonexistent(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.read_sprint_doc("SPRINT_NOPE.md") is None


class TestBorisAdapterInbox:
    """Test inbox listing."""

    def test_list_inbox_empty(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.list_inbox() == []

    def test_list_inbox(self, tmp_path):
        inbox_dir = tmp_path / "docs" / "planning" / "inbox"
        inbox_dir.mkdir(parents=True)
        (inbox_dir / "SPRINT_INTAKE_AUTH_2026-03-23.md").write_text("# Intake")
        (inbox_dir / "IDEA_DARK_MODE_2026-03-23.md").write_text("# Idea")

        adapter = BorisAdapter(str(tmp_path))
        items = adapter.list_inbox()
        assert len(items) == 2

        types = {i["type"] for i in items}
        assert "intake" in types
        assert "idea" in types

    def test_inbox_item_has_path(self, tmp_path):
        inbox_dir = tmp_path / "docs" / "planning" / "inbox"
        inbox_dir.mkdir(parents=True)
        (inbox_dir / "IDEA_TEST_2026-03-23.md").write_text("# Test")

        adapter = BorisAdapter(str(tmp_path))
        items = adapter.list_inbox()
        assert items[0]["path"].startswith("docs/planning/inbox/")


class TestBorisAdapterGovernance:
    """Test governance tool wrappers (lint, herald, curator, deps)."""

    def test_run_lint_no_venv(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        clean, output = adapter.run_lint()
        assert not clean
        assert "venv not found" in output

    def test_run_herald_sync_no_script(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        success, output = adapter.run_herald_sync("test")
        assert not success
        assert "not found" in output

    def test_run_curator_audit_no_venv(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        clean, output = adapter.run_curator_audit()
        assert not clean

    def test_run_sprint_deps_check_no_venv(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        clean, output = adapter.run_sprint_deps_check("SPRINT_X.md")
        assert not clean
