---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
type: TECHNICAL_SPECIFICATION
hoort_bij: SPRINT_INTAKE_DEVHUB_DASHBOARD_NICEGUI_2026-03-28.md
---

# Technische Specificatie: `/profile` — Dynamisch Deskundigheidsplatform

Vervangt de huidige Growth tab. Wordt de 8e top-level pagina (navigatie: Overview, Health, Planning, Knowledge, Governance, Research, Projects, **Profile**). Growth verdwijnt als aparte pagina — alle bestaande Growth-functionaliteit wordt geabsorbeerd in het profiel.

---

## SOTA-onderbouwing

### Bronnen en referenties

| Concept | Bron | Toepassing |
|---------|------|------------|
| **Skills Ontologie** | Gloat (2026), TechWolf 5 AI Layers, INOP Skills Intelligence | Skills als verbonden graaf i.p.v. geïsoleerde punten. Inference van impliciete skills uit activiteit. |
| **SFIA 9** | SFIA Foundation (2024) | 7 verantwoordelijkheidsniveaus × 100+ skills als extern referentiekader naast interne Dreyfus-schaal. |
| **Adaptive Skill Assessment** | Pluralsight Iris / Skill IQ | Bayesian assessment die adaptief is — maar wij baseren op werk-output i.p.v. multiple-choice. |
| **Activity-Driven Inference** | Jellyfish Engineering Intelligence | Skills afgeleid uit git/sprint/review-activiteit zonder handmatige input. |
| **Evidence-Based Portfolio** | VetsWhoCode (2025), EU DigComp | Expertise-claims onderbouwd met artifacts, niet zelf-gerapporteerd. |
| **Adaptive Learning Trajecten** | Degreed Maestro (2025), Degreed Vision 2025 | AI-gestuurde pad-suggesties op basis van huidige vaardigheden, rol, en doelen. |
| **Deliberate Practice** | Ericsson et al. (1993, 2019 revisit), Frontiers in Psychology | Groei met reflectie = expertise; groei zonder reflectie = alleen ervaring. |
| **LXP Architecture** | Degreed MCP Server (2025) | Model Context Protocol voor skills/rol/learning context in AI-systemen. |

**EVIDENCE-grading:** SILVER — gebaseerd op framework-documentatie (SFIA 9, Degreed, Pluralsight), industriestandaarden (INOP, Gloat), en peer-reviewed research (Ericsson deliberate practice).

---

## Architectuur: zes lagen

```
┌─────────────────────────────────────────────────┐
│              /profile                            │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ LAAG 1: Identity Card                     │   │
│  │ Naam · Rol · Overall level · T-shape ·    │   │
│  │ Expertise-signatuur · Actief sinds        │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ LAAG 2: Evidence Portfolio                │   │
│  │ Per domein: artifacts · sprints · grading │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌─────────────────┐  ┌────────────────────┐   │
│  │ LAAG 3: Growth   │  │ LAAG 4: Expertise  │   │
│  │ Analytics         │  │ Graph              │   │
│  │ Curves · Velocity │  │ Verbindingen ·     │   │
│  │ ZPD · Benchmarks  │  │ Clusters · Infer.  │   │
│  └─────────────────┘  └────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ LAAG 5: Growth Trajectory                 │   │
│  │ Doel-profiel · Pad · Milestones · Timeline│   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ LAAG 6: Reflection Journal                │   │
│  │ Sprint reflecties · Maandrapport · Narr.  │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Laag 1: Identity Card

### Doel
De "hero section" — wie je bent als developer in één oogopslag. Vergelijkbaar met een LinkedIn profiel-header, maar evidence-based en dynamisch berekend.

### Data-bronnen

```python
@dataclass(frozen=True)
class DeveloperIdentity:
    """Profiel identity card — berekend uit evidence."""
    name: str
    role: str                           # Uit YAML of handmatig
    overall_dreyfus: float              # Gewogen gemiddelde over domeinen
    primary_expertise: str              # Domein met hoogste level
    expertise_signature: str            # Korte beschrijving (gegenereerd)
    t_shape_deep: tuple[str, ...]       # Domeinen level >= 3
    t_shape_broad: tuple[str, ...]      # Domeinen level 2
    t_shape_gaps: tuple[str, ...]       # Domeinen level 1
    active_since: str                   # Eerste sprint datum
    total_sprints: int
    total_tests_contributed: int        # Tests die via sprints zijn toegevoegd
    unique_value: str                   # Wat maakt dit profiel bijzonder

    @classmethod
    def from_profile_and_tracker(
        cls,
        radar: SkillRadarProfile,
        sprint_count: int,
        test_delta_total: int,
        first_sprint_date: str,
    ) -> DeveloperIdentity:
        """Bereken identity uit bestaande data."""
        levels = [d.level for d in radar.domains]
        weights = [max(0.1, d.growth_velocity) for d in radar.domains]
        weighted_avg = sum(l * w for l, w in zip(levels, weights)) / sum(weights)

        primary = max(radar.domains, key=lambda d: (d.level, d.growth_velocity))

        return cls(
            name=radar.developer,
            role="Solo Developer & System Architect",
            overall_dreyfus=round(weighted_avg, 1),
            primary_expertise=primary.name,
            expertise_signature=cls._generate_signature(radar),
            t_shape_deep=tuple(d.name for d in radar.domains if d.level >= 3),
            t_shape_broad=tuple(d.name for d in radar.domains if d.level == 2),
            t_shape_gaps=tuple(d.name for d in radar.domains if d.level == 1),
            active_since=first_sprint_date,
            total_sprints=sprint_count,
            total_tests_contributed=test_delta_total,
            unique_value=radar.developer + " — visie, sturing, kwaliteitsbewustzijn",
        )
```

### Visuele componenten

1. **Hero Card**: naam, rol, overall Dreyfus (groot getal + label), expertise-signatuur
2. **T-Shape visueel**: bestaande T-shape component (uit Growth), nu berekend uit evidence
3. **Stats strip**: "43 sprints · 1424+ tests · Actief sinds feb 2026 · 8 domeinen"
4. **Unique Value callout**: de context uit de YAML — "Niet een programmeur, maar een systeemdenker met AI als uitvoeringspartner"

### Info-tooltips (laag 1)

| Item | Tooltip |
|------|---------|
| Overall Dreyfus | Gewogen gemiddelde over alle domeinen. Weging: domeinen met hogere groeisnelheid tellen zwaarder. Schaal: 1 (Novice) – 5 (Expert). |
| Primary expertise | Domein met de hoogste combinatie van level + groeisnelheid. |
| Expertise-signatuur | AI-gegenereerde samenvatting van je unieke expertise-combinatie. Gebaseerd op T-shape + evidence patronen. |
| T-Shape | Horizontaal = breedte (level 2+), verticaal = diepte (level 3+). Gaps = level 1. Doel: breed fundament + diepte. |
| Unique Value | Wat maakt je als developer bijzonder — context die niet in levels te vangen is. |

---

## Laag 2: Evidence Portfolio

### Doel
Elke expertise-claim onderbouwd met artifacts. Automatisch gevuld uit bestaande data. EVIDENCE-grading toegepast op expertise-claims zelf.

### Data-bronnen

```python
@dataclass(frozen=True)
class EvidenceArtifact:
    """Eén bewijs-artifact gekoppeld aan een domein."""
    artifact_id: str
    domain: str                     # Welk domein dit evidence is voor
    artifact_type: str              # sprint | test | adr | governance | skill | agent | research
    title: str                      # Beschrijving
    source: str                     # Bestandspad of sprint-referentie
    date: str
    evidence_grade: EvidenceGrade   # GOLD | SILVER | BRONZE | SPECULATIVE
    auto_inferred: bool = True      # Automatisch afgeleid of handmatig

@dataclass(frozen=True)
class DomainEvidenceCard:
    """Volledige evidence card per domein."""
    domain: str
    level: DreyfusLevel
    evidence_grade: EvidenceGrade    # Hoogste grade van de artifacts
    artifacts: tuple[EvidenceArtifact, ...]
    artifact_count: int
    last_activity: str               # Datum van meest recente artifact
    growth_velocity: float
    velocity_trend: str              # "accelerating" | "stable" | "decelerating" | "stagnant"
    days_since_activity: int
    stagnation_warning: bool         # True als >60 dagen geen activiteit
```

### Evidence-mapping regels

Per sprint uit SPRINT_TRACKER worden domeinen automatisch afgeleid:

| Sprint-kenmerk | Domein-mapping |
|----------------|---------------|
| Type FEAT in devhub-core | Python, Architecture |
| Type SPIKE | Research-domein (afh. van inhoud) |
| Governance-impact in intake | Governance |
| Test delta > 0 | Testing (proportioneel) |
| Security-gerelateerd (red-team, ASI) | Security |
| Agent/skill gebouwd | AI-Engineering |
| Shape Up / planning artefact | Methodiek |
| Git/Docker/CI in scope | DevOps/Tooling |

```python
class EvidenceCollector:
    """Verzamelt evidence uit alle beschikbare bronnen."""

    def __init__(self, root: Path, sprint_parser: SprintTrackerParser):
        self.root = root
        self.parser = sprint_parser

    def collect_all(self) -> list[EvidenceArtifact]:
        """Aggregeer evidence uit alle bronnen."""
        artifacts = []
        artifacts.extend(self._from_sprints())
        artifacts.extend(self._from_governance())
        artifacts.extend(self._from_skills_and_agents())
        artifacts.extend(self._from_knowledge())
        artifacts.extend(self._from_research())
        return artifacts

    def _from_sprints(self) -> list[EvidenceArtifact]:
        """Elke sprint = 1+ evidence artifacts op basis van domein-mapping."""
        entries = self.parser.parse_sprint_log()
        artifacts = []
        for entry in entries:
            domains = self._infer_domains(entry)
            for domain in domains:
                artifacts.append(EvidenceArtifact(
                    artifact_id=f"sprint-{entry.nummer}-{domain}",
                    domain=domain,
                    artifact_type="sprint",
                    title=f"Sprint {entry.nummer}: {entry.naam}",
                    source="docs/planning/SPRINT_TRACKER.md",
                    date=entry.datum if hasattr(entry, 'datum') else "",
                    evidence_grade="SILVER",  # Intern bewezen
                    auto_inferred=True,
                ))
        return artifacts

    def _from_governance(self) -> list[EvidenceArtifact]:
        """ADRs, DEV_CONSTITUTION, governance artifacts."""
        artifacts = []
        # DEV_CONSTITUTION
        constitution = self.root / "docs" / "compliance" / "DEV_CONSTITUTION.md"
        if constitution.exists():
            artifacts.append(EvidenceArtifact(
                artifact_id="governance-constitution",
                domain="Governance",
                artifact_type="governance",
                title="DEV_CONSTITUTION.md — 9 artikelen",
                source=str(constitution),
                date="2026-03",
                evidence_grade="SILVER",
            ))
        # ADRs
        adr_dir = self.root / "docs" / "adr"
        if adr_dir.exists():
            for adr in sorted(adr_dir.glob("*.md")):
                artifacts.append(EvidenceArtifact(
                    artifact_id=f"governance-adr-{adr.stem}",
                    domain="Governance",
                    artifact_type="adr",
                    title=f"ADR: {adr.stem}",
                    source=str(adr),
                    date="2026-03",
                    evidence_grade="SILVER",
                ))
        return artifacts

    def _from_skills_and_agents(self) -> list[EvidenceArtifact]:
        """Gebouwde skills en agents = AI-Engineering evidence."""
        artifacts = []
        for skill_dir in self.root.glob(".claude/skills/devhub-*"):
            artifacts.append(EvidenceArtifact(
                artifact_id=f"ai-eng-skill-{skill_dir.name}",
                domain="AI-Engineering",
                artifact_type="skill",
                title=f"Skill gebouwd: {skill_dir.name}",
                source=str(skill_dir),
                date="2026-03",
                evidence_grade="SILVER",
            ))
        for agent_file in self.root.glob("agents/*.md"):
            artifacts.append(EvidenceArtifact(
                artifact_id=f"ai-eng-agent-{agent_file.stem}",
                domain="AI-Engineering",
                artifact_type="agent",
                title=f"Agent ontworpen: {agent_file.stem}",
                source=str(agent_file),
                date="2026-03",
                evidence_grade="SILVER",
            ))
        return artifacts

    def _from_knowledge(self) -> list[EvidenceArtifact]:
        """Kennisartikelen en research."""
        # Skill radar YAML = evidence voor zelfinzicht (meta-evidence)
        artifacts = []
        for yaml_file in self.root.glob("knowledge/skill_radar/*.yaml"):
            artifacts.append(EvidenceArtifact(
                artifact_id=f"meta-{yaml_file.stem}",
                domain="Methodiek",
                artifact_type="research",
                title=f"Skill Radar self-assessment: {yaml_file.stem}",
                source=str(yaml_file),
                date="2026-03-26",
                evidence_grade="BRONZE",  # Zelf-gerapporteerd
            ))
        return artifacts

    def _from_research(self) -> list[EvidenceArtifact]:
        """Research voorstellen en resultaten."""
        artifacts = []
        for research in self.root.glob("docs/planning/inbox/RESEARCH_VOORSTEL_*.md"):
            artifacts.append(EvidenceArtifact(
                artifact_id=f"research-{research.stem}",
                domain="Methodiek",
                artifact_type="research",
                title=f"Research: {research.stem.replace('RESEARCH_VOORSTEL_', '')}",
                source=str(research),
                date="2026-03",
                evidence_grade="BRONZE",
            ))
        return artifacts
```

### EVIDENCE-grading op expertise-claims

| Grade | Betekenis | Voorbeeld |
|-------|-----------|-----------|
| **GOLD** | Extern gevalideerd | Certificering, productie-deployment bij klant, peer review |
| **SILVER** | Intern bewezen | Sprint afgerond, tests geschreven, artifact geproduceerd |
| **BRONZE** | Ervaring | Betrokken bij, meegedacht, maar niet leidend |
| **SPECULATIVE** | Zelf-gerapporteerd | Nog niet bewezen met artifacts |

### Visuele componenten

1. **Evidence Cards Grid** — per domein een uitklapbare kaart
2. **Evidence grade badge** — kleurgecodeerd (GOLD/SILVER/BRONZE)
3. **Artifact lijst** — per kaart: icoon + titel + datum + bron
4. **Activity indicator** — "Laatste activiteit: 3 dagen geleden" + stagnatie-waarschuwing
5. **Auto-inferred badge** — onderscheidt automatisch afgeleide vs. handmatige evidence

### Info-tooltips (laag 2)

| Item | Tooltip |
|------|---------|
| Evidence grade | GOLD = extern gevalideerd. SILVER = intern bewezen (sprints, tests). BRONZE = ervaring. SPECULATIVE = zelf-gerapporteerd. |
| Auto-inferred | ⚙️ Automatisch afgeleid uit sprint-data en bestandsstructuur. Handmatig toevoegen is ook mogelijk. |
| Artifact count | Totaal bewijs-artifacts voor dit domein. Meer artifacts = robuuster bewijs voor het level. |
| Stagnatie waarschuwing | Geen activiteit in dit domein in >60 dagen. Overweeg een sprint of challenge in dit gebied. |

---

## Laag 3: Growth Analytics

### Doel
Niet alleen *waar* je staat, maar *hoe snel en waarheen* je beweegt. Stagnatie-detectie, ZPD-heatmap, en benchmarking.

### Data-bronnen

```python
@dataclass(frozen=True)
class DomainGrowthMetrics:
    """Groei-analytics per domein."""
    domain: str
    current_level: DreyfusLevel
    level_6_months_ago: float        # Interpolatie uit evidence-timeline
    growth_velocity: float           # Level-verandering per maand
    velocity_trend: str              # accelerating | stable | decelerating | stagnant
    learning_curve: tuple[tuple[str, float], ...]  # (datum, level) punten voor sparkline
    zpd_status: str                  # "sweet_spot" | "too_easy" | "too_hard" | "stagnant"
    time_to_next_level: int | None   # Geschatte dagen tot volgend level (None als onbekend)
    sprint_count_in_domain: int      # Aantal sprints met activiteit in dit domein
    last_activity_date: str

@dataclass(frozen=True)
class OverallGrowthAnalytics:
    """Profiel-brede growth analytics."""
    domains: tuple[DomainGrowthMetrics, ...]
    overall_velocity: float          # Gemiddelde groeisnelheid
    fastest_growing: str             # Domein met hoogste velocity
    most_stagnant: str               # Domein met laagste velocity
    zpd_sweet_spots: tuple[str, ...]  # Domeinen in de "sweet spot"
    total_evidence_artifacts: int
    sfia_benchmark: SfiaBenchmark | None

@dataclass(frozen=True)
class SfiaBenchmark:
    """SFIA 9 vergelijking voor rol-context."""
    role_name: str                   # "Solo Developer / System Architect"
    sfia_level: int                  # Verwacht SFIA verantwoordelijkheidsniveau (1-7)
    domain_gaps: tuple[str, ...]     # Domeinen onder verwachting
    domain_exceeds: tuple[str, ...]  # Domeinen boven verwachting
    benchmark_source: str            # "SFIA 9 illustrative profiles"
```

### ZPD-berekening

```python
def calculate_zpd_status(domain: DomainGrowthMetrics) -> str:
    """Bepaal ZPD-status op basis van groeisnelheid en activiteit.

    - sweet_spot: groeisnelheid > 0.1 én recent actief (< 30 dagen)
    - too_easy: hoge groeisnelheid maar level al >= 3 (consolidatie nodig)
    - too_hard: veel activiteit maar geen level-verandering (> 3 sprints, velocity < 0.05)
    - stagnant: geen activiteit > 60 dagen
    """
```

### Visuele componenten

1. **Growth Velocity Dashboard** — 8 mini-cards met sparkline per domein
2. **ZPD Heatmap** — matrix met domeinen als rijen, status als kleur (groen=sweet spot, blauw=consolidatie, rood=te moeilijk, grijs=stagnant)
3. **Learning Curves** — Plotly multi-line chart: level over tijd per domein
4. **Stagnation Alerts** — prominente waarschuwingen bij >60 dagen inactiviteit
5. **SFIA Benchmark radar** — overlay op skill radar: jouw levels vs. SFIA verwachting voor je rol

### Info-tooltips (laag 3)

| Item | Tooltip |
|------|---------|
| Growth velocity | Level-verandering per maand. >0.1 = actieve groei, <0.05 = stagnatie. Berekend uit evidence-timeline. |
| ZPD sweet spot | Zone of Proximal Development — het domein is precies moeilijk genoeg om optimaal te leren. Niet te makkelijk (verveling), niet te moeilijk (frustratie). |
| SFIA benchmark | Vergelijking met SFIA 9 verwachtingen voor de rol "Solo Developer / System Architect". Extern referentiekader naast interne Dreyfus-schaal. |
| Time to next level | Geschatte dagen tot volgend Dreyfus level op basis van huidige groeisnelheid. Puur indicatief. |
| Learning curve | Level-ontwikkeling over tijd per domein. Steiler = snellere groei. Vlak = consolidatie of stagnatie. |

---

## Laag 4: Expertise Graph

### Doel
Domeinen als verbonden netwerk i.p.v. geïsoleerde radar-punten. Toont hoe expertise-gebieden elkaar versterken, clusteren, en afhankelijk zijn.

### Data-bronnen

```python
@dataclass(frozen=True)
class ExpertiseEdge:
    """Verbinding tussen twee domeinen in de expertise-graaf."""
    source: str                     # Domein A
    target: str                     # Domein B
    weight: float                   # Sterkte van de verbinding (0.0-1.0)
    relationship_type: str          # "synergy" | "dependency" | "co_occurrence" | "inferred"
    evidence: str                   # Waarom deze verbinding bestaat

@dataclass(frozen=True)
class ExpertiseCluster:
    """Cluster van verwante domeinen."""
    cluster_name: str               # "System Builder", "Quality Guardian", etc.
    domains: tuple[str, ...]
    synergy_description: str        # Wat de combinatie oplevert

@dataclass(frozen=True)
class InferredSkill:
    """Automatisch afgeleide sub-skill uit activiteitspatronen."""
    skill_name: str
    parent_domain: str
    confidence: float               # 0.0-1.0
    inferred_from: tuple[str, ...]  # Welke activiteiten dit suggereren
```

### Ontologie-definitie

Statische ontologie (configureerbaar, uitbreidbaar):

```yaml
# config/expertise_ontology.yml
clusters:
  system_builder:
    name: "System Builder"
    domains: [AI-Engineering, Python, Architecture]
    synergy: "Combinatie maakt het mogelijk complete systemen te ontwerpen en aansturen"

  quality_guardian:
    name: "Quality Guardian"
    domains: [Governance, Testing, Security]
    synergy: "Combinatie borgt kwaliteit van code tot compliance"

  delivery_engine:
    name: "Delivery Engine"
    domains: [Methodiek, DevOps/Tooling, Architecture]
    synergy: "Combinatie maakt efficiënte, herhaalbare delivery mogelijk"

edges:
  - source: Python
    target: Testing
    type: dependency
    evidence: "Testing vereist Python-leesvaardigheid om testcode te beoordelen"

  - source: Architecture
    target: Security
    type: dependency
    evidence: "Security-beoordeling vereist architectureel inzicht"

  - source: AI-Engineering
    target: Python
    type: dependency
    evidence: "AI-Engineering met Claude vereist begrip van Python-output"

  - source: Governance
    target: Architecture
    type: synergy
    evidence: "Samen vormen ze compliance-driven design"

  - source: Methodiek
    target: Governance
    type: synergy
    evidence: "Sprint-discipline versterkt governance-tracking"

  - source: AI-Engineering
    target: Governance
    type: co_occurrence
    evidence: "Agent-design en governance worden vaak samen geraakt in sprints"

skill_inference_rules:
  - if_skills: [AI-Engineering >= 2, Python >= 1]
    infer: "prompt engineering"
    confidence: 0.8

  - if_skills: [Governance >= 2, Architecture >= 2]
    infer: "compliance-driven design"
    confidence: 0.7

  - if_skills: [Methodiek >= 2, Governance >= 2]
    infer: "sprint-discipline"
    confidence: 0.8
```

### Dynamische edges

Naast statische ontologie worden edges **dynamisch berekend** uit sprint co-occurrence:

```python
def calculate_co_occurrence_edges(
    evidence: list[EvidenceArtifact],
) -> list[ExpertiseEdge]:
    """Bereken edge-gewicht uit hoe vaak twee domeinen in dezelfde sprint voorkomen."""
    # Tel per sprint welke domeinen geraakt worden
    sprint_domains: dict[str, set[str]] = {}
    for artifact in evidence:
        if artifact.artifact_type == "sprint":
            sprint_id = artifact.artifact_id.split("-")[1]
            sprint_domains.setdefault(sprint_id, set()).add(artifact.domain)

    # Bereken co-occurrence
    from itertools import combinations
    co_counts: dict[tuple[str, str], int] = {}
    total_sprints = len(sprint_domains)
    for domains in sprint_domains.values():
        for a, b in combinations(sorted(domains), 2):
            co_counts[(a, b)] = co_counts.get((a, b), 0) + 1

    edges = []
    for (a, b), count in co_counts.items():
        weight = count / total_sprints  # Normaliseer
        if weight > 0.1:  # Minimale drempel
            edges.append(ExpertiseEdge(
                source=a, target=b,
                weight=round(weight, 2),
                relationship_type="co_occurrence",
                evidence=f"Samen geraakt in {count}/{total_sprints} sprints",
            ))
    return edges
```

### Visuele componenten

1. **Force-directed graph** — Plotly of D3 network visualisatie
   - Nodes = domeinen (grootte = evidence volume, kleur = Dreyfus level)
   - Edges = ontologie + co-occurrence (dikte = weight)
   - Clusters visueel gegroepeerd met achtergrondkleur
2. **Cluster cards** — per cluster een kaart met beschrijving en synergie-uitleg
3. **Inferred skills lijst** — automatisch afgeleide sub-skills met confidence badge

### Info-tooltips (laag 4)

| Item | Tooltip |
|------|---------|
| Node grootte | Groter = meer evidence artifacts. Meer bewijs = meer zekerheid over het level. |
| Edge dikte | Dikker = vaker samen geraakt in dezelfde sprint. Sterke verbindingen = synergieën. |
| Cluster | Groep van domeinen die samen een specifieke capability vormen. |
| Inferred skill | Automatisch afgeleid: als je X en Y op level N hebt, heb je waarschijnlijk ook Z. Confidence toont zekerheid. |

---

## Laag 5: Growth Trajectory

### Doel
Adaptief pad van huidig naar gewenst profiel. Gekoppeld aan project-behoeften.

### Data-bronnen

```python
@dataclass(frozen=True)
class GrowthGoal:
    """Eén groeidoel voor een specifiek domein."""
    domain: str
    current_level: DreyfusLevel
    target_level: DreyfusLevel
    priority: str                    # "critical" | "high" | "medium" | "low"
    reason: str                      # Waarom dit doel (project-need, persoonlijk, ZPD)
    estimated_months: float          # Op basis van growth velocity
    milestones: tuple[GrowthMilestone, ...]

@dataclass(frozen=True)
class GrowthMilestone:
    """Meetbaar tussenstap op weg naar een groeidoel."""
    milestone_id: str
    description: str                 # "Eerste eigen pytest fixture schrijven"
    domain: str
    estimated_effort: str            # "1 sprint" | "2 uur" etc.
    completed: bool = False
    completed_date: str | None = None
    evidence_artifact: str | None = None  # Link naar evidence bij completion

@dataclass(frozen=True)
class GrowthTrajectory:
    """Volledig groeitraject met doelen en paden."""
    goals: tuple[GrowthGoal, ...]
    project_alignment: tuple[ProjectNeed, ...]
    recommended_next_sprint_focus: str  # Welk domein voor de volgende sprint
    recommended_challenge: DevelopmentChallenge | None

@dataclass(frozen=True)
class ProjectNeed:
    """Project-behoefte die groei-prioriteit beïnvloedt."""
    project_name: str               # "BORIS"
    domain: str                     # Welk domein nodig is
    urgency: str                    # "high" | "medium" | "low"
    description: str                # Waarom dit project dit domein nodig heeft
```

### Project-alignment

```python
def align_with_project_needs(
    trajectory: GrowthTrajectory,
    project_needs: list[ProjectNeed],
) -> GrowthTrajectory:
    """Pas groei-prioriteiten aan op basis van project-behoeften.

    Voorbeeld: BORIS heeft security nodig → Security-doel krijgt priority boost.
    """
```

### Visuele componenten

1. **Doel-profiel radar overlay** — bestaande skill radar + dashed overlay voor doel-levels
2. **Milestone timeline** — horizontale tijdlijn met milestones als punten, afgeronde groen
3. **Project alignment cards** — per project wat het profiel nodig heeft
4. **Recommended Next Actions** — top 3 concrete stappen (sprint, challenge, studie)
5. **Challenges & Recommendations** — de bestaande Growth-componenten (geabsorbeerd)
   - Challenge Engine paneel (DevelopmentChallenge cards met start/skip/complete)
   - Learning Recommendations (LearningRecommendation cards)

### Info-tooltips (laag 5)

| Item | Tooltip |
|------|---------|
| Doel-profiel | Gewenst level per domein over 6 maanden. Overlay op de skill radar. Stel bij via "Edit Goals". |
| Milestone | Meetbaar tussenstap. Groen = afgerond (met evidence). Grijs = open. |
| Project alignment | Projecten die DevHub beheert hebben eigen competentie-behoeften. Die beïnvloeden de groei-prioriteiten. |
| Estimated months | Geschat op basis van huidige growth velocity. Puur indicatief — versnelling of vertraging is normaal. |

---

## Laag 6: Reflection Journal

### Doel
Deliberate practice vereist reflectie (Ericsson). Sprint-retrospectives als groei-instrument, gekoppeld aan evidence portfolio.

### Data-bronnen

```python
@dataclass(frozen=True)
class SprintReflection:
    """Reflectie na een sprint — deliberate practice instrument."""
    reflection_id: str
    sprint_nummer: int
    date: str
    what_learned: str               # "Wat heb ik geleerd?"
    where_stuck: str                # "Waar liep ik vast?"
    what_different: str             # "Wat zou ik anders doen?"
    domains_touched: tuple[str, ...] # Welke domeinen raakte deze sprint
    growth_insight: str | None      # Optioneel: meta-inzicht over groeipatroon
    mood: str = "neutral"           # "energized" | "neutral" | "frustrated" | "proud"

@dataclass(frozen=True)
class MonthlyRetrospective:
    """Automatisch gegenereerd maandoverzicht."""
    month: str                      # "2026-03"
    reflections: tuple[SprintReflection, ...]
    sprints_completed: int
    domains_active: tuple[str, ...]
    growth_highlight: str           # Belangrijkste groei-moment
    pattern_detected: str | None    # Terugkerend patroon in reflecties
    narrative: str                  # Samenvatting als verhaal

class ReflectionStore:
    """File-based opslag voor reflecties."""

    def __init__(self, root: Path):
        self.path = root / "data" / "profile" / "reflections"

    def save_reflection(self, reflection: SprintReflection) -> None:
        """Sla reflectie op als YAML bestand."""
        # data/profile/reflections/sprint_42_2026-03-28.yml

    def load_reflections(self, limit: int = 20) -> list[SprintReflection]:
        """Laad recente reflecties."""

    def generate_monthly(self, month: str) -> MonthlyRetrospective:
        """Genereer maandoverzicht uit reflecties."""
```

### Visuele componenten

1. **Reflectie formulier** — na elke sprint: 3 vragen + domein-tags + mood selector
2. **Reflectie timeline** — chronologische lijst met mood-indicatoren
3. **Maandoverzicht card** — samenvatting met highlight + patroon-detectie
4. **Growth Narrative** — langere tekst die de ontwikkeling over tijd beschrijft
5. **Patroon-alerts** — "Je noemt 'vasthouden aan het grotere plaatje' in 4 van de 6 reflecties — dit is een kracht"

### Info-tooltips (laag 6)

| Item | Tooltip |
|------|---------|
| Sprint reflectie | Deliberate practice vereist reflectie (Ericsson). 3 vragen die je helpen bewust te groeien. |
| Mood indicator | Je energieniveau na een sprint. Patronen hierin helpen bepalen welk werk je energie geeft. |
| Maandoverzicht | Automatisch gegenereerd uit je reflecties. Detecteert patronen en groei-momenten. |
| Growth Narrative | Je ontwikkelingsgeschiedenis als verhaal. Wordt rijker naarmate je meer reflecties schrijft. |

---

## ProfileProvider — data-aggregator

```python
class ProfileProvider:
    """Centrale data provider voor de /profile pagina.

    Aggregeert data uit:
    - SkillRadarProfile (YAML)
    - SprintTrackerParser
    - EvidenceCollector
    - ExpertiseOntology (YAML)
    - ReflectionStore
    - GrowthProvider (bestaand)
    """

    def __init__(self, root: Path):
        self.root = root
        self.evidence_collector = EvidenceCollector(root, SprintTrackerParser(root))
        self.reflection_store = ReflectionStore(root)
        self.growth_provider = GrowthProvider(root)  # Bestaand

    def get_identity(self) -> DeveloperIdentity: ...
    def get_evidence_portfolio(self) -> list[DomainEvidenceCard]: ...
    def get_growth_analytics(self) -> OverallGrowthAnalytics: ...
    def get_expertise_graph(self) -> tuple[list[ExpertiseEdge], list[ExpertiseCluster], list[InferredSkill]]: ...
    def get_trajectory(self) -> GrowthTrajectory: ...
    def get_reflections(self, limit: int = 20) -> list[SprintReflection]: ...
    def get_monthly_retrospective(self, month: str) -> MonthlyRetrospective: ...
```

---

## Bestandsstructuur na implementatie

### Nieuwe bestanden

```
packages/devhub-dashboard/devhub_dashboard/
├── pages/
│   └── profile.py                  # NIEUW — /profile pagina (vervangt growth.py)
├── components/
│   ├── identity_card.py            # NIEUW — hero section
│   ├── evidence_card.py            # NIEUW — domein evidence cards
│   ├── growth_analytics.py         # NIEUW — sparklines, ZPD heatmap, learning curves
│   ├── expertise_graph.py          # NIEUW — force-directed graph
│   ├── trajectory_panel.py         # NIEUW — doelen, milestones, alignment
│   ├── reflection_form.py          # NIEUW — reflectie input formulier
│   └── reflection_timeline.py      # NIEUW — reflectie overzicht
├── data/
│   ├── providers.py                # UITBREID met ProfileProvider
│   └── evidence_collector.py       # NIEUW — evidence aggregatie
├── config.py                       # UITBREID met PROFILE_TOOLTIPS

config/
└── expertise_ontology.yml          # NIEUW — domein-relaties en clusters

data/profile/
├── reflections/                    # NIEUW — sprint reflecties (YAML)
├── goals.yml                       # NIEUW — groeidoelen
└── trajectory_cache.json           # NIEUW — berekende trajectory cache
```

### Verwijderde/gewijzigde bestanden

| Bestand | Wijziging |
|---------|-----------|
| `pages/growth.py` | VERWIJDERD — functionaliteit geabsorbeerd in `pages/profile.py` |
| `app.py` | Route `/growth` → redirect naar `/profile`. Nieuwe route `/profile`. Navigatie bijgewerkt. |
| Alle pagina's | Quick Actions: "Growth" categorie → "Profile" categorie |

### Totaal: 10 nieuwe bestanden, 4 uitgebreide, 1 verwijderd

---

## Migratie van Growth naar Profile

De bestaande Growth-componenten worden niet weggegooid maar **ingebed**:

| Bestaand (Growth) | Nieuw (Profile) | Laag |
|-------------------|-----------------|------|
| Skill Radar chart | Identity Card T-shape + Trajectory doel-overlay | 1 + 5 |
| Domain Detail Cards | Evidence Portfolio Cards (uitgebreid met artifacts) | 2 |
| T-Shape profiel | Identity Card T-Shape (berekend i.p.v. hardcoded) | 1 |
| Challenge Engine | Trajectory: Challenges & Recommendations panel | 5 |
| Learning Recommendations | Trajectory: Recommended Next Actions | 5 |
| GrowthProvider | ProfileProvider (wropt GrowthProvider) | alle |

---

## BORIS-blauwdruk potentieel

| DevHub Profile | BORIS Equivalent |
|----------------|-----------------|
| Sprint evidence | Casuïstiek, behandelingen, interventies |
| Dreyfus levels | BIG-registratie niveaus, competenties |
| Skills ontologie | Zorgdomein-competentie-framework (V&VN) |
| Growth trajectory | Persoonlijk Ontwikkelplan (POP) |
| Reflection journal | Supervisie-verslagen, intervisie |
| SFIA benchmark | V&VN competentieprofiel, BIG-register |
| Evidence grading | Portfolio-assessment, EVC (Eerder Verworven Competenties) |

De datastructuren zijn generiek. `EvidenceArtifact`, `ExpertiseEdge`, `SprintReflection` zijn domein-agnostisch en herbruikbaar in BORIS.

---

## Test strategie

### Nieuwe tests (~40-50)

| Test | Type | Dekt |
|------|------|------|
| `test_evidence_collector.py` | Unit | Artifact discovery uit alle bronnen, domein-mapping, grading |
| `test_domain_evidence_card.py` | Unit | Evidence aggregatie per domein, velocity_trend, stagnation |
| `test_expertise_graph.py` | Unit | Ontologie loading, co-occurrence berekening, edge normalisatie |
| `test_expertise_clusters.py` | Unit | Cluster-detectie, inferred skills, confidence |
| `test_growth_analytics.py` | Unit | ZPD berekening, learning curves, SFIA benchmark |
| `test_trajectory.py` | Unit | Goal generation, milestone tracking, project alignment |
| `test_reflection_store.py` | Unit | YAML read/write, monthly generation |
| `test_profile_provider.py` | Integration | Volledige provider pipeline |
| `test_identity_card.py` | Integration | DeveloperIdentity.from_profile_and_tracker |
| `test_profile_page.py` | Integration | NiceGUI page rendering |

### Bestaande tests
Growth-gerelateerde tests in `test_growth_contracts.py` blijven behouden — de contracts veranderen niet, alleen de provider die ze gebruikt.

---

## Quick Actions voor Profile

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Refresh Evidence | 📋 | `ProfileProvider.get_evidence_portfolio()` (force reload) | ObservationEmitted |
| Update Skill Radar | 📡 | `GrowthProvider.reload_radar()` | ObservationEmitted |
| New Reflection | ✍️ | Opent reflectie-formulier | — (form) |
| Next Challenge | 🎯 | `GrowthProvider.next_challenge()` | — (instant) |
| Recalculate Trajectory | 🗺️ | `ProfileProvider.get_trajectory()` (force recalc) | ObservationEmitted |

---

## Open vragen voor Claude Code

1. **Expertise graph renderer**: Plotly network graph (via `go.Scatter` met edges) of D3 via `ui.html()`? Plotly is consistent met rest van dashboard, D3 is interactiever voor grafen.

2. **Evidence collector performance**: Bij 43+ sprints + git history + file scanning — cachen? Suggestie: evidence cache met 5 minuten TTL, force-refresh via Quick Action.

3. **Reflection formulier UX**: NiceGUI `ui.input()` + `ui.textarea()` + `ui.select()`. Mood als emoji-knoppen of dropdown?

4. **SFIA benchmark data**: Statisch ingebakken (config/sfia_benchmark.yml) of dynamisch ophalen? Statisch is simpeler en voldoende voor v1.

5. **Growth narrative generatie**: Maandoverzicht is een samenvatting van reflecties. Door de ProfileProvider zelf (template-based) of via mentor-agent? Template-based voor v1, agent voor v2.

6. **Backwards-compatible routing**: `/growth` moet redirecten naar `/profile`. NiceGUI `app.add_redirect('/growth', '/profile')` of simpeler?

---

## DEV_CONSTITUTION impact

| Artikel | Impact |
|---------|--------|
| Art. 4 (Transparantie) | Profiel maakt expertise-onderbouwing transparant en traceerbaar |
| Art. 5 (Kennisintegriteit) | EVIDENCE-grading op expertise-claims versterkt Art. 5 |
| Art. 7 (Impact-zonering) | GREEN — nieuwe bestanden, growth.py wordt vervangen maar functionaliteit behouden |
| Art. 9 (Planning) | Reflection journal koppelt aan sprint-tracking |

---

## Relatie met andere intakes

| Intake | Relatie |
|--------|---------|
| Dashboard Bestaande Panelen Upgrade | Growth-sectie in die spec wordt vervangen door deze Profile spec |
| Dashboard Projects + Quick Actions | Profile krijgt Quick Actions, Projects kan profile-data tonen per developer |
| Kennisketen End-to-End | Evidence Portfolio wordt rijker na kennisketen sprint |
| Mentor Supervisor Systeem (Track M S3) | Reflection Journal en Growth Trajectory voeden de mentor-agent |
