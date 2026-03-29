# Sprint Tracker — DevHub

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: ACTIEF
actieve_fase: null
laatste_sprint: 46
test_baseline: 1735
laatst_bijgewerkt: 2026-03-29
---

## Fase-overzicht

```
Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 2b ✅ → Fase 3 ✅ → Fase 4 🔄 → Fase 5 🔲
```

**Fase 4 gate:** Goedgekeurd door Niels (2026-03-28).

---

## Strategisch Overzicht

### Now

Geen actieve sprint. Laatste: Sprint 46 (Dual-Format Machine-Leesbare Systeembestanden) ✅

### Next

| Intake | Stroom | Type |
|--------|--------|------|
| Planning-herstructurering Drie Lagen | Governance | CHORE |
| Dashboard NiceGUI → FastAPI+HTMX | Gebruikerservaring | FEAT |
| Kennisketen End-to-End | Kennis & Research | FEAT |

### Later

- Fase 5: Agent Teams, plugin marketplace, 2e project PoC
- n8n Event Scheduler implementatie (SPIKE GO, wacht op Docker setup)
- Mentor Supervisor Systeem

---

## Fase 0-3 (Afgerond)

| Fase | Sprints | Tests | Duur | Kern |
|------|---------|-------|------|------|
| 0 — Fundament | 2 | 0 → 397 | <1 dag | Tooling, infra, architectuurbeslissingen |
| 1 — Kernagents | 2 | 218 → 339 | 1 dag | Agents + infra |
| 2 — Skills | 4 | 339 → 395 | 2 dagen | Skills + governance + red-team |
| 3 — Knowledge | 22 | 395 → 1191 | 3 dagen | Vectorstore, storage, mentor, governance, kennispipeline |

_Fase 3 golfplanning: [archive/FASE3_GOLFPLANNING_ARCHIEF.md](archive/FASE3_GOLFPLANNING_ARCHIEF.md)_
_Fase 3 retrospective: `knowledge/retrospectives/RETRO_FASE3_KNOWLEDGE_MEMORY.md`_

---

## Work Streams

### Kern-platform

_Packages, contracts, event bus, runtime-infra_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 1 | FASE1_BOOTSTRAP | FEAT | +81 | Kernagents + infra |
| 2 | FASE2_SKILLS_GOVERNANCE | FEAT | +40 | Skills + governance |
| 5 | UV_WORKSPACE_TRANSITIE | CHORE | +0 | UV workspace herstructurering |
| 30 | Provider Pattern | FEAT | +4 | BorisAdapter → BORIS, registry sys.path support |
| 42 | Event Bus Lifecycle Hooks | FEAT | +67 | EventBus ABC + InMemoryEventBus + 10 events |

**Totaal:** 5 sprints | +192 tests

### Kennis & Research

_Kennispipeline, vectorstore, Research Compas, documentatie_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 10 | Vectorstore Interface + ChromaDB | FEAT | +78 | Interface + ChromaDB adapter |
| 15 | Vectorstore: Weaviate + Multi-tenancy | FEAT | +59 | Weaviate adapter |
| 18 | KP Golf 1: Research Contracts | FEAT | +79 | DocumentInterface + contracts |
| 19 | Track C S5: EmbeddingProvider | FEAT | +30 | Embedding implementaties |
| 20 | KP Golf 2A: KnowledgeCurator | FEAT | +53 | Curator + Researcher verrijking |
| 21 | KP Golf 2B: KWP DEV Bootstrap | FEAT | +29 | Knowledge Workspace DEV |
| 22 | KP Golf 3: Analyse Pipeline | FEAT | +39 | Analyse pipeline |
| 29 | KWP DEV Operationeel | FEAT | +11 | KWP DEV operationeel |
| 32 | Diataxis+ Taxonomie & PoC | FEAT | +70 | 12 categorien, 8 templates |
| 33 | Research Compas — Config & Contracts | FEAT | +56 | 16 domeinen, RQ-tags, agent profiles |
| 34 | Doc Pipeline & BORIS-blauwdruk | FEAT | +71 | DocumentService, FolderRouter |
| 35 | Research Compas — Runtime & Bootstrap | FEAT | +83 | KnowledgeScanner, ConfigDrivenBootstrap |

**Totaal:** 12 sprints | +658 tests

### Governance & Kwaliteit

_DEV_CONSTITUTION, security, tests, guardrails, health_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 4 | CODE_CHECK_ARCHITECTUUR | FEAT | +24 | Code check architectuur |
| 13 | Governance: QA Checks | FEAT | +51 | QA agent checks |
| 17 | Governance: SecurityScanner | FEAT | +34 | Security scanner |
| 25 | SPIKE: Lifecycle Hygiene | SPIKE | +0 | Onderzoek lifecycle |
| 26 | FEAT: Lifecycle Hygiene Impl. | FEAT | +0 | Implementatie |
| 27 | FEAT: Lifecycle Hygiene Afr. | CHORE | +0 | Afronding |
| 36 | Node-Guardrails devhub-sprint | CHORE | +0 | Node-keuze, DevHub-pad |
| 37 | Node-Guardrails 3 skills | CHORE | +0 | sprint-prep, health, review |
| 46 | Dual-Format Systeembestanden | FEAT | +53 | YAML-blokken, Art. 4.6, reviewer enforcement |

**Totaal:** 9 sprints | +162 tests

### Integraties

_Google Drive, n8n, BorisAdapter, externe systemen_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 3 | N8N_CICD_FOUNDATION | FEAT | +31 | n8n CI/CD fundament |
| 9 | Storage Interface + LocalAdapter | FEAT | +100 | Storage ABC + lokale adapter |
| 14 | Storage: Google Drive adapter | FEAT | +56 | Google Drive adapter |
| 24 | Storage: SharePoint adapter | FEAT | +34 | SharePoint adapter |
| 28 | Storage: Reconciliation Engine | FEAT | +35 | Reconciliation engine |
| 38 | DriveSyncAdapter | FEAT | +475 | Google Drive via filesystem sync |
| 40 | n8n Event Scheduler SPIKE | SPIKE | +0 | GO — architectuur + PoC |
| 41 | n8n Docker Setup | CHORE | +0 | Health RED→YELLOW, deps gepind |

**Totaal:** 8 sprints | +731 tests

### Gebruikerservaring

_Dashboard, mentor-systeem, skills, agent UX_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 12 | Mentor: Skill Radar + Contracts | FEAT | +36 | Growth contracts + skill radar |
| 16 | Mentor: Challenge Engine | FEAT | +43 | Challenge engine + scaffolding |
| 23 | Mentor S3: Research Advisor | FEAT | +49 | Research advisor + dashboard |
| 43 | DevHub Dashboard NiceGUI | FEAT | +65 | 7 panelen, ResearchQueueManager |
| 44 | Dashboard Panelen Upgrade | FEAT | +110 | 5 panelen upgraded, SprintTrackerParser |
| 45 | Dashboard Kennisbibliotheek | FEAT | +81 | ArticleParser, 3 nieuwe pagina's |

**Totaal:** 6 sprints | +384 tests

### Verkenning

_SPIKEs, research-sprints, proof-of-concepts_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 6 | OPERATIONELE_VALIDATIE | SPIKE | +1 | Ops validatie |
| 31 | Claude Optimalisatie Research | RESEARCH | +0 | Actualisatie + conclusie |
| 39 | Agent Teams SPIKE | SPIKE | +0 | GEPARKEERD — nog experimenteel |

**Totaal:** 3 sprints | +1 tests

### Meta

_Planning, opschoning, tracking_

| # | Sprint | Type | Tests Δ | Toelichting |
|---|--------|------|---------|-------------|
| 7 | Quick Fixes | CHORE | +2 | Ops validatie fixes |
| 8 | Planning Opschoning | CHORE | +0 | Opschoning |
| 11 | Planning & Tracking Systeem | FEAT | +0 | Planning systeem |

**Totaal:** 3 sprints | +2 tests

---

## Metrics (samenvatting)

| Metric | Waarde |
|--------|--------|
| Sprints afgerond | 46 |
| Test baseline | 1735 |
| Gem. test-delta | +50.8/sprint |
| Schattingsnauwkeurigheid | 100% (46/46) |

_Volledig overzicht: [VELOCITY_LOG.md](VELOCITY_LOG.md)_

---

## Risico's & Blokkades

| # | Risico | Impact | Status | Mitigatie |
|---|--------|--------|--------|-----------|
| R1 | Track B+C patroon-inconsistentie | Hoog | GEMITIGEERD | Consistent ABC + frozen dataclasses + factory patroon |
| R2 | sentence-transformers dependency (~500MB) | Middel | GEMITIGEERD | Optional dependency + lazy loading |
| R3 | Weaviate versie-incompatibiliteit | Middel | GEMITIGEERD | Opgelost in Track C S2+S5 |
| R4 | GA-06 raakt NodeInterface ABC | Middel | GEMITIGEERD | Concrete default methode, backward compatible |
| R5 | Capaciteitsoverschatting (avonduren) | Middel | OPEN | Conservatief plannen, max 2 parallel |

---

## Hill Chart Legenda

```
            /\
    Uphill /  \ Downhill
   (figuring  (executing
    it out)    with confidence)
  /            \
/                \

░░░░░░░░░░░░  Niet gestart
▓░░░░░░░░░░░  Net gestart, veel onbekenden
▓▓▓░░░░░░░░░  Verkennend, aanpak aan het vormen
▓▓▓▓▓▓░░░░░░  Halverwege uphill, kernbeslissingen genomen
▓▓▓▓▓▓▓░░░░░  Top van de hill — alles duidelijk
▓▓▓▓▓▓▓▓▓░░░  Downhill, implementatie loopt
▓▓▓▓▓▓▓▓▓▓▓░  Bijna klaar, laatste details
████████████  Afgerond
```

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
| Now-Next-Later | Janna Bastow (ProdPad, 2019) | SILVER |
| Work Streams | AWS Prescriptive Guidance: Workstream Architecture | SILVER |
| Velocity tracking | Agile/Scrum body of knowledge (decennia) | GOLD |
| Cycle time | Lean/Kanban (Taiichi Ohno, 1988) | GOLD |
| Estimation accuracy | "Software Estimation" (McConnell, 2006) | GOLD |
| Roadmap-as-Code | Emerging pattern (RaC, 2024+) | BRONZE |
| Planning-as-docs | git-native planning (solo-dev community) | BRONZE |
