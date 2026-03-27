# Sprint Intake: Planning & Tracking Systeem

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
prioriteit: P2
sprint_type: FEAT
cynefin: complicated (bekende patronen uit Lean/Agile/Shape Up, vereist engineering-integratie)
impact_zone: YELLOW (wijzigt sprint-prep skill, planner agent, en planning-documenten)
---

## Doel

Geef DevHub een geïntegreerd tracking-systeem dat het Fase 3 totaalbeeld borgt: golfplanning, Hill Chart-voortgang, velocity tracking, cycle time, en capaciteitsplanning — allemaal als docs-in-git, beheerd door bestaande skills en agents.

## Probleemstelling

DevHub heeft een volwassen item-lifecycle (INBOX → BACKLOG → SPRINT → RETRO) en goede governance-integratie. Maar nu Fase 3 vier parallelle tracks heeft (B, C, Mentor, Governance) met elk meerdere sprints, ontbreekt er:

1. **Geen totaalbeeld** — ROADMAP.md beschrijft fases op hoog niveau maar niet het golfpatroon van parallelle sprints.
2. **Geen voortgangsvisualisatie** — Er is geen mechanisme om mid-sprint te zien waar werk staat (uphill vs. downhill).
3. **Geen velocity/forecasting** — Test-baselines per sprint bestaan, maar geen sprint-velocity, cycle time, of schattingsnauwkeurigheid. Zonder dit kun je niet voorspellen wanneer Track B+C klaar is.
4. **Geen capaciteitsplanning** — Bij parallelle tracks moet je weten hoeveel tegelijk realistisch is (avonduren/weekenden context).

### Waarom nu

Met 4 parallelle tracks en ~14 sprints in Fase 3 is handmatig bijhouden niet schaalbaar. De planning-skills en planner-agent zijn het juiste integratiepunt — zij beheren al de inbox/backlog/sprint pipeline.

## Deliverables

### Sprint 1: FASE3_TRACKER + Skill/Agent integratie — 🎯 DIRECT UITVOERBAAR

#### D1: FASE3_TRACKER.md operationeel maken

Een initieel FASE3_TRACKER.md is al aangemaakt door Cowork (zie `docs/planning/inbox/FASE3_TRACKER.md`). Claude Code moet dit document:
- [ ] Verplaatsen naar `docs/planning/FASE3_TRACKER.md` (naast ROADMAP.md en TRIAGE_INDEX.md)
- [ ] Valideren tegen werkelijke bestandssituatie (inbox/sprints/parked tellingen)
- [ ] Integreren in het bestaande planning-ecosysteem

#### D2: sprint-prep skill uitbreiden

- [ ] `devhub-sprint-prep` scant nu ook `FASE3_TRACKER.md` bij sprint-voorbereiding
- [ ] Bij sprint-start: update Hill Chart positie van de betreffende sprint (░ → ▓)
- [ ] Bij sprint-closure: update status (🔄 → ✅), registreer test-delta, en bereken velocity

#### D3: planner agent uitbreiden

- [ ] `planner` agent kent de golfplanning en kan adviseren welke sprint(s) volgende zijn
- [ ] Bij sprint-closure: planner updatet automatisch de FASE3_TRACKER
- [ ] Planner detecteert stilstaande sprints (>7 dagen geen beweging) als blokkade-signaal

#### D4: Velocity tracking bootstrappen

- [ ] Historische sprints (6 afgerond) invullen in velocity log met werkelijke duur en test-delta
- [ ] Sprint-grootte normaliseren: XS=1, S=2, M=3, L=5 punten (Fibonacci-achtig, pragmatisch)
- [ ] Gemiddelde velocity berekenen als referentie voor toekomstige sprints
- [ ] Schattingsnauwkeurigheid bijhouden: gepland vs. werkelijk per sprint

#### D5: Cycle time tracking

- [ ] Automatisch cycle time berekenen: inbox-datum → sprint-start → sprint-klaar
- [ ] SLA-doelen definiëren (inbox → start: <7 dagen, sprint-duur: afhankelijk van grootte)
- [ ] Afwijkingen signaleren in planner-output

#### D6: Capaciteitsplanning

- [ ] Capaciteitsadvies in planner-output: max 2-3 feature-sprints tegelijk (avonduren/weekenden context)
- [ ] Bij sprint-start: check of er capaciteit is (niet meer dan 2 actieve feature-sprints)
- [ ] Waarschuwing bij overbelasting

### Sprint 2: Forecasting + DEVHUB_BRIEF integratie (na 3+ sprints data)

- [ ] Na 3 Fase 3 sprints: velocity-based forecast berekenen voor resterende tracks
- [ ] Forecast opnemen in DEVHUB_BRIEF sessie-opening
- [ ] Trendanalyse: groeit/daalt velocity, groeit/daalt test-delta per sprint
- [ ] Estimation accuracy tracking: hoe vaak kloppen de appetite-schattingen

## Grenzen (wat we NIET doen)

- Geen extern tooling (Jira, Linear, etc.) — alles blijft docs-in-git
- Geen burndown charts met dagelijkse granulariteit — te veel overhead voor solo-dev
- Geen story points op deliverable-niveau — alleen op sprint-niveau (XS/S/M/L → punten)
- Geen automatische Hill Chart updates mid-sprint — dat doet de developer (Niels) handmatig of bij coaching-sessie
- Sprint 2 (forecasting) pas starten na minimaal 3 Fase 3 sprints met velocity-data

## Appetite

**Sprint 1: Small (S)** — de FASE3_TRACKER bestaat al als startdocument. Hoofdwerk zit in skill/agent integratie (sprint-prep, planner) en velocity bootstrapping. ~1 sprint.

**Sprint 2: Extra Small (XS)** — forecasting is een toevoeging op bestaande velocity-data. Pas uitvoerbaar na 3+ sprints. ~0.5 sprint.

## Afhankelijkheden

- **Geblokkeerd door:** Planning Opschoning (FASE3_TRACKER verwijst naar opgeschoonde structuur)
- **BORIS impact:** Nee
- **Parallel met:** Track B/C Sprint 1 (geen code-overlap; tracker raakt planning-docs, niet packages)

## Technische richting

(Claude Code mag afwijken)

- FASE3_TRACKER.md is een Markdown-bestand met vaste secties (golfplanning, velocity, cycle time, risico's)
- sprint-prep skill leest en schrijft naar FASE3_TRACKER.md (bestaand patroon: skill leest planning-docs)
- planner agent gebruikt FASE3_TRACKER als input voor sprint-advies
- Velocity-data als tabel in Markdown (geen database nodig bij 6-20 sprints)
- Hill Chart als ASCII-art (geen rendering-dependency)

## Open vragen voor Claude Code

1. Moet FASE3_TRACKER.md automatisch gegenereerd worden bij fase-overgang, of is het een eenmalig document per fase?
2. Moet de planner agent de Hill Chart positie kunnen updaten, of is dat alleen handmatig/via sprint-prep?
3. Is velocity-normalisatie (XS=1, S=2, M=3, L=5) de juiste schaal, of is een andere verdeling beter?
4. Moet sprint-prep bij elke run de FASE3_TRACKER volledig herberekenen, of alleen delta's toevoegen?

## DEV_CONSTITUTION impact

- **Art. 4** (Traceerbaarheid): FASE3_TRACKER versterkt traceerbaarheid door alle sprints in één overzicht te tonen
- **Art. 7** (Impact-zonering): YELLOW — wijzigt sprint-prep skill en planner agent (bestaande componenten)

## SOTA-onderbouwing

| Concept | Bron | Kennisgradering | Toepassing |
|---------|------|----------------|------------|
| Hill Charts | Shape Up (Basecamp, 2019) | SILVER | Visuele voortgang per sprint: uphill (onzekerheid) vs. downhill (uitvoering) |
| Velocity tracking | Agile/Scrum body of knowledge | GOLD | Sprint-grootte meten en voorspellen; decennia validatie |
| Cycle time | Lean/Kanban (Taiichi Ohno, 1988; Anderson, 2010) | GOLD | Doorlooptijd item-lifecycle; SLA-doelen; bottleneck-detectie |
| Estimation accuracy | "Software Estimation" (McConnell, 2006) | GOLD | Gepland vs. werkelijk vergelijken; Cone of Uncertainty voor toekomstige schattingen |
| Roadmap-as-Code | Emerging pattern (RaC, 2024+) | BRONZE | Roadmaps in git, versioned, reviewbaar; past bij docs-as-code filosofie |
| Workstream architecture | AWS Prescriptive Guidance | SILVER | Parallelle tracks met eigen backlogs en afhankelijkheden; formalisatie van wat DevHub informeel al doet |
| Capacity planning (solo) | "The Mythical Man-Month" (Brooks, 1975) + "Deep Work" (Newport, 2016) | GOLD/SILVER | Cognitieve limiet: max 2-3 parallelle complexe taken; focus-blokken > context-switching |
