# Fase 3 Tracker — Knowledge & Memory

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: ACTIEF
fase: 3
laatst_bijgewerkt: 2026-03-26
---

## Fase-positie

```
Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 2b ✅ → FASE 3 🔄
```

**Start:** 2026-03-25 (na Ops Validatie SPIKE)
**Baseline:** 395 tests | 6 agents | 8 skills | 3 packages (core active, storage+vectorstore stubs)
**Huidig:** 575 tests | 6 agents | 8 skills | 3 packages (core v0.2.0, storage v0.2.0, vectorstore v0.2.0)
**Fase 3 doel:** Knowledge & Memory lagen operationeel — vectorstore, storage, KWP DEV, mentor-systeem, governance-automatisering.
**Fase 4 gate:** NIET starten zonder expliciete Niels-goedkeuring (DEV_CONSTITUTION Art. 1).

---

## Golfplanning

### Golf 0: Opruiming ✅

| Sprint | Track | Size | Status | Hill |
|--------|-------|------|--------|------|
| Quick Fixes Ops Validatie | — | XS | ✅ DONE | ████████████ |
| Planning Opschoning | — | XS | ✅ DONE | ████████████ |

### Golf 1: Fundament (actief)

Max 2-3 tegelijk aanbevolen. Track B+C afgerond, rest beschikbaar.

| Sprint | Track | Size | Status | Hill | Codepad |
|--------|-------|------|--------|------|---------|
| Storage: Interface + LocalAdapter | B | S | ✅ DONE | ████████████ | `packages/devhub-storage/` |
| Vectorstore: Interface + ChromaDB | C | S | ✅ DONE | ████████████ | `packages/devhub-vectorstore/` |
| Planning & Tracking Systeem | — | S | 🔄 ACTIEF | ▓▓▓░░░░░░░░░ | `docs/planning/` + `skills/` + `agents/` |
| Mentor: Skill Radar + Contracts | M | S | 📋 KLAAR | ░░░░░░░░░░░░ | `contracts/growth_contracts.py` + `skills/` |
| Governance: QA Checks | G | S | 📋 KLAAR | ░░░░░░░░░░░░ | `agents/qa_agent.py` |

### Golf 2: Uitbouw

Elke sprint bouwt voort op Golf 1. Start pas na succesvolle afronding van de bijbehorende Sprint 1.

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: Google Drive adapter | B | S | 📋 KLAAR | ░░░░░░░░░░░░ | — |
| Vectorstore: Weaviate + Multi-tenancy | C | S | 📋 KLAAR | ░░░░░░░░░░░░ | — |
| Mentor: Challenge Engine + Scaffolding | M | S | ⏳ WACHT | ░░░░░░░░░░░░ | Mentor S1 |
| Governance: SecurityScanner | G | S | ⏳ WACHT | ░░░░░░░░░░░░ | Governance S1 |

### Golf 3: Verrijking

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: SharePoint adapter | B | S | ⏳ WACHT | ░░░░░░░░░░░░ | Track B S2 |
| Vectorstore: Embeddings + DevHub Weaviate | C | S | ⏳ WACHT | ░░░░░░░░░░░░ | Track C S2 |
| Mentor: Research Advisor + Dashboard | M | S | ⏳ WACHT | ░░░░░░░░░░░░ | Mentor S2 |

### Golf 4: Afsluiting & Integratie

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: Reconciliation engine | B | S | ⏳ WACHT | ░░░░░░░░░░░░ | Track B S3 |
| KWP DEV setup | — | S | ⏳ WACHT | ░░░░░░░░░░░░ | Track C S2+ |

---

## Kritiek pad

```
Track C (Vectorstore) is het langste pad naar het Fase 3 einddoel (KWP DEV):

Track C S1 → Track C S2 → Track C S3 → KWP DEV setup
  (1 sprint)    (1 sprint)    (0.5 sprint)   (0.5 sprint)
                                              = ~3 sprints totaal

Track B loopt parallel maar is niet blokkerend voor KWP DEV.
Mentor en Governance zijn complementair maar niet op het kritieke pad.
```

### Afhankelijkheidsdiagram

```
Golf 0                Golf 1              Golf 2              Golf 3              Golf 4
──────                ──────              ──────              ──────              ──────
Quick Fixes ✅
                   ┌─ Track B S1 ──────── Track B S2 ──────── Track B S3 ──────── Track B S4
Planning ──────────┤
Opschoning         ├─ Track C S1 ──────── Track C S2 ──────── Track C S3 ─┐
                   │                                                       ├──── KWP DEV
                   ├─ Mentor S1 ─────────  Mentor S2 ─────────  Mentor S3  │
                   │                                                       │
                   └─ Governance S1 ────── Governance S2                   │
                                                                           │
                                           Claude Optimalisatie ───────────┘
                                           (background research)
```

---

## Hill Chart Legenda

Geïnspireerd op Shape Up (Basecamp). Het Hill Chart model toont werk in twee fases:

```
            ╱╲
    Uphill ╱  ╲ Downhill
   (figuring  (executing
    it out)    with confidence)
  ╱            ╲
╱                ╲

░░░░░░░░░░░░  Niet gestart
▓░░░░░░░░░░░  Net gestart, veel onbekenden
▓▓▓░░░░░░░░░  Verkennend, aanpak aan het vormen
▓▓▓▓▓▓░░░░░░  Halverwege uphill, kernbeslissingen genomen
▓▓▓▓▓▓▓░░░░░  Top van de hill — alles duidelijk, klaar om uit te voeren
▓▓▓▓▓▓▓▓▓░░░  Downhill, implementatie loopt
▓▓▓▓▓▓▓▓▓▓▓░  Bijna klaar, laatste details
████████████  Afgerond
```

**Stilstaande dot = blokkade.** Als een sprint meerdere updates geen beweging toont, is er een probleem.

---

## Velocity Tracking

### Sprint Log

| # | Sprint | Gepland | Werkelijk | Tests Δ | Schatting-nauwkeurigheid |
|---|--------|---------|-----------|---------|--------------------------|
| 1 | FASE1_BOOTSTRAP | 1 sprint | 1 sprint | +81 | 100% |
| 2 | FASE2_SKILLS_GOVERNANCE | 1 sprint | 1 sprint | +40 | 100% |
| 3 | N8N_CICD_FOUNDATION | 1 sprint | 1 sprint | +31 | 100% |
| 4 | CODE_CHECK_ARCHITECTUUR | 1 sprint | 1 sprint | +24 | 100% |
| 5 | UV_WORKSPACE_TRANSITIE | 1 sprint | 1 sprint | +0* | 100% |
| 6 | OPERATIONELE_VALIDATIE | 1 sprint | 1 sprint (SPIKE) | +1 | 100% |
| 7 | Quick Fixes | XS (<1.5u) | XS (<1u) | +2 | 100% |
| 8 | Planning Opschoning | XS (<1u) | XS (<1u) | +0 | 100% |
| 9 | Storage Interface + LocalAdapter | S (1 sprint) | S (1 sprint) | +100 | 100% |
| 10 | Vectorstore Interface + ChromaDB | S (1 sprint) | S (1 sprint) | +78 | 100% |

*\* UV Workspace = herstructurering, geen nieuwe tests verwacht.*

### Afgeleide metrics

| Metric | Waarde | Toelichting |
|--------|--------|-------------|
| Sprints afgerond | 10 | Alle binnen geschatte tijd |
| Test baseline | 575 | Na Sprint 10 (Vectorstore S1) |
| Gemiddelde test-delta | +35.7 | Per sprint (excl. UV workspace + Planning Opschoning) |
| Schattingsnauwkeurigheid | 100% | 10/10 sprints binnen appetite |
| Gemiddelde sprint-grootte | S-M | XS=1, S=2, M=3 (Fibonacci-achtig) |

**Opmerking:** De schattingsnauwkeurigheid is opvallend hoog. Dit kan betekenen dat (a) de schattingen conservatief zijn, of (b) de scope goed afgebakend is. Na Fase 3 sprints herijken.

---

## Cycle Time

### Item Lifecycle Tracking

| Item | Inbox datum | Sprint start | Sprint klaar | Cycle time |
|------|-------------|--------------|--------------|------------|
| FASE1_BOOTSTRAP | 2026-03-23 | 2026-03-23 | 2026-03-23 | <1 dag |
| FASE2_SKILLS_GOVERNANCE | 2026-03-23 | 2026-03-23 | 2026-03-23 | <1 dag |
| RED_TEAM_AGENT | 2026-03-23 | 2026-03-23 | 2026-03-25 | 2 dagen |
| N8N_CICD_FOUNDATION | 2026-03-24 | 2026-03-24 | 2026-03-25 | 1 dag |
| CODE_CHECK_ARCHITECTUUR | 2026-03-23 | 2026-03-25 | 2026-03-25 | 2 dagen |
| OPS_VALIDATIE | 2026-03-25 | 2026-03-25 | 2026-03-25 | <1 dag |
| Quick Fixes | 2026-03-25 | 2026-03-26 | 2026-03-26 | 1 dag |
| Planning Opschoning | 2026-03-25 | 2026-03-26 | 2026-03-26 | 1 dag |
| Storage Interface | 2026-03-24 | 2026-03-26 | 2026-03-26 | 2 dagen |
| Vectorstore Interface | 2026-03-24 | 2026-03-26 | 2026-03-26 | 2 dagen |

### Afgeleide SLA's

| Metric | Huidig | Doel |
|--------|--------|------|
| Inbox → Sprint start | 0-2 dagen | <7 dagen |
| Sprint duur | <1 dag (intensief) | 1-3 dagen |
| Inbox → Parked | 1-2 dagen | n.v.t. |

**Opmerking:** De huidige cycle times zijn extreem kort omdat alle sprints tot nu toe in enkele sessies zijn afgerond. Bij Fase 3 (grotere sprints, avonduren/weekenden) zal dit veranderen.

---

## Capaciteitsplanning

**Context:** Niels werkt solo, avonduren + weekenden (zie user_work_context memory).

### Golf 1 capaciteit (actueel)

| Week | Beschikbaar | Allocatie | Status |
|------|-------------|-----------|--------|
| Week 1 (26 mrt) | Normaal | Golf 0 + Track B S1 + Track C S1 | ✅ Afgerond |
| Week 2 | Normaal | Planning Tracking (S) + Governance S1 of Mentor S1 | 🔄 Actief |
| Week 3 | Normaal | Resterende Golf 1 sprint | ⏳ |

**Advies:** Niet meer dan 2 feature-sprints tegelijk. De derde plek gebruiken voor een CHORE of achtergrond-research.

---

## Risico's & Blokkades

| # | Risico | Impact | Status | Mitigatie |
|---|--------|--------|--------|-----------|
| R1 | Track B+C patroon-inconsistentie | Hoog | GEMITIGEERD | Beide S1's afgerond met consistent ABC + frozen dataclasses + factory patroon |
| R2 | sentence-transformers dependency (~500MB) | Middel | OPEN | Optional dependency, lazy loading (Track C S2+) |
| R3 | Weaviate versie-incompatibiliteit | Middel | OPEN | Pin op 1.27.x (Track C S2) |
| R4 | GA-06 raakt NodeInterface ABC | Middel | OPEN | Architectureel review vóór implementatie (Governance S1) |
| R5 | Capaciteitsoverschatting (avonduren) | Middel | OPEN | Conservatief plannen, max 2 parallel |

---

## Status-conventies

| Symbool | Betekenis |
|---------|-----------|
| ✅ DONE | Afgerond en geverifieerd |
| 🔄 ACTIEF | Loopt bij Claude Code |
| 📋 KLAAR | Intake geshaped, klaar voor Claude Code |
| ⏳ WACHT | Geblokkeerd door afhankelijkheid |
| 🔴 BLOK | Geblokkeerd, actie nodig |
| 🅿️ PARK | Bewust geparkeerd |

---

## Bronverantwoording

| Concept | Bron | Kennisgradering |
|---------|------|----------------|
| Hill Charts | Shape Up (Basecamp, 2019) | SILVER |
| Golfplanning (parallel tracks) | AWS Prescriptive Guidance: Workstream Architecture | SILVER |
| Velocity tracking | Agile/Scrum body of knowledge (decennia) | GOLD |
| Cycle time | Lean/Kanban (Taiichi Ohno, 1988) | GOLD |
| Estimation accuracy | "Software Estimation" (McConnell, 2006) | GOLD |
| Roadmap-as-Code | Emerging pattern (RaC, 2024+) | BRONZE |
| Planning-as-docs | git-native planning (solo-dev community) | BRONZE |
