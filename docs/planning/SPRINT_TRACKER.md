# Sprint Tracker — DevHub

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: ACTIEF
actieve_fase: null
laatste_sprint: 28
test_baseline: 1191
laatst_bijgewerkt: 2026-03-27
---

## Fase-overzicht

```
Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 2b ✅ → Fase 3 ✅ → Fase 4 🔲 → Fase 5 🔲
```

**Fase 4 gate:** NIET starten zonder expliciete Niels-goedkeuring (DEV_CONSTITUTION Art. 1).

---

## Fase 0 (Afgerond 2026-03-23)

Fundament — tooling, infra, architectuurbeslissingen.

| Sprints | Tests | Duur |
|---------|-------|------|
| 2 (Quick Fixes + Planning Opschoning) | 0 → 397 | <1 dag |

---

## Fase 1 (Afgerond 2026-03-23)

Kernagents + Infra.

| Sprints | Tests | Duur |
|---------|-------|------|
| 2 (FASE1_BOOTSTRAP + FASE2_SKILLS_GOVERNANCE) | 218 → 339 | 1 dag |

---

## Fase 2 (Afgerond 2026-03-25)

Skills + Governance (incl. 2b red-team).

| Sprints | Tests | Duur |
|---------|-------|------|
| 4 (N8N_CICD + CODE_CHECK + UV_WORKSPACE + OPS_VALIDATIE) | 339 → 395 | 2 dagen |

---

## Fase 3 — Knowledge & Memory (Afgerond 2026-03-27)

**Start:** 2026-03-25 (na Ops Validatie SPIKE)
**Baseline:** 395 tests | 6 agents | 8 skills | 3 packages
**Eindstand:** 1191 tests | 6 agents | 8 skills | 3 packages (core v0.2.0, storage v0.3.0, vectorstore v0.3.0) + kennispipeline
**Fase 3 doel:** Knowledge & Memory lagen operationeel — vectorstore, storage, KWP DEV, mentor-systeem, governance-automatisering.

| Sprints | Tests | Duur |
|---------|-------|------|
| 22 (Sprint 7-28, 5 tracks + KP) | 395 → 1191 (+796) | 3 dagen |

**Retrospective:** `knowledge/retrospectives/RETRO_FASE3_KNOWLEDGE_MEMORY.md`

---

## Golfplanning (Fase 3)

### Golf 0: Opruiming ✅

| Sprint | Track | Size | Status | Hill |
|--------|-------|------|--------|------|
| Quick Fixes Ops Validatie | — | XS | ✅ DONE | ████████████ |
| Planning Opschoning | — | XS | ✅ DONE | ████████████ |

### Golf 1: Fundament ✅

| Sprint | Track | Size | Status | Hill | Codepad |
|--------|-------|------|--------|------|---------|
| Storage: Interface + LocalAdapter | B | S | ✅ DONE | ████████████ | `packages/devhub-storage/` |
| Vectorstore: Interface + ChromaDB | C | S | ✅ DONE | ████████████ | `packages/devhub-vectorstore/` |
| Planning & Tracking Systeem | — | S | ✅ DONE | ████████████ | `docs/planning/` + `skills/` + `agents/` |
| Mentor: Skill Radar + Contracts | M | S | ✅ DONE | ████████████ | `contracts/growth_contracts.py` + `skills/` |
| Governance: QA Checks | G | S | ✅ DONE | ████████████ | `agents/qa_agent.py` |

### Golf 2: Uitbouw ✅

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: Google Drive adapter | B | S | ✅ DONE | ████████████ | — |
| Vectorstore: Weaviate + Multi-tenancy | C | S | ✅ DONE | ████████████ | — |
| Mentor: Challenge Engine + Scaffolding | M | S | ✅ DONE | ████████████ | Mentor S1 ✅ |
| Governance: SecurityScanner | G | S | ✅ DONE | ████████████ | Governance S1 ✅ |

### Golf 3: Verrijking ✅

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: SharePoint adapter | B | S | ✅ DONE | ████████████ | Track B S2 ✅ |
| Vectorstore: Embeddings + DevHub Weaviate | C | S | ✅ DONE | ████████████ | Track C S2 ✅ |
| Mentor: Research Advisor + Dashboard | M | S | ✅ DONE | ████████████ | Mentor S2 ✅ |

### Kennispipeline Track (toegevoegd Golf 3+)

_Nieuwe track — niet voorzien in originele planning. Uitgegroeid uit Track C vectorstore-werk._

| Sprint | Track | Size | Status | Hill | Toelichting |
|--------|-------|------|--------|------|-------------|
| KP Golf 1: Research Contracts + DocumentInterface | KP | S | ✅ DONE | ████████████ | +79 tests, 931 totaal |
| Track C S5: EmbeddingProvider implementaties | C | S | ✅ DONE | ████████████ | +30 tests, 961 totaal |
| KP Golf 2A: KnowledgeCurator + Researcher verrijking | KP | S | ✅ DONE | ████████████ | +53 tests, 1014 totaal |
| KP Golf 2B: KWP DEV Bootstrap | KP | S | ✅ DONE | ████████████ | +29 tests, 1043 totaal |
| KP Golf 3: Analyse Pipeline | KP | S | ✅ DONE | ████████████ | +39 tests, 1082 totaal |

### Golf 4: Afsluiting & Integratie

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: Reconciliation engine | B | S | ✅ DONE | ████████████ | Track B S3 ✅ |
| KWP DEV setup | — | S | ✅ DONE | ████████████ | KP Golf 2B ✅ |
| SPIKE: Sprint Lifecycle Hygiene | — | XS | ✅ DONE | ████████████ | — |
| FEAT: Lifecycle Hygiene Implementatie | — | S | ✅ DONE | ████████████ | SPIKE ✅ |
| FEAT: Lifecycle Hygiene Afronding | — | XS | ✅ DONE | ████████████ | FEAT Implementatie ✅ |

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
| 11 | Planning & Tracking Systeem | S (1 sprint) | S (1 sprint) | +0 | 100% |
| 12 | Mentor: Skill Radar + Contracts | S (1 sprint) | S (1 sprint) | +36 | 100% |
| 13 | Governance: QA Checks | S (1 sprint) | S (1 sprint) | +51 | 100% |
| 14 | Storage: Google Drive adapter | S (1 sprint) | S (1 sprint) | +56 | 100% |
| 15 | Vectorstore: Weaviate + Multi-tenancy | S (1 sprint) | S (1 sprint) | +59 | 100% |
| 16 | Mentor: Challenge Engine + Scaffolding | S (1 sprint) | S (1 sprint) | +43 | 100% |
| 17 | Governance: SecurityScanner | S (1 sprint) | S (1 sprint) | +34 | 100% |
| 18 | KP Golf 1: Research Contracts + DocumentInterface | S (1 sprint) | S (1 sprint) | +79 | 100% |
| 19 | Track C S5: EmbeddingProvider implementaties | S (1 sprint) | S (1 sprint) | +30 | 100% |
| 20 | KP Golf 2A: KnowledgeCurator + Researcher verrijking | S (1 sprint) | S (1 sprint) | +53 | 100% |
| 21 | KP Golf 2B: KWP DEV Bootstrap | S (1 sprint) | S (1 sprint) | +29 | 100% |
| 22 | KP Golf 3: Analyse Pipeline | S (1 sprint) | S (1 sprint) | +39 | 100% |
| 23 | Mentor S3: Research Advisor + Dashboard | S (1 sprint) | S (1 sprint) | +49 | 100% |
| 24 | Storage: SharePoint adapter | S (1 sprint) | S (1 sprint) | +34 | 100% |
| 25 | SPIKE: Sprint Lifecycle Hygiene | XS (<1u) | XS (<1u) | +0 | 100% |
| 26 | FEAT: Lifecycle Hygiene Implementatie | S (1 sprint) | S (1 sprint) | +0 | 100% |
| 27 | FEAT: Lifecycle Hygiene Afronding | XS (<1u) | XS (<1u) | +0 | 100% |
| 28 | Storage: Reconciliation Engine | S (1 sprint) | S (1 sprint) | +35 | 100% |

*\* UV Workspace = herstructurering, geen nieuwe tests verwacht.*

### Afgeleide metrics

| Metric | Waarde | Toelichting |
|--------|--------|-------------|
| Sprints afgerond | 28 | Alle binnen geschatte tijd |
| Test baseline | 1191 | Geverifieerd na Sprint 28 (1191 passed, 2 skipped) |
| Gemiddelde test-delta | +42.1 | Per sprint (excl. UV workspace + Planning Opschoning + SPIKEs + FEAT hygiene) |
| Schattingsnauwkeurigheid | 100% | 28/28 sprints binnen appetite |
| Gemiddelde sprint-grootte | S-M | XS=1, S=2, M=3 (Fibonacci-achtig) |

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
| Planning & Tracking | 2026-03-26 | 2026-03-26 | 2026-03-26 | <1 dag |
| Mentor S1 | 2026-03-23 | 2026-03-26 | 2026-03-26 | 3 dagen |
| Governance S1 | 2026-03-25 | 2026-03-26 | 2026-03-26 | 1 dag |
| Storage: Google Drive | 2026-03-24 | 2026-03-26 | 2026-03-26 | 2 dagen |
| Vectorstore: Weaviate | 2026-03-24 | 2026-03-26 | 2026-03-26 | 2 dagen |
| Mentor: Challenge Engine | 2026-03-23 | 2026-03-26 | 2026-03-26 | 3 dagen |
| Governance: SecurityScanner | 2026-03-25 | 2026-03-26 | 2026-03-26 | 1 dag |
| KP Golf 1: Research Contracts | 2026-03-26 | 2026-03-26 | 2026-03-26 | <1 dag |
| Track C S5: EmbeddingProvider | 2026-03-26 | 2026-03-26 | 2026-03-26 | <1 dag |
| KP Golf 2A: KnowledgeCurator | 2026-03-26 | 2026-03-26 | 2026-03-26 | <1 dag |
| KP Golf 2B: KWP DEV Bootstrap | 2026-03-26 | 2026-03-26 | 2026-03-26 | <1 dag |
| KP Golf 3: Analyse Pipeline | 2026-03-26 | 2026-03-26 | 2026-03-26 | <1 dag |
| Mentor S3: Research Advisor | 2026-03-23 | 2026-03-27 | 2026-03-27 | 4 dagen |
| Storage: SharePoint adapter | 2026-03-24 | 2026-03-27 | 2026-03-27 | 3 dagen |
| SPIKE: Lifecycle Hygiene | 2026-03-27 | 2026-03-27 | 2026-03-27 | <1 dag |
| FEAT: Lifecycle Hygiene Impl. | 2026-03-27 | 2026-03-27 | 2026-03-27 | <1 dag |
| FEAT: Lifecycle Hygiene Afr. | 2026-03-27 | 2026-03-27 | 2026-03-27 | <1 dag |
| Storage: Reconciliation Engine | 2026-03-24 | 2026-03-27 | 2026-03-27 | 3 dagen |

### Afgeleide SLA's

| Metric | Huidig | Doel |
|--------|--------|------|
| Inbox → Sprint start | 0-2 dagen | <7 dagen |
| Sprint duur | <1 dag (intensief) | 1-3 dagen |
| Inbox → Parked | 1-2 dagen | n.v.t. |

---

## Capaciteitsplanning

**Context:** Niels werkt solo, avonduren + weekenden.

### Golf 1-3 capaciteit (gerealiseerd)

| Week | Beschikbaar | Allocatie | Status |
|------|-------------|-----------|--------|
| Week 1 (26 mrt) | Normaal | Golf 0 + Track B S1 + Track C S1 | ✅ Afgerond |
| Week 2 (26 mrt) | Normaal | Golf 1 (alle tracks) + Golf 2 (alle tracks) | ✅ Afgerond |
| Week 3 (27 mrt) | Normaal | Kennispipeline Golf 1-3 + Track C S5 + Golf 4 (KWP DEV) | ✅ Afgerond |

### Golf 4+ capaciteit (huidig)

| Week | Beschikbaar | Allocatie | Status |
|------|-------------|-----------|--------|
| Week 4 (27 mrt+) | Normaal | Golf 4: Lifecycle Hygiene FEAT + Afronding | ✅ Afgerond |

**Advies:** Niet meer dan 2 feature-sprints tegelijk.

---

## Risico's & Blokkades

| # | Risico | Impact | Status | Mitigatie |
|---|--------|--------|--------|-----------|
| R1 | Track B+C patroon-inconsistentie | Hoog | GEMITIGEERD | Beide S1's afgerond met consistent ABC + frozen dataclasses + factory patroon |
| R2 | sentence-transformers dependency (~500MB) | Middel | GEMITIGEERD | Optional dependency + lazy loading geïmplementeerd in Track C S5 |
| R3 | Weaviate versie-incompatibiliteit | Middel | GEMITIGEERD | Opgelost in Track C S2+S5 |
| R4 | GA-06 raakt NodeInterface ABC | Middel | GEMITIGEERD | Concrete default methode (niet abstract), backward compatible |
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
