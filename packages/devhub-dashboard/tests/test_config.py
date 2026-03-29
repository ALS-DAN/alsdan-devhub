"""Tests voor DashboardConfig."""

from pathlib import Path

from devhub_dashboard.config import DashboardConfig


class TestDashboardConfig:
    def test_defaults(self):
        config = DashboardConfig()
        assert config.port == 8765
        assert config.host == "127.0.0.1"
        assert config.dark_mode is True
        assert config.refresh_interval_seconds == 30

    def test_custom_values(self):
        config = DashboardConfig(port=9090, dark_mode=False)
        assert config.port == 9090
        assert config.dark_mode is False

    def test_frozen(self):
        config = DashboardConfig()
        try:
            config.port = 9999  # type: ignore[misc]
            raise AssertionError("Should be frozen")
        except AttributeError:
            pass

    def test_derived_paths(self, tmp_path: Path):
        config = DashboardConfig(devhub_root=tmp_path)
        assert config.history_path == tmp_path / "data" / "dashboard_history"
        assert config.sprint_tracker_path == tmp_path / "docs" / "planning" / "SPRINT_TRACKER.md"
        assert config.inbox_path == tmp_path / "docs" / "planning" / "inbox"
        assert config.nodes_config_path == tmp_path / "config" / "nodes.yml"
