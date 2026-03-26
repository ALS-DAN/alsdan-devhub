"""
Challenge Engine — Genereert DevelopmentChallenge op basis van SkillRadarProfile.

Deterministische selectie: kiest challenge-type op basis van Dreyfus-level,
prioriteert primary_gap domein en laagste growth_velocity.
Laadt templates uit YAML met hardcoded fallback.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from devhub_core.contracts.growth_contracts import (
    ChallengeType,
    DevelopmentChallenge,
    DreyfusLevel,
    ScaffoldingLevel,
    SkillDomain,
    SkillRadarProfile,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dreyfus → Challenge type mapping
# ---------------------------------------------------------------------------

_DREYFUS_CHALLENGE_MAP: dict[DreyfusLevel, tuple[ChallengeType, ...]] = {
    1: ("explain_it", "teach_back"),
    2: ("stretch", "reverse_engineer"),
    3: ("cross_domain", "adversarial"),
    4: ("cross_domain", "adversarial"),
    5: ("cross_domain", "adversarial"),
}

# Dreyfus → Scaffolding level mapping
_DREYFUS_SCAFFOLDING_MAP: dict[DreyfusLevel, ScaffoldingLevel] = {
    1: "HIGH",
    2: "MEDIUM",
    3: "LOW",
    4: "NONE",
    5: "NONE",
}

# Hardcoded fallback templates
_FALLBACK_TEMPLATES: list[dict[str, Any]] = [
    {
        "challenge_type": "explain_it",
        "description_template": "Leg uit in eigen woorden: {zpd_task}",
        "success_criteria": [
            "Uitleg is correct",
            "Geen onnodig jargon",
        ],
        "estimated_minutes": 30,
    },
    {
        "challenge_type": "teach_back",
        "description_template": "Leg aan een collega uit hoe {zpd_task} werkt",
        "success_criteria": [
            "Collega begrijpt het na uitleg",
            "Kernconcepten correct benoemd",
        ],
        "estimated_minutes": 30,
    },
    {
        "challenge_type": "stretch",
        "description_template": "Pas toe in een nieuw scenario: {zpd_task}",
        "success_criteria": [
            "Scenario correct opgezet",
            "Resultaat werkt en is geverifieerd",
        ],
        "estimated_minutes": 60,
    },
    {
        "challenge_type": "reverse_engineer",
        "description_template": "Analyseer bestaande code en beschrijf: {zpd_task}",
        "success_criteria": [
            "Stappen correct geïdentificeerd",
            "Ontwerpkeuzes benoemd",
        ],
        "estimated_minutes": 45,
    },
    {
        "challenge_type": "cross_domain",
        "description_template": "Verbind kennis uit een ander domein met: {zpd_task}",
        "success_criteria": [
            "Verbinding is relevant en correct",
            "Inzicht toegevoegd aan het domein",
        ],
        "estimated_minutes": 60,
    },
    {
        "challenge_type": "adversarial",
        "description_template": "Zoek zwakke plekken en edge cases in: {zpd_task}",
        "success_criteria": [
            "Minimaal 2 zwakke plekken gevonden",
            "Verbetervoorstel geformuleerd",
        ],
        "estimated_minutes": 60,
    },
]


class ChallengeEngine:
    """Genereert DevelopmentChallenge objecten op basis van een SkillRadarProfile.

    Deterministisch: dezelfde input produceert dezelfde output.
    """

    def __init__(self, templates_path: Path | None = None) -> None:
        self._templates = self._load_templates(templates_path)

    def generate_challenges(
        self,
        profile: SkillRadarProfile,
        count: int = 2,
    ) -> list[DevelopmentChallenge]:
        """Genereer challenges op basis van skill radar profiel.

        Prioriteert primary_gap domein, daarna laagste growth_velocity.
        """
        if not profile.domains:
            return []

        if count < 1:
            raise ValueError(f"count must be >= 1, got {count}")

        # Sort domains: primary_gap first, then by growth_velocity ascending
        sorted_domains = self._prioritize_domains(profile)
        today = date.today().isoformat()

        challenges: list[DevelopmentChallenge] = []
        for i, domain in enumerate(sorted_domains):
            if len(challenges) >= count:
                break

            challenge_type = self.select_challenge_type(domain)
            template = self._find_template(challenge_type)
            zpd_task = domain.zpd_tasks[0] if domain.zpd_tasks else domain.name
            scaffolding = _DREYFUS_SCAFFOLDING_MAP[domain.level]

            challenge = DevelopmentChallenge(
                challenge_id=f"CH-{today}-{i + 1:02d}",
                challenge_type=challenge_type,
                domain=domain.name,
                description=template["description_template"].format(zpd_task=zpd_task),
                zpd_rationale=f"ZPD focus voor {domain.name} (Dreyfus {domain.level})",
                success_criteria=tuple(template.get("success_criteria", ())),
                estimated_minutes=template.get("estimated_minutes", 60),
                scaffolding_level=scaffolding,
                status="PROPOSED",
                created=today,
            )
            challenges.append(challenge)

        return challenges

    def select_challenge_type(self, domain: SkillDomain) -> ChallengeType:
        """Selecteer challenge-type op basis van Dreyfus-level."""
        types = _DREYFUS_CHALLENGE_MAP[domain.level]
        # Deterministic: pick first type for the level
        return types[0]

    def _prioritize_domains(self, profile: SkillRadarProfile) -> list[SkillDomain]:
        """Sorteer domeinen: primary_gap eerst, dan laagste growth_velocity."""
        domains = list(profile.domains)

        def sort_key(d: SkillDomain) -> tuple[int, float]:
            is_primary = 0 if d.name == profile.primary_gap else 1
            return (is_primary, d.growth_velocity)

        domains.sort(key=sort_key)
        return domains

    def _find_template(self, challenge_type: ChallengeType) -> dict[str, Any]:
        """Zoek template voor challenge type."""
        for t in self._templates:
            if t["challenge_type"] == challenge_type:
                return t
        # Fallback to hardcoded
        for t in _FALLBACK_TEMPLATES:
            if t["challenge_type"] == challenge_type:
                return t
        # Should never happen, but return minimal
        return {
            "challenge_type": challenge_type,
            "description_template": "{zpd_task}",
            "success_criteria": [],
            "estimated_minutes": 60,
        }

    @staticmethod
    def _load_templates(path: Path | None) -> list[dict[str, Any]]:
        """Laad templates uit YAML, fallback naar hardcoded."""
        if path is None or not path.exists():
            logger.debug("No template file found, using fallback templates")
            return list(_FALLBACK_TEMPLATES)
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            templates = data.get("templates", [])
            if not templates:
                logger.warning("Template file empty, using fallback")
                return list(_FALLBACK_TEMPLATES)
            return templates
        except Exception:
            logger.warning("Failed to load templates, using fallback", exc_info=True)
            return list(_FALLBACK_TEMPLATES)
