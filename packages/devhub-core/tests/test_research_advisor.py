"""Tests voor ResearchAdvisor — Mentor S3."""

from __future__ import annotations

from devhub_core.agents.research_advisor import ResearchAdvisor, _ResourceEntry
from devhub_core.contracts.growth_contracts import (
    LearningRecommendation,
    SkillDomain,
    SkillRadarProfile,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _make_domain(name: str = "Security", level: int = 2) -> SkillDomain:
    return SkillDomain(name=name, level=level)


def _make_profile(
    domains: tuple[SkillDomain, ...] | None = None,
    primary_gap: str = "Security",
    zpd_focus: str = "Security",
) -> SkillRadarProfile:
    _domains = domains or (
        _make_domain("Security", 2),
        _make_domain("Python", 3),
        _make_domain("AI-Engineering", 3),
    )
    return SkillRadarProfile(
        developer="Niels",
        date="2026-03-27",
        domains=_domains,
        primary_gap=primary_gap,
        zpd_focus=zpd_focus,
    )


def _make_catalogue() -> list[_ResourceEntry]:
    return [
        _ResourceEntry(
            domain="Security",
            title="OWASP basics (level 1)",
            resource_type="docs",
            url=None,
            estimated_minutes=20,
            difficulty=1,
            evidence_grade="GOLD",
            rationale="Intro-niveau security",
        ),
        _ResourceEntry(
            domain="Security",
            title="Security intermediate (level 2)",
            resource_type="tutorial",
            url=None,
            estimated_minutes=30,
            difficulty=2,
            evidence_grade="GOLD",
            rationale="Basis security patronen",
        ),
        _ResourceEntry(
            domain="Security",
            title="Security stretch (level 3)",
            resource_type="paper",
            url=None,
            estimated_minutes=45,
            difficulty=3,
            evidence_grade="SILVER",
            rationale="Verdieping security",
        ),
        _ResourceEntry(
            domain="Security",
            title="Security te moeilijk (level 4)",
            resource_type="paper",
            url=None,
            estimated_minutes=60,
            difficulty=4,
            evidence_grade="SILVER",
            rationale="Te ver boven ZPD",
        ),
        _ResourceEntry(
            domain="Python",
            title="Python intermediate (level 3)",
            resource_type="tutorial",
            url=None,
            estimated_minutes=30,
            difficulty=3,
            evidence_grade="GOLD",
            rationale="Python op huidig niveau",
        ),
    ]


# ---------------------------------------------------------------------------
# Tests: ZPD-alignment
# ---------------------------------------------------------------------------


class TestZpdAlignment:
    def test_stretch_als_resource_een_niveau_hoger(self) -> None:
        advisor = ResearchAdvisor()
        assert advisor._zpd_alignment(3, 2) == "stretch"

    def test_exact_als_zelfde_niveau(self) -> None:
        advisor = ResearchAdvisor()
        assert advisor._zpd_alignment(2, 2) == "exact"

    def test_review_als_resource_lager(self) -> None:
        advisor = ResearchAdvisor()
        assert advisor._zpd_alignment(1, 2) == "review"

    def test_review_als_resource_twee_lager(self) -> None:
        advisor = ResearchAdvisor()
        assert advisor._zpd_alignment(1, 3) == "review"

    def test_review_fallback_als_te_moeilijk(self) -> None:
        # Delta +2 (te moeilijk) → valt terug op "review" (niet in ZPD map)
        advisor = ResearchAdvisor()
        assert advisor._zpd_alignment(4, 2) == "review"


# ---------------------------------------------------------------------------
# Tests: ZPD filtering (te moeilijke resources worden uitgesloten)
# ---------------------------------------------------------------------------


class TestZpdFiltering:
    def test_te_moeilijke_resource_niet_aanbevolen(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile, max_per_domain=5, max_total=10)
        titles = [r.title for r in recs]
        assert "Security te moeilijk (level 4)" not in titles

    def test_stretch_resource_wel_aanbevolen(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile, max_per_domain=5, max_total=10)
        titles = [r.title for r in recs]
        assert "Security stretch (level 3)" in titles


# ---------------------------------------------------------------------------
# Tests: Prioritering (stretch > exact > review)
# ---------------------------------------------------------------------------


class TestPrioritization:
    def test_stretch_heeft_urgent_prioriteit(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile, max_per_domain=5, max_total=10)
        stretch_recs = [r for r in recs if r.zpd_alignment == "stretch"]
        assert all(r.priority == "URGENT" for r in stretch_recs)

    def test_exact_heeft_important_prioriteit(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile, max_per_domain=5, max_total=10)
        exact_recs = [r for r in recs if r.zpd_alignment == "exact"]
        assert all(r.priority == "IMPORTANT" for r in exact_recs)

    def test_primary_gap_domein_eerst(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(
                _make_domain("Python", 3),
                _make_domain("Security", 2),
            ),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile, max_per_domain=2, max_total=4)
        assert len(recs) > 0
        assert recs[0].domain == "Security"


# ---------------------------------------------------------------------------
# Tests: max_per_domain en max_total limieten
# ---------------------------------------------------------------------------


class TestLimits:
    def test_max_per_domain_gelimiteerd(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile, max_per_domain=1, max_total=10)
        security_recs = [r for r in recs if r.domain == "Security"]
        assert len(security_recs) <= 1

    def test_max_total_gelimiteerd(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile()
        recs = advisor.curate(profile, max_per_domain=5, max_total=2)
        assert len(recs) <= 2

    def test_leeg_resultaat_bij_geen_passende_resources(self) -> None:
        catalogue = [
            _ResourceEntry(
                domain="DevOps/Tooling",
                title="Iets",
                resource_type="docs",
                url=None,
                estimated_minutes=20,
                difficulty=3,
                evidence_grade="GOLD",
                rationale="Ander domein",
            )
        ]
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(_make_domain("Security", 2),),
            primary_gap="Security",
            zpd_focus="Security",
        )
        recs = advisor.curate(profile)
        assert len(recs) == 0


# ---------------------------------------------------------------------------
# Tests: curate_for_domain
# ---------------------------------------------------------------------------


class TestCurateForDomain:
    def test_curate_for_domain_retourneert_alleen_dat_domein(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(
                _make_domain("Security", 2),
                _make_domain("Python", 3),
            )
        )
        recs = advisor.curate_for_domain(profile, "Security")
        assert all(r.domain == "Security" for r in recs)

    def test_curate_for_domain_respecteert_max_results(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(
                _make_domain("Security", 2),
                _make_domain("Python", 3),
            )
        )
        recs = advisor.curate_for_domain(profile, "Security", max_results=1)
        assert len(recs) <= 1


# ---------------------------------------------------------------------------
# Tests: concept_intro
# ---------------------------------------------------------------------------


class TestConceptIntro:
    def test_geen_intro_als_niveau_ge3(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(
                _make_domain("Python", 3),
                _make_domain("Security", 2),
            ),
        )
        result = advisor.concept_intro(profile, "Python", "typing")
        assert result is None

    def test_intro_aanbeveling_als_niveau_lt3(self) -> None:
        catalogue = _make_catalogue()
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(
                _make_domain("Security", 2),
                _make_domain("Python", 3),
            ),
        )
        result = advisor.concept_intro(profile, "Security", "OWASP")
        assert result is not None
        assert result.domain == "Security"
        # Intro moet "exact" of "review" zijn, niet "stretch"
        assert result.zpd_alignment in ("exact", "review")

    def test_intro_prefereert_gold_bron(self) -> None:
        catalogue = [
            _ResourceEntry(
                domain="Security",
                title="GOLD bron",
                resource_type="docs",
                url=None,
                estimated_minutes=20,
                difficulty=2,
                evidence_grade="GOLD",
                rationale="Test",
            ),
            _ResourceEntry(
                domain="Security",
                title="SILVER bron",
                resource_type="tutorial",
                url=None,
                estimated_minutes=30,
                difficulty=2,
                evidence_grade="SILVER",
                rationale="Test",
            ),
        ]
        advisor = ResearchAdvisor(catalogue=catalogue)
        profile = _make_profile(
            domains=(
                _make_domain("Security", 2),
                _make_domain("Python", 3),
            ),
        )
        result = advisor.concept_intro(profile, "Security", "concept")
        assert result is not None
        assert result.evidence_grade == "GOLD"


# ---------------------------------------------------------------------------
# Tests: builtin catalogue aanwezig
# ---------------------------------------------------------------------------


class TestBuiltinCatalogue:
    def test_builtin_catalogue_bevat_meerdere_domeinen(self) -> None:
        advisor = ResearchAdvisor()
        domains = {e.domain for e in advisor._catalogue}
        assert len(domains) >= 5

    def test_builtin_catalogue_geen_url_required(self) -> None:
        advisor = ResearchAdvisor()
        # Alle entries hebben een rationale
        assert all(e.rationale for e in advisor._catalogue)

    def test_curate_met_realistisch_profiel(self) -> None:
        advisor = ResearchAdvisor()
        profile = SkillRadarProfile(
            developer="Niels",
            date="2026-03-27",
            domains=(
                _make_domain("AI-Engineering", 3),
                _make_domain("Python", 3),
                _make_domain("Governance", 4),
                _make_domain("Testing", 2),
                _make_domain("Security", 2),
            ),
            primary_gap="Security",
            zpd_focus="Testing",
            t_shape_deep=("Governance",),
            t_shape_broad=("AI-Engineering", "Python", "Governance", "Testing", "Security"),
        )
        recs = advisor.curate(profile, max_per_domain=2, max_total=5)
        assert len(recs) <= 5
        assert all(isinstance(r, LearningRecommendation) for r in recs)
