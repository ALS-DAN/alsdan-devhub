"""
Research Advisor — Developer growth modus voor de researcher agent.

Cureert leeslijsten op basis van SkillRadarProfile met ZPD-filtering:
niet te basis (verveling), niet te geavanceerd (frustratie).
Geïmplementeerd als deterministisch Python (geen LLM) — reproduceerbaar.

Sprint 3 van de Mentor Supervisor track (SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM).
"""

from __future__ import annotations

import logging

from devhub_core.contracts.growth_contracts import (
    DreyfusLevel,
    EvidenceGrade,
    LearningRecommendation,
    Priority,
    ResourceType,
    SkillRadarProfile,
    ZpdAlignment,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ZPD-filtering constants
# ---------------------------------------------------------------------------

# ZPD-alignment logica: resource-level t.o.v. developer-level
# - "review": resource_level < developer_level (repetitie, consolidatie)
# - "exact": resource_level == developer_level (comfort zone, versterking)
# - "stretch": resource_level == developer_level + 1 (ZPD — optimaal)
# Resources op level developer+2 of hoger worden niet aanbevolen (te moeilijk)

_ZPD_ALIGNMENT_MAP: dict[int, ZpdAlignment] = {
    -2: "review",
    -1: "review",
    0: "exact",
    1: "stretch",
}

_PRIORITY_MAP: dict[ZpdAlignment, Priority] = {
    "stretch": "URGENT",
    "exact": "IMPORTANT",
    "review": "NICE_TO_HAVE",
}

# ---------------------------------------------------------------------------
# Builtin resource catalogue
# Per domein: een set annotated resources met moeilijkheidsgraad + metadata.
# Dit is de fallback catalogue; uitbreidbaar via YAML (toekomstig).
# ---------------------------------------------------------------------------


class _ResourceEntry:
    """Intern record voor catalogue-entries."""

    __slots__ = (
        "domain",
        "title",
        "resource_type",
        "url",
        "estimated_minutes",
        "difficulty",
        "evidence_grade",
        "rationale",
    )

    def __init__(
        self,
        domain: str,
        title: str,
        resource_type: ResourceType,
        url: str | None,
        estimated_minutes: int,
        difficulty: DreyfusLevel,
        evidence_grade: EvidenceGrade,
        rationale: str,
    ) -> None:
        self.domain = domain
        self.title = title
        self.resource_type = resource_type
        self.url = url
        self.estimated_minutes = estimated_minutes
        self.difficulty = difficulty
        self.evidence_grade = evidence_grade
        self.rationale = rationale


# ---------------------------------------------------------------------------
# Resource catalogue
# ---------------------------------------------------------------------------

_CATALOGUE: list[_ResourceEntry] = [
    # AI-Engineering
    _ResourceEntry(
        domain="AI-Engineering",
        title="Claude Agent SDK — Officiële documentatie",
        resource_type="docs",
        url=None,
        estimated_minutes=45,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Fundament voor multi-agent orchestratie in DevHub",
    ),
    _ResourceEntry(
        domain="AI-Engineering",
        title="Anthropic: Tool use patterns (prompt engineering gids)",
        resource_type="docs",
        url=None,
        estimated_minutes=30,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Kernconcept voor alle agent-tool interacties",
    ),
    _ResourceEntry(
        domain="AI-Engineering",
        title="Multi-agent architecturen: orchestrator vs. swarm vs. pipeline",
        resource_type="tutorial",
        url=None,
        estimated_minutes=60,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Vergelijking van patronen die direct relevant zijn voor DevHub-architectuur",
    ),
    _ResourceEntry(
        domain="AI-Engineering",
        title="Context window management in agentic systemen",
        resource_type="tutorial",
        url=None,
        estimated_minutes=45,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Kritisch voor lange sessies in DevHub agents",
    ),
    _ResourceEntry(
        domain="AI-Engineering",
        title="RAG-systemen: design trade-offs en evaluatiemethoden",
        resource_type="paper",
        url=None,
        estimated_minutes=60,
        difficulty=4,
        evidence_grade="SILVER",
        rationale="Verdieping relevant voor BORIS kennispipeline-architectuur",
    ),
    # Python
    _ResourceEntry(
        domain="Python",
        title="Python dataclasses: frozen, slots en post_init patronen",
        resource_type="docs",
        url=None,
        estimated_minutes=30,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Kernpatroon in DevHub contracts (ADR-049)",
    ),
    _ResourceEntry(
        domain="Python",
        title="Python typing: Protocol, TypeAlias, TypeVar in de praktijk",
        resource_type="tutorial",
        url=None,
        estimated_minutes=45,
        difficulty=3,
        evidence_grade="GOLD",
        rationale="Versterkt type-veiligheid in alle DevHub packages",
    ),
    _ResourceEntry(
        domain="Python",
        title="Pytest: property-based testing met Hypothesis",
        resource_type="tutorial",
        url=None,
        estimated_minutes=60,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Volgende stap na unit/integration tests voor contracts",
    ),
    _ResourceEntry(
        domain="Python",
        title="uv workspace management en dependency resolution",
        resource_type="docs",
        url=None,
        estimated_minutes=30,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Dagelijks gebruikt in DevHub workspace",
    ),
    # Testing
    _ResourceEntry(
        domain="Testing",
        title="Test doubles: mock vs. stub vs. spy — wanneer wat",
        resource_type="tutorial",
        url=None,
        estimated_minutes=30,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Fundamenteel onderscheid voor goede test-architectuur",
    ),
    _ResourceEntry(
        domain="Testing",
        title="Integration testing patronen voor async/event-driven systemen",
        resource_type="tutorial",
        url=None,
        estimated_minutes=45,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Relevant voor n8n workflow-testing in BORIS",
    ),
    # Security
    _ResourceEntry(
        domain="Security",
        title="OWASP Agentic AI Threats & Mitigations 2026",
        resource_type="docs",
        url=None,
        estimated_minutes=45,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Directe basis voor DevHub red-team skill en SecurityScanner",
    ),
    _ResourceEntry(
        domain="Security",
        title="Prompt injection in multi-agent systemen: aanvalspatronen",
        resource_type="paper",
        url=None,
        estimated_minutes=30,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Praktisch risico voor DevHub agents die user-input verwerken",
    ),
    _ResourceEntry(
        domain="Security",
        title="Supply chain aanvallen op Python packages: detectie en mitigatie",
        resource_type="tutorial",
        url=None,
        estimated_minutes=45,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Relevant voor pip-audit integratie in SecurityScanner",
    ),
    _ResourceEntry(
        domain="Security",
        title="Red team methodologie voor AI-systemen (DeepTeam aanpak)",
        resource_type="docs",
        url=None,
        estimated_minutes=60,
        difficulty=4,
        evidence_grade="SILVER",
        rationale="Verdieping voor devhub-redteam skill uitbreidingen",
    ),
    # Governance
    _ResourceEntry(
        domain="Governance",
        title="ADR-patronen: wanneer een Architecture Decision Record schrijven",
        resource_type="tutorial",
        url=None,
        estimated_minutes=20,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Kernpraktijk in DevHub (57+ ADRs in BORIS)",
    ),
    _ResourceEntry(
        domain="Governance",
        title="DEV_CONSTITUTION: alle 8 artikelen met voorbeelden",
        resource_type="docs",
        url=None,
        estimated_minutes=30,
        difficulty=1,
        evidence_grade="GOLD",
        rationale="Fundament van DevHub governance",
    ),
    _ResourceEntry(
        domain="Governance",
        title="Compliance-as-code: automatisch governance checks in CI/CD",
        resource_type="tutorial",
        url=None,
        estimated_minutes=45,
        difficulty=3,
        evidence_grade="SILVER",
        rationale="Volgende stap voor DevHub governance automation",
    ),
    # Architecture
    _ResourceEntry(
        domain="Architecture",
        title="Hexagonale architectuur (ports & adapters) in Python",
        resource_type="tutorial",
        url=None,
        estimated_minutes=60,
        difficulty=3,
        evidence_grade="GOLD",
        rationale="Het patroon achter NodeInterface + Provider adapters in DevHub",
    ),
    _ResourceEntry(
        domain="Architecture",
        title="Event-driven architectuur: CQRS en event sourcing fundamenten",
        resource_type="tutorial",
        url=None,
        estimated_minutes=60,
        difficulty=4,
        evidence_grade="SILVER",
        rationale="Relevant voor toekomstige BORIS pipeline-architectuur",
    ),
    # Methodiek
    _ResourceEntry(
        domain="Methodiek",
        title="Shape Up (Basecamp): appetite, betting table en hills",
        resource_type="book_chapter",
        url=None,
        estimated_minutes=90,
        difficulty=2,
        evidence_grade="SILVER",
        rationale="De sprint-methodiek achter DevHub's planning systeem",
    ),
    _ResourceEntry(
        domain="Methodiek",
        title="Cynefin framework: complex vs. complicated vs. chaotic werk",
        resource_type="tutorial",
        url=None,
        estimated_minutes=30,
        difficulty=2,
        evidence_grade="GOLD",
        rationale="Basis voor sprint-type classificatie in DevHub",
    ),
]


# ---------------------------------------------------------------------------
# ResearchAdvisor
# ---------------------------------------------------------------------------


class ResearchAdvisor:
    """Cureert leeslijsten op basis van SkillRadarProfile (developer growth modus).

    ZPD-filtering zorgt dat aanbevelingen precies in de Zone of Proximal
    Development vallen: niet te gemakkelijk (review), niet te moeilijk (2+
    levels boven developer-niveau). Prioriteit: stretch > exact > review.
    """

    def __init__(self, catalogue: list[_ResourceEntry] | None = None) -> None:
        self._catalogue = catalogue if catalogue is not None else _CATALOGUE

    def curate(
        self,
        profile: SkillRadarProfile,
        max_per_domain: int = 2,
        max_total: int = 5,
    ) -> tuple[LearningRecommendation, ...]:
        """Genereer geprioriteerde leeslijst op basis van het skill-profiel.

        Selectie-logica:
        1. Prioriteer primary_gap domein (meest dringende gap)
        2. Daarna zpd_focus domein
        3. Dan overige domeinen in volgorde van laagste level
        4. Per domein: max max_per_domain aanbevelingen (stretch eerst)
        5. Totaal: max max_total aanbevelingen

        Args:
            profile: Huidig skill radar profiel van de developer.
            max_per_domain: Maximum aanbevelingen per domein.
            max_total: Maximum totaal aanbevelingen.

        Returns:
            Tuple van LearningRecommendation, gesorteerd op prioriteit.
        """
        domain_levels = {d.name: d.level for d in profile.domains}
        ordered_domains = self._prioritize_domains(profile, domain_levels)

        recommendations: list[LearningRecommendation] = []

        for domain_name in ordered_domains:
            if len(recommendations) >= max_total:
                break

            dev_level = domain_levels.get(domain_name, 2)
            domain_recs = self._curate_for_domain(domain_name, dev_level, max_per_domain)
            remaining = max_total - len(recommendations)
            recommendations.extend(domain_recs[:remaining])

        logger.info(
            "ResearchAdvisor: %d aanbevelingen voor %s (primary_gap=%s, zpd_focus=%s)",
            len(recommendations),
            profile.developer,
            profile.primary_gap,
            profile.zpd_focus,
        )
        return tuple(recommendations)

    def curate_for_domain(
        self,
        profile: SkillRadarProfile,
        domain_name: str,
        max_results: int = 3,
    ) -> tuple[LearningRecommendation, ...]:
        """Cureer leeslijst specifiek voor één domein.

        Nuttig bij concept-introductie protocol: één domein dieper belichten.
        """
        domain_levels = {d.name: d.level for d in profile.domains}
        dev_level = domain_levels.get(domain_name, 2)
        return tuple(self._curate_for_domain(domain_name, dev_level, max_results))

    def concept_intro(
        self,
        profile: SkillRadarProfile,
        domain_name: str,
        concept: str,
    ) -> LearningRecommendation | None:
        """Selecteer de meest geschikte introductie-resource voor een concept.

        Concept-introductie protocol (uit sprint-intake):
        - Als developer < level 3 voor dit domein: geef een intro-resource
        - Filter op 'exact' of 'review' alignment (niet te zwaar voor intro)
        - Retourneer de hoogst-gegradeerde resource

        Returns:
            De beste intro-resource, of None als developer >= level 3.
        """
        domain_levels = {d.name: d.level for d in profile.domains}
        dev_level = domain_levels.get(domain_name, 2)

        if dev_level >= 3:
            logger.debug(
                "concept_intro: %s level %d >= 3, geen intro nodig voor '%s'",
                domain_name,
                dev_level,
                concept,
            )
            return None

        domain_entries = [e for e in self._catalogue if e.domain == domain_name]
        intro_entries = [
            e
            for e in domain_entries
            if self._zpd_alignment(e.difficulty, dev_level) in ("exact", "review")
        ]

        if not intro_entries:
            return None

        # Prioriteer op evidence_grade: GOLD > SILVER > BRONZE
        grade_order = {"GOLD": 0, "SILVER": 1, "BRONZE": 2}
        best = min(intro_entries, key=lambda e: grade_order.get(e.evidence_grade, 3))

        return self._to_recommendation(best, dev_level)

    # --- Private helpers ---

    def _prioritize_domains(
        self,
        profile: SkillRadarProfile,
        domain_levels: dict[str, DreyfusLevel],
    ) -> list[str]:
        """Bepaal domein-volgorde: primary_gap → zpd_focus → rest (oplopend level)."""
        ordered: list[str] = []

        if profile.primary_gap and profile.primary_gap in domain_levels:
            ordered.append(profile.primary_gap)

        if (
            profile.zpd_focus
            and profile.zpd_focus in domain_levels
            and profile.zpd_focus not in ordered
        ):
            ordered.append(profile.zpd_focus)

        rest = sorted(
            [d for d in domain_levels if d not in ordered],
            key=lambda d: domain_levels[d],
        )
        ordered.extend(rest)

        return ordered

    def _curate_for_domain(
        self,
        domain_name: str,
        dev_level: DreyfusLevel,
        max_results: int,
    ) -> list[LearningRecommendation]:
        """Selecteer gefilterde en geprioriteerde resources voor één domein."""
        domain_entries = [e for e in self._catalogue if e.domain == domain_name]

        # Filter: alleen resources tot max developer_level + 1
        filtered = [e for e in domain_entries if e.difficulty <= dev_level + 1]

        if not filtered:
            logger.debug("ResearchAdvisor: geen resources voor domein '%s'", domain_name)
            return []

        # Annoteer met ZPD-alignment
        annotated = [(e, self._zpd_alignment(e.difficulty, dev_level)) for e in filtered]

        # Sorteer: stretch eerst, dan exact, dan review; bij gelijke alignment op evidence
        alignment_order = {"stretch": 0, "exact": 1, "review": 2}
        grade_order = {"GOLD": 0, "SILVER": 1, "BRONZE": 2}
        annotated.sort(
            key=lambda ea: (
                alignment_order[ea[1]],
                grade_order.get(ea[0].evidence_grade, 3),
            )
        )

        return [self._to_recommendation(e, dev_level) for e, _ in annotated[:max_results]]

    def _zpd_alignment(self, resource_difficulty: int, dev_level: int) -> ZpdAlignment:
        """Bepaal ZPD-alignment van een resource t.o.v. het developer-level."""
        delta = resource_difficulty - dev_level
        return _ZPD_ALIGNMENT_MAP.get(delta, "review")

    def _to_recommendation(
        self,
        entry: _ResourceEntry,
        dev_level: int,
    ) -> LearningRecommendation:
        """Converteer catalogue-entry naar LearningRecommendation."""
        alignment = self._zpd_alignment(entry.difficulty, dev_level)
        priority = _PRIORITY_MAP[alignment]

        return LearningRecommendation(
            domain=entry.domain,
            title=entry.title,
            resource_type=entry.resource_type,
            url=entry.url,
            estimated_minutes=entry.estimated_minutes,
            zpd_alignment=alignment,
            evidence_grade=entry.evidence_grade,
            rationale=entry.rationale,
            priority=priority,
        )
