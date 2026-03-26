# Sprint: Vectorstore Weaviate + Multi-tenancy (Track C S2)

## Meta
- **Track:** C (Vectorstore), Sprint 2
- **Golf:** 2 (Uitbouw)
- **Status:** ACTIEF
- **Baseline:** 662 tests
- **Parallel met:** Track B S2 (Storage Google Drive)

## Doel
Weaviate adapter voor VectorStoreInterface — compatibel met BORIS Weaviate (1.27.x, 384-dim embeddings). Multi-tenancy ondersteuning via PER_ZONE en PER_KWP strategieen. Kritiek pad naar KWP DEV.

## Deliverables

| # | Deliverable | Pad |
|---|-------------|-----|
| D1 | WeaviateZonedStore klasse | `packages/devhub-vectorstore/devhub_vectorstore/adapters/weaviate_adapter.py` |
| D2 | Multi-tenancy (PER_ZONE + PER_KWP) | Geintegreerd in D1 |
| D3 | Factory-uitbreiding | `packages/devhub-vectorstore/devhub_vectorstore/factory.py` |
| D4 | Unit tests (mocked Weaviate) | `packages/devhub-vectorstore/tests/test_vectorstore_weaviate.py` |
| D5 | pyproject.toml update | `packages/devhub-vectorstore/pyproject.toml` |

## Fasen

### Fase 1: Weaviate adapter basis
- WeaviateZonedStore klasse met lazy import
- Constructor: url, api_key, zones, collection_prefix, tenant_strategy
- Zone-collection mapping: `{prefix}_{zone.value}`
- Configuratie-validatie

### Fase 2: CRUD operaties
- add_chunk / add_chunks: batch insert
- query: near_vector search, zone-filtering, score-conversie
- count / count_by_zone: aggregate queries
- reset: collection delete + recreate

### Fase 3: Multi-tenancy
- PER_ZONE: 1 collection per zone (default)
- PER_KWP: 1 collection per KWP-domein, zones als metadata-filter
- ensure_tenant / list_tenants

### Fase 4: Factory + health + QA
- Factory update: backend="weaviate"
- health(): cluster status
- Tests groen, ruff clean

## DoR Checklist
- [x] Scope gedefinieerd
- [x] Baseline tests slagen (662)
- [x] Afhankelijkheden afgerond (Vectorstore S1)
- [x] Acceptatiecriteria: 9 interface-methoden + multi-tenancy + factory
- [x] Risico's: R2 (sentence-transformers), R3 (Weaviate versie)
- [x] n8n impact: geen

## BORIS-compatibiliteit
- Weaviate 1.27.x, 384-dim vectoren
- BORIS code wordt NIET geimporteerd (Art. 6)
- Adapter is generiek, werkt met elke Weaviate instantie

## Risico's
| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Weaviate v4 API changes | Middel | Pin >=4.0,<5.0 |
| sentence-transformers (500MB) | Middel | Optional dep, Sprint 5 |
