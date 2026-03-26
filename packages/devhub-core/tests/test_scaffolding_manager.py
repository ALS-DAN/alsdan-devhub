"""Tests voor ScaffoldingManager — Mentor S2."""

from __future__ import annotations

import pytest

from devhub_core.agents.scaffolding_manager import ScaffoldingManager
from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    SkillDomain,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_domain(name: str = "Python", level: int = 1) -> SkillDomain:
    return SkillDomain(name=name, level=level)


def _make_challenge(scaffolding: str = "HIGH") -> DevelopmentChallenge:
    return DevelopmentChallenge(
        challenge_id="CH-TEST-01",
        challenge_type="explain_it",
        domain="Python",
        description="Test challenge",
        scaffolding_level=scaffolding,
    )


# ---------------------------------------------------------------------------
# get_scaffolding
# ---------------------------------------------------------------------------


class TestGetScaffolding:
    def test_level_1_returns_high(self) -> None:
        mgr = ScaffoldingManager()
        assert mgr.get_scaffolding(1) == "HIGH"

    def test_level_2_returns_medium(self) -> None:
        mgr = ScaffoldingManager()
        assert mgr.get_scaffolding(2) == "MEDIUM"

    def test_level_3_returns_low(self) -> None:
        mgr = ScaffoldingManager()
        assert mgr.get_scaffolding(3) == "LOW"

    def test_level_4_returns_none(self) -> None:
        mgr = ScaffoldingManager()
        assert mgr.get_scaffolding(4) == "NONE"

    def test_level_5_returns_none(self) -> None:
        mgr = ScaffoldingManager()
        assert mgr.get_scaffolding(5) == "NONE"

    def test_invalid_level_raises(self) -> None:
        mgr = ScaffoldingManager()
        with pytest.raises(ValueError, match="level must be 1-5"):
            mgr.get_scaffolding(6)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# should_reduce
# ---------------------------------------------------------------------------


class TestShouldReduce:
    def test_level_4_no_reduction(self) -> None:
        mgr = ScaffoldingManager()
        domain = _make_domain(level=4)
        assert mgr.should_reduce(domain, challenges_completed=3) is False

    def test_level_5_no_reduction(self) -> None:
        mgr = ScaffoldingManager()
        domain = _make_domain(level=5)
        assert mgr.should_reduce(domain, challenges_completed=5) is False

    def test_level_3_with_completed_challenges(self) -> None:
        mgr = ScaffoldingManager()
        domain = _make_domain(level=3)
        assert mgr.should_reduce(domain, challenges_completed=1) is True

    def test_stagnation_detected(self) -> None:
        mgr = ScaffoldingManager()
        domain = _make_domain(level=2)
        assert mgr.should_reduce(domain, challenges_completed=2, sprints_at_level=3) is True

    def test_no_stagnation_within_threshold(self) -> None:
        mgr = ScaffoldingManager()
        domain = _make_domain(level=2)
        assert mgr.should_reduce(domain, challenges_completed=1, sprints_at_level=2) is False

    def test_no_completed_challenges_no_reduction(self) -> None:
        mgr = ScaffoldingManager()
        domain = _make_domain(level=2)
        assert mgr.should_reduce(domain, challenges_completed=0, sprints_at_level=5) is False


# ---------------------------------------------------------------------------
# apply_scaffolding
# ---------------------------------------------------------------------------


class TestApplyScaffolding:
    def test_returns_new_instance(self) -> None:
        mgr = ScaffoldingManager()
        original = _make_challenge("HIGH")
        result = mgr.apply_scaffolding(original, level=3)
        assert result is not original

    def test_sets_correct_level(self) -> None:
        mgr = ScaffoldingManager()
        ch = _make_challenge("HIGH")
        result = mgr.apply_scaffolding(ch, level=2)
        assert result.scaffolding_level == "MEDIUM"

    def test_preserves_other_fields(self) -> None:
        mgr = ScaffoldingManager()
        original = _make_challenge("HIGH")
        result = mgr.apply_scaffolding(original, level=3)
        assert result.challenge_id == original.challenge_id
        assert result.domain == original.domain
        assert result.description == original.description
        assert result.challenge_type == original.challenge_type

    def test_frozen_original_unchanged(self) -> None:
        mgr = ScaffoldingManager()
        original = _make_challenge("HIGH")
        mgr.apply_scaffolding(original, level=5)
        assert original.scaffolding_level == "HIGH"


# ---------------------------------------------------------------------------
# reduce_scaffolding
# ---------------------------------------------------------------------------


class TestReduceScaffolding:
    def test_high_to_medium(self) -> None:
        mgr = ScaffoldingManager()
        ch = _make_challenge("HIGH")
        result = mgr.reduce_scaffolding(ch)
        assert result.scaffolding_level == "MEDIUM"

    def test_medium_to_low(self) -> None:
        mgr = ScaffoldingManager()
        ch = _make_challenge("MEDIUM")
        result = mgr.reduce_scaffolding(ch)
        assert result.scaffolding_level == "LOW"

    def test_low_to_none(self) -> None:
        mgr = ScaffoldingManager()
        ch = _make_challenge("LOW")
        result = mgr.reduce_scaffolding(ch)
        assert result.scaffolding_level == "NONE"

    def test_none_stays_none(self) -> None:
        mgr = ScaffoldingManager()
        ch = _make_challenge("NONE")
        result = mgr.reduce_scaffolding(ch)
        assert result.scaffolding_level == "NONE"


# ---------------------------------------------------------------------------
# is_lower_than
# ---------------------------------------------------------------------------


class TestIsLowerThan:
    def test_none_lower_than_high(self) -> None:
        assert ScaffoldingManager.is_lower_than("NONE", "HIGH") is True

    def test_high_not_lower_than_none(self) -> None:
        assert ScaffoldingManager.is_lower_than("HIGH", "NONE") is False

    def test_same_not_lower(self) -> None:
        assert ScaffoldingManager.is_lower_than("MEDIUM", "MEDIUM") is False
