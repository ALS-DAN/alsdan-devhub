"""Tests voor de HistoryStore — snapshot opslag/ophalen."""

from pathlib import Path

from devhub_core.contracts.node_interface import FullHealthReport, HealthCheckResult, HealthStatus

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.history import HealthSnapshot, HistoryStore


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


class TestHealthSnapshot:
    def test_from_report(self):
        report = FullHealthReport(
            node_id="devhub",
            timestamp="2026-03-28T12:00:00+00:00",
            checks=(
                HealthCheckResult(dimension="tests", status=HealthStatus.HEALTHY, summary="ok"),
            ),
        )
        snapshot = HealthSnapshot.from_report(report, test_files=50, packages=5)
        assert snapshot.overall == "healthy"
        assert snapshot.dimensions_checked == 1
        assert snapshot.test_files == 50
        assert snapshot.packages == 5

    def test_roundtrip_dict(self):
        snapshot = HealthSnapshot(
            timestamp="2026-03-28T12:00:00",
            overall="healthy",
            dimensions_checked=3,
            p1_count=0,
            p2_count=1,
            test_files=42,
            packages=4,
        )
        data = snapshot.to_dict()
        restored = HealthSnapshot.from_dict(data)
        assert restored == snapshot

    def test_from_dict_ignores_extra_keys(self):
        data = {
            "timestamp": "2026-01-01",
            "overall": "healthy",
            "dimensions_checked": 1,
            "p1_count": 0,
            "p2_count": 0,
            "test_files": 10,
            "packages": 2,
            "extra_field": "ignored",
        }
        snapshot = HealthSnapshot.from_dict(data)
        assert snapshot.timestamp == "2026-01-01"


class TestHistoryStore:
    def test_save_and_load(self, tmp_path: Path):
        store = HistoryStore(_make_config(tmp_path))
        snapshot = HealthSnapshot(
            timestamp="2026-03-28T12:00:00",
            overall="healthy",
            dimensions_checked=2,
            p1_count=0,
            p2_count=0,
            test_files=50,
            packages=5,
        )
        path = store.save_snapshot(snapshot)
        assert path.exists()

        loaded = store.load_snapshots()
        assert len(loaded) == 1
        assert loaded[0] == snapshot

    def test_load_empty(self, tmp_path: Path):
        store = HistoryStore(_make_config(tmp_path))
        assert store.load_snapshots() == []

    def test_load_multiple_sorted(self, tmp_path: Path):
        store = HistoryStore(_make_config(tmp_path))
        timestamps = ["2026-03-26T10:00:00", "2026-03-27T10:00:00", "2026-03-28T10:00:00"]
        for i, ts in enumerate(timestamps):
            store.save_snapshot(
                HealthSnapshot(
                    timestamp=ts,
                    overall="healthy",
                    dimensions_checked=i + 1,
                    p1_count=0,
                    p2_count=0,
                    test_files=i * 10,
                    packages=4,
                )
            )

        loaded = store.load_snapshots()
        assert len(loaded) == 3
        # Chronological order
        assert loaded[0].timestamp == "2026-03-26T10:00:00"
        assert loaded[2].timestamp == "2026-03-28T10:00:00"

    def test_get_trend_data(self, tmp_path: Path):
        store = HistoryStore(_make_config(tmp_path))
        store.save_snapshot(
            HealthSnapshot(
                timestamp="2026-03-28T12:00:00",
                overall="healthy",
                dimensions_checked=1,
                p1_count=0,
                p2_count=0,
                test_files=42,
                packages=4,
            )
        )

        timestamps, counts = store.get_trend_data()
        assert timestamps == ["2026-03-28"]
        assert counts == [42]

    def test_corrupt_file_skipped(self, tmp_path: Path):
        config = _make_config(tmp_path)
        store = HistoryStore(config)

        # Schrijf een corrupt bestand
        history_dir = config.history_path
        history_dir.mkdir(parents=True)
        (history_dir / "health_2026-03-28T12-00-00.json").write_text("not json!")

        # Schrijf een geldig bestand
        store.save_snapshot(
            HealthSnapshot(
                timestamp="2026-03-29T10:00:00",
                overall="healthy",
                dimensions_checked=1,
                p1_count=0,
                p2_count=0,
                test_files=10,
                packages=3,
            )
        )

        loaded = store.load_snapshots()
        assert len(loaded) == 1
        assert loaded[0].timestamp == "2026-03-29T10:00:00"

    def test_limit_parameter(self, tmp_path: Path):
        store = HistoryStore(_make_config(tmp_path))
        for i in range(10):
            store.save_snapshot(
                HealthSnapshot(
                    timestamp=f"2026-03-{20 + i:02d}T10:00:00",
                    overall="healthy",
                    dimensions_checked=1,
                    p1_count=0,
                    p2_count=0,
                    test_files=i,
                    packages=1,
                )
            )

        loaded = store.load_snapshots(limit=3)
        assert len(loaded) == 3
        # Meest recente 3, chronologisch
        assert loaded[0].timestamp.startswith("2026-03-27")
        assert loaded[2].timestamp.startswith("2026-03-29")
