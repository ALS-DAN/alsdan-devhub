# ADR-003: Planning Single Source of Truth

| Veld | Waarde |
|------|--------|
| Status | Accepted |
| Datum | 2026-03-28 |
| Context | Sprint 25-27: Lifecycle Hygiene (SPIKE + FEAT) |
| Impact-zone | YELLOW (planning-architectuur, alle skills geraakt) |

## Context

Fase 3 groeide organisch van 5 naar 22 sprints. Daarbij ontstonden meerdere overlappende planning-documenten die elk een deel van de waarheid bevatten:

- **FASE3_TRACKER.md** — golfplanning, hill charts, sprint-status
- **DEVHUB_BRIEF.md** — actieve sprint, tellingen, context
- **TRIAGE_INDEX.md** — intake/backlog status
- **ROADMAP.md** — strategische richting

Dit leidde tot 4 sync-punten: bij elke sprint-update moesten meerdere bestanden handmatig bijgewerkt worden. Skills laadden verschillende bestanden voor dezelfde informatie. Bij fase-overgang moest een compleet nieuw tracker-bestand aangemaakt worden.

De Lifecycle Hygiene SPIKE (Sprint 25) identificeerde dit als structureel probleem. De FEAT (Sprint 26) loste het op.

## Beslissing

**SPRINT_TRACKER.md is het enige actieve tracking-document voor alle fasen.**

### Regels

1. **Geen fase-specifieke trackers.** Er worden geen FASE4_TRACKER, FASE5_TRACKER etc. aangemaakt. Bij fase-overgang: nieuw golf-blok toevoegen aan SPRINT_TRACKER, vorige fase inklappen tot samenvatting.

2. **Skills lezen alleen SPRINT_TRACKER.** Geen enkele skill of agent leest een fase-specifiek tracker-bestand.

3. **FASE3_TRACKER blijft als archief.** Het bestand wordt niet verwijderd (bevat waardevolle historische data) maar is read-only en wordt niet meer bijgewerkt.

4. **Velocity en cycle time zijn doorlopend.** Metrics worden niet per fase gereset maar lopen door over alle fasen heen.

## Consequenties

### Positief

- Elimineert 4 sync-punten → 1 update-punt per sprint
- Skills hoeven niet bijgewerkt te worden bij fase-overgang
- Eén plek voor alle planning-informatie
- Velocity-data is vergelijkbaar over fasen heen

### Negatief

- SPRINT_TRACKER.md groeit over tijd → secties inklappen bij fase-afronding
- Historisch detail per fase is beperkt tot samenvatting (detail in archief-trackers)

## Bronnen

| Document | Relevantie |
|----------|------------|
| `knowledge/retrospectives/RETRO_LIFECYCLE_HYGIENE_FEAT.md` | Validatie: "SPRINT_TRACKER als SSoT: elimineert 4 sync-punten" |
| `knowledge/retrospectives/RETRO_FASE3_KNOWLEDGE_MEMORY.md` | Bevestiging op fase-niveau |
| `knowledge/retrospectives/RETRO_PLANNING_TRACKING_SYSTEEM.md` | Oorspronkelijke probleemidentificatie |
| `docs/planning/inbox/SPRINT_INTAKE_SPIKE_SPRINT_LIFECYCLE_HYGIENE_2026-03-27.md` | Analyse van 4 structurele problemen |
