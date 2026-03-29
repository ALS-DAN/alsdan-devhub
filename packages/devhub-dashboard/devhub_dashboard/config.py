"""Dashboard configuratie — poort, refresh interval, storage paden."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DashboardConfig:
    """Immutable dashboard configuratie."""

    port: int = 8765
    host: str = "127.0.0.1"
    title: str = "DevHub Dashboard"
    refresh_interval_seconds: int = 30
    dark_mode: bool = True
    devhub_root: Path = field(default_factory=lambda: Path.cwd())
    history_dir: str = "data/dashboard_history"

    @property
    def history_path(self) -> Path:
        return self.devhub_root / self.history_dir

    @property
    def sprint_tracker_path(self) -> Path:
        return self.devhub_root / "docs" / "planning" / "SPRINT_TRACKER.md"

    @property
    def inbox_path(self) -> Path:
        return self.devhub_root / "docs" / "planning" / "inbox"

    @property
    def nodes_config_path(self) -> Path:
        return self.devhub_root / "config" / "nodes.yml"
