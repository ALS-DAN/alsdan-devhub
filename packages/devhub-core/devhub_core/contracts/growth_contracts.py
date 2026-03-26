"""
Growth Contracts — Mentor S1 groei-tracking contracten.

Definieert SkillDomain, SkillRadarProfile, LearningRecommendation,
DevelopmentChallenge en GrowthReport voor de mentor agent.
Gebaseerd op Dreyfus skill model, Zone of Proximal Development (ZPD)
en T-shaped developer profiel. Frozen voor immutability
(conform ADR-049 pattern).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# Type aliases
DreyfusLevel = Literal[1, 2, 3, 4, 5]
ChallengeType = Literal[
    "stretch",
    "explain_it",
    "reverse_engineer",
    "teach_back",
    "cross_domain",
    "adversarial",
]
ScaffoldingLevel = Literal["HIGH", "MEDIUM", "LOW", "NONE"]
ChallengeStatus = Literal["PROPOSED", "ACCEPTED", "COMPLETED", "SKIPPED"]
ResourceType = Literal["paper", "docs", "tutorial", "video", "book_chapter"]
ZpdAlignment = Literal["exact", "stretch", "review"]
EvidenceGrade = Literal["GOLD", "SILVER", "BRONZE"]
Priority = Literal["URGENT", "IMPORTANT", "NICE_TO_HAVE"]


@dataclass(frozen=True)
class SkillDomain:
    """Eén domein in de skill radar."""

    name: str
    level: DreyfusLevel
    subdomains: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    last_assessed: str = ""
    growth_velocity: float = 0.0
    zpd_tasks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if not (1 <= self.level <= 5):
            raise ValueError(f"level must be 1-5 (Dreyfus scale), got {self.level}")


@dataclass(frozen=True)
class SkillRadarProfile:
    """Compleet skill radar snapshot."""

    developer: str
    date: str
    domains: tuple[SkillDomain, ...] = ()
    t_shape_deep: tuple[str, ...] = ()
    t_shape_broad: tuple[str, ...] = ()
    primary_gap: str = ""
    zpd_focus: str = ""

    def __post_init__(self) -> None:
        if not self.developer:
            raise ValueError("developer is required")
        if not self.date:
            raise ValueError("date is required")


@dataclass(frozen=True)
class LearningRecommendation:
    """Eén leerresource-aanbeveling."""

    domain: str
    title: str
    resource_type: ResourceType
    url: str | None = None
    estimated_minutes: int = 30
    zpd_alignment: ZpdAlignment = "exact"
    evidence_grade: EvidenceGrade = "SILVER"
    rationale: str = ""
    priority: Priority = "IMPORTANT"

    def __post_init__(self) -> None:
        if not self.domain:
            raise ValueError("domain is required")
        if not self.title:
            raise ValueError("title is required")
        if not self.rationale:
            raise ValueError("rationale is required")
        if self.estimated_minutes <= 0:
            raise ValueError(f"estimated_minutes must be > 0, got {self.estimated_minutes}")


@dataclass(frozen=True)
class DevelopmentChallenge:
    """Eén deliberate practice challenge."""

    challenge_id: str
    challenge_type: ChallengeType
    domain: str
    description: str
    zpd_rationale: str = ""
    success_criteria: tuple[str, ...] = ()
    estimated_minutes: int = 60
    scaffolding_level: ScaffoldingLevel = "MEDIUM"
    status: ChallengeStatus = "PROPOSED"
    feedback: str | None = None
    created: str = ""
    completed: str | None = None

    def __post_init__(self) -> None:
        if not self.challenge_id:
            raise ValueError("challenge_id is required")
        if not self.description:
            raise ValueError("description is required")
        if not self.domain:
            raise ValueError("domain is required")
        if self.estimated_minutes <= 0:
            raise ValueError(f"estimated_minutes must be > 0, got {self.estimated_minutes}")


@dataclass(frozen=True)
class GrowthReport:
    """Periodiek groeirapport."""

    report_id: str
    period: str
    skill_radar: SkillRadarProfile | None = None
    challenges_completed: int = 0
    challenges_proposed: int = 0
    challenges_skipped: int = 0
    growth_velocity_overall: float = 0.0
    zpd_shift: str | None = None
    learning_recommendations: tuple[LearningRecommendation, ...] = ()
    strategic_insights: tuple[str, ...] = ()
    deliberate_practice_minutes: int = 0
    scaffolding_reductions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.report_id:
            raise ValueError("report_id is required")
        if not self.period:
            raise ValueError("period is required")
