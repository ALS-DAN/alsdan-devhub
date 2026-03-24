"""Tests voor F5 BorisAdapter mentor methods: get_developer_profile, coaching signal computation."""

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from devhub_core.adapters.boris_adapter import BorisAdapter
from devhub_core.contracts.node_interface import (
    CoachingSignal,
    DeveloperPhase,
)


@pytest.fixture
def boris_path(tmp_path):
    """Maak een minimal BORIS-achtige structuur met developer_progress.db."""
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "python").write_text("#!/bin/sh\n")
    (tmp_path / "mkdocs.yml").write_text("nav: []\n")
    return tmp_path


@pytest.fixture
def adapter(boris_path):
    return BorisAdapter(str(boris_path))


def _create_db(boris_path: Path) -> Path:
    """Maak een developer_progress.db met schema."""
    data_dir = boris_path / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "developer_progress.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE developer_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,
            fase TEXT NOT NULL,
            gedaan TEXT NOT NULL,
            geleerd TEXT NOT NULL,
            blocker TEXT NOT NULL,
            morgen TEXT NOT NULL,
            tests_total INTEGER NOT NULL DEFAULT 0,
            tests_delta INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    return db_path


def _insert_entry(db_path: Path, datum: str, fase: str, blocker: str = "geen",
                   tests_total: int = 100, tests_delta: int = 5):
    """Insert een developer entry."""
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO developer_entries (datum, fase, gedaan, geleerd, blocker, morgen, tests_total, tests_delta, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datum, fase, "test gedaan", "test geleerd", blocker, "test morgen", tests_total, tests_delta,
         datetime.now(UTC).isoformat()),
    )
    conn.commit()
    conn.close()


class TestGetDeveloperProfileNoDb:
    def test_no_db_returns_orienteren(self, adapter):
        profile = adapter.get_developer_profile()
        assert profile.current_phase == DeveloperPhase.ORIENTEREN
        assert profile.coaching_signal == CoachingSignal.STAGNATION
        assert profile.recent_entry_count == 0

    def test_empty_db_returns_orienteren(self, adapter, boris_path):
        _create_db(boris_path)
        profile = adapter.get_developer_profile()
        assert profile.current_phase == DeveloperPhase.ORIENTEREN
        assert profile.coaching_signal == CoachingSignal.STAGNATION


class TestGetDeveloperProfileWithData:
    def test_active_bouwen(self, adapter, boris_path):
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date()
        for i in range(5):
            d = (today - timedelta(days=i)).isoformat()
            _insert_entry(db_path, d, "BOUWEN", tests_delta=10)

        profile = adapter.get_developer_profile(days=30)
        assert profile.current_phase == DeveloperPhase.BOUWEN
        assert profile.coaching_signal == CoachingSignal.GREEN
        assert profile.streak_days >= 4
        assert profile.tests_delta_total == 50
        assert profile.recent_entry_count == 5

    def test_mixed_phases_conservatief(self, adapter, boris_path):
        """Bij gelijkspel wint ORIËNTEREN."""
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date()
        _insert_entry(db_path, today.isoformat(), "BOUWEN")
        _insert_entry(db_path, (today - timedelta(days=1)).isoformat(), "ORIËNTEREN")

        profile = adapter.get_developer_profile(days=7)
        assert profile.current_phase == DeveloperPhase.ORIENTEREN

    def test_beheersen_majority(self, adapter, boris_path):
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date()
        for i in range(3):
            _insert_entry(db_path, (today - timedelta(days=i)).isoformat(), "BEHEERSEN")
        _insert_entry(db_path, (today - timedelta(days=3)).isoformat(), "BOUWEN")

        profile = adapter.get_developer_profile(days=7)
        assert profile.current_phase == DeveloperPhase.BEHEERSEN

    def test_blockers_trigger_attention(self, adapter, boris_path):
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date()
        _insert_entry(db_path, today.isoformat(), "BOUWEN", blocker="CI faalt op test_foo")

        profile = adapter.get_developer_profile(days=7)
        assert profile.coaching_signal == CoachingSignal.ATTENTION
        assert profile.blockers_open == 1

    def test_tests_declining_attention(self, adapter, boris_path):
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date()
        _insert_entry(db_path, today.isoformat(), "BOUWEN", tests_delta=-5)

        profile = adapter.get_developer_profile(days=7)
        assert profile.coaching_signal == CoachingSignal.ATTENTION

    def test_old_entries_stagnation(self, adapter, boris_path):
        """Entries >5 dagen oud zonder recente → stagnatie."""
        db_path = _create_db(boris_path)
        old = (datetime.now(UTC).date() - timedelta(days=10)).isoformat()
        _insert_entry(db_path, old, "BOUWEN")

        profile = adapter.get_developer_profile(days=30)
        assert profile.coaching_signal == CoachingSignal.STAGNATION

    def test_last_entry_date(self, adapter, boris_path):
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date().isoformat()
        _insert_entry(db_path, today, "BOUWEN")

        profile = adapter.get_developer_profile(days=7)
        assert profile.last_entry_date == today


class TestGetRecentProgressEntries:
    def test_no_db_returns_empty(self, adapter):
        assert adapter.get_recent_progress_entries() == []

    def test_returns_recent(self, adapter, boris_path):
        db_path = _create_db(boris_path)
        today = datetime.now(UTC).date()
        _insert_entry(db_path, today.isoformat(), "BOUWEN")
        _insert_entry(db_path, (today - timedelta(days=1)).isoformat(), "BOUWEN")

        entries = adapter.get_recent_progress_entries(days=7)
        assert len(entries) == 2
        assert "gedaan" in entries[0]
        assert "fase" in entries[0]


class TestComputeCoachingSignal:
    def test_green(self):
        signal = BorisAdapter._compute_coaching_signal(
            days_since_last=0, blockers_open=0, tests_delta=10,
            current_phase=DeveloperPhase.BOUWEN, entry_count=5, days_window=7,
        )
        assert signal == CoachingSignal.GREEN

    def test_stagnation_no_entries(self):
        signal = BorisAdapter._compute_coaching_signal(
            days_since_last=6, blockers_open=0, tests_delta=0,
            current_phase=DeveloperPhase.BOUWEN, entry_count=0, days_window=7,
        )
        assert signal == CoachingSignal.STAGNATION

    def test_attention_blocker(self):
        signal = BorisAdapter._compute_coaching_signal(
            days_since_last=0, blockers_open=2, tests_delta=5,
            current_phase=DeveloperPhase.BOUWEN, entry_count=5, days_window=7,
        )
        assert signal == CoachingSignal.ATTENTION

    def test_attention_tests_declining(self):
        signal = BorisAdapter._compute_coaching_signal(
            days_since_last=0, blockers_open=0, tests_delta=-3,
            current_phase=DeveloperPhase.BOUWEN, entry_count=5, days_window=7,
        )
        assert signal == CoachingSignal.ATTENTION

    def test_stagnation_long_orienteren(self):
        signal = BorisAdapter._compute_coaching_signal(
            days_since_last=1, blockers_open=0, tests_delta=0,
            current_phase=DeveloperPhase.ORIENTEREN, entry_count=14, days_window=14,
        )
        assert signal == CoachingSignal.STAGNATION
