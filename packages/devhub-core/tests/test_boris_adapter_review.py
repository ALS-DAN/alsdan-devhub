"""Tests voor F7 BorisAdapter review methods: git diff, changed files, anti-pattern scan."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from devhub_core.adapters.boris_adapter import BorisAdapter


@pytest.fixture
def boris_path(tmp_path):
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "python").write_text("#!/bin/sh\n")
    (tmp_path / "mkdocs.yml").write_text("nav: []\n")
    return tmp_path


@pytest.fixture
def adapter(boris_path):
    return BorisAdapter(str(boris_path))


class TestGetGitDiff:
    @patch("devhub_core.adapters.boris_adapter.subprocess.run")
    def test_unstaged_diff(self, mock_run, adapter):
        mock_run.return_value = MagicMock(stdout="diff --git a/foo.py\n+new line\n")
        result = adapter.get_git_diff(staged=False)
        assert "foo.py" in result
        args = mock_run.call_args[0][0]
        assert "--staged" not in args

    @patch("devhub_core.adapters.boris_adapter.subprocess.run")
    def test_staged_diff(self, mock_run, adapter):
        mock_run.return_value = MagicMock(stdout="diff --git a/bar.py\n")
        result = adapter.get_git_diff(staged=True)
        assert "bar.py" in result
        args = mock_run.call_args[0][0]
        assert "--staged" in args

    @patch("devhub_core.adapters.boris_adapter.subprocess.run")
    def test_diff_failure(self, mock_run, adapter):
        mock_run.side_effect = Exception("git not found")
        result = adapter.get_git_diff()
        assert result == ""


class TestGetChangedFiles:
    @patch("devhub_core.adapters.boris_adapter.subprocess.run")
    def test_changed_files(self, mock_run, adapter):
        mock_run.return_value = MagicMock(stdout="agents/vera.py\nrag/store.py\n")
        files = adapter.get_changed_files()
        assert len(files) == 2
        assert "agents/vera.py" in files

    @patch("devhub_core.adapters.boris_adapter.subprocess.run")
    def test_no_changes(self, mock_run, adapter):
        mock_run.return_value = MagicMock(stdout="")
        files = adapter.get_changed_files()
        assert files == []

    @patch("devhub_core.adapters.boris_adapter.subprocess.run")
    def test_failure_returns_empty(self, mock_run, adapter):
        mock_run.side_effect = Exception("fail")
        assert adapter.get_changed_files() == []


class TestScanAntiPatterns:
    def test_detects_chromadb_direct(self, adapter, boris_path):
        py = boris_path / "bad.py"
        py.write_text('from chromadb import Client\nclient = chromadb.Client()\n')
        findings = adapter.scan_anti_patterns(["bad.py"])
        assert len(findings) >= 1
        assert any("ChromaDB" in f["description"] for f in findings)

    def test_detects_hardcoded_secret(self, adapter, boris_path):
        py = boris_path / "config.py"
        py.write_text('api_key = "sk-1234567890abcdefghij"\n')
        findings = adapter.scan_anti_patterns(["config.py"])
        assert any("secret" in f["description"].lower() or "Hardcoded" in f["description"] for f in findings)

    def test_skips_non_python(self, adapter, boris_path):
        md = boris_path / "readme.md"
        md.write_text('ChromaDB is great\n')
        findings = adapter.scan_anti_patterns(["readme.md"])
        assert findings == []

    def test_skips_print_in_tests(self, adapter, boris_path):
        test = boris_path / "tests" / "test_foo.py"
        test.parent.mkdir(parents=True)
        test.write_text('print("debug output")\n')
        findings = adapter.scan_anti_patterns(["tests/test_foo.py"])
        assert not any("print()" in f["description"] for f in findings)

    def test_allows_zone_in_safety_policy(self, adapter, boris_path):
        sp = boris_path / "safety" / "policy.py"
        sp.parent.mkdir(parents=True)
        sp.write_text('if zone == "RED":\n    block()\n')
        findings = adapter.scan_anti_patterns(["safety/policy.py"])
        assert not any("RED-zone" in f["description"] for f in findings)

    def test_empty_files_list(self, adapter):
        assert adapter.scan_anti_patterns([]) == []

    def test_nonexistent_file(self, adapter):
        findings = adapter.scan_anti_patterns(["nonexistent.py"])
        assert findings == []

    def test_finding_has_required_fields(self, adapter, boris_path):
        py = boris_path / "leak.py"
        py.write_text('password = "supersecret123"\n')
        findings = adapter.scan_anti_patterns(["leak.py"])
        assert len(findings) >= 1
        f = findings[0]
        assert "file" in f
        assert "line" in f
        assert "severity" in f
        assert "description" in f
        assert "match" in f


class TestGetReviewContext:
    @patch.object(BorisAdapter, "get_changed_files")
    @patch.object(BorisAdapter, "get_git_diff")
    @patch.object(BorisAdapter, "scan_anti_patterns")
    def test_full_context(self, mock_scan, mock_diff, mock_files, adapter):
        mock_files.return_value = ["foo.py"]
        mock_diff.return_value = "diff output"
        mock_scan.return_value = []

        ctx = adapter.get_review_context()
        assert "diff_unstaged" in ctx
        assert "diff_staged" in ctx
        assert "files_all" in ctx
        assert "anti_patterns" in ctx

    @patch.object(BorisAdapter, "get_changed_files")
    @patch.object(BorisAdapter, "get_git_diff")
    @patch.object(BorisAdapter, "scan_anti_patterns")
    def test_context_keys_complete(self, mock_scan, mock_diff, mock_files, adapter):
        mock_files.return_value = []
        mock_diff.return_value = ""
        mock_scan.return_value = []

        ctx = adapter.get_review_context()
        expected = {"diff_unstaged", "diff_staged", "files_unstaged", "files_staged", "files_all", "anti_patterns"}
        assert set(ctx.keys()) == expected
