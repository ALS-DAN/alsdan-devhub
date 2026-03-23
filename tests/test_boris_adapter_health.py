"""Tests voor F4 BorisAdapter health methods: pip_audit, version_info, architecture_scan, etc."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from devhub.adapters.boris_adapter import BorisAdapter
from devhub.contracts.node_interface import HealthStatus


@pytest.fixture
def boris_path(tmp_path):
    """Maak een minimal BORIS-achtige directory structuur."""
    # Venv
    venv_bin = tmp_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").write_text("#!/bin/sh\n")
    (venv_bin / "python").chmod(0o755)

    # main.py met versie
    (tmp_path / "main.py").write_text('app = FastAPI(version="2.4.0")\n')

    # pyproject.toml
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "2.4.0"\n')

    # OVERDRACHT.md
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "OVERDRACHT.md").write_text("# Overdracht\nVersie: 2.4.0\n")

    # Module directories
    for mod in ["agents", "rag", "safety", "mcp_server", "middleware", "ingest", "sharepoint", "weaviate_store"]:
        (tmp_path / mod).mkdir()

    # Agent files
    (tmp_path / "agents" / "__init__.py").write_text("")
    (tmp_path / "agents" / "vera.py").write_text("class Vera: pass")
    (tmp_path / "agents" / "herald.py").write_text("class Herald: pass")

    # MCP server
    (tmp_path / "mcp_server" / "server.py").write_text(
        "@mcp.tool\ndef health(): pass\n@mcp.tool\ndef search(): pass\n@tool\ndef ingest(): pass\n"
    )

    # Config files
    (tmp_path / "pyproject.toml").exists()  # already created
    (tmp_path / "mkdocs.yml").write_text("nav: []\n")
    (tmp_path / ".mcp.json").write_text("{}\n")
    (tmp_path / "docker-compose.yml").write_text("version: '3'\n")

    # CI pipeline
    ci_dir = tmp_path / ".github" / "workflows"
    ci_dir.mkdir(parents=True)
    (ci_dir / "ci.yml").write_text("name: CI\n")

    # Data directories
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for zone in ["chromadb_green", "chromadb_yellow"]:
        z = data_dir / zone
        z.mkdir()
        (z / "test.db").write_text("data")

    return tmp_path


@pytest.fixture
def adapter(boris_path):
    return BorisAdapter(str(boris_path))


class TestVersionInfo:
    def test_all_versions_match(self, adapter):
        versions = adapter.get_version_info()
        assert versions["main_py"] == "2.4.0"
        assert versions["pyproject"] == "2.4.0"
        assert versions["overdracht"] == "2.4.0"

    def test_version_mismatch(self, adapter, boris_path):
        (boris_path / "main.py").write_text('app = FastAPI(version="2.5.0")\n')
        versions = adapter.get_version_info()
        assert versions["main_py"] == "2.5.0"
        assert versions["pyproject"] == "2.4.0"

    def test_missing_main_py(self, adapter, boris_path):
        (boris_path / "main.py").unlink()
        versions = adapter.get_version_info()
        assert versions["main_py"] is None

    def test_no_version_in_overdracht(self, adapter, boris_path):
        (boris_path / ".claude" / "OVERDRACHT.md").write_text("# Overdracht\nGeen versie hier.\n")
        versions = adapter.get_version_info()
        assert versions["overdracht"] is None


class TestArchitectureScan:
    def test_full_scan(self, adapter):
        scan = adapter.get_architecture_scan()
        assert scan["modules"]["agents"] is True
        assert scan["modules"]["rag"] is True
        assert scan["modules"]["safety"] is True
        assert scan["modules"]["sharepoint"] is True
        assert scan["modules"]["weaviate_store"] is True

    def test_agent_count(self, adapter):
        scan = adapter.get_architecture_scan()
        assert scan["agent_count"] == 2  # vera.py + herald.py

    def test_mcp_tool_count(self, adapter):
        scan = adapter.get_architecture_scan()
        assert scan["mcp_tool_count"] == 3  # 2x @mcp.tool + 1x @tool

    def test_ci_present(self, adapter):
        scan = adapter.get_architecture_scan()
        assert scan["ci_present"] is True

    def test_ci_missing(self, adapter, boris_path):
        (boris_path / ".github" / "workflows" / "ci.yml").unlink()
        scan = adapter.get_architecture_scan()
        assert scan["ci_present"] is False

    def test_config_files(self, adapter):
        scan = adapter.get_architecture_scan()
        assert scan["config_files"]["mkdocs.yml"] is True
        assert scan["config_files"][".mcp.json"] is True
        assert scan["config_files"]["docker-compose.yml"] is True


class TestVectorstoreDirs:
    def test_existing_zones(self, adapter):
        zones = adapter.check_vectorstore_dirs()
        assert zones["chromadb_green"]["exists"] is True
        assert zones["chromadb_green"]["non_empty_files"] >= 1
        assert zones["chromadb_yellow"]["exists"] is True

    def test_missing_zone(self, adapter):
        zones = adapter.check_vectorstore_dirs()
        assert zones["chromadb_red"]["exists"] is False


class TestN8nStatus:
    @patch("devhub.adapters.boris_adapter.subprocess.run")
    def test_n8n_offline(self, mock_run):
        """n8n niet bereikbaar → graceful degradation."""
        mock_run.side_effect = FileNotFoundError("curl not found")
        adapter = BorisAdapter.__new__(BorisAdapter)
        adapter.boris_path = Path("/tmp/fake")
        result = adapter.check_n8n_status()
        assert result["reachable"] is False
        assert result["error"] is not None

    @patch("devhub.adapters.boris_adapter.subprocess.run")
    def test_n8n_online(self, mock_run):
        """n8n bereikbaar → workflow count."""
        def side_effect(cmd, **kwargs):
            mock = MagicMock()
            if "-w" in cmd:
                mock.stdout = "200"
                mock.returncode = 0
            else:
                mock.stdout = json.dumps({"data": [{"id": 1}, {"id": 2}]})
                mock.returncode = 0
            return mock

        mock_run.side_effect = side_effect
        adapter = BorisAdapter.__new__(BorisAdapter)
        adapter.boris_path = Path("/tmp/fake")
        result = adapter.check_n8n_status()
        assert result["reachable"] is True
        assert result["workflow_count"] == 2


class TestPipAudit:
    @patch("devhub.adapters.boris_adapter.subprocess.run")
    def test_pip_audit_clean(self, mock_run, adapter):
        mock_run.return_value = MagicMock(returncode=0, stdout="No known vulnerabilities found\n", stderr="")
        clean, output = adapter.run_pip_audit()
        assert clean is True

    @patch("devhub.adapters.boris_adapter.subprocess.run")
    def test_pip_audit_cves(self, mock_run, adapter):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Name   Version   ID          Fix\nfoo    1.0       PYSEC-2024  1.1\n",
            stderr="",
        )
        clean, output = adapter.run_pip_audit()
        assert clean is False
        assert "PYSEC" in output

    def test_pip_audit_no_venv(self, tmp_path):
        (tmp_path / "dummy").write_text("")
        adapter = BorisAdapter(str(tmp_path))
        clean, output = adapter.run_pip_audit()
        assert clean is False
        assert "venv not found" in output


class TestFullHealthCheck:
    """Test de geïntegreerde run_full_health_check()."""

    @patch.object(BorisAdapter, "run_tests")
    @patch.object(BorisAdapter, "run_lint")
    @patch.object(BorisAdapter, "run_pip_audit")
    @patch.object(BorisAdapter, "run_curator_audit")
    @patch.object(BorisAdapter, "check_n8n_status")
    def test_all_healthy(self, mock_n8n, mock_curator, mock_pip, mock_lint, mock_tests, adapter):
        from devhub.contracts.node_interface import TestResult
        mock_tests.return_value = TestResult(total=100, passed=100, failed=0, errors=0, duration_seconds=5.0)
        mock_lint.return_value = (True, "")
        mock_pip.return_value = (True, "No vulnerabilities")
        mock_curator.return_value = (True, "OK")
        mock_n8n.return_value = {"reachable": False, "workflow_count": 0, "error": "offline"}

        report = adapter.run_full_health_check()
        assert report.node_id == "boris-buurts"
        assert report.overall == HealthStatus.HEALTHY
        assert len(report.checks) == 6
        assert len(report.alert_findings) == 0

    @patch.object(BorisAdapter, "run_tests")
    @patch.object(BorisAdapter, "run_lint")
    @patch.object(BorisAdapter, "run_pip_audit")
    @patch.object(BorisAdapter, "run_curator_audit")
    @patch.object(BorisAdapter, "check_n8n_status")
    def test_failing_tests_critical(self, mock_n8n, mock_curator, mock_pip, mock_lint, mock_tests, adapter):
        from devhub.contracts.node_interface import TestResult
        mock_tests.return_value = TestResult(total=100, passed=95, failed=5, errors=0, duration_seconds=5.0)
        mock_lint.return_value = (True, "")
        mock_pip.return_value = (True, "Clean")
        mock_curator.return_value = (True, "OK")
        mock_n8n.return_value = {"reachable": False, "workflow_count": 0, "error": "offline"}

        report = adapter.run_full_health_check()
        assert report.overall == HealthStatus.CRITICAL
        assert len(report.p1_findings) == 1
        assert "5 tests failed" in report.p1_findings[0].message

    @patch.object(BorisAdapter, "run_tests")
    @patch.object(BorisAdapter, "run_lint")
    @patch.object(BorisAdapter, "run_pip_audit")
    @patch.object(BorisAdapter, "run_curator_audit")
    @patch.object(BorisAdapter, "check_n8n_status")
    def test_lint_errors_attention(self, mock_n8n, mock_curator, mock_pip, mock_lint, mock_tests, adapter):
        from devhub.contracts.node_interface import TestResult
        mock_tests.return_value = TestResult(total=100, passed=100, failed=0, errors=0, duration_seconds=5.0)
        mock_lint.return_value = (False, "E501: line too long")
        mock_pip.return_value = (True, "Clean")
        mock_curator.return_value = (True, "OK")
        mock_n8n.return_value = {"reachable": False, "workflow_count": 0, "error": "offline"}

        report = adapter.run_full_health_check()
        assert report.overall == HealthStatus.ATTENTION
        assert len(report.p2_findings) >= 1

    @patch.object(BorisAdapter, "run_tests")
    @patch.object(BorisAdapter, "run_lint")
    @patch.object(BorisAdapter, "run_pip_audit")
    @patch.object(BorisAdapter, "run_curator_audit")
    @patch.object(BorisAdapter, "check_n8n_status")
    def test_report_has_timestamp(self, mock_n8n, mock_curator, mock_pip, mock_lint, mock_tests, adapter):
        from devhub.contracts.node_interface import TestResult
        mock_tests.return_value = TestResult(total=10, passed=10, failed=0, errors=0, duration_seconds=1.0)
        mock_lint.return_value = (True, "")
        mock_pip.return_value = (True, "Clean")
        mock_curator.return_value = (True, "OK")
        mock_n8n.return_value = {"reachable": False, "workflow_count": 0, "error": "offline"}

        report = adapter.run_full_health_check()
        assert "2026" in report.timestamp or "T" in report.timestamp
