# devhub-sprint-prep — Node-Agnostische Sprint Voorbereiding Skill

**Versie:** 1.1.0
**Basis:** BORIS boris-sprint-prep v1.0 → gemigreerd naar DevHub
**Changelog:** v1.1.0 — FASE3_TRACKER integratie + § Fase-voortgang sectie in SPRINT_INPUT

## Trigger
Activeer bij:
- Handmatige aanroep vóór een sprintplanning
- Scheduled task (maandagochtend ~07:45)
- "sprint prep", "klaarmaak voor sprint", "wat moet ik weten voor sprint X"

## Doel
Synthetiseer alle beschikbare bronnen tot een beslissingsklare SPRINT_INPUT. Het voorbereidende detectivewerk is gedaan zodat de sprint zelf meteen productief is.

**Kernprincipe:** Claude Code hoeft bij sprint-start geen vragen te stellen. Alle context, open beslissingen, afhankelijkheden en relevante docs zijn al gesyntheseerd.

---

## Setup

```python
from devhub_core.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")
```

---

## Workflow

### Stap 1: Alle context in één call ophalen

```python
ctx = adapter.get_sprint_prep_context()
```

Dit levert een dict met:
| Key | Bron |
|-----|------|
| `health_status` | HEALTH_STATUS.md (compact, <25 regels) |
| `health_report_latest` | Meest recente health-report-*.md |
| `developer_profile` | DeveloperProfile (fase, signaal, streak, blockers) |
| `claude_md` | CLAUDE.md (actieve sprint, constraints) |
| `overdracht` | OVERDRACHT.md (recente beslissingen) |
| `decisions` | decisions.md (open/gesloten besluiten) |
| `inbox` | Inbox items (SPRINT_INTAKE_*, IDEA_*) |
| `sprint_docs` | Actieve sprint-documenten |
| `adr_files` | Beschikbare ADR bestanden |

### Stap 1b: DevHub planningssysteem scannen

Naast project-specifieke context, scan de DevHub planning directories:

```
docs/planning/inbox/              — Nieuwe items (SPRINT_INTAKE_*, IDEA_*, RESEARCH_*)
docs/planning/backlog/            — Shaped items klaar voor sprint
docs/planning/sprints/            — Afgeronde en actieve sprints
docs/planning/parked/             — Buiten huidige fase, niet vergeten
docs/planning/TRIAGE_INDEX.md     — Overzicht van alle items + tellingen
docs/planning/ROADMAP.md          — Strategische roadmap + fase-positie
docs/planning/SPRINT_TRACKER.md    — Golfplanning, velocity, cycle time, capaciteit
```

**Acties:**
1. Lees `docs/planning/TRIAGE_INDEX.md` voor actuele tellingen en fase-positie
2. Lees `docs/planning/SPRINT_TRACKER.md` voor golfplanning-status, velocity en capaciteit
3. Scan `docs/planning/backlog/` voor items die klaar zijn voor de komende sprint
4. Scan `docs/planning/inbox/` voor nieuwe items die nog getriaged moeten worden
5. Controleer of backlog-items voldoen aan de DoR voordat ze in de sprint opgenomen worden
6. Vermeld het aantal items per directory in de SPRINT_INPUT output

### Stap 2: Systeem-status analyseren

```python
health_status = ctx["health_status"]
health_report = ctx["health_report_latest"]
```

**Vraag:** zijn er P1/P2 health issues die de sprint blokkeren of verplichte items opleveren?

| Status | Implicatie |
|--------|-----------|
| ✅ Gezond | Sprint kan starten zonder health-gerelateerde items |
| ⚠️ Actie nodig | P2-items toevoegen als sprint-items |
| ❌ Kritiek | P1 moet EERST opgelost — sprint kan niet starten |

### Stap 3: Developer-signaal interpreteren

```python
profile = ctx["developer_profile"]
phase = profile["phase"]    # ORIËNTEREN / BOUWEN / BEHEERSEN
signal = profile["signal"]  # GROEN / AANDACHT / STAGNATIE
```

| Signaal | Sprint-tempo advies |
|---------|-------------------|
| GROEN + BOUWEN | Hoog tempo, volledige scope |
| GROEN + BEHEERSEN | Normaal, focus op architectuurkeuzes |
| AANDACHT | Conservatief, blocker eerst opruimen |
| STAGNATIE | Conservatief, meer uitlegmomenten inbouwen |

### Stap 4: Open beslissingen scannen

```python
decisions = ctx["decisions"]
```

Zoek naar beslissingen met status OPEN of INBOX. Controleer:
1. Blokkeert dit de komende sprint?
2. Wie is eigenaar?
3. Hoe lang staat dit al open?

### Stap 5: Relevante ADRs laden

```python
adr_files = ctx["adr_files"]

# Lees alleen relevante ADRs
for adr_name in relevant_adrs:
    content = adapter.read_adr(adr_name)
```

Scan ADRs die gerefereerd worden in:
- De SPRINT_INTAKE van de komende sprint
- Health report bevindingen
- Open decisions

### Stap 6: SPRINT_INPUT.md genereren

Schrijf naar de node's `docs/planning/SPRINT_INPUT.md`:

```markdown
# Sprint Input — [SPRINT NAAM] — [DATUM]
_Gegenereerd door: devhub-sprint-prep | Node: [node_id]_

---

## § Systeem-status
**Health overall:** [✅ / ⚠️ / ❌] — [1 zin kernbevinding]
**Open P1/P2 issues:** [lijst of "geen"]
**Sprint-impact:** [blokkeert / vereist item / geen impact]

---

## § Developer-signaal
**O-B-B fase:** [ORIËNTEREN / BOUWEN / BEHEERSEN]
**Coaching-signaal:** [GROEN / AANDACHT / STAGNATIE]
**Actieve blocker:** [beschrijving of "geen"]
**Sprint-tempo advies:** [Hoog / Normaal / Conservatief] — [motivatie]

---

## § Open beslissingen die blokkeren
[Genummerd, alleen echte blockers]

Of: _Geen open beslissingen die deze sprint blokkeren._

---

## § Fase-voortgang (uit FASE3_TRACKER)
**Huidige golf:** [Golf N — naam]
**Test baseline:** [N tests]
**Afgeronde sprints deze golf:** [N/M]
**Actieve sprints:** [lijst]
**Volgende kandidaten:** [lijst met status 📋 KLAAR]
**Capaciteit:** [N actieve feature-sprints / max 2-3]
**Velocity (gem.):** [+N tests/sprint]

---

## § Voorgestelde sprint-items
| Prioriteit | Item | Bron | Grootte |
|-----------|------|------|---------|
| P1 Kritiek | [beschrijving] | health-report | Klein/Middel/Groot |
| P2 Aandacht | [beschrijving] | decisions | Klein/Middel/Groot |
| Scope | [beschrijving] | SPRINT_INTAKE | Klein/Middel/Groot |

---

## § Pre-sprint leeslijst
| # | Bestand | Waarom | Leestijd |
|---|---------|--------|----------|
| 1 | HEALTH_STATUS.md | Systeemcontext | 1 min |
| 2 | [SPRINT_INTAKE] | Scope en DoR | 5 min |
| 3 | [OVERDRACHT] | Open werk | 3 min |
| N | [ADR-XXX] | Relevant voor [component] | 2 min |

**Totale leestijd:** ~[X] minuten

---

## § Wat de developer moet beslissen vóór sprint-start
[Alleen echte go/no-go beslissingen]

Of: _Geen open beslissingen — sprint kan direct starten._
```

---

## Regels

- **READ-ONLY** — schrijft alleen SPRINT_INPUT.md
- **Synthese boven opsomming** — trek conclusies, niet alles herhalen
- **Leeslijst is verplicht** — altijd invullen
- **Prioriteit:** health P1/P2 > open blockers > sprint-scope > nice-to-have
- **Mentor-signaal telt mee:** STAGNATIE of open blocker = conservatief plannen
- **Ontbrekende bronnen expliciet vermelden** — niet stilzwijgend overslaan

## Contract Referentie

| Methode | Doel |
|---------|------|
| `adapter.get_sprint_prep_context()` | Alle context in één call |
| `adapter.read_health_status()` | Compact health overzicht |
| `adapter.read_decisions()` | Open/gesloten besluiten |
| `adapter.list_adr_files()` | Beschikbare ADRs |
| `adapter.read_adr(name)` | Specifiek ADR lezen |
| `adapter.list_health_reports()` | Health rapporten (nieuwste eerst) |
| `adapter.get_developer_profile()` | DeveloperProfile met coaching signaal |
