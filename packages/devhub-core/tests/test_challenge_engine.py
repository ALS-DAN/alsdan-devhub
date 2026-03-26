"""Tests voor ChallengeEngine — Mentor S2."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from devhub_core.agents.challenge_engine import ChallengeEngine
from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    SkillDomain,
    SkillRadarProfile,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_domain(
    name: str = "Python",
    level: int = 1,
    growth_velocity: float = 0.1,
    zpd_tasks: tuple[str, ...] = ("Een test lezen",),
) -> SkillDomain:
    return SkillDomain(
        name=name,
        level=level,
        growth_velocity=growth_velocity,
        zpd_tasks=zpd_tasks,
    )


def _make_profile(
    domains: tuple[SkillDomain, ...] | None = None,
    primary_gap: str = "Python",
) -> SkillRadarProfile:
    if domains is None:
        domains = (
            _make_domain("Python", 1, 0.1),
            _make_domain("AI-Engineering", 2, 0.2),
            _make_domain("Architecture", 3, 0.1),
        )
    return SkillRadarProfile(
        developer="Niels",
        date="2026-03-26",
        domains=domains,
        primary_gap=primary_gap,
    )


# ---------------------------------------------------------------------------
# ChallengeEngine initialization
# ---------------------------------------------------------------------------


class TestChallengeEngineInit:
    def test_init_without_templates(self) -> None:
        engine = ChallengeEngine()
        assert engine._templates is not None
        assert len(engine._templates) == 6  # 6 fallback templates

    def test_init_with_nonexistent_path(self) -> None:
        engine = ChallengeEngine(templates_path=Path("/nonexistent/path.yml"))
        assert len(engine._templates) == 6

    def test_init_with_valid_templates(self, tmp_path: Path) -> None:
        templates_file = tmp_path / "templates.yml"
        templates_file.write_text(
            yaml.dump(
                {
                    "templates": [
                        {
                            "challenge_type": "stretch",
                            "description_template": "Test: {zpd_task}",
                            "success_criteria": ["Test ok"],
                            "estimated_minutes": 15,
                        }
                    ]
                }
            )
        )
        engine = ChallengeEngine(templates_path=templates_file)
        assert len(engine._templates) == 1

    def test_init_with_empty_templates_file(self, tmp_path: Path) -> None:
        templates_file = tmp_path / "templates.yml"
        templates_file.write_text(yaml.dump({"templates": []}))
        engine = ChallengeEngine(templates_path=templates_file)
        assert len(engine._templates) == 6  # Falls back


# ---------------------------------------------------------------------------
# Challenge generation
# ---------------------------------------------------------------------------


class TestGenerateChallenges:
    def test_empty_profile_returns_empty(self) -> None:
        engine = ChallengeEngine()
        profile = SkillRadarProfile(developer="Niels", date="2026-03-26", domains=())
        result = engine.generate_challenges(profile)
        assert result == []

    def test_generates_requested_count(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile()
        result = engine.generate_challenges(profile, count=2)
        assert len(result) == 2

    def test_generates_single_challenge(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile()
        result = engine.generate_challenges(profile, count=1)
        assert len(result) == 1

    def test_count_capped_by_domains(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile(domains=(_make_domain(),))
        result = engine.generate_challenges(profile, count=5)
        assert len(result) == 1

    def test_invalid_count_raises(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile()
        with pytest.raises(ValueError, match="count must be >= 1"):
            engine.generate_challenges(profile, count=0)

    def test_output_is_development_challenge(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile()
        result = engine.generate_challenges(profile, count=1)
        assert isinstance(result[0], DevelopmentChallenge)

    def test_challenge_has_required_fields(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile()
        ch = engine.generate_challenges(profile, count=1)[0]
        assert ch.challenge_id.startswith("CH-")
        assert ch.domain == "Python"  # primary_gap first
        assert ch.description  # Non-empty
        assert ch.zpd_rationale  # Non-empty
        assert ch.status == "PROPOSED"
        assert ch.created

    def test_primary_gap_prioritized(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile(primary_gap="Python")
        result = engine.generate_challenges(profile, count=1)
        assert result[0].domain == "Python"

    def test_growth_velocity_ordering(self) -> None:
        engine = ChallengeEngine()
        domains = (
            _make_domain("Fast", 2, growth_velocity=0.9),
            _make_domain("Slow", 2, growth_velocity=0.01),
        )
        profile = _make_profile(domains=domains, primary_gap="")
        result = engine.generate_challenges(profile, count=2)
        # Slow velocity domain should come first (more need)
        assert result[0].domain == "Slow"
        assert result[1].domain == "Fast"

    def test_challenges_are_frozen(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile()
        ch = engine.generate_challenges(profile, count=1)[0]
        with pytest.raises(AttributeError):
            ch.status = "COMPLETED"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Challenge type selection
# ---------------------------------------------------------------------------


class TestSelectChallengeType:
    def test_level_1_gets_explain_it(self) -> None:
        engine = ChallengeEngine()
        domain = _make_domain(level=1)
        assert engine.select_challenge_type(domain) == "explain_it"

    def test_level_2_gets_stretch(self) -> None:
        engine = ChallengeEngine()
        domain = _make_domain(level=2)
        assert engine.select_challenge_type(domain) == "stretch"

    def test_level_3_gets_cross_domain(self) -> None:
        engine = ChallengeEngine()
        domain = _make_domain(level=3)
        assert engine.select_challenge_type(domain) == "cross_domain"

    def test_level_4_gets_cross_domain(self) -> None:
        engine = ChallengeEngine()
        domain = _make_domain(level=4)
        assert engine.select_challenge_type(domain) == "cross_domain"

    def test_level_5_gets_cross_domain(self) -> None:
        engine = ChallengeEngine()
        domain = _make_domain(level=5)
        assert engine.select_challenge_type(domain) == "cross_domain"


# ---------------------------------------------------------------------------
# Scaffolding assignment in challenges
# ---------------------------------------------------------------------------


class TestScaffoldingInChallenges:
    def test_level_1_gets_high_scaffolding(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile(domains=(_make_domain(level=1),))
        ch = engine.generate_challenges(profile, count=1)[0]
        assert ch.scaffolding_level == "HIGH"

    def test_level_2_gets_medium_scaffolding(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile(domains=(_make_domain(level=2),), primary_gap="Python")
        ch = engine.generate_challenges(profile, count=1)[0]
        assert ch.scaffolding_level == "MEDIUM"

    def test_level_3_gets_low_scaffolding(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile(domains=(_make_domain(level=3),), primary_gap="Python")
        ch = engine.generate_challenges(profile, count=1)[0]
        assert ch.scaffolding_level == "LOW"

    def test_level_5_gets_none_scaffolding(self) -> None:
        engine = ChallengeEngine()
        profile = _make_profile(domains=(_make_domain(level=5),), primary_gap="Python")
        ch = engine.generate_challenges(profile, count=1)[0]
        assert ch.scaffolding_level == "NONE"


# ---------------------------------------------------------------------------
# ZPD task integration
# ---------------------------------------------------------------------------


class TestZpdIntegration:
    def test_zpd_task_in_description(self) -> None:
        engine = ChallengeEngine()
        zpd = "Een error traceback lezen"
        domain = _make_domain(zpd_tasks=(zpd,))
        profile = _make_profile(domains=(domain,))
        ch = engine.generate_challenges(profile, count=1)[0]
        assert zpd in ch.description

    def test_domain_name_fallback_when_no_zpd(self) -> None:
        engine = ChallengeEngine()
        domain = _make_domain(zpd_tasks=())
        profile = _make_profile(domains=(domain,))
        ch = engine.generate_challenges(profile, count=1)[0]
        assert domain.name in ch.description
