# devhub-growth — Periodiek Developer Growth Report

**Versie:** 1.0.0
**Basis:** SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM Sprint 3 — Research Advisor + Dashboard

## Trigger
Activeer bij: "growth report", "groeirapport", "skill radar", "hoe groei ik", "leeslijst", "learning recommendations", "ZPD", "welke skills ontbreken", "developer growth", "periodiek rapport".

## Doel
Genereer een periodiek GrowthReport dat laat zien waar de developer staat (Skill Radar), wat er geleerd kan worden (leeslijst met ZPD-filtering), en welke strategische inzichten er zijn. Combineert sprint-data, challenges en een geprioriteerde leeslijst tot één overzicht.

De kracht: (1) ZPD-filtering geeft leesaanbevelingen die precies op het juiste niveau zitten, (2) het rapport combineert automatisch skill radar + challenges + leeslijst, (3) strategische inzichten detecteren patronen die niet voor de hand liggen.

---

## Setup

```python
from devhub_core.agents.growth_report_generator import GrowthReportGenerator
from devhub_core.agents.research_advisor import ResearchAdvisor
from devhub_core.contracts.growth_contracts import SkillRadarProfile

gen = GrowthReportGenerator()
```

---

## Workflow

### Stap 1: SkillRadarProfile ophalen of construeren

**Optie A — uit bestaand YAML bestand:**
```python
import yaml
from pathlib import Path

profile_data = yaml.safe_load(Path("knowledge/skill_radar.yml").read_text())
# Verwerk naar SkillRadarProfile frozen dataclass
```

**Optie B — handmatig invoeren (als er nog geen profiel is):**
```
Vraag aan Niels:
- Dreyfus-level (1-5) per domein: AI-Engineering, Python, Governance,
  Testing, Security, Architecture, DevOps/Tooling, Methodiek
- Welk domein is het primary_gap?
- Welk domein is de huidige zpd_focus?
```

### Stap 2: Challenges ophalen (optioneel)

```python
from devhub_core.contracts.growth_contracts import DevelopmentChallenge

# Challenges uit actieve sprint of scratchpad
challenges: list[DevelopmentChallenge] = []  # of geladen uit YAML/JSON
```

### Stap 3: GrowthReport genereren

```python
report = gen.generate(
    period="sprint-22",           # of "week-2026-13"
    profile=profile,
    challenges=challenges,
    report_id="GROWTH-2026-03-27",
)
```

### Stap 4: Rapport tonen

```python
print(gen.format_text(report))
```

### Stap 5: Concept-introductie protocol (optioneel)

Wanneer een sprint-intake een concept vereist dat Niels nog niet op COMPETENT-niveau (≥3) beheerst:

```python
from devhub_core.agents.research_advisor import ResearchAdvisor

advisor = ResearchAdvisor()
intro = advisor.concept_intro(profile, domain_name="Security", concept="OWASP ASI")

if intro:
    print(f"Intro aanbeveling voor '{concept}':")
    print(f"  {intro.title} ({intro.estimated_minutes} min, {intro.evidence_grade})")
    print(f"  {intro.rationale}")
```

---

## Output format

```
═══════════════════════════════════════════════════
DEVELOPER GROWTH REPORT — sprint-22
═══════════════════════════════════════════════════

SKILL RADAR
  AI-Engineering        ███░░  3/5
  Python                ███░░  3/5
  Governance            ████░  4/5
  Testing               ██░░░  2/5  → gap gedetecteerd
  Security              ██░░░  2/5  → ZPD focus (primary gap)

T-SHAPE
  Deep (≥4): Governance
  Broad (≥2): AI-Engineering, Python, Governance, Testing, Security
  Gap: Security → ZPD focus

DELIBERATE PRACTICE — sprint-22
  Voltooid: 2
  Openstaand: 1
  Overgeslagen: 0
  Totale DP-tijd: 60 min

LEESLIJST (geprioriteerd op ZPD)
  🔴 OWASP Agentic AI Threats & Mitigations 2026 (45 min, GOLD, stretch)
  🟡 OWASP basics (20 min, GOLD, exact)
  🟢 DEV_CONSTITUTION: alle 8 artikelen (30 min, GOLD, review)

STRATEGISCH INZICHT
  "De gap in 'Security' (Dreyfus level 2) is het grootste groeipotentieel.
   Focus hier op stretch-challenges."
```

---

## Contract Referentie

| Component | Pad | Functie |
|-----------|-----|---------|
| `GrowthReportGenerator` | `devhub_core/agents/growth_report_generator.py` | Genereert GrowthReport |
| `ResearchAdvisor` | `devhub_core/agents/research_advisor.py` | ZPD-gefilterde leeslijst |
| `GrowthReport` | `devhub_core/contracts/growth_contracts.py` | Frozen dataclass output |
| `SkillRadarProfile` | `devhub_core/contracts/growth_contracts.py` | Developer skill snapshot |
| `DevelopmentChallenge` | `devhub_core/contracts/growth_contracts.py` | DP challenge contract |
| `LearningRecommendation` | `devhub_core/contracts/growth_contracts.py` | Leesaanbeveling contract |

---

## ZPD-filtering logica

| Resource-level t.o.v. developer | ZPD-alignment | Prioriteit |
|----------------------------------|---------------|-----------|
| Developer-level + 1 | stretch | URGENT |
| Developer-level | exact | IMPORTANT |
| Developer-level - 1 of lager | review | NICE_TO_HAVE |
| Developer-level + 2 of hoger | — | **Niet aanbevolen** |

---

## Regels

- Growth Report is **altijd informatief** — Niels beslist wat hij ermee doet (Art. 1)
- Leeslijsten zijn aanbevelingen, geen verplichtingen
- Skill-niveaus worden onderbouwd met evidence, niet aangenomen
- Bij onzekerheid over niveau: vraag Niels, niet raden
- Rapport-inhoud respecteert kennisgradering (Art. 5): GOLD/SILVER/BRONZE/SPECULATIVE
