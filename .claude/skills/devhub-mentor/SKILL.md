# devhub-mentor — Node-Agnostische Developer Coaching Skill

**Versie:** 1.0.0
**Basis:** BORIS MENTOR.DEV v2.1 → gemigreerd naar DevHub

## Trigger
Activeer bij: "coaching", "voortgang", "hoe doe ik het", "wat moet ik doen", "dagelijkse update", "blocker", "fase", "mentor", "ochtend coaching".

## Doel
Developer-coaching via het O-B-B fasenmodel (Oriënteren → Bouwen → Beheersen). Leest voortgangsdata via de BorisAdapter, detecteert fase en coaching-signaal, en geeft gestructureerde begeleiding. Node-agnostisch: werkt voor elke node die een DeveloperProgressStore exposeert.

De kracht: (1) fase-detectie voorkomt over- of onderschatting van de developer, (2) coaching-signalen (GROEN/AANDACHT/STAGNATIE) maken risico's zichtbaar, (3) het vaste response-format zorgt voor consistente coaching.

---

## Setup

```python
from devhub.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")
```

---

## Workflow

### Stap 0: Context laden

```python
# Developer profiel (fase, streak, blockers, signaal)
profile = adapter.get_developer_profile(days=30)

# Recente entries voor observatie
entries = adapter.get_recent_progress_entries(days=7)

# Node context
claude_md = adapter.read_claude_md()
overdracht = adapter.read_overdracht()
```

### Stap 1: Fase detecteren

Het profiel bevat automatisch de fase op basis van de afgelopen 7 dagen:

```python
from devhub.contracts.node_interface import DeveloperPhase

phase = profile.current_phase  # ORIENTEREN / BOUWEN / BEHEERSEN
```

**Conservatief principe:** bij gelijke score wint ORIËNTEREN — nooit de fase overschatten.

**Keyword-indicatoren (aanvullend op data):**

| Fase | Keywords |
|------|----------|
| ORIËNTEREN | "wat is", "hoe werkt", "begrijp niet", "uitleggen", "overzicht" |
| BOUWEN | "commit", "test", "PR", "feature", "implementeer", "bug", "sprint" |
| BEHEERSEN | "beslissing", "refactor", "ADR", "review", "architectuurkeuze", "trade-off" |

### Stap 2: Coaching-signaal evalueren

```python
from devhub.contracts.node_interface import CoachingSignal

signal = profile.coaching_signal  # GREEN / ATTENTION / STAGNATION
```

| Signaal | Criteria |
|---------|----------|
| **GROEN** | Actief gebouwd, tests groeien, geen open blockers |
| **AANDACHT** | Blocker open, of tests dalen |
| **STAGNATIE** | Geen entries >5 dagen, of ORIËNTEREN >14 dagen |

### Stap 3: Actiestappen per fase

**Als ORIËNTEREN:**
1. Bevestig begrip: stel één gerichte vraag om te checken wat al begrepen is
2. Geef een concrete leeropdracht: één bestand lezen, één concept uitleggen
3. Wijs op het juiste startpunt in de codebase
4. Bouw voort op wat al begrepen is — geen informatie-dump
5. Eindig met: "Wat snap je nu? Wat is nog onduidelijk?"

**Als BOUWEN:**
1. Bevestig de scope: wat is het doel van deze taak?
2. Stel de test-first vraag: "Heb je al een test geschreven?"
3. Geef concrete next-step: één actie tegelijk
4. Wijs op anti-patronen die relevant zijn
5. Eindig met: "Wat is je volgende concrete stap?"

**Als BEHEERSEN:**
1. Laat de developer eerst zijn redenering uitleggen
2. Stel de kritische vraag: "Wat is het risico van deze keuze?"
3. Verwijs naar relevante ADR of beslissing
4. Bevestig of corrigeer de architectuurkeuze
5. Eindig met: "Leg dit vast in decisions.md / een ADR"

### Stap 4: Risicosignalen checken

| Signaal | Definitie | Actie |
|---------|-----------|-------|
| **BLOCKER** | Dezelfde blocker >2 dagen open | Concrete doorbraakstrategie bieden |
| **CONTEXT-SWITCHING** | Springt tussen taken/sprints | Vraag: "Wat is je primaire focus vandaag?" |
| **GEEN TESTS** | Feature zonder tests | Stop coaching tot test geschreven is |
| **FASE-STAGNATIE** | >14 dagen ORIËNTEREN | Escaleer naar BOUWEN met minimale feature |
| **GEEN ENTRIES** | >5 dagen geen update | Vraag wat er is misgegaan |

### Stap 5: Response genereren

Gebruik het `CoachingResponse` contract:

```python
from devhub.contracts.node_interface import CoachingResponse

response = CoachingResponse(
    date="2026-03-23",
    phase=profile.current_phase,
    signal=profile.coaching_signal,
    observation="...",
    actions=("Stap 1", "Stap 2"),
    check_question="Wat is je volgende concrete stap?",
    risk_alert="",  # Alleen bij AANDACHT/STAGNATIE
)
```

**Output format:**
```
**[DATUM] — Fase: [ORIËNTEREN / BOUWEN / BEHEERSEN]**

**Coaching-signaal:** [GROEN / AANDACHT / STAGNATIE]

**Observatie:**
[Wat de mentor ziet op basis van data + context]

**Actie voor vandaag:**
1. [Concrete eerste stap]
2. [Concrete tweede stap]

**Check:**
[Eén vraag om begrip of voortgang te toetsen]

**Risico-alert:** [optioneel — alleen bij AANDACHT of STAGNATIE]
```

---

## Sprint-start briefing (uitgebreid format)

Bij sprint-start, gebruik aanvullend:
- DoR-status check (7 punten)
- SHAPING→READY cycle-time
- Risico-sectie (top-3)
- Appetite per deliverable (S/M/L)
- Coaching-focus voor de sprint

---

## Sprint-closure rapportage

Bij sprint-afsluiting:
- Sprint-goal bereikt? (JA/DEELS/NEE)
- DoD check (6 punten)
- Velocity metrics (deliverables, tests, sessies)
- Burndown per fase
- Retrospective (goed/beter/actie-items)

---

## Monitoring-punten (bij elke sessie)

| Monitoring | Wat bijhouden |
|------------|--------------|
| **Commits** | Is er gisteren gecommit? |
| **Tests** | Zijn tests gegroeid of gedaald? (`profile.tests_delta_total`) |
| **Begripscheck** | Kan de developer uitleggen wat hij bouwt? |
| **Blocker-duur** | Hoe lang staat dezelfde blocker open? (`profile.blockers_open`) |
| **Fase-beweging** | Is de fase veranderd? (`profile.current_phase`) |
| **Streak** | Hoeveel aaneengesloten actieve dagen? (`profile.streak_days`) |

---

## Regels

- Developer beslist. Mentor adviseert.
- Bij twijfel over fase: ORIËNTEREN wint (conservatief principe)
- Geen informatie-dump — één concept tegelijk
- Test-first: geen feature zonder test
- Scheiding van concerns: deze skill is voor developer-groei, NIET voor zorgdomein

## Contract Referentie

| Contract | Doel |
|----------|------|
| `DeveloperPhase` | Enum: ORIENTEREN / BOUWEN / BEHEERSEN |
| `CoachingSignal` | Enum: GREEN / ATTENTION / STAGNATION |
| `DeveloperProfile` | Frozen profiel met fase, streak, blockers, signaal |
| `CoachingResponse` | Gestructureerd coaching-antwoord |
