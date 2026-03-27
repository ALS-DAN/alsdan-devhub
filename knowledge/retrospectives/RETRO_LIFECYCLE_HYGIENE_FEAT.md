---
title: Retrospective — Lifecycle Hygiene FEAT (Sprint 25-27)
domain: retrospectives
grade: SILVER
date: 2026-03-27
author: devhub-sprint
sprint: Lifecycle Hygiene (SPIKE + FEAT + Afronding)
---

# Retrospective — Lifecycle Hygiene FEAT

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprints | 25 (SPIKE), 26 (FEAT), 27 (Afronding) |
| Duur | 2026-03-27 → 2026-03-27 |
| Tests start | 1156 |
| Tests eind | 1156 |
| Tests delta | +0 (docs/skills-only sprint) |
| Deliverables | 5/5 SPIKE-voorstellen geimplementeerd + 6 residuele fixes |
| QA verdict | PASS (geen code, alleen markdown) |

## Wat ging goed

- **SPIKE-first aanpak werkte**: analyse vooraf (Sprint 25) maakte implementatie (Sprint 26) snel en gericht
- **Status-marker archivering**: eenvoudiger dan file-verplaatsing, consistent met bestaand patroon
- **SPRINT_TRACKER als SSoT**: elimineert 4 sync-punten, skills hoeven nooit meer bijgewerkt bij fase-overgang
- **Conditionele node-loading**: DevHub-sprints laden nu geen overbodige BORIS-context meer

## Wat kan beter

- **Sprint 26 miste 6 FASE3_TRACKER referenties** in actieve skills/agents — grep-verificatie had onderdeel moeten zijn van de implementatie-sprint, niet een aparte afronding
- **SPRINT_TRACKER header was inconsistent** met golf-tabel (actief vs DONE) — automatische consistentie-check zou dit kunnen voorkomen
- **Sprint-close flow mist verificatie-stap**: de flow heeft geen expliciete "grep voor oude referenties" check

## Actiepunten

| # | Actie | Prioriteit | Status |
|---|-------|-----------|--------|
| 1 | Voeg grep-verificatie toe aan sprint-close flow (6E bis) | P3 | VOORSTEL — niet urgent, handmatig voldoende |
| 2 | Overweeg linting voor document-referenties (FASE3_TRACKER → SPRINT_TRACKER type fouten) | P4 | IDEE — pas bij voldoende volume |

## Kenniswinst

- **Provider Pattern / SPI**: nieuw inbox-item (IDEA_PROVIDER_PATTERN) ontstond als bijvangst — de adapter-scheiding werd zichtbaar door de node-conditie in sprint-start
- **Document-lifecycle**: 4 documenten → 2 (SPRINT_TRACKER + TRIAGE_INDEX) + 1 archief (ROADMAP) is een gezonde reductie
- **Intake-archivering operationeel**: 9 intakes succesvol gearchiveerd via status-marker, sprint-prep filtert correct
