"""History provider — snapshot opslag/ophalen via LocalAdapter of filesystem.

Slaat health-snapshots op als JSON-bestanden, gesorteerd op datum.
Gebruikt voor trend-grafieken in het dashboard.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from devhub_core.contracts.node_interface import FullHealthReport

from devhub_dashboard.config import DashboardConfig


@dataclass(frozen=True)
class HealthSnapshot:
    """Een moment-opname van de health status."""

    timestamp: str
    overall: str  # "healthy" | "attention" | "critical"
    dimensions_checked: int
    p1_count: int
    p2_count: int
    test_files: int
    packages: int
    # Sprint 44: uitgebreide health metrics (backward compatible defaults)
    knowledge_items: int = 0
    knowledge_freshness: float = 0.0  # 0.0-1.0
    dependency_issues: int = 0
    sprint_hygiene_score: float = 1.0  # 0.0-1.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> HealthSnapshot:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_report(cls, report: FullHealthReport, *, test_files: int = 0, packages: int = 0):
        return cls(
            timestamp=report.timestamp,
            overall=report.overall.value,
            dimensions_checked=len(report.checks),
            p1_count=len(report.p1_findings),
            p2_count=len(report.p2_findings),
            test_files=test_files,
            packages=packages,
        )


class HistoryStore:
    """Beheert historische snapshots op disk."""

    def __init__(self, config: DashboardConfig) -> None:
        self._dir = config.history_path

    def save_snapshot(self, snapshot: HealthSnapshot) -> Path:
        """Sla een snapshot op als JSON-bestand."""
        self._dir.mkdir(parents=True, exist_ok=True)
        ts = snapshot.timestamp.replace(":", "-").replace("+", "_")[:19]
        path = self._dir / f"health_{ts}.json"
        path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
        return path

    def load_snapshots(self, limit: int = 50) -> list[HealthSnapshot]:
        """Laad de meest recente snapshots, gesorteerd op timestamp."""
        if not self._dir.exists():
            return []

        files = sorted(self._dir.glob("health_*.json"), reverse=True)[:limit]
        snapshots = []
        for f in reversed(files):  # Chronologische volgorde
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                snapshots.append(HealthSnapshot.from_dict(data))
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
        return snapshots

    def get_trend_data(self, limit: int = 50) -> tuple[list[str], list[int]]:
        """Haal trend-data op voor test-bestanden over tijd.

        Returns:
            Tuple van (timestamps, test_files_counts).
        """
        snapshots = self.load_snapshots(limit)
        timestamps = [s.timestamp[:10] for s in snapshots]
        test_counts = [s.test_files for s in snapshots]
        return timestamps, test_counts
