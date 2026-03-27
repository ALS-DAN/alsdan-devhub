"""Tests voor GrowthReportGenerator — Mentor S3."""

from __future__ import annotations

import pytest

from devhub_core.agents.growth_report_generator import GrowthReportGenerator
from devhub_core.agents.research_advisor import ResearchAdvisor, _ResourceEntry
from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    GrowthReport,
    SkillDomain,
    SkillRadarProfile,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_domain(name: str = "Security", level: int = 2) -> SkillDomain:
    return SkillDomain(name=name, level=level)


def _make_profile(primary_gap: str = "Security") -> SkillRadarProfile:
    return SkillRadarProfile(
        developer="Niels",
        date="2026-03-27",
        domains=(
            _make_domain("Security", 2),
            _make_domain("Python", 3),
            _make_domain("AI-Engineering", 3),
        ),
        primary_gap=primary_gap,
        zpd_focus=primary_gap,
        t_shape_deep=("AI-Engineering",),
        t_shape_broad=("Security", "Python", "AI-Engineering"),
    )


def _make_challenge(
    domain: str = "Security",
    status: str = "COMPLETED",
    scaffolding_level: str = "MEDIUM",
    challenge_type: str = "stretch",
    estimated_minutes: int = 30,
) -> DevelopmentChallenge:
    return DevelopmentChallenge(
        challenge_id=f"CH-{domain}-{status}",
        challenge_type=challenge_type,  # type: ignore[arg-type]
        domain=domain,
        description=f"Test challenge voor {domain}",
        scaffolding_level=scaffolding_level,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        estimated_minutes=estimated_minutes,
    )


def _minimal_catalogue() -> list[_ResourceEntry]:
    return [
        _ResourceEntry(
            domain="Security",
            title="Security basics",
            resource_type="docs",
            url=None,
            estimated_minutes=20,
            difficulty=2,
            evidence_grade="GOLD",
            rationale="Test",
        ),
    ]


# ---------------------------------------------------------------------------
# Tests: generate() basisgedrag
# ---------------------------------------------------------------------------


class TestGenerate:
    def test_genereert_report_met_juiste_period(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile()
        report = gen.generate("sprint-22", profile)
        assert report.period == "sprint-22"

    def test_genereert_report_is_frozen(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile()
        report = gen.generate("sprint-22", profile)
        assert isinstance(report, GrowthReport)
        with pytest.raises((AttributeError, TypeError)):
            report.period = "ander"  # type: ignore[misc]

    def test_report_id_standaard_bevat_datum(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        assert report.report_id.startswith("GROWTH-")

    def test_rapport_id_overschrijfbaar(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile(), report_id="TEST-001")
        assert report.report_id == "TEST-001"

    def test_zonder_challenges_is_alles_nul(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        assert report.challenges_completed == 0
        assert report.challenges_proposed == 0
        assert report.challenges_skipped == 0
        assert report.deliberate_practice_minutes == 0

    def test_leeslijst_niet_leeg_bij_geldig_profiel(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        # Met builtin catalogue en een profiel: moet aanbevelingen hebben
        assert len(report.learning_recommendations) >= 1

    def test_skill_radar_gekoppeld_aan_report(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile()
        report = gen.generate("sprint-22", profile)
        assert report.skill_radar == profile


# ---------------------------------------------------------------------------
# Tests: challenge-statistieken
# ---------------------------------------------------------------------------


class TestChallengeStats:
    def test_completed_challenges_geteld(self) -> None:
        gen = GrowthReportGenerator()
        challenges = [
            _make_challenge(status="COMPLETED"),
            _make_challenge(status="COMPLETED"),
            _make_challenge(status="PROPOSED"),
        ]
        report = gen.generate("sprint-22", _make_profile(), challenges=challenges)
        assert report.challenges_completed == 2
        assert report.challenges_proposed == 1

    def test_skipped_challenges_geteld(self) -> None:
        gen = GrowthReportGenerator()
        challenges = [
            _make_challenge(status="COMPLETED"),
            _make_challenge(status="SKIPPED"),
        ]
        report = gen.generate("sprint-22", _make_profile(), challenges=challenges)
        assert report.challenges_skipped == 1

    def test_dp_minuten_alleen_voor_completed(self) -> None:
        gen = GrowthReportGenerator()
        challenges = [
            _make_challenge(status="COMPLETED", estimated_minutes=30),
            _make_challenge(status="COMPLETED", estimated_minutes=20),
            _make_challenge(status="PROPOSED", estimated_minutes=60),
        ]
        report = gen.generate("sprint-22", _make_profile(), challenges=challenges)
        assert report.deliberate_practice_minutes == 50  # 30 + 20


# ---------------------------------------------------------------------------
# Tests: ZPD-shift detectie
# ---------------------------------------------------------------------------


class TestZpdShift:
    def test_zpd_shift_als_gap_challenge_voltooid(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile(primary_gap="Security")
        challenges = [_make_challenge(domain="Security", status="COMPLETED")]
        report = gen.generate("sprint-22", profile, challenges=challenges)
        assert report.zpd_shift is not None
        assert "Security" in report.zpd_shift

    def test_geen_zpd_shift_zonder_gap_challenges(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile(primary_gap="Security")
        challenges = [_make_challenge(domain="Python", status="COMPLETED")]
        report = gen.generate("sprint-22", profile, challenges=challenges)
        assert report.zpd_shift is None

    def test_geen_zpd_shift_zonder_primary_gap(self) -> None:
        gen = GrowthReportGenerator()
        profile = SkillRadarProfile(
            developer="Niels",
            date="2026-03-27",
            domains=(_make_domain("Security", 2),),
            primary_gap="",
            zpd_focus="",
        )
        report = gen.generate("sprint-22", profile)
        assert report.zpd_shift is None


# ---------------------------------------------------------------------------
# Tests: scaffolding reductions
# ---------------------------------------------------------------------------


class TestScaffoldingReductions:
    def test_scaffolding_reductie_bij_none_en_hoog_level(self) -> None:
        gen = GrowthReportGenerator()
        profile = SkillRadarProfile(
            developer="Niels",
            date="2026-03-27",
            domains=(_make_domain("AI-Engineering", 4),),
            primary_gap="",
            zpd_focus="",
        )
        challenges = [
            _make_challenge(domain="AI-Engineering", status="COMPLETED", scaffolding_level="NONE")
        ]
        report = gen.generate("sprint-22", profile, challenges=challenges)
        assert "AI-Engineering" in report.scaffolding_reductions

    def test_geen_reductie_bij_laag_level(self) -> None:
        gen = GrowthReportGenerator()
        profile = SkillRadarProfile(
            developer="Niels",
            date="2026-03-27",
            domains=(_make_domain("Security", 2),),
            primary_gap="",
            zpd_focus="",
        )
        challenges = [
            _make_challenge(domain="Security", status="COMPLETED", scaffolding_level="NONE")
        ]
        report = gen.generate("sprint-22", profile, challenges=challenges)
        assert "Security" not in report.scaffolding_reductions


# ---------------------------------------------------------------------------
# Tests: strategische inzichten
# ---------------------------------------------------------------------------


class TestStrategicInsights:
    def test_max_drie_inzichten(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile()
        report = gen.generate("sprint-22", profile)
        assert len(report.strategic_insights) <= 3

    def test_gap_inzicht_aanwezig_bij_laag_niveau(self) -> None:
        gen = GrowthReportGenerator()
        profile = SkillRadarProfile(
            developer="Niels",
            date="2026-03-27",
            domains=(_make_domain("Security", 1),),  # level 1 = Dreyfus novice
            primary_gap="Security",
            zpd_focus="Security",
        )
        report = gen.generate("sprint-22", profile)
        gap_insights = [i for i in report.strategic_insights if "Security" in i]
        assert len(gap_insights) >= 1

    def test_momentum_inzicht_bij_geen_challenges(self) -> None:
        gen = GrowthReportGenerator()
        profile = _make_profile()
        challenges = [_make_challenge(status="PROPOSED")]  # niet completed
        report = gen.generate("sprint-22", profile, challenges=challenges)
        momentum_insights = [i for i in report.strategic_insights if "challenge" in i.lower()]
        assert len(momentum_insights) >= 1


# ---------------------------------------------------------------------------
# Tests: format_text()
# ---------------------------------------------------------------------------


class TestFormatText:
    def test_format_bevat_periode(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        text = gen.format_text(report)
        assert "sprint-22" in text

    def test_format_bevat_skill_radar_sectie(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        text = gen.format_text(report)
        assert "SKILL RADAR" in text

    def test_format_bevat_leeslijst_sectie(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        text = gen.format_text(report)
        assert "LEESLIJST" in text

    def test_format_bevat_developer_name_header(self) -> None:
        gen = GrowthReportGenerator()
        report = gen.generate("sprint-22", _make_profile())
        text = gen.format_text(report)
        assert "DEVELOPER GROWTH REPORT" in text


# ---------------------------------------------------------------------------
# Tests: extra_recommendations samenvoegen
# ---------------------------------------------------------------------------


class TestExtraRecommendations:
    def test_extra_recommendations_toegevoegd(self) -> None:
        from devhub_core.contracts.growth_contracts import LearningRecommendation

        gen = GrowthReportGenerator(research_advisor=ResearchAdvisor(catalogue=[]))
        extra = [
            LearningRecommendation(
                domain="Security",
                title="Extra bron",
                resource_type="docs",
                rationale="Handmatig toegevoegd",
                estimated_minutes=15,
            )
        ]
        report = gen.generate("sprint-22", _make_profile(), extra_recommendations=extra)
        titles = [r.title for r in report.learning_recommendations]
        assert "Extra bron" in titles

    def test_duplicaten_worden_gededupliceerd(self) -> None:
        from devhub_core.contracts.growth_contracts import LearningRecommendation

        catalogue = _minimal_catalogue()
        gen = GrowthReportGenerator(research_advisor=ResearchAdvisor(catalogue=catalogue))
        extra = [
            LearningRecommendation(
                domain="Security",
                title="Security basics",  # Zelfde titel als in catalogue
                resource_type="docs",
                rationale="Duplicaat",
                estimated_minutes=20,
            )
        ]
        profile = SkillRadarProfile(
            developer="Niels",
            date="2026-03-27",
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        report = gen.generate("sprint-22", profile, extra_recommendations=extra)
        titles = [r.title for r in report.learning_recommendations]
        assert titles.count("Security basics") == 1
