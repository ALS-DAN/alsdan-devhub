# DevHub Roadmap — Geconsolideerd

---
laatst_bijgewerkt: 2026-03-25
gegenereerd_door: "Cowork Architect — alsdan-devhub"
---

## Huidige positie

```
Fase 0 ✅  Fundament
Fase 1 ✅  Kernagents + Infra
Fase 2 ✅  Skills + Governance (incl. 2b red-team)
Fase 3 🔄  Knowledge + Memory + Infrastructure
           ↑ WE ZIJN HIER — 394 tests, 6 agents, 8 skills, Track A ✅
Fase 4 🔲  BORIS-migratie (GATE: Niels-goedkeuring)
Fase 5 🔲  Uitbreiding
```

## Fase 2 → Fase 3 overgangswerk (AFGEROND)

| Sprint | Wat | Status |
|--------|-----|--------|
| **n8n CI/CD Foundation** | Health Check + Governance Check + PR Quality Gate | ✅ 339 → 370 tests |
| **Code Check Architectuur** | 5-layer code check, verdiept reviewer agent | ✅ 370 → 394 tests |

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

| Stap | Wat | Zonering |
|------|-----|----------|
| B1 | StorageInterface ABC + LocalAdapter | GROEN |
| B2 | Google Drive adapter + auth | GEEL |
| B3 | Organizable/Watchable mixins | GEEL |
| B4 | Reconciliation (drift-rapportage) | GEEL |
| B5 | Reconciliation (correctieve acties) | ROOD |

Geschat: 2-3 sprints. Track A ✅ — kan starten.

### Track C: devhub-vectorstore (Weaviate)

| Stap | Wat | Zonering |
|------|-----|----------|
| C1 | VectorStoreInterface ABC + contracts | GROEN |
| C2 | ChromaDB adapter (dev/test) | GROEN |
| C3 | Weaviate adapter (zones, CRUD) | GEEL |
| C4 | Multi-tenancy (per_zone + per_kwp) | GEEL |
| C5 | Embedding providers (MiniLM, later bge-m3) | GROEN |
| C6 | DevHub eigen Weaviate-instantie (KWP DEV) | GEEL |

Geschat: 2-3 sprints. Track A ✅ — kan starten. Parallel met Track B.

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
NU:     Track B + C parallel (storage + vectorstore)
DAN:    KWP DEV + Mentor Supervisor + EVIDENCE
GATE:   Fase 4 — BORIS-migratie (Niels-goedkeuring)
LATER:  Fase 5 — Uitbreiding
```
