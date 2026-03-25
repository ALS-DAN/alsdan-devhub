# Sprint Intake: Planning Opschoning

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 3
prioriteit: P1
sprint_type: CHORE
cynefin: obvious
impact_zone: GREEN (alleen planning-documenten, geen code-impact)
bron:
  - docs/planning/sprints/TRIAGE_UPDATE_FASE3_OVERGANG_2026-03-25.md
  - docs/planning/backlog/SPRINT_INTAKE_PLANNING_GOVERNANCE_2026-03-24.md
---

## Doel

Maak het planningssysteem schoon en compleet voor Fase 3. Verplaats afgeronde en geparkeerde items naar de juiste mappen, rond de 5 openstaande governance-deliverables af, en verifieer dat de administratie klopt.

## Probleemstelling

De Planning Governance intake (5/10 deliverables af) is nooit afgerond. De Triage Update beschreef 9 file moves, maar verificatie toont dat 7 daarvan al zijn uitgevoerd. Er resteren concrete opruimtaken plus skill/agent updates die nodig zijn zodat de planningspipeline betrouwbaar is voor Fase 3.

## Huidige staat (geverifieerd 2026-03-25)

| Map | Aantal | Inhoud |
|-----|--------|--------|
| inbox/ | 8 | 5 echte Fase 3 kandidaten + Quick Fixes + Planning Opschoning + Ops Validatie (DONE) |
| backlog/ | 2 | Code Check Architectuur (Fase 1), Planning Governance (5/10 af) |
| sprints/ | 13 | Afgeronde sprints incl. al verplaatste items |
| parked/ | 14 | Geparkeerde IDEAs en research |

**Al uitgevoerd** (7/9 moves uit Triage Update):
- [x] Red Team Agent, N8N Docker Fix → sprints/
- [x] N8N Health/Governance/PR Quality/UV Workspace → sprints/
- [x] IDEA_DEVHUB_ROADMAP, MONOREPO_RESEARCH → parked/

## Deliverables

### Fase 1: Resterende bestandsverplaatsingen (2 moves)

- [ ] `inbox/SPRINT_INTAKE_OPERATIONELE_VALIDATIE_2026-03-25.md` → `sprints/` (status: DONE, hoort niet meer in inbox)
- [ ] `backlog/SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR_2026-03-23.md` → `sprints/` (Fase 1, afgerond)

### Fase 2: Planning Governance afronding (3 resterende items)

Uit SPRINT_INTAKE_PLANNING_GOVERNANCE_2026-03-24.md — 5/10 deliverables af, duplicaat-moves al gedaan:
- [ ] `sprint-prep` skill updaten: scant nu ook `backlog/` in plaats van alleen `inbox/`
- [ ] `planner` agent updaten: kent backlog-promotie als taak
- [ ] `DEVHUB_BRIEF.md` updaten met nieuwe planningsstructuur + correcte tellingen

### Fase 3: Administratieve updates

- [ ] `TRIAGE_INDEX.md` bijwerken zodat het de werkelijke staat na opschoning reflecteert
- [ ] `ROADMAP.md` bijwerken: Fase 3 tracks (B, C) als actief markeren
- [ ] Planning Governance intake in `backlog/` markeren als DONE (of verplaatsen naar `sprints/`)

### Fase 4: Verificatie

- [ ] 394+ tests nog steeds groen
- [ ] Inbox bevat alleen echte Fase 3 kandidaten (verwacht: 5-6 items)
- [ ] Backlog is leeg of bevat alleen actief geprioriteerde items
- [ ] Parked bevat alle bewust geparkeerde items (verwacht: ~14 items)
- [ ] DEVHUB_BRIEF.md tellingen kloppen met werkelijke bestandstellingen

## Afhankelijkheden

- Geblokkeerd door: geen
- BORIS impact: nee
- Kan parallel met Quick Fixes sprint lopen (geen overlap)

## Fase-context

Fase 3 (overgang). Dit is housekeeping die nodig is zodat de planningspipeline betrouwbaar is wanneer Track B en C starten. Zonder dit is onduidelijk wat de werkelijke scope van Fase 3 is.

## Open vragen voor Claude Code

1. Moet `sprint-prep` skill de `TRIAGE_INDEX.md` automatisch bijwerken bij elke run?
2. Moet de `planner` agent een "triage-modus" krijgen als apart commando?
3. Willen we een pre-commit hook die waarschuwt als `inbox/` >15 items bevat?

## DEV_CONSTITUTION impact

- Art. 4 (Traceerbaarheid): TRIAGE_INDEX.md borgt zichtbaarheid van alle items
- Art. 7 (Impact-zonering): GREEN — geen code-impact buiten skill/agent docs

## Appetite

**Extra Small (XS)** — maximaal 1 uur. Scope is kleiner dan verwacht: 7/9 file moves al gedaan, 2/5 governance-items al gedaan. Restwerk is 2 moves + 3 skill/agent/doc updates + admin + verificatie.
