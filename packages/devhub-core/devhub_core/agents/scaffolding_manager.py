"""
Scaffolding Manager — Dreyfus-gekoppelde scaffolding voor challenges.

Beheert de mapping van Dreyfus-level naar scaffolding-niveau en
implementeert het anti-Zone-of-No-Development mechanisme.
"""

from __future__ import annotations

from dataclasses import replace

from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    DreyfusLevel,
    ScaffoldingLevel,
    SkillDomain,
)


# Dreyfus → Scaffolding level mapping
_DREYFUS_SCAFFOLDING_MAP: dict[DreyfusLevel, ScaffoldingLevel] = {
    1: "HIGH",
    2: "MEDIUM",
    3: "LOW",
    4: "NONE",
    5: "NONE",
}

# Scaffolding order for comparison
_SCAFFOLDING_ORDER: dict[ScaffoldingLevel, int] = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "NONE": 0,
}


class ScaffoldingManager:
    """Beheert scaffolding-niveaus gekoppeld aan Dreyfus skill levels.

    Anti-Zone-of-No-Development: scaffolding reduceert automatisch
    bij level-up. Stagnatie wordt gedetecteerd als het level niet
    verandert na meerdere voltooide challenges.
    """

    def get_scaffolding(self, level: DreyfusLevel) -> ScaffoldingLevel:
        """Geef het scaffolding-niveau voor een Dreyfus-level."""
        if level not in _DREYFUS_SCAFFOLDING_MAP:
            raise ValueError(f"level must be 1-5 (Dreyfus), got {level}")
        return _DREYFUS_SCAFFOLDING_MAP[level]

    def should_reduce(
        self,
        domain: SkillDomain,
        challenges_completed: int,
        sprints_at_level: int = 0,
    ) -> bool:
        """Bepaal of scaffolding gereduceerd moet worden.

        Retourneert True als:
        - Het domein op level >= 3 staat (altijd LOW of NONE)
        - Er stagnatie is: >2 sprints op hetzelfde level met challenges voltooid
        """
        # Level 4-5 altijd NONE
        if domain.level >= 4:
            return False  # Already at NONE, nothing to reduce

        # Level 3 → should be LOW, check if challenges were done
        if domain.level >= 3 and challenges_completed > 0:
            return True

        # Stagnation detection: domain has completed challenges but
        # hasn't leveled up in >2 sprints
        if sprints_at_level > 2 and challenges_completed > 0:
            return True

        return False

    def apply_scaffolding(
        self,
        challenge: DevelopmentChallenge,
        level: DreyfusLevel,
    ) -> DevelopmentChallenge:
        """Pas scaffolding-niveau toe op een challenge.

        Retourneert een nieuw frozen DevelopmentChallenge object.
        Muteert nooit het origineel.
        """
        new_scaffolding = self.get_scaffolding(level)
        return replace(challenge, scaffolding_level=new_scaffolding)

    def reduce_scaffolding(
        self,
        challenge: DevelopmentChallenge,
    ) -> DevelopmentChallenge:
        """Reduceer scaffolding met één stap.

        HIGH → MEDIUM → LOW → NONE. Als al NONE, geen verandering.
        """
        reduction_map: dict[ScaffoldingLevel, ScaffoldingLevel] = {
            "HIGH": "MEDIUM",
            "MEDIUM": "LOW",
            "LOW": "NONE",
            "NONE": "NONE",
        }
        new_level = reduction_map[challenge.scaffolding_level]
        return replace(challenge, scaffolding_level=new_level)

    @staticmethod
    def is_lower_than(level_a: ScaffoldingLevel, level_b: ScaffoldingLevel) -> bool:
        """Vergelijk twee scaffolding-niveaus. True als a < b."""
        return _SCAFFOLDING_ORDER[level_a] < _SCAFFOLDING_ORDER[level_b]
