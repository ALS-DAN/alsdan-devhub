# SPRINT_INTAKE_EVENT_BUS_LIFECYCLE_HOOKS_2026-03-28

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 4
cynefin: complicated
---

## Doel

Bouw een lightweight event bus met pub/sub en typed events in `devhub_core/events/`, zodat agents reactief kunnen samenwerken via lifecycle hooks (`SprintClosed`, `TaskCompleted`, `HealthDegraded`, etc.) in plaats van via handmatige triggers.

## Probleemstelling

### Waarom nu

DevHub's agents en pipelines zijn code-compleet, maar werken in isolatie. De kern van het probleem: **er gebeurt niks automatisch**. Drie concrete symptomen:

1. **Kennispipeline is dood na sprint-close:** De AnalysisPipeline, KnowledgeCurator en ResearchAdvisor bestaan en zijn getest, maar worden nooit automatisch getriggerd. Als een sprint sluit, moet iemand handmatig kennis-extractie starten. Dat gebeurt niet → kennis accumuleert niet.

2. **Observaties worden gelogd maar niet gehoord:** De AnalysisPipeline emit al observaties via `_emit_observation(obs_type, payload, severity)` — maar dit is logging naar Python's logger. Niemand luistert. Een `HEALTH_DEGRADED` event verdwijnt in een logbestand in plaats van een reactie te triggeren.

3. **Agent-handoffs zijn manueel en sequentieel:** Coder klaar → reviewer moet handmatig gestart worden. QA-rapport klaar → docs-generatie moet handmatig getriggerd worden. Er is geen mechanisme voor "als X klaar is, start Y automatisch".

### SOTA-onderbouwing

- **AG2 (AutoGen v0.4):** Core herschreven rond async event-driven actor model. Drie lagen: Core (async messaging, agent lifecycle), AgentChat (group coordination), Extensions. Elke conversatie draait op een event bus die state isoleert en agents concurrent laat werken. **Kennisgradering: SILVER** — framework is productie-klaar, architectuur is breed gevalideerd (bron: [AG2 architecture](https://arxiv.org/html/2601.13671v1)).

- **Event-driven agent orchestratie:** "Production implementations use explicit hooks and event handlers as production code — versioning them, validating them, keeping them idempotent." (bron: [Multi-Agent Orchestration Patterns](https://www.ai-agentsplus.com/blog/multi-agent-orchestration-patterns-2026)). **Kennisgradering: SILVER**.

- **Anthropic multi-agent research system:** LeadResearcher spawnt subagents op basis van events, met automatische convergentie en result-aggregatie. Vergelijkbaar met DevHub's dev-lead → coder/reviewer flow, maar event-driven i.p.v. sequentieel. **Kennisgradering: SILVER** (bron: [Anthropic engineering blog](https://www.anthropic.com/engineering/multi-agent-research-system)).

- **Microsoft AI Agent Design Patterns:** Event-driven als een van de vier kernpatronen naast graph-based, hierarchical en swarm. Aanbeveling: "model the system as a state machine or graph where transitions happen independently." **Kennisgradering: SILVER** (bron: [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)).

### Fase-context

Fase 4 Golf 2 (Intelligentie toevoegen). De event bus is de **kern-verbinding** die alle Fase 3-componenten (kennispipeline, vectorstore, analysis pipeline) reactief maakt. Zonder event bus blijft alles manueel — met event bus wordt het systeem zelfstandig lerend.

### Wat er al staat (geverifieerd)

| Component | Status | Gap |
|-----------|--------|-----|
| `_emit_observation()` in AnalysisPipeline | ✅ Logging-based | → Moet echte event publish worden |
| `ObservationType` enum | ✅ Bestaat | → Wordt basis voor typed events |
| DevOrchestrator scratchpad queues | ✅ JSON-based | → Kunnen event-driven worden |
| ResearchQueue (in-memory, priority-based) | ✅ Werkt | → Kan subscriben op `KnowledgeGapDetected` |
| DevTaskResult, QAReport, DocGenRequest | ✅ Frozen dataclasses | → Worden event payloads (al immutable) |
| Sprint lifecycle hooks | ❌ Bestaan niet | → Nieuw te bouwen |
| Agent lifecycle hooks | ❌ Bestaan niet | → Nieuw te bouwen |
| Reactive observation handlers | ❌ Bestaan niet | → Nieuw te bouwen |

## Deliverables

### Kern: Event Bus

- [ ] **EB-01** — `EventBus` klasse in `packages/devhub-core/devhub_core/events/bus.py`
  - Pub/sub met typed events
  - Sync + async support
  - Handler-registratie via decorators of expliciete subscribe
  - Thread-safe (meerdere agents kunnen concurrent publiceren)
  - Event history (laatste N events bewaren voor debugging)

- [ ] **EB-02** — `Event` base class + typed events in `devhub_core/events/types.py`
  - `SprintStarted(sprint_id, node_id, sprint_type)`
  - `SprintClosed(sprint_id, node_id, results: DevTaskResult)`
  - `TaskCompleted(task_id, agent_id, result: DevTaskResult)`
  - `TaskFailed(task_id, agent_id, error)`
  - `QACompleted(task_id, report: QAReport)`
  - `DocGenRequested(request: DocGenRequest)`
  - `KnowledgeGapDetected(domain, gap_description, requesting_agent)`
  - `HealthDegraded(dimension, score, threshold)`
  - `ObservationEmitted(obs_type: ObservationType, payload, severity)`
  - Alle events als frozen dataclasses (consistent met bestaande contracts)
  - Timestamp + event_id + source_agent automatisch

- [ ] **EB-03** — Event bus contract in `devhub_core/contracts/event_contracts.py`
  - `EventBusInterface` ABC (zodat de bus zelf vervangbaar is, net als storage/vectorstore)
  - `EventHandler` protocol
  - `EventFilter` voor selectieve subscriptions

### Lifecycle Hooks

- [ ] **LH-01** — Sprint lifecycle hooks
  - `on_sprint_start` → emit `SprintStarted`
  - `on_sprint_close` → emit `SprintClosed` → triggers kennisextractie, retrospective
  - Integratie met devhub-sprint skill (stap toevoegen aan close-flow)

- [ ] **LH-02** — Agent lifecycle hooks
  - `on_task_assigned(agent_id, task)` → emit event
  - `on_task_completed(agent_id, result)` → emit `TaskCompleted`
  - `on_task_failed(agent_id, error)` → emit `TaskFailed`

- [ ] **LH-03** — Kennispipeline hooks
  - `SprintClosed` → KnowledgeCurator.extract_learnings()
  - `KnowledgeGapDetected` → ResearchQueue.submit()
  - `ObservationEmitted(HEALTH_DEGRADED)` → GrowthReportGenerator.flag()

### Integratie

- [ ] **INT-01** — AnalysisPipeline migratie
  - `_emit_observation()` → `event_bus.publish(ObservationEmitted(...))`
  - Backwards-compatible (logging blijft, event bus erbij)

- [ ] **INT-02** — DevOrchestrator integratie
  - Na task-creatie → `TaskAssigned` event
  - Na task-completion → `TaskCompleted` event
  - Doc queue → `DocGenRequested` event (naast bestaande JSON)

- [ ] **INT-03** — ResearchQueue integratie
  - Subscribe op `KnowledgeGapDetected` → automatisch ResearchRequest aanmaken

### Tests

- [ ] **T-01** — Unit tests EventBus (publish, subscribe, unsubscribe, filtering, thread-safety)
- [ ] **T-02** — Unit tests typed events (serialization, immutability, timestamp)
- [ ] **T-03** — Integratie tests: sprint-close → kennisextractie flow
- [ ] **T-04** — Integratie tests: task-complete → reviewer trigger flow

## Grenzen (wat we NIET doen)

- NIET persistent event storage (events zijn in-memory, niet in database — dat is een later item)
- NIET distributed events (geen cross-process/cross-machine — DevHub draait lokaal)
- NIET n8n-integratie (dat is Sprint 3)
- NIET Agent Teams integratie (dat is Sprint 1 — maar de event bus moet er wel mee compatibel zijn)
- NIET BORIS-specifieke events (alleen DevHub-interne events)
- NIET de bestaande JSON-queues verwijderen — event bus komt erbij, migratie is geleidelijk
- NIET meer dan 10-12 event types in eerste versie — uitbreidbaar houden

## Afhankelijkheden

| Type | Beschrijving |
|------|-------------|
| Geblokkeerd door | Geen — kan direct starten (profiteert van Sprint 1 inzichten maar niet hard geblokkeerd) |
| Blokkeert | Sprint 3 (n8n) — n8n kan events consumeren/publiceren via de bus |
| BORIS impact | Nee — raakt alleen devhub-core internals |
| Raakt packages | devhub-core (primair), devhub-storage + devhub-vectorstore (event-aware worden later) |
| Raakt agents | DevOrchestrator, AnalysisPipeline, KnowledgeCurator, ResearchAdvisor |
| Raakt skills | devhub-sprint (close-flow uitbreiden met event publish) |

## Open vragen voor Claude Code

1. Moet de EventBus een singleton zijn (globaal per sessie) of per-orchestrator? Suggestie: singleton met namespacing per node_id.
2. Hoe integreren we de event bus met Agent Teams? Als teammates eigen context windows hebben, kunnen ze niet dezelfde in-memory bus delen. Mogelijk via file-based event log als bridge?
3. Moet event_history persistent zijn (SQLite, zoals BORIS' ObservationStore) of is in-memory voldoende voor v1?
4. Hoe voorkom je event-loops? (bijv. `TaskCompleted` → handler publiceert `DocGenRequested` → handler publiceert `TaskCompleted` → ∞). Suggestie: max recursion depth of event-type blacklist per handler.
5. Zijn er bestaande tests die de `_emit_observation()` in AnalysisPipeline testen? Die moeten backwards-compatible blijven.

## Prioriteit

**Hoog** — Dit is de kern-verbinding die alle Fase 3 componenten reactief maakt. Zonder event bus blijft DevHub een verzameling losse tools die je handmatig moet aansturen.

## DEV_CONSTITUTION impact

| Artikel | Geraakt | Toelichting |
|---------|---------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Automatische triggers vereisen duidelijke grenzen — alleen GREEN zone acties automatisch, YELLOW/RED altijd via Niels |
| Art. 2 (Verificatieplicht) | Ja | Event handlers moeten claims verifiëren, niet blind doorsturen |
| Art. 3 (Codebase Integriteit) | Ja | Backwards-compatible met bestaande tests (882+) |
| Art. 4 (Transparantie) | Ja | Event history = audit trail van alle automatische acties |
| Art. 7 (Impact-zonering) | GEEL | Nieuwe module in devhub-core, raakt meerdere subsystemen |

## Technische richting (Claude Code mag afwijken)

Aanbevolen aanpak:

1. **Start met de bus zelf** — minimale EventBus + 3-4 event types, uitgebreid getest
2. **Dan één integratie end-to-end** — `SprintClosed` → KnowledgeCurator (bewijs dat de flow werkt)
3. **Dan de rest** — overige events, overige integraties
4. **Backwards-compatible** — bestaande JSON-queues en logging blijven werken, event bus is additioneel

Design-principes:
- Events zijn immutable (frozen dataclasses, consistent met bestaande contracts)
- Handlers zijn idempotent (meerdere keren dezelfde event = zelfde resultaat)
- Bus is vervangbaar via ABC (EventBusInterface) — net als StorageInterface en VectorstoreInterface
- Event types zijn uitbreidbaar zonder bus-wijziging

## Relatie met andere sprints

```
Sprint 1: Agent Teams SPIKE
    ↓ inzicht: hoe communiceren teammates?
Sprint 2: Event Bus FEAT (deze)
    ↓ event-triggers beschikbaar
Sprint 3: n8n Scheduler SPIKE — n8n als externe event-consumer/producer
```
