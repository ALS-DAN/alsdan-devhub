# Sprint Intake: devhub-vectorstore — VectorStore Package

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 3 (Track C)
prioriteit: P2
sprint_type: FEAT (stap 1-3), SPIKE→FEAT (stap 4-5)
---

## Doel

DevHub krijgt een eigen vectorstore-package (`devhub-vectorstore`) met Weaviate als productie-backend en ChromaDB als dev/test fallback. Dit package wordt ook gedistribueerd naar producten (BORIS, toekomstige projecten) — elk product draait een eigen standalone Weaviate-instantie.

## Probleemstelling

DevHub heeft een eigen KWP DEV nodig voor dev-kennis, governance, research en ADRs. Daar hoort een vectordatabase bij voor semantisch zoeken. BORIS heeft dit al gebouwd in `weaviate_store/` maar dat is product-code — DevHub mag die niet importeren (Art. 6, project-soevereiniteit). DevHub moet zijn eigen vectorstore-stack bouwen die dezelfde functionaliteit biedt.

Bij delivery krijgt elk product dit package als versioned dependency met een eigen Weaviate-instantie. DevHub beheert de databases van producten niet. Na delivery is de enige verbinding de Claude Code plugin.

**Waarom nu (fase-context):** Track A (uv workspace) is afgerond. Het `devhub-vectorstore` package bestaat al als stub (v0.1.0) in `packages/devhub-vectorstore/`. DevHub's KWP DEV (Fase 3 kerndeliverable) vereist een vectorstore. Parallel met Track B (storage), niet afhankelijk ervan.

## BORIS Weaviate-referentie (geverifieerd)

Gebaseerd op lezing van BORIS repo deze sessie:

| Aspect | BORIS implementatie |
|--------|-------------------|
| Versie | Weaviate 1.27.6 |
| Hosting | Docker (8080 HTTP + 50051 gRPC) |
| Collecties | BuurtsRed, BuurtsYellow, BuurtsGreen, BuurtsInteraction, Evidence |
| Embeddings | Lokaal: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, sentence-transformers) |
| Vectorizer | `none` (Weaviate berekent niets zelf) |
| Multi-tenancy | Per KWP via Weaviate native tenant-sharding |
| Dev fallback | ChromaDB |
| Toekomstig | `BAAI/bge-m3` (1024-dim, hybrid retrieval) — ADR-041 |

DevHub's package volgt dezelfde patronen maar met eigen collecties en configuratie.

## Deliverables

### Stap 1: Interface + contracts (GROEN) — 🎯 SPRINT 1
- [ ] `packages/devhub-vectorstore/` uitbouwen van bestaande stub (v0.1.0)
- [ ] `VectorStoreInterface` ABC met kernoperaties: add_chunk, add_chunks, query, count, count_by_zone, reset, ensure_tenant, list_tenants, health
- [ ] Frozen dataclasses: `DocumentChunk`, `RetrievalRequest`, `RetrievalResponse`, `SearchResult`, `VectorStoreHealth`
- [ ] `DataZone` enum (configureerbaar per product — niet hardcoded als Red/Yellow/Green)
- [ ] `TenantStrategy` enum (per_zone, per_kwp)
- [ ] Unit tests voor contract-validatie (frozen, immutable)

### Stap 2: ChromaDB adapter (GROEN) — 🎯 SPRINT 1
- [ ] `ChromaDBZonedStore(VectorStoreInterface)` — dev/test fallback
- [ ] Zone-collecties aanmaken op basis van configuratie
- [ ] CRUD operaties + query
- [ ] Tests (snel, geen externe services nodig)

### Stap 3: Weaviate adapter (GEEL)
- [ ] `WeaviateZonedStore(VectorStoreInterface)` — productie-backend
- [ ] Zone-collecties schema-provisioning
- [ ] gRPC + HTTP connectie-opties
- [ ] Mock-based tests (geen running Weaviate in CI, conform BORIS-patroon)
- [ ] Docker-compose voor lokale Weaviate

### Stap 4: Multi-tenancy (GEEL)
- [ ] `per_zone` strategie: data-isolatie via aparte collecties
- [ ] `per_kwp` strategie: Weaviate native tenant-sharding binnen collecties
- [ ] `ensure_tenant()`, `list_tenants()` implementatie
- [ ] Tenant-scoped queries
- [ ] Tests voor isolatie-garanties

### Stap 5: Embedding providers (GROEN)
- [ ] `EmbeddingProvider` ABC
- [ ] `MiniLMProvider`: paraphrase-multilingual-MiniLM-L12-v2 (384-dim)
- [ ] `BgeM3Provider`: BAAI/bge-m3 (1024-dim, hybrid) — voorbereid, niet verplicht initieel
- [ ] Configureerbare provider via factory
- [ ] Benchmark-tests: embedding latency + dimensie-validatie

### Stap 6: DevHub eigen Weaviate (GEEL)
- [ ] Docker-compose voor DevHub's Weaviate-instantie
- [ ] DevHub-specifieke collecties: DevKnowledge, DevResearch, DevADR, DevGovernance
- [ ] Initiële inrichting KWP DEV
- [ ] Health check integratie met devhub-health skill

### Stap 7: BORIS-migratie (ROOD — Fase 4, apart traject)
- [ ] BORIS migreert van eigen `weaviate_store/` naar devhub-vectorstore package
- [ ] BORIS behoudt eigen Weaviate-instantie met eigen collecties
- [ ] **Vereist expliciete Niels-goedkeuring (Art. 1)**

## Grenzen (wat we NIET doen)

- Geen gedeelde Weaviate-instantie tussen DevHub en producten — elk krijgt eigen instantie
- Geen BORIS-specifieke collectienamen (BuurtsRed etc.) in het package — collecties zijn configureerbaar
- Geen hybrid search in eerste versie — dense search (cosine) eerst, hybrid later via bge-m3
- Geen Weaviate Cloud integratie — Docker self-hosted als standaard
- DevHub beheert na delivery geen product-databases

## Appetite

Stap 1-2: 1 sprint (FEAT). Stap 3-4: 1 sprint (FEAT). Stap 5: 0.5 sprint. Stap 6: 0.5 sprint. Totaal: 2-3 sprints verspreid over Fase 3. Stap 7 is Fase 4 (apart traject).

## Sprint 1 scope (direct uitvoerbaar)

**Alleen Stap 1 + 2** — volledig GROEN, geen externe afhankelijkheden.

Deliverables Sprint 1:
- VectorStoreInterface ABC (9 kernoperaties)
- 5 frozen dataclasses (DocumentChunk, RetrievalRequest, RetrievalResponse, SearchResult, VectorStoreHealth)
- DataZone enum (configureerbaar, niet hardcoded)
- TenantStrategy enum (per_zone, per_kwp)
- ChromaDBZonedStore adapter implementatie
- Unit tests (snel, geen externe services nodig)
- Package correct geregistreerd in uv workspace

**Acceptatiecriteria:**
- Alle bestaande tests (394+) blijven groen
- ChromaDB adapter CRUD + query operaties werken
- DataZone is configureerbaar per product (geen BuurtsRed/Yellow/Green hardcoding)
- Package importeerbaar vanuit andere workspace packages
- EmbeddingProvider ABC voorbereid (Stap 5) maar niet verplicht voor Sprint 1

**Na Sprint 1:** Stap 3 (Weaviate adapter, GEEL) en 4 (Multi-tenancy, GEEL) worden apart gepland.

## Afhankelijkheden

- **Geblokkeerd door:** ~~Track A (uv workspace transitie)~~ → **Niets meer** (Track A afgerond, stub bestaat)
- **Niet afhankelijk van:** Track B (storage) — volledig parallel
- **BORIS impact:** Indirect. Stap 7 (BORIS-migratie) is Fase 4 en vereist Niels-goedkeuring. Stap 1-6 raken BORIS niet.

## Technische richting

(Claude Code mag afwijken)

- Interface volgt NodeInterface-patroon: ABC + frozen dataclasses
- Weaviate client v4.5+ (conform BORIS)
- Embeddings lokaal berekend via sentence-transformers (vectorizer: none)
- Factory pattern met YAML-config (conform `config/nodes.yml` patroon)
- Collectienamen configureerbaar, niet hardcoded
- Docker-compose per instantie

**Gedeeld patroon met Track B (devhub-storage):** Beide packages volgen identiek architectuurpatroon (ABC + frozen dataclasses + factory + YAML-config). Sprint 1 van beide tracks loopt parallel — zorg dat het patroon consistent is. Overweeg een gedeelde base class of utility in devhub-core als dat de consistentie borgt.

## Risico's

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Scope creep (te veel BORIS-features kopiëren) | Hoog | Alleen interface + 2 adapters + embedding. BORIS-specifieke logica blijft bij BORIS. |
| Weaviate versie-incompatibiliteit | Middel | Pin op 1.27.x, upgrade pas bij bewezen stabiliteit |
| Embedding model wisseling breekt indexen | Hoog | Versie-metadata per collectie, re-index tooling |
| sentence-transformers dependency zwaar (~500MB) | Middel | Optional dependency, lazy loading |

## Open vragen voor Claude Code

1. Exacte collectie-schema: welke properties zijn generiek vs. product-specifiek?
2. Hoe configureren we collectienamen per product? Via `config/nodes.yml` of apart config-bestand?
3. Migratie-tooling: moeten we ChromaDB → Weaviate migratie meenemen (zoals BORIS heeft)?
4. Health check: integreren we vectorstore-health in de bestaande 6-dimensie health check of wordt het dimensie 7?

## DEV_CONSTITUTION impact

- **Art. 3** (Codebase-integriteit): Nieuw package, geen bestaande code raakt
- **Art. 5** (Kennisintegriteit): KWP DEV collecties krijgen EVIDENCE-grading
- **Art. 6** (Project-soevereiniteit): BORIS' `weaviate_store/` wordt niet geïmporteerd of gewijzigd
- **Art. 7** (Impact-zonering): Stap 1-2 GROEN, stap 3-6 GEEL, stap 7 ROOD
- **Art. 8** (Dataminimalisatie): Weaviate auth-tokens niet in commits
