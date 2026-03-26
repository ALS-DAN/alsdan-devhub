# Sprint 4 — devhub-vectorstore (Stap 1 + 2)

---
status: DONE ✅
start: 2026-03-26
einde: 2026-03-26
type: FEAT
zone: GREEN
package: devhub-vectorstore v0.2.0
---

## Doel

DevHub krijgt een eigen vectorstore-package met contracts en ChromaDB adapter als dev/test backend. Eerste twee stappen van het 7-staps vectorstore-plan.

## Deliverables

### Stap 1: Interface + Contracts ✅

- `DataZone` enum — RESTRICTED, CONTROLLED, OPEN (generiek, niet product-specifiek)
- `TenantStrategy` enum — PER_ZONE, PER_KWP
- 5 frozen dataclasses: `DocumentChunk`, `RetrievalRequest`, `RetrievalResponse`, `SearchResult`, `VectorStoreHealth`
- `VectorStoreInterface` ABC — 9 abstractmethods
- `EmbeddingProvider` ABC — stub voor Sprint 5
- 41 contract-tests

### Stap 2: ChromaDB Adapter ✅

- `ChromaDBZonedStore(VectorStoreInterface)` — volledige implementatie
- Zone-isolatie via aparte ChromaDB collecties
- CRUD, batch operations, query met score filtering
- Tenant management (metadata-based)
- ChromaDB als optional dependency (lazy import)
- 28 adapter-tests (ephemeral client, geïsoleerd per test)

### Integratie ✅

- `VectorStoreFactory.create("chromadb", zones=[...])` — factory pattern
- String-naar-enum conversie voor zones
- Publieke exports via `__init__.py`
- Root testpaths uitgebreid
- 9 factory/import-tests

## Test-delta

| Metric | Start | Einde | Delta |
|--------|-------|-------|-------|
| Tests totaal | 497 | 575 | +78 |
| Lint errors | 0 | 0 | 0 |
| Package versie | 0.1.0 | 0.2.0 | — |

## Design-keuzes

1. **DataZone = RESTRICTED/CONTROLLED/OPEN** — generiek, producten mappen eigen zones
2. **Metadata als `tuple[tuple[str,str],...]`** — echte immutability, `metadata_dict` property voor gemak
3. **ChromaDB = optional dependency** — contracts importeerbaar zonder chromadb
4. **Embedding optioneel op DocumentChunk** — ChromaDB kan zonder, Weaviate-adapter vereist ze later
5. **Config via factory kwargs** — geen YAML-config in Sprint 1

## Fixes onderweg

- `.venv/bin/pytest` had stale shebang naar oud `buurts-devhub` pad → gefixt via `uv sync --reinstall`
- ChromaDB EphemeralClient deelt state → test-isolatie via unieke collection-prefix per test
- ChromaDB rejects leeg metadata dict → `None` gebruiken i.p.v. `{}`
- Test-bestandsnamen moeten uniek zijn over workspace packages → prefix `test_vectorstore_*`

## Bestanden (nieuw)

```
packages/devhub-vectorstore/
  devhub_vectorstore/
    __init__.py                              (gewijzigd)
    contracts/
      __init__.py                            (nieuw)
      vectorstore_contracts.py               (nieuw — kernbestand)
    adapters/
      __init__.py                            (nieuw)
      chromadb_adapter.py                    (nieuw — kernbestand)
    factory.py                               (nieuw)
  tests/
    test_vectorstore_contracts.py            (nieuw)
    test_vectorstore_chromadb.py             (nieuw)
    test_vectorstore_factory.py              (nieuw)
  pyproject.toml                             (gewijzigd → v0.2.0)
```

Root: `pyproject.toml` — testpaths uitgebreid, chromadb als dev-dependency.

## Volgende sprint

Stap 3 (Weaviate adapter, GEEL) en Stap 4 (Multi-tenancy, GEEL) — apart te plannen.
