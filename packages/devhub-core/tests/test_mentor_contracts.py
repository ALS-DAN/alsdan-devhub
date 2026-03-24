"""Tests voor F5 mentor contracts: DeveloperPhase, CoachingSignal, DeveloperProfile, CoachingResponse."""

import pytest

from devhub_core.contracts.node_interface import (
    CoachingResponse,
    CoachingSignal,
    DeveloperPhase,
    DeveloperProfile,
)


class TestDeveloperPhase:
    def test_phase_values(self):
        assert DeveloperPhase.ORIENTEREN.value == "ORIËNTEREN"
        assert DeveloperPhase.BOUWEN.value == "BOUWEN"
        assert DeveloperPhase.BEHEERSEN.value == "BEHEERSEN"

    def test_all_phases(self):
        assert len(DeveloperPhase) == 3


class TestCoachingSignal:
    def test_signal_values(self):
        assert CoachingSignal.GREEN.value == "GROEN"
        assert CoachingSignal.ATTENTION.value == "AANDACHT"
        assert CoachingSignal.STAGNATION.value == "STAGNATIE"


class TestDeveloperProfile:
    def test_valid_profile(self):
        p = DeveloperProfile(
            current_phase=DeveloperPhase.BOUWEN,
            streak_days=5,
            blockers_open=0,
            tests_delta_total=42,
            recent_entry_count=7,
            last_entry_date="2026-03-23",
            coaching_signal=CoachingSignal.GREEN,
        )
        assert p.current_phase == DeveloperPhase.BOUWEN
        assert p.streak_days == 5
        assert p.coaching_signal == CoachingSignal.GREEN

    def test_frozen(self):
        p = DeveloperProfile(
            current_phase=DeveloperPhase.ORIENTEREN,
            streak_days=0,
            blockers_open=0,
            tests_delta_total=0,
            recent_entry_count=0,
        )
        with pytest.raises(AttributeError):
            p.streak_days = 10  # type: ignore[misc]

    def test_negative_streak_raises(self):
        with pytest.raises(ValueError, match="streak_days"):
            DeveloperProfile(
                current_phase=DeveloperPhase.ORIENTEREN,
                streak_days=-1,
                blockers_open=0,
                tests_delta_total=0,
                recent_entry_count=0,
            )

    def test_negative_entry_count_raises(self):
        with pytest.raises(ValueError, match="recent_entry_count"):
            DeveloperProfile(
                current_phase=DeveloperPhase.ORIENTEREN,
                streak_days=0,
                blockers_open=0,
                tests_delta_total=0,
                recent_entry_count=-1,
            )

    def test_defaults(self):
        p = DeveloperProfile(
            current_phase=DeveloperPhase.ORIENTEREN,
            streak_days=0,
            blockers_open=0,
            tests_delta_total=0,
            recent_entry_count=0,
        )
        assert p.last_entry_date is None
        assert p.coaching_signal == CoachingSignal.GREEN

    def test_stagnation_profile(self):
        p = DeveloperProfile(
            current_phase=DeveloperPhase.ORIENTEREN,
            streak_days=0,
            blockers_open=0,
            tests_delta_total=0,
            recent_entry_count=0,
            coaching_signal=CoachingSignal.STAGNATION,
        )
        assert p.coaching_signal == CoachingSignal.STAGNATION


class TestCoachingResponse:
    def test_valid_response(self):
        r = CoachingResponse(
            date="2026-03-23",
            phase=DeveloperPhase.BOUWEN,
            signal=CoachingSignal.GREEN,
            observation="Actief aan F5 gewerkt, tests groeien",
            actions=("Schrijf mentor adapter tests", "Run full suite"),
            check_question="Wat is je volgende concrete stap?",
        )
        assert r.phase == DeveloperPhase.BOUWEN
        assert len(r.actions) == 2
        assert r.risk_alert == ""

    def test_response_with_risk(self):
        r = CoachingResponse(
            date="2026-03-23",
            phase=DeveloperPhase.ORIENTEREN,
            signal=CoachingSignal.ATTENTION,
            observation="Blocker al 3 dagen open",
            actions=("Beschrijf de blocker concreet",),
            check_question="Wat houdt je exact tegen?",
            risk_alert="BLOCKER >2 dagen — doorbraakstrategie nodig",
        )
        assert r.risk_alert != ""

    def test_empty_observation_raises(self):
        with pytest.raises(ValueError, match="observation"):
            CoachingResponse(
                date="2026-03-23",
                phase=DeveloperPhase.BOUWEN,
                signal=CoachingSignal.GREEN,
                observation="",
                actions=("doe iets",),
                check_question="hoe gaat het?",
            )

    def test_empty_actions_raises(self):
        with pytest.raises(ValueError, match="action"):
            CoachingResponse(
                date="2026-03-23",
                phase=DeveloperPhase.BOUWEN,
                signal=CoachingSignal.GREEN,
                observation="bezig",
                actions=(),
                check_question="hoe gaat het?",
            )

    def test_empty_check_question_raises(self):
        with pytest.raises(ValueError, match="check_question"):
            CoachingResponse(
                date="2026-03-23",
                phase=DeveloperPhase.BOUWEN,
                signal=CoachingSignal.GREEN,
                observation="bezig",
                actions=("stap 1",),
                check_question="",
            )

    def test_frozen(self):
        r = CoachingResponse(
            date="2026-03-23",
            phase=DeveloperPhase.BOUWEN,
            signal=CoachingSignal.GREEN,
            observation="ok",
            actions=("stap",),
            check_question="vraag?",
        )
        with pytest.raises(AttributeError):
            r.signal = CoachingSignal.ATTENTION  # type: ignore[misc]
