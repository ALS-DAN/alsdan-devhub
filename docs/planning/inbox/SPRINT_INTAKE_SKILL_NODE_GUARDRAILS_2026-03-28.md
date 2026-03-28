---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: CHORE
fase: 3
---

# Sprint: Skill Node-Guardrails

## Probleem

Drie DevHub-skills (sprint-prep, health, review) claimen "node-agnostisch" te zijn maar hardcoden `boris-buurts` in hun Setup-blok en missen een node-keuze stap. Dit leidt tot:
1. Onnodig laden van BORIS-context bij DevHub-taken (tokens/tijd verspild)
2. Geen werkend DevHub-pad — skills werken alleen voor BORIS

## Oplossing

Dezelfde guardrails toepassen als in Sprint 36 voor devhub-sprint:
- **Stap -1: Node bepalen** — vraag of detecteer de node vóór context laden
- **DevHub-pad** — directe file reads zonder adapter
- **BORIS-pad** — adapter calls (bestaande workflow)
- **Regels-sectie** uitbreiden met node-keuze, mode-bewaking, memory-toestemming

## Scope per skill

### devhub-sprint-prep
- Setup: `boris-buurts` → generiek voorbeeld
- Stap 1: adapter.get_sprint_prep_context() is BORIS-only → splits in DevHub-pad (directe reads van planning dirs) en BORIS-pad
- Stap 1b bestaat al voor DevHub-planning maar wordt pas NA de adapter-call aangeroepen

### devhub-health
- Setup: `boris-buurts` → generiek voorbeeld
- Stap 0: laadt direct BORIS-context → node-keuze stap toevoegen
- DevHub-pad: run tests/lint lokaal, skip adapter-specifieke checks
- BORIS-pad: bestaande workflow via adapter

### devhub-review
- Setup: `boris-buurts` → generiek voorbeeld
- Stap 1: adapter.get_review_context() is BORIS-only → DevHub-pad: directe git diff + QA Agent
- Regels aanvullen

## Grenzen (wat NIET)
- Geen nieuwe functionaliteit
- Geen Python-code wijzigingen
- Alleen skill-documenten (.md)

## Appetite
S — 1 sessie, 3 bestanden
