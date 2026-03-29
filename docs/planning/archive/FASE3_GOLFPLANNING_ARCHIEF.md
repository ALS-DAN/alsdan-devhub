# Fase 3 — Golfplanning Archief

_Gearchiveerd vanuit SPRINT_TRACKER.md bij planning-herstructurering (2026-03-29)._

---

## Golf 0: Opruiming

| Sprint | Track | Size | Status | Hill |
|--------|-------|------|--------|------|
| Quick Fixes Ops Validatie | — | XS | DONE | Afgerond |
| Planning Opschoning | — | XS | DONE | Afgerond |

## Golf 1: Fundament

| Sprint | Track | Size | Status | Hill | Codepad |
|--------|-------|------|--------|------|---------|
| Storage: Interface + LocalAdapter | B | S | DONE | Afgerond | `packages/devhub-storage/` |
| Vectorstore: Interface + ChromaDB | C | S | DONE | Afgerond | `packages/devhub-vectorstore/` |
| Planning & Tracking Systeem | — | S | DONE | Afgerond | `docs/planning/` + `skills/` + `agents/` |
| Mentor: Skill Radar + Contracts | M | S | DONE | Afgerond | `contracts/growth_contracts.py` + `skills/` |
| Governance: QA Checks | G | S | DONE | Afgerond | `agents/qa_agent.py` |

## Golf 2: Uitbouw

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: Google Drive adapter | B | S | DONE | Afgerond | — |
| Vectorstore: Weaviate + Multi-tenancy | C | S | DONE | Afgerond | — |
| Mentor: Challenge Engine + Scaffolding | M | S | DONE | Afgerond | Mentor S1 |
| Governance: SecurityScanner | G | S | DONE | Afgerond | Governance S1 |

## Golf 3: Verrijking

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: SharePoint adapter | B | S | DONE | Afgerond | Track B S2 |
| Vectorstore: Embeddings + DevHub Weaviate | C | S | DONE | Afgerond | Track C S2 |
| Mentor: Research Advisor + Dashboard | M | S | DONE | Afgerond | Mentor S2 |

## Kennispipeline Track (toegevoegd Golf 3+)

_Nieuwe track — niet voorzien in originele planning. Uitgegroeid uit Track C vectorstore-werk._

| Sprint | Track | Size | Status | Hill | Toelichting |
|--------|-------|------|--------|------|-------------|
| KP Golf 1: Research Contracts + DocumentInterface | KP | S | DONE | Afgerond | +79 tests, 931 totaal |
| Track C S5: EmbeddingProvider implementaties | C | S | DONE | Afgerond | +30 tests, 961 totaal |
| KP Golf 2A: KnowledgeCurator + Researcher verrijking | KP | S | DONE | Afgerond | +53 tests, 1014 totaal |
| KP Golf 2B: KWP DEV Bootstrap | KP | S | DONE | Afgerond | +29 tests, 1043 totaal |
| KP Golf 3: Analyse Pipeline | KP | S | DONE | Afgerond | +39 tests, 1082 totaal |

## Golf 4: Afsluiting & Integratie

| Sprint | Track | Size | Status | Hill | Geblokkeerd door |
|--------|-------|------|--------|------|------------------|
| Storage: Reconciliation engine | B | S | DONE | Afgerond | Track B S3 |
| KWP DEV setup | — | S | DONE | Afgerond | KP Golf 2B |
| SPIKE: Sprint Lifecycle Hygiene | — | XS | DONE | Afgerond | — |
| FEAT: Lifecycle Hygiene Implementatie | — | S | DONE | Afgerond | SPIKE |
| FEAT: Lifecycle Hygiene Afronding | — | XS | DONE | Afgerond | FEAT Implementatie |

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

## Afhankelijkheidsdiagram

```
Golf 0                Golf 1              Golf 2              Golf 3              Golf 4
──────                ──────              ──────              ──────              ──────
Quick Fixes
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
