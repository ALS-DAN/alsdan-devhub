"""Tests voor Growth Contracts — Mentor S1 groei-tracking contracten."""

import pytest

from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    GrowthReport,
    LearningRecommendation,
    SkillDomain,
    SkillRadarProfile,
)


# ---------------------------------------------------------------------------
# SkillDomain
# ---------------------------------------------------------------------------


class TestSkillDomain:
    def test_valid_domain(self):
        d = SkillDomain(
            name="python",
            level=3,
            subdomains=("asyncio", "typing"),
            evidence=("Completed async refactor",),
            last_assessed="2026-03-20",
            growth_velocity=0.5,
            zpd_tasks=("Implement custom event loop",),
        )
        assert d.name == "python"
        assert d.level == 3
        assert d.subdomains == ("asyncio", "typing")
        assert d.evidence == ("Completed async refactor",)
        assert d.growth_velocity == 0.5

    def test_minimal_domain(self):
        d = SkillDomain(name="testing", level=1)
        assert d.name == "testing"
        assert d.level == 1
        assert d.subdomains == ()
        assert d.evidence == ()
        assert d.last_assessed == ""
        assert d.growth_velocity == 0.0
        assert d.zpd_tasks == ()

    def test_frozen(self):
        d = SkillDomain(name="python", level=3)
        with pytest.raises(AttributeError):
            d.level = 4  # type: ignore[misc]

    def test_empty_name(self):
        with pytest.raises(ValueError, match="name is required"):
            SkillDomain(name="", level=3)

    def test_level_too_low(self):
        with pytest.raises(ValueError, match="level must be 1-5"):
            SkillDomain(name="python", level=0)

    def test_level_too_high(self):
        with pytest.raises(ValueError, match="level must be 1-5"):
            SkillDomain(name="python", level=6)

    def test_all_dreyfus_levels(self):
        """All Dreyfus levels 1-5 are accepted."""
        for level in (1, 2, 3, 4, 5):
            d = SkillDomain(name="test", level=level)
            assert d.level == level


# ---------------------------------------------------------------------------
# SkillRadarProfile
# ---------------------------------------------------------------------------


class TestSkillRadarProfile:
    def test_valid_profile(self):
        domain = SkillDomain(name="python", level=4)
        p = SkillRadarProfile(
            developer="niels",
            date="2026-03-20",
            domains=(domain,),
            t_shape_deep=("python",),
            t_shape_broad=("devops", "testing"),
            primary_gap="security",
            zpd_focus="async patterns",
        )
        assert p.developer == "niels"
        assert p.date == "2026-03-20"
        assert len(p.domains) == 1
        assert p.t_shape_deep == ("python",)
        assert p.primary_gap == "security"

    def test_minimal_profile(self):
        p = SkillRadarProfile(developer="niels", date="2026-03-20")
        assert p.domains == ()
        assert p.t_shape_deep == ()
        assert p.t_shape_broad == ()
        assert p.primary_gap == ""
        assert p.zpd_focus == ""

    def test_frozen(self):
        p = SkillRadarProfile(developer="niels", date="2026-03-20")
        with pytest.raises(AttributeError):
            p.developer = "other"  # type: ignore[misc]

    def test_empty_developer(self):
        with pytest.raises(ValueError, match="developer is required"):
            SkillRadarProfile(developer="", date="2026-03-20")

    def test_empty_date(self):
        with pytest.raises(ValueError, match="date is required"):
            SkillRadarProfile(developer="niels", date="")


# ---------------------------------------------------------------------------
# LearningRecommendation
# ---------------------------------------------------------------------------


class TestLearningRecommendation:
    def test_valid_recommendation(self):
        r = LearningRecommendation(
            domain="python",
            title="Advanced Asyncio Patterns",
            resource_type="paper",
            url="https://example.com/paper",
            estimated_minutes=45,
            zpd_alignment="stretch",
            evidence_grade="GOLD",
            rationale="Fills async knowledge gap",
            priority="URGENT",
        )
        assert r.domain == "python"
        assert r.title == "Advanced Asyncio Patterns"
        assert r.resource_type == "paper"
        assert r.url == "https://example.com/paper"
        assert r.estimated_minutes == 45
        assert r.zpd_alignment == "stretch"
        assert r.evidence_grade == "GOLD"
        assert r.priority == "URGENT"

    def test_minimal_recommendation(self):
        r = LearningRecommendation(
            domain="testing",
            title="Pytest Best Practices",
            resource_type="docs",
            rationale="Improve test coverage strategy",
        )
        assert r.url is None
        assert r.estimated_minutes == 30
        assert r.zpd_alignment == "exact"
        assert r.evidence_grade == "SILVER"
        assert r.priority == "IMPORTANT"

    def test_frozen(self):
        r = LearningRecommendation(
            domain="python",
            title="Test",
            resource_type="tutorial",
            rationale="Test rationale",
        )
        with pytest.raises(AttributeError):
            r.domain = "other"  # type: ignore[misc]

    def test_empty_domain(self):
        with pytest.raises(ValueError, match="domain is required"):
            LearningRecommendation(
                domain="",
                title="Test",
                resource_type="docs",
                rationale="Test",
            )

    def test_empty_title(self):
        with pytest.raises(ValueError, match="title is required"):
            LearningRecommendation(
                domain="python",
                title="",
                resource_type="docs",
                rationale="Test",
            )

    def test_empty_rationale(self):
        with pytest.raises(ValueError, match="rationale is required"):
            LearningRecommendation(
                domain="python",
                title="Test",
                resource_type="docs",
                rationale="",
            )

    def test_estimated_minutes_zero(self):
        with pytest.raises(ValueError, match="estimated_minutes must be > 0"):
            LearningRecommendation(
                domain="python",
                title="Test",
                resource_type="docs",
                rationale="Test",
                estimated_minutes=0,
            )

    def test_estimated_minutes_negative(self):
        with pytest.raises(ValueError, match="estimated_minutes must be > 0"):
            LearningRecommendation(
                domain="python",
                title="Test",
                resource_type="docs",
                rationale="Test",
                estimated_minutes=-5,
            )

    def test_all_resource_types(self):
        for rt in ("paper", "docs", "tutorial", "video", "book_chapter"):
            r = LearningRecommendation(
                domain="test",
                title="Test",
                resource_type=rt,
                rationale="Test",
            )
            assert r.resource_type == rt


# ---------------------------------------------------------------------------
# DevelopmentChallenge
# ---------------------------------------------------------------------------


class TestDevelopmentChallenge:
    def test_valid_challenge(self):
        c = DevelopmentChallenge(
            challenge_id="ch-001",
            challenge_type="stretch",
            domain="python",
            description="Build async event-driven system",
            zpd_rationale="Just beyond current async skills",
            success_criteria=("All tests pass", "No blocking calls"),
            estimated_minutes=120,
            scaffolding_level="LOW",
            status="ACCEPTED",
            feedback=None,
            created="2026-03-20",
            completed=None,
        )
        assert c.challenge_id == "ch-001"
        assert c.challenge_type == "stretch"
        assert c.domain == "python"
        assert c.estimated_minutes == 120
        assert c.scaffolding_level == "LOW"
        assert c.status == "ACCEPTED"

    def test_minimal_challenge(self):
        c = DevelopmentChallenge(
            challenge_id="ch-002",
            challenge_type="explain_it",
            domain="architecture",
            description="Explain CQRS pattern",
        )
        assert c.zpd_rationale == ""
        assert c.success_criteria == ()
        assert c.estimated_minutes == 60
        assert c.scaffolding_level == "MEDIUM"
        assert c.status == "PROPOSED"
        assert c.feedback is None
        assert c.created == ""
        assert c.completed is None

    def test_frozen(self):
        c = DevelopmentChallenge(
            challenge_id="ch-001",
            challenge_type="stretch",
            domain="python",
            description="Test",
        )
        with pytest.raises(AttributeError):
            c.status = "COMPLETED"  # type: ignore[misc]

    def test_empty_challenge_id(self):
        with pytest.raises(ValueError, match="challenge_id is required"):
            DevelopmentChallenge(
                challenge_id="",
                challenge_type="stretch",
                domain="python",
                description="Test",
            )

    def test_empty_description(self):
        with pytest.raises(ValueError, match="description is required"):
            DevelopmentChallenge(
                challenge_id="ch-001",
                challenge_type="stretch",
                domain="python",
                description="",
            )

    def test_empty_domain(self):
        with pytest.raises(ValueError, match="domain is required"):
            DevelopmentChallenge(
                challenge_id="ch-001",
                challenge_type="stretch",
                domain="",
                description="Test",
            )

    def test_estimated_minutes_zero(self):
        with pytest.raises(ValueError, match="estimated_minutes must be > 0"):
            DevelopmentChallenge(
                challenge_id="ch-001",
                challenge_type="stretch",
                domain="python",
                description="Test",
                estimated_minutes=0,
            )

    def test_all_challenge_types(self):
        for ct in (
            "stretch",
            "explain_it",
            "reverse_engineer",
            "teach_back",
            "cross_domain",
            "adversarial",
        ):
            c = DevelopmentChallenge(
                challenge_id="ch-test",
                challenge_type=ct,
                domain="test",
                description="Test challenge",
            )
            assert c.challenge_type == ct

    def test_all_scaffolding_levels(self):
        for sl in ("HIGH", "MEDIUM", "LOW", "NONE"):
            c = DevelopmentChallenge(
                challenge_id="ch-test",
                challenge_type="stretch",
                domain="test",
                description="Test",
                scaffolding_level=sl,
            )
            assert c.scaffolding_level == sl

    def test_all_statuses(self):
        for status in ("PROPOSED", "ACCEPTED", "COMPLETED", "SKIPPED"):
            c = DevelopmentChallenge(
                challenge_id="ch-test",
                challenge_type="stretch",
                domain="test",
                description="Test",
                status=status,
            )
            assert c.status == status


# ---------------------------------------------------------------------------
# GrowthReport
# ---------------------------------------------------------------------------


class TestGrowthReport:
    def test_valid_report(self):
        radar = SkillRadarProfile(developer="niels", date="2026-03-20")
        rec = LearningRecommendation(
            domain="python",
            title="Test",
            resource_type="docs",
            rationale="Test",
        )
        r = GrowthReport(
            report_id="gr-001",
            period="sprint-11",
            skill_radar=radar,
            challenges_completed=3,
            challenges_proposed=5,
            challenges_skipped=1,
            growth_velocity_overall=0.15,
            zpd_shift="async -> distributed systems",
            learning_recommendations=(rec,),
            strategic_insights=("Focus on async patterns",),
            deliberate_practice_minutes=240,
            scaffolding_reductions=("testing",),
        )
        assert r.report_id == "gr-001"
        assert r.period == "sprint-11"
        assert r.skill_radar is not None
        assert r.challenges_completed == 3
        assert r.growth_velocity_overall == 0.15
        assert r.zpd_shift == "async -> distributed systems"
        assert len(r.learning_recommendations) == 1
        assert r.deliberate_practice_minutes == 240

    def test_minimal_report(self):
        r = GrowthReport(report_id="gr-002", period="week-2026-W13")
        assert r.skill_radar is None
        assert r.challenges_completed == 0
        assert r.challenges_proposed == 0
        assert r.challenges_skipped == 0
        assert r.growth_velocity_overall == 0.0
        assert r.zpd_shift is None
        assert r.learning_recommendations == ()
        assert r.strategic_insights == ()
        assert r.deliberate_practice_minutes == 0
        assert r.scaffolding_reductions == ()

    def test_frozen(self):
        r = GrowthReport(report_id="gr-001", period="sprint-11")
        with pytest.raises(AttributeError):
            r.report_id = "changed"  # type: ignore[misc]

    def test_empty_report_id(self):
        with pytest.raises(ValueError, match="report_id is required"):
            GrowthReport(report_id="", period="sprint-11")

    def test_empty_period(self):
        with pytest.raises(ValueError, match="period is required"):
            GrowthReport(report_id="gr-001", period="")
