---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
node: devhub
sprint_type: FEAT
fase: 4
---

# Sprint Intake: Kennisketen End-to-End — Ingestion, Productie & Drie-Stromen Governance

## Doel

Sluit de twee ontbrekende schakels in de kennisketen zodat het volledige pad van onderzoeksopdracht tot document in Google Drive end-to-end werkt, met drie governance-niveaus voor verschillende kennisstromen.

## Probleemstelling

DevHub heeft alle bouwblokken voor een complete kennisketen, maar de keten is op twee plaatsen verbroken:

**Gat 1 — Knowledge Ingestion:** De research-loop skill schrijft kennis naar `knowledge/{domain}/*.md`, maar niemand duwt die bestanden naar de vectorstore. DocumentService queryt de vectorstore, maar die bevat geen kennis-artikelen. De keten is verbroken tussen "kennis verzamelen" en "kennis gebruiken."

**Gat 2 — Document Production Trigger:** DocumentService is volledig geïmplementeerd (vectorstore → document → storage → Drive), maar er is geen skill, agent of interface die `DocumentService.produce()` aanroept. De orchestrator staat klaar maar wordt nooit getriggerd.

```
research-loop → knowledge/*.md → [GAT 1] → vectorstore → DocumentService → [GAT 2] → Drive
```

Daarnaast ontbreekt een **governance-model** voor drie verschillende kennisstromen:

1. **Basiskennis (stroom 1):** KWP DEV development-kennis die agents nodig hebben. Mag automatisch lopen met kwaliteitsgarantie via KnowledgeCurator.
2. **Systeemkennis (stroom 2):** Kennis die agents detecteren als nodig tijdens hun werk. Vereist menselijke goedkeuring (Art. 1) — agent stelt voor, Niels keurt goed via dashboard.
3. **Niels-kennis (stroom 3):** Onderwerpen die Niels zelf wil onderzoeken. Directe trigger via dashboard of Cowork.

**Waarom nu:** Alle bouwblokken bestaan (documentatie-pipeline Sprint 32+34, Event Bus Sprint 42, DriveSyncAdapter Sprint 38, vectorstore, KnowledgeCurator). Dit is het sluitstuk dat ze verbindt tot een werkend geheel.

**Fase-context:** Fase 4 — Verbindingen. Dit is bij uitstek een "verbindingen"-sprint: geen nieuw package, maar bestaande packages aan elkaar knopen.

## Deliverables

### Knowledge Ingestion Service

- [ ] **KnowledgeIngestor** — nieuwe service in devhub-core die `knowledge/` bestanden verwerkt naar vectorstore:
  - Scan `knowledge/{domain}/*.md` bestanden
  - Parse YAML frontmatter (grade, sources, domain, tags)
  - Chunk content (respecteer heading-structuur)
  - Genereer embeddings via bestaande EmbeddingProvider
  - Push naar vectorstore met metadata (domain, grade, source_id, ingested_at)
  - Track ingestion state: welke bestanden al geïngest zijn (checksum-vergelijking) om duplicaten te voorkomen
  - Incremental: alleen nieuwe of gewijzigde bestanden verwerken

### Drie-Stromen Governance

- [ ] **Stroom 1 — Automatische basiskennis:**
  - Event Bus wiring: `KnowledgeGapDetected` (domein in KWP DEV scope) → auto-research → auto-ingest
  - Kwaliteitsgate: KnowledgeCurator valideert vóór ingestion (minimaal BRONZE, bronvermelding verplicht)
  - Afwijzingen worden gelogd (ObservationEmitted met INGEST_REJECTION)
  - Transparantie: elke auto-actie logt naar Event Bus (auditbaar via dashboard)

- [ ] **Stroom 2 — Agent-geïnitieerde research met goedkeuring:**
  - `ResearchProposal` contract (frozen dataclass): topic, domain, rationale, requesting_agent, priority, proposed_depth
  - Research Queue: file-based (`config/research_queue.yml`) met status per voorstel (PENDING/APPROVED/REJECTED/IN_PROGRESS/COMPLETED)
  - Event Bus: `KnowledgeGapDetected` (buiten KWP DEV scope) → `ResearchProposal` op queue → wacht op goedkeuring
  - Goedkeuring via dashboard (Research-paneel) of via YAML-edit
  - Na goedkeuring: research-loop → ingest → optioneel document produceren

- [ ] **Stroom 3 — Niels-geïnitieerde research:**
  - `ResearchRequest` contract (bestaand) uitbreiden met `requested_by: str` en `output_preference: Optional[DocumentCategory]`
  - Directe trigger: request gaat direct naar IN_PROGRESS (geen goedkeuring nodig)
  - Output: kennis-artikel in vectorstore + optioneel document in Google Drive

### Nieuwe Event Types

- [ ] **`ResearchCompleted`** event — published wanneer research-loop een kennisartikel afrondt. Payload: domain, article_path, grade, source_count.
- [ ] **`KnowledgeIngested`** event — published wanneer KnowledgeIngestor een artikel in de vectorstore plaatst. Payload: article_id, domain, chunk_count, grade.
- [ ] **`DocumentPublished`** event — published wanneer DocumentService een document naar storage schrijft. Payload: document_path, category, storage_path, node_id.

### Document Production Trigger

- [ ] **DocumentService Event Bus integratie:**
  - DocumentService accepteert optionele `event_bus` parameter (consistent met bestaand patroon)
  - Publiceert `DocumentPublished` na succesvolle productie
- [ ] **Programmatische trigger:** `produce_from_knowledge(domain, category, node_id)` — helper die vectorstore queryt op domein en DocumentService aanroept
- [ ] **Wiring helper:** `wire_knowledge_to_docs(bus, document_service)` — optionele automatische flow: `KnowledgeIngested` → auto-produce document (alleen voor stroom 1, configureerbaar)

### End-to-End Verificatie

- [ ] **E2E test:** Schrijf een kennisartikel naar `knowledge/` → ingest naar vectorstore → trigger DocumentService → verifieer document in `output/documents/` met correcte metadata en content uit vectorstore
- [ ] **Drive-test:** Verifieer dat DriveSyncAdapter het document naar het Google Drive sync-pad schrijft (met tmp-dir fallback voor CI)
- [ ] **Stroom-test per governance-niveau:** test dat stroom 1 auto-doorloopt, stroom 2 stopt bij queue, stroom 3 direct triggert

## Afhankelijkheden

- **Geblokkeerd door:** geen — alle benodigde packages en Event Bus zijn operationeel
- **Event Bus (Sprint 42):** ✅ afgerond — InMemoryEventBus, typed events, `wire_knowledge_pipeline()` helper bestaan
- **DocumentService (Sprint 34):** ✅ afgerond — orchestrator, FolderRouter, DriveSyncAdapter werken
- **Vectorstore (Sprint 15+19):** ✅ afgerond — Weaviate + ChromaDB + EmbeddingProvider
- **KnowledgeCurator (Sprint 20):** ✅ afgerond — validate_article(), health_audit()
- **BORIS-impact:** nee — dit is DevHub-intern. BORIS profiteert indirect: zodra BORIS kennis genereert, kan dezelfde pipeline die verwerken.
- **Dashboard relatie:** het NiceGUI dashboard (aparte sprint) wordt de UI voor stroom 2+3. Deze sprint bouwt de backend; het dashboard bouwt de frontend. Kunnen parallel lopen — dashboard leest research_queue.yml, deze sprint schrijft die.

## Fase-context

Fase 4 — Verbindingen. Deze sprint verbindt:
- devhub-vectorstore (kennis opslaan) ↔ knowledge/ directory (kennis bestanden)
- devhub-core/DocumentService (document produceren) ↔ Event Bus (reactief triggeren)
- Research-loop skill (kennis verzamelen) ↔ KnowledgeIngestor (kennis indexeren)

Geen nieuw package nodig. Alle code past in bestaande packages (devhub-core voor services en events, config/ voor research queue).

## Open vragen voor Claude Code

1. **KnowledgeIngestor locatie:** in devhub-core/agents/ (naast DocumentService, KnowledgeCurator)? Of in devhub-vectorstore (dichter bij de vectorstore)? Suggestie: devhub-core — het orkestreert meerdere packages.
2. **Chunking-strategie:** heading-based chunking (split op ## headers) met overlap? Of vaste chunk-grootte? Research-artikelen hebben typisch een heading-structuur — heading-based lijkt logischer.
3. **Ingestion state tracking:** waar bewaar je welke bestanden al geïngest zijn? Opties: (A) `.ingestion_state.yml` in knowledge/ directory, (B) vectorstore metadata query (check of source_id bestaat), (C) devhub-storage. Optie B is simpelst en vereist geen extra state-bestand.
4. **Stroom 1 scope-definitie:** hoe bepaal je welke `KnowledgeGapDetected` events tot stroom 1 (auto) behoren vs stroom 2 (goedkeuring)? Suggestie: domein-gebaseerd — KWP DEV core-domeinen (uit `knowledge.yml` Ring 1) = auto, alles daarbuiten = goedkeuring.
5. **Research Queue formaat:** platte YAML-lijst of geneste structuur? Suggestie:
   ```yaml
   research_queue:
     - id: "rq-001"
       topic: "Event-driven multi-agent architectuur"
       domain: "ai_engineering"
       status: PENDING  # PENDING | APPROVED | REJECTED | IN_PROGRESS | COMPLETED
       requested_by: "coder"  # agent naam of "niels"
       stream: 2  # 1=auto, 2=agent-voorstel, 3=niels
       created_at: "2026-03-28T20:00:00"
       approved_at: null
       completed_at: null
   ```
6. **Document auto-productie:** moet stroom 1 automatisch documenten produceren na ingestion, of alleen kennis in de vectorstore plaatsen? Documenten produceren kost resources — misschien alleen op aanvraag of bij voldoende nieuw materiaal per domein.

## Prioriteit

**Hoog** — dit is het sluitstuk van de hele kennisketen die sinds Fase 3 gebouwd wordt. Zonder deze sprint is DocumentService een motor zonder brandstof (vectorstore leeg) en zonder startknop (geen trigger). Het drie-stromen model geeft Niels de controle die Art. 1 vereist terwijl basiskennis autonoom op peil blijft.

## Technische richting (suggestie — Claude Code mag afwijken)

- KnowledgeIngestor als nieuwe service in `devhub-core/agents/` — consistent met DocumentService en KnowledgeCurator
- ResearchProposal als frozen dataclass in `devhub-core/contracts/pipeline_contracts.py` (uitbreiding)
- Drie nieuwe events in `devhub-core/contracts/event_contracts.py` (uitbreiding)
- Research queue als `config/research_queue.yml` — file-based, dashboard leest/schrijft
- Wire helpers in `devhub-core/events/integrations.py` (uitbreiding van bestaande wire_* functies)
- Stroom-routing: domein-check tegen `knowledge.yml` Ring 1 definitie
- Incrementele ingestion: checksum-vergelijking via vectorstore metadata query

## DEV_CONSTITUTION impact

- **Art. 1 (Menselijke regie):** drie-stromen model garandeert dat stroom 2 en 3 Niels-gestuurd zijn. Stroom 1 is autonoom maar transparant (event logging).
- **Art. 2 (Verificatieplicht):** KnowledgeCurator valideert kennis vóór ingestion — geen ongevalideerde kennis in de vectorstore.
- **Art. 4 (Transparantie):** alle events gelogd, research queue traceerbaar, ingestion state controleerbaar.
- **Art. 5 (Kennisintegriteit):** EVIDENCE-grading doorgetrokken van research → ingestion → document. Documenten erven minimale grade van hun bronnen.
- **Art. 7 (Impact-zonering):** YELLOW — wijzigt bestaande contracts (event_contracts.py, pipeline_contracts.py) en voegt nieuwe services toe. Geen destructieve wijzigingen, maar wel cross-package impact.

## Architectuuroverzicht

```
                    Stroom 1 (auto)          Stroom 2 (goedkeuring)      Stroom 3 (Niels)
                    ────────────────         ──────────────────────      ─────────────────
                    KnowledgeGapDetected     KnowledgeGapDetected        Dashboard formulier
                    (KWP DEV scope)          (buiten scope)              of Cowork
                         │                        │                          │
                         ▼                        ▼                          ▼
                    Auto-research            ResearchProposal →          ResearchRequest →
                         │                   research_queue.yml          direct IN_PROGRESS
                         │                        │                          │
                         │                   Dashboard: Approve?             │
                         │                        │                          │
                         ▼                        ▼                          ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │              research-loop skill                        │
                    │              → knowledge/{domain}/*.md                  │
                    │              → ResearchCompleted event                  │
                    └───────────────────────┬─────────────────────────────────┘
                                            ▼
                    ┌───────────────────────────────────────────────────────┐
                    │              KnowledgeIngestor                        │
                    │              → KnowledgeCurator.validate()            │
                    │              → chunking → embedding → vectorstore     │
                    │              → KnowledgeIngested event                │
                    └───────────────────────┬───────────────────────────────┘
                                            ▼
                    ┌───────────────────────────────────────────────────────┐
                    │              DocumentService.produce()                │
                    │              (auto voor stroom 1, on-demand 2+3)     │
                    │              → FolderRouter → DriveSyncAdapter        │
                    │              → DocumentPublished event                │
                    └───────────────────────┬───────────────────────────────┘
                                            ▼
                                    Google Drive sync
```
