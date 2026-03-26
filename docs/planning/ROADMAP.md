# DevHub Roadmap — Geconsolideerd

---
laatst_bijgewerkt: 2026-03-26
gegenereerd_door: "Cowork Architect — alsdan-devhub"
---

## Huidige positie

```
Fase 0 ✅  Fundament
Fase 1 ✅  Kernagents + Infra
Fase 2 ✅  Skills + Governance (incl. 2b red-team)
Fase 3 🔄  Knowledge + Memory + Infrastructure
           ↑ WE ZIJN HIER — 575 tests, 6 agents, 8 skills, Track A+B1+C1 ✅, Golf 2 READY
Fase 4 🔲  BORIS-migratie (GATE: Niels-goedkeuring)
Fase 5 🔲  Uitbreiding
```

## Fase 2 → Fase 3 overgangswerk (AFGEROND)

| Sprint | Wat | Status |
|--------|-----|--------|
| **n8n CI/CD Foundation** | Health Check + Governance Check + PR Quality Gate | ✅ 339 → 370 tests |
| **Code Check Architectuur** | 5-layer code check, verdiept reviewer agent | ✅ 370 → 394 tests |
| **Operationele Validatie** | Alle 3 lagen bewezen end-to-end (n8n, Python, Skills) | ✅ 394 → 395 tests |

## Fase 3: Knowledge + Memory + Infrastructure

Drie parallelle tracks nadat bovenstaand overgangswerk af is.

### Track A: uv Workspace transitie ✅ AFGEROND

| Stap | Wat | Status |
|------|-----|--------|
| A1 | uv workspace config, `devhub/` → `packages/devhub-core/` | ✅ |
| A2 | Imports updaten, 394 tests groen | ✅ |
| A3 | Agents, skills, governance als aparte packages | Doorgeschoven |
| A4 | PEX packaging valideren | Doorgeschoven |

Afgerond: 394 tests. Stap A3-A4 zijn niet-blokkerend en doorgeschoven naar later.

### Track B: devhub-storage (bestandsopslag)

| Stap | Wat | Zonering | Status |
|------|-----|----------|--------|
| B1 | StorageInterface ABC + LocalAdapter | GROEN | ✅ v0.2.0 (575 tests) |
| B2 | Google Drive adapter + auth | GEEL | 📋 KLAAR |
| B3 | Organizable/Watchable mixins | GEEL | ⏳ na B2 |
| B4 | Reconciliation (drift-rapportage) | GEEL | ⏳ na B3 |
| B5 | Reconciliation (correctieve acties) | ROOD | ⏳ na B4 |

Sprint 1 (B1) afgerond: +100 tests, frozen dataclasses, factory patroon.

### Track C: devhub-vectorstore (Weaviate)

| Stap | Wat | Zonering | Status |
|------|-----|----------|--------|
| C1 | VectorStoreInterface ABC + contracts | GROEN | ✅ v0.2.0 (575 tests) |
| C2 | ChromaDB adapter (dev/test) | GROEN | ✅ v0.2.0 |
| C3 | Weaviate adapter (zones, CRUD) | GEEL | 📋 KLAAR |
| C4 | Multi-tenancy (per_zone + per_kwp) | GEEL | ⏳ na C3 |
| C5 | Embedding providers (MiniLM, later bge-m3) | GROEN | ⏳ na C3 |
| C6 | DevHub eigen Weaviate-instantie (KWP DEV) | GEEL | ⏳ na C4+C5 |

Sprint 1 (C1+C2) afgerond: +78 tests, frozen dataclasses, factory patroon. Parallel met Track B.

### Fase 3 overig

| Sprint | Wat | Afhankelijk van |
|--------|-----|-----------------|
| KWP DEV setup | Development knowledge domain inrichten | Track C (vectorstore) |
| EVIDENCE-kopie | EVIDENCE-methodiek van BORIS → DevHub | Geen |
| Retrospective learnings | Automatisch extraheren bij sprint-closure | KWP DEV |
| Mentor Supervisor | Proactief groeisysteem (Vygotsky/Dreyfus) | KWP DEV |
| Claude Optimalisatie | Prompt-optimalisatie research | Geen |

## Fase 4: BORIS-migratie (GATE)

**Start NOOIT zonder expliciete Niels-goedkeuring.**

- BORIS migreert van eigen `weaviate_store/` naar devhub-vectorstore package
- BORIS dev-skills vervangen door DevHub plugin-skills
- BORIS krijgt standalone Weaviate + MS365-koppeling
- Na delivery: BORIS communiceert met DevHub alleen via Claude Code plugin

## Fase 5: Uitbreiding

- Agent Teams (multi-agent orchestratie)
- Plugin marketplace-ready
- 2e project proof-of-concept
- Zelfverbeterend systeem (feedback loops)
- Karpathy Experiment Loop

## Volgorde-samenvatting

```
DONE:   n8n CI/CD Foundation ✅
DONE:   Code Check Architectuur ✅
DONE:   Track A — uv Workspace ✅ (394 tests)
DONE:   Operationele Validatie ✅ (395 tests)
DONE:   Track B S1 — Storage Interface + LocalAdapter ✅ (497 tests)
DONE:   Track C S1 — Vectorstore Interface + ChromaDB ✅ (575 tests)
NU:     Golf 1 restant (Mentor S1, Governance S1) + Planning & Tracking 🔄
DAN:    Golf 2 (Track B S2 + Track C S2) → KWP DEV + Mentor Supervisor
GATE:   Fase 4 — BORIS-migratie (Niels-goedkeuring)
LATER:  Fase 5 — Uitbreiding
```
