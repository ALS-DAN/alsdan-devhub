"""Tests voor BorisAdapter."""

import json
import pytest

from devhub.adapters.boris_adapter import BorisAdapter
from devhub.contracts.node_interface import NodeReport


class TestBorisAdapter:
    """Tests for BorisAdapter — read-only BORIS interface."""

    def test_init_valid_path(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.boris_path == tmp_path

    def test_init_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            BorisAdapter("/nonexistent/path/to/boris")

    def test_get_health_no_lumen(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        health = adapter.get_health()
        assert health.status == "UP"
        assert health.test_count == 0

    def test_get_health_from_lumen(self, tmp_path):
        report = {
            "node_id": "boris-buurts",
            "timestamp": "2026-03-23T12:00:00Z",
            "health": {
                "status": "DEGRADED",
                "components": {"weaviate": "UP", "ollama": "DOWN"},
                "test_count": 2229,
                "test_pass_rate": 0.99,
                "coverage_pct": 75.0,
            },
        }
        report_dir = tmp_path / ".claude" / "scratchpad"
        report_dir.mkdir(parents=True)
        (report_dir / "dev_report.json").write_text(json.dumps(report))

        adapter = BorisAdapter(str(tmp_path))
        health = adapter.get_health()
        assert health.status == "DEGRADED"
        assert health.test_count == 2229
        assert health.components["ollama"] == "DOWN"

    def test_get_report_from_lumen(self, tmp_path):
        report = {
            "node_id": "boris-buurts",
            "timestamp": "2026-03-23T12:00:00Z",
            "health": {
                "status": "UP",
                "components": {},
                "test_count": 100,
                "test_pass_rate": 1.0,
                "coverage_pct": 80.0,
            },
            "doc_status": {
                "total_pages": 50,
                "stale_pages": 2,
                "diataxis_coverage": {"tutorial": 5, "howto": 10},
            },
            "observations": ["[HOOG] safety: check zones"],
            "safety_zones": {"green": 80, "yellow": 15, "red": 5},
        }
        report_dir = tmp_path / ".claude" / "scratchpad"
        report_dir.mkdir(parents=True)
        (report_dir / "dev_report.json").write_text(json.dumps(report))

        adapter = BorisAdapter(str(tmp_path))
        node_report = adapter.get_report()

        assert isinstance(node_report, NodeReport)
        assert node_report.node_id == "boris-buurts"
        assert node_report.health.status == "UP"
        assert node_report.doc_status.total_pages == 50
        assert len(node_report.observations) == 1
        assert node_report.safety_zones["green"] == 80

    def test_get_report_fallback_no_lumen(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        report = adapter.get_report()
        assert report.node_id == "boris-buurts"
        assert report.health.status == "UP"

    def test_list_docs_no_mkdocs(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        assert adapter.list_docs() == []

    def test_list_docs_with_mkdocs(self, tmp_path):
        mkdocs_content = """
site_name: Test
nav:
  - Home: index.md
  - Guide:
    - Setup: guide/setup.md
    - Usage: guide/usage.md
"""
        (tmp_path / "mkdocs.yml").write_text(mkdocs_content)

        adapter = BorisAdapter(str(tmp_path))
        docs = adapter.list_docs()
        assert "index.md" in docs
        assert "guide/setup.md" in docs
        assert "guide/usage.md" in docs

    def test_parse_pytest_output(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        stdout = "2229 passed, 3 warnings in 45.23s"
        result = adapter._parse_pytest_output(stdout, 0)
        assert result.total == 2229
        assert result.passed == 2229
        assert result.failed == 0
        assert result.duration_seconds == 45.23

    def test_parse_pytest_output_with_failures(self, tmp_path):
        adapter = BorisAdapter(str(tmp_path))
        stdout = "2200 passed, 29 failed in 52.10s"
        result = adapter._parse_pytest_output(stdout, 1)
        assert result.total == 2229
        assert result.passed == 2200
        assert result.failed == 29

    def test_corrupt_lumen_report(self, tmp_path):
        report_dir = tmp_path / ".claude" / "scratchpad"
        report_dir.mkdir(parents=True)
        (report_dir / "dev_report.json").write_text("not valid json{{{")

        adapter = BorisAdapter(str(tmp_path))
        # Should fallback gracefully
        report = adapter.get_report()
        assert report.node_id == "boris-buurts"
