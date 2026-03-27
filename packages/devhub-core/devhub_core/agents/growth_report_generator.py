"""
Growth Report Generator — Combineert sprint-data, challenges en leeslijst
tot een periodiek GrowthReport.

Deterministisch: verwerkt beschikbare data zonder LLM-aanroepen.
Produceert een volledig ingevuld GrowthReport frozen dataclass.

Sprint 3 van de Mentor Supervisor track (SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM).
"""

from __future__ import annotations

import logging
from datetime import date

from devhub_core.agents.research_advisor import ResearchAdvisor
from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    GrowthReport,
    LearningRecommendation,
    SkillRadarProfile,
)

logger = logging.getLogger(__name__)


class GrowthReportGenerator:
    """Genereert een GrowthReport vanuit sprint-data, challenges en skill radar.

    Combineert drie datastromen:
    1. SkillRadarProfile — huidig skill-niveau
    2. DevelopmentChallenge lijst — voltooide en openstaande challenges
    3. ResearchAdvisor.curate() — geprioriteerde leeslijst

    Produceert strategische inzichten op basis van eenvoudige regels.
    """

    def __init__(self, research_advisor: ResearchAdvisor | None = None) -> None:
        self._advisor = research_advisor or ResearchAdvisor()

    def generate(
        self,
        period: str,
        profile: SkillRadarProfile,
        challenges: list[DevelopmentChallenge] | None = None,
        extra_recommendations: list[LearningRecommendation] | None = None,
        report_id: str | None = None,
    ) -> GrowthReport:
        """Genereer een GrowthReport voor een periode.

        Args:
            period: Periode-aanduiding, bijv. "sprint-22" of "week-2026-13".
            profile: Huidig SkillRadarProfile van de developer.
            challenges: Lijst van challenges (kan leeg of None zijn).
            extra_recommendations: Extra leesaanbevelingen (worden samengevoegd).
            report_id: Optioneel rapport-ID; standaard "GROWTH-{datum}".

        Returns:
            Ingevuld GrowthReport frozen dataclass.
        """
        _challenges = challenges or []
        _report_id = report_id or f"GROWTH-{date.today().isoformat()}"

        # Challenge statistieken
        completed = sum(1 for c in _challenges if c.status == "COMPLETED")
        proposed = sum(1 for c in _challenges if c.status in ("PROPOSED", "ACCEPTED"))
        skipped = sum(1 for c in _challenges if c.status == "SKIPPED")
        dp_minutes = sum(c.estimated_minutes for c in _challenges if c.status == "COMPLETED")

        # Scaffolding reductions: domeinen waar alle challenges NONE scaffolding hebben
        scaffolding_reductions = self._detect_scaffolding_reductions(profile, _challenges)

        # ZPD shift: heeft het primary_gap domein challenges voltooid?
        zpd_shift = self._detect_zpd_shift(profile, _challenges)

        # Growth velocity (gemiddeld over alle domeinen)
        growth_velocity = self._compute_growth_velocity(profile)

        # Leeslijst via ResearchAdvisor
        advisor_recs = self._advisor.curate(profile, max_per_domain=2, max_total=5)
        all_recs = list(advisor_recs) + (extra_recommendations or [])
        # Deduplicate op titel
        seen_titles: set[str] = set()
        unique_recs: list[LearningRecommendation] = []
        for rec in all_recs:
            if rec.title not in seen_titles:
                seen_titles.add(rec.title)
                unique_recs.append(rec)

        # Strategische inzichten (op basis van eenvoudige regels)
        insights = self._generate_insights(profile, _challenges, completed)

        report = GrowthReport(
            report_id=_report_id,
            period=period,
            skill_radar=profile,
            challenges_completed=completed,
            challenges_proposed=proposed,
            challenges_skipped=skipped,
            growth_velocity_overall=growth_velocity,
            zpd_shift=zpd_shift,
            learning_recommendations=tuple(unique_recs),
            strategic_insights=tuple(insights),
            deliberate_practice_minutes=dp_minutes,
            scaffolding_reductions=tuple(scaffolding_reductions),
        )

        logger.info(
            "GrowthReportGenerator: %s — %d challenges, %d aanbevelingen, %d inzichten",
            period,
            len(_challenges),
            len(unique_recs),
            len(insights),
        )
        return report

    def format_text(self, report: GrowthReport) -> str:
        """Formateer een GrowthReport als leesbare tekst (terminal-output).

        Gebaseerd op het format uit de sprint-intake.
        """
        lines: list[str] = [
            "═══════════════════════════════════════════════════",
            f"DEVELOPER GROWTH REPORT — {report.period}",
            "═══════════════════════════════════════════════════",
            "",
        ]

        # Skill Radar
        if report.skill_radar and report.skill_radar.domains:
            lines.append("SKILL RADAR")
            for domain in report.skill_radar.domains:
                bar = "█" * domain.level + "░" * (5 - domain.level)
                velocity_str = ""
                if domain.growth_velocity > 0:
                    velocity_str = f"  → +{domain.growth_velocity:.1f} deze sprint"
                elif domain.growth_velocity < 0:
                    velocity_str = f"  → {domain.growth_velocity:.1f} this sprint"
                lines.append(f"  {domain.name:<20} {bar}  {domain.level}/5{velocity_str}")
            lines.append("")

        # T-Shape
        if report.skill_radar:
            lines.append("T-SHAPE")
            deep = ", ".join(report.skill_radar.t_shape_deep) or "—"
            broad = ", ".join(report.skill_radar.t_shape_broad) or "—"
            lines.append(f"  Deep (≥4): {deep}")
            lines.append(f"  Broad (≥2): {broad}")
            if report.skill_radar.primary_gap:
                lines.append(f"  Gap: {report.skill_radar.primary_gap} → ZPD focus")
            lines.append("")

        # Deliberate Practice
        if report.deliberate_practice_minutes > 0 or report.challenges_completed > 0:
            lines.append(f"DELIBERATE PRACTICE — {report.period}")
            lines.append(f"  Voltooid: {report.challenges_completed}")
            lines.append(f"  Openstaand: {report.challenges_proposed}")
            lines.append(f"  Overgeslagen: {report.challenges_skipped}")
            lines.append(f"  Totale DP-tijd: {report.deliberate_practice_minutes} min")
            lines.append("")

        # Scaffolding reductions
        if report.scaffolding_reductions:
            lines.append("SCAFFOLDING-AFBOUW")
            for domain in report.scaffolding_reductions:
                lines.append(f"  {domain}: scaffolding gereduceerd")
            lines.append("")

        # ZPD shift
        if report.zpd_shift:
            lines.append(f"ZPD VERSCHUIVING: {report.zpd_shift}")
            lines.append("")

        # Leeslijst
        if report.learning_recommendations:
            lines.append("LEESLIJST (geprioriteerd op ZPD)")
            priority_icons = {"URGENT": "🔴", "IMPORTANT": "🟡", "NICE_TO_HAVE": "🟢"}
            for rec in report.learning_recommendations:
                icon = priority_icons.get(rec.priority, "•")
                lines.append(
                    f"  {icon} {rec.title} ({rec.estimated_minutes} min,"
                    f" {rec.evidence_grade}, {rec.zpd_alignment})"
                )
            lines.append("")

        # Strategische inzichten
        if report.strategic_insights:
            lines.append("STRATEGISCH INZICHT")
            for insight in report.strategic_insights:
                lines.append(f'  "{insight}"')
            lines.append("")

        return "\n".join(lines)

    # --- Private helpers ---

    def _detect_scaffolding_reductions(
        self,
        profile: SkillRadarProfile,
        challenges: list[DevelopmentChallenge],
    ) -> list[str]:
        """Detecteer domeinen waar scaffolding-niveau is gereduceerd.

        Logica: als een domein level >= 3 heeft EN voltooide challenges op NONE
        scaffolding, beschouw het als gereduceerd t.o.v. beginstaat.
        """
        reductions: list[str] = []
        domain_levels = {d.name: d.level for d in profile.domains}
        domains_with_none = {
            c.domain
            for c in challenges
            if c.status == "COMPLETED" and c.scaffolding_level == "NONE"
        }
        for domain, level in domain_levels.items():
            if domain in domains_with_none and level >= 4:
                reductions.append(domain)
        return reductions

    def _detect_zpd_shift(
        self,
        profile: SkillRadarProfile,
        challenges: list[DevelopmentChallenge],
    ) -> str | None:
        """Detecteer of het primary_gap domein challenges heeft voltooid.

        Als ja: rapporteer dat het ZPD voor dit domein actief wordt bewerkt.
        """
        if not profile.primary_gap:
            return None

        gap_challenges_done = [
            c for c in challenges if c.domain == profile.primary_gap and c.status == "COMPLETED"
        ]
        if gap_challenges_done:
            return (
                f"{profile.primary_gap}: {len(gap_challenges_done)} challenge(s) "
                "voltooid — gap wordt actief verkleind"
            )
        return None

    def _compute_growth_velocity(self, profile: SkillRadarProfile) -> float:
        """Bereken gemiddelde growth_velocity over alle domeinen."""
        if not profile.domains:
            return 0.0
        total = sum(d.growth_velocity for d in profile.domains)
        return round(total / len(profile.domains), 2)

    def _generate_insights(
        self,
        profile: SkillRadarProfile,
        challenges: list[DevelopmentChallenge],
        completed_count: int,
    ) -> list[str]:
        """Genereer 1-3 strategische inzichten op basis van eenvoudige regels."""
        insights: list[str] = []

        # Insight 1: primary_gap
        if profile.primary_gap:
            gap_domain = next((d for d in profile.domains if d.name == profile.primary_gap), None)
            if gap_domain and gap_domain.level <= 2:
                insights.append(
                    f"De gap in '{profile.primary_gap}' (Dreyfus level {gap_domain.level}) "
                    "is het grootste groeipotentieel. Focus hier op stretch-challenges."
                )

        # Insight 2: T-shape breedte
        if profile.t_shape_deep and len(profile.t_shape_deep) >= 3:
            insights.append(
                f"Je T-shape verdiept zich goed ({len(profile.t_shape_deep)} domeinen op ≥4). "
                "Overweeg een 'cross-domain' challenge om patronen tussen domeinen te zien."
            )

        # Insight 3: challenge momentum
        if completed_count == 0 and challenges:
            insights.append(
                "Nog geen challenges voltooid deze periode. "
                "Begin met de kortste 'explain_it' challenge — 20-30 minuten is genoeg."
            )
        elif completed_count >= 3:
            insights.append(
                f"{completed_count} challenges voltooid — goed momentum. "
                "Verhoog de moeilijkheidsgraad: kies een 'adversarial' of 'cross_domain' challenge."
            )

        return insights[:3]  # Max 3 inzichten
