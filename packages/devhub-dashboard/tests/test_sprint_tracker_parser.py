"""Tests voor SprintTrackerParser — parsing van SPRINT_TRACKER.md."""

from pathlib import Path


from devhub_dashboard.data.sprint_tracker_parser import (
    SprintTrackerParser,
    TrackerFrontmatter,
    _parse_cycle_time_to_days,
)

# Minimale SPRINT_TRACKER.md in drie-lagen structuur
_MINIMAL_TRACKER = """\
---
gegenereerd_door: "Cowork — alsdan-devhub"
status: ACTIEF
actieve_fase: null
laatste_sprint: 5
test_baseline: 500
laatst_bijgewerkt: 2026-03-28
---

## Fase-overzicht

```
Fase 0 ✅ → Fase 1 ✅ → Fase 2 🔄 → Fase 3 🔲 → Fase 4 🔲 → Fase 5 🔲
```

## Strategisch Overzicht

### Now

Geen actieve sprint. Laatste: Sprint 5 (Planning Opschoning) ✅

### Next

| Intake | Stroom | Type |
|--------|--------|------|
| Example Intake | Governance | FEAT |

### Later

- Fase 5 visie

## Fase 0-3 (Afgerond)

| Fase | Sprints | Tests | Duur | Kern |
|------|---------|-------|------|------|
| 0 — Fundament | 2 | 0 → 397 | <1 dag | Tooling |
| 1 — Kernagents | 2 | 218 → 339 | 1 dag | Agents |

## Metrics (samenvatting)

| Metric | Waarde |
|--------|--------|
| Sprints afgerond | 5 |

_Volledig overzicht: [VELOCITY_LOG.md](VELOCITY_LOG.md)_
"""

# Minimale VELOCITY_LOG.md
_MINIMAL_VELOCITY_LOG = """\
---
gegenereerd_door: "Cowork — alsdan-devhub"
laatst_bijgewerkt: 2026-03-28
---

## Sprint Log

| # | Sprint | Gepland | Werkelijk | Tests Δ | Schatting-nauwkeurigheid |
|---|--------|---------|-----------|---------|--------------------------|
| 1 | Bootstrap | 1 sprint | 1 sprint | +81 | 100% |
| 2 | Skills Governance | 1 sprint | 1 sprint | +40 | 100% |
| 3 | N8N CICD | 1 sprint | 1 sprint | +31 | 100% |
| 4 | Quick Fixes | XS (<1.5u) | XS (<1u) | +2 | 100% |
| 5 | Planning Opschoning | XS (<1u) | XS (<1u) | +0 | 100% |

## Cycle Time

### Item Lifecycle Tracking

| Item | Inbox datum | Sprint start | Sprint klaar | Cycle time |
|------|-------------|--------------|--------------|------------|
| Bootstrap | 2026-03-23 | 2026-03-23 | 2026-03-23 | <1 dag |
| Skills Governance | 2026-03-23 | 2026-03-23 | 2026-03-23 | <1 dag |
| N8N CICD | 2026-03-24 | 2026-03-24 | 2026-03-25 | 1 dag |
| Quick Fixes | 2026-03-25 | 2026-03-26 | 2026-03-26 | 1 dag |
| Planning Opschoning | 2026-03-25 | 2026-03-26 | 2026-03-26 | 2 dagen |
"""

# Legacy tracker zonder velocity log (backward compatibility)
_LEGACY_TRACKER = """\
---
gegenereerd_door: "Cowork — alsdan-devhub"
status: ACTIEF
actieve_fase: null
laatste_sprint: 5
test_baseline: 500
laatst_bijgewerkt: 2026-03-28
---

## Fase-overzicht

```
Fase 0 ✅ → Fase 1 ✅ → Fase 2 🔄 → Fase 3 🔲 → Fase 4 🔲 → Fase 5 🔲
```

## Velocity Tracking

### Sprint Log

| # | Sprint | Gepland | Werkelijk | Tests Δ | Schatting-nauwkeurigheid |
|---|--------|---------|-----------|---------|--------------------------|
| 1 | Bootstrap | 1 sprint | 1 sprint | +81 | 100% |
| 2 | Skills Governance | 1 sprint | 1 sprint | +40 | 100% |
| 3 | N8N CICD | 1 sprint | 1 sprint | +31 | 100% |
| 4 | Quick Fixes | XS (<1.5u) | XS (<1u) | +2 | 100% |
| 5 | Planning Opschoning | XS (<1u) | XS (<1u) | +0 | 100% |

### Afgeleide metrics

| Metric | Waarde |
|--------|--------|
| Sprints afgerond | 5 |

## Cycle Time

### Item Lifecycle Tracking

| Item | Inbox datum | Sprint start | Sprint klaar | Cycle time |
|------|-------------|--------------|--------------|------------|
| Bootstrap | 2026-03-23 | 2026-03-23 | 2026-03-23 | <1 dag |
| Skills Governance | 2026-03-23 | 2026-03-23 | 2026-03-23 | <1 dag |
| N8N CICD | 2026-03-24 | 2026-03-24 | 2026-03-25 | 1 dag |
| Quick Fixes | 2026-03-25 | 2026-03-26 | 2026-03-26 | 1 dag |
| Planning Opschoning | 2026-03-25 | 2026-03-26 | 2026-03-26 | 2 dagen |
"""


def _write_files(
    tmp_path: Path,
    tracker: str = _MINIMAL_TRACKER,
    velocity_log: str | None = _MINIMAL_VELOCITY_LOG,
) -> tuple[Path, Path | None]:
    tracker_path = tmp_path / "SPRINT_TRACKER.md"
    tracker_path.write_text(tracker, encoding="utf-8")
    velocity_path = None
    if velocity_log is not None:
        velocity_path = tmp_path / "VELOCITY_LOG.md"
        velocity_path.write_text(velocity_log, encoding="utf-8")
    return tracker_path, velocity_path


class TestTrackerFrontmatter:
    def test_parse_frontmatter(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        fm = parser.parse_frontmatter()
        assert fm.status == "ACTIEF"
        assert fm.laatste_sprint == 5
        assert fm.test_baseline == 500
        assert fm.laatst_bijgewerkt == "2026-03-28"

    def test_parse_frontmatter_missing_file(self, tmp_path: Path):
        parser = SprintTrackerParser(tmp_path / "nonexistent.md")
        fm = parser.parse_frontmatter()
        assert fm == TrackerFrontmatter()

    def test_parse_frontmatter_no_frontmatter(self, tmp_path: Path):
        path = tmp_path / "tracker.md"
        path.write_text("# Just a heading\nNo frontmatter here.")
        parser = SprintTrackerParser(path)
        fm = parser.parse_frontmatter()
        assert fm.laatste_sprint == 0


class TestSprintHistory:
    def test_parse_sprint_history_from_velocity_log(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        history = parser.parse_sprint_history()
        assert len(history) == 5

    def test_first_sprint_data(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        history = parser.parse_sprint_history()
        first = history[0]
        assert first.nummer == 1
        assert first.naam == "Bootstrap"
        assert first.tests_delta == 81
        assert first.status == "DONE"

    def test_sprint_type_inference(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        history = parser.parse_sprint_history()
        opschoning = next(h for h in history if "Opschoning" in h.naam)
        assert opschoning.sprint_type == "CHORE"

    def test_sprint_size_inference(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        history = parser.parse_sprint_history()
        quick = next(h for h in history if "Quick" in h.naam)
        assert quick.size == "XS"
        bootstrap = history[0]
        assert bootstrap.size == "S"

    def test_empty_history(self, tmp_path: Path):
        parser = SprintTrackerParser(tmp_path / "nonexistent.md")
        assert parser.parse_sprint_history() == []

    def test_zero_delta_sprint(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        history = parser.parse_sprint_history()
        opschoning = next(h for h in history if "Opschoning" in h.naam)
        assert opschoning.tests_delta == 0

    def test_fallback_to_tracker_without_velocity_log(self, tmp_path: Path):
        """Zonder velocity_log_path valt de parser terug op de tracker zelf."""
        tracker_path, _ = _write_files(tmp_path, tracker=_LEGACY_TRACKER, velocity_log=None)
        parser = SprintTrackerParser(tracker_path)
        history = parser.parse_sprint_history()
        assert len(history) == 5


class TestCycleTime:
    def test_parse_cycle_times(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        entries = parser.parse_cycle_times()
        assert len(entries) == 5

    def test_cycle_time_data(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        entries = parser.parse_cycle_times()
        first = entries[0]
        assert first.item == "Bootstrap"
        assert first.inbox_datum == "2026-03-23"
        assert first.cycle_time == "<1 dag"

    def test_cycle_time_to_days(self):
        assert _parse_cycle_time_to_days("<1 dag") == 0.5
        assert _parse_cycle_time_to_days("1 dag") == 1.0
        assert _parse_cycle_time_to_days("2 dagen") == 2.0
        assert _parse_cycle_time_to_days("4 dagen") == 4.0

    def test_empty_cycle_times(self, tmp_path: Path):
        parser = SprintTrackerParser(tmp_path / "nonexistent.md")
        assert parser.parse_cycle_times() == []

    def test_cycle_times_from_legacy_tracker(self, tmp_path: Path):
        tracker_path, _ = _write_files(tmp_path, tracker=_LEGACY_TRACKER, velocity_log=None)
        parser = SprintTrackerParser(tracker_path)
        entries = parser.parse_cycle_times()
        assert len(entries) == 5


class TestFaseProgress:
    def test_parse_fase_progress(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        fases = parser.parse_fase_progress()
        assert len(fases) == 6

    def test_fase_done_status(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        fases = parser.parse_fase_progress()
        assert fases[0].done is True  # Fase 0 ✅
        assert fases[1].done is True  # Fase 1 ✅
        assert fases[2].done is False  # Fase 2 🔄

    def test_fase_active_status(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        fases = parser.parse_fase_progress()
        assert fases[2].active is True  # Fase 2 🔄
        assert fases[0].active is False

    def test_fase_names(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        fases = parser.parse_fase_progress()
        assert fases[0].naam == "Fundament"
        assert fases[4].naam == "Verbindingen"

    def test_fase_sprint_count_from_summary_table(self, tmp_path: Path):
        """Fase sprint counts uit gecollabste samenvattingstabel."""
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        fases = parser.parse_fase_progress()
        assert fases[0].sprint_count == 2  # Fase 0: 2 sprints
        assert fases[1].sprint_count == 2  # Fase 1: 2 sprints


class TestVelocityData:
    def test_get_velocity_data(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        labels, deltas = parser.get_velocity_data()
        assert len(labels) == 5
        assert labels[0] == "#1"
        assert deltas[0] == 81

    def test_get_cycle_time_days(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        labels, days = parser.get_cycle_time_days()
        assert len(labels) == 5
        assert days[0] == 0.5  # <1 dag
        assert days[2] == 1.0  # 1 dag


class TestDerivedMetrics:
    def test_get_derived_metrics(self, tmp_path: Path):
        tracker_path, velocity_path = _write_files(tmp_path)
        parser = SprintTrackerParser(tracker_path, velocity_path)
        metrics = parser.get_derived_metrics()
        assert metrics["sprints_afgerond"] == 5
        assert metrics["test_baseline"] == 500
        assert metrics["avg_test_delta"] > 0
        assert metrics["total_sprints_with_tests"] == 4  # Opschoning heeft 0

    def test_derived_metrics_empty(self, tmp_path: Path):
        parser = SprintTrackerParser(tmp_path / "nonexistent.md")
        metrics = parser.get_derived_metrics()
        assert metrics["sprints_afgerond"] == 0
        assert metrics["avg_test_delta"] == 0.0
