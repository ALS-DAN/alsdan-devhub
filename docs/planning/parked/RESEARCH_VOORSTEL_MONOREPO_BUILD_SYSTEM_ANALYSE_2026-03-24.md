# Architectuuranalyse: DevHub Monorepo + uv Workspaces

---
gegenereerd_door: "Cowork Architect — alsdan-devhub"
status: INBOX
fase: "2-3 (cross-fase: infrastructure + knowledge)"
datum: 2026-03-24
type: RESEARCH + ARCHITECTUURANALYSE
impact_zonering: YELLOW (architectuur-impact, meerdere componenten)
dev_constitution_impact: "Art. 3 (codebase-integriteit), Art. 4 (traceerbaarheid), Art. 7 (impact-zonering)"
---

## Genomen beslissingen

| Beslissing | Keuze | Motivatie |
|------------|-------|-----------|
| Build-systeem | **uv workspaces + pex** (niet Pants) | Pants is overkill voor DevHub's omvang (~2K regels, 18 tests, 1 dev). uv biedt 90% van de voordelen bij 20% van de complexiteit. Pants als escape hatch als DevHub >20 packages groeit. |
| Fasering | **Gescheiden tracks** | Track A (monorepo) eerst, daarna Track B (storage) en Track C (vectorstore) parallel |
| StorageInterface scope | **Alle operaties, gefaseerd als mixins** | Kerninterface (9 ops) eerst, dan Organizable, Watchable, Reconcilable als extensies per adapter |

## Architectuurmodel

```
DevHub (producent)
│
├── Eigen Weaviate-instantie          ← KWP DEV, dev-kennis, governance
│
├── Levert packages aan producten:
│   ├── devhub-core                   ← contracts, adapters, registry
│   ├── devhub-storage                ← bestandsopslag (Drive, SharePoint, lokaal)
│   ├── devhub-vectorstore            ← Weaviate/ChromaDB vectorstore stack
│   ├── devhub-agents                 ← plugin agents
│   ├── devhub-skills                 ← plugin skills
│   └── devhub-governance             ← compliance checks
│
└── Producten (standalone na delivery):
    ├── BORIS
    │   ├── Eigen Weaviate-instantie  ← BuurtsRed/Yellow/Green, Evidence
    │   ├── MS365-koppeling           ← SharePoint/OneDrive
    │   └── Communiceert met DevHub alleen via Claude Code plugin
    │
    └── Toekomstig product X
        ├── Eigen Weaviate-instantie
        └── Standalone, niet gekoppeld aan DevHub
```

**Kernprincipe:** Elk product krijgt bij delivery een eigen standalone database. DevHub beheert de databases van producten niet. Na delivery is de enige verbinding de Claude Code plugin voor development-taken.

## Package: devhub-vectorstore

Gebaseerd op BORIS's bewezen `weaviate_store/` patronen (geverifieerd in repo). DevHub bouwt dit als distribueerbaar package. BORIS's eigen `weaviate_store/` wordt op termijn (Fase 4, met Niels-goedkeuring) vervangen door dit package.

**BORIS's huidige Weaviate-setup (geverifieerd):**
- Weaviate 1.27.6, Docker (8080 HTTP + 50051 gRPC)
- 5 collecties: BuurtsRed, BuurtsYellow, BuurtsGreen, BuurtsInteraction, Evidence
- Embeddings lokaal berekend: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim)
- Multi-tenancy per KWP via Weaviate native tenant-sharding
- ChromaDB als dev/test fallback
- Factory pattern, swappable backends

**devhub-vectorstore bevat dezelfde functionaliteit, vendor-neutraal:**

```
packages/devhub-vectorstore/
├── pyproject.toml
├── devhub_vectorstore/
│   ├── interface.py            # VectorStoreInterface ABC
│   ├── contracts.py            # Zone, Tenant, DocumentChunk, RetrievalRequest/Response
│   ├── zones.py                # DataZone enum + zone-configuratie
│   ├── tenancy.py              # TenantStrategy (per_zone, per_kwp)
│   ├── adapters/
│   │   ├── weaviate/
│   │   │   ├── zoned_store.py  # WeaviateZonedVectorStore
│   │   │   ├── interaction.py  # InteractionStore
│   │   │   ├── collections.py  # Schema-provisioning
│   │   │   └── migration.py    # Migratie-tooling
│   │   └── chromadb/
│   │       └── zoned_store.py  # Dev/test fallback
│   ├── embeddings/
│   │   ├── provider.py         # EmbeddingProvider ABC
│   │   ├── minilm.py           # MiniLM-L12-v2 (384-dim)
│   │   └── bge_m3.py           # bge-m3 (1024-dim, hybrid)
│   ├── config.py               # Connection, tenant strategy
│   ├── factory.py              # YAML-driven instantiatie
│   └── health.py               # Health checks
└── tests/
```

## Package: devhub-storage

Bestandsopslag — Google Drive, SharePoint, S3, lokaal filesystem. Gescheiden van vectorstore.

**Interface-opbouw via mixins:**

```python
# Fase 1 — kerninterface (9 operaties)
class StorageInterface(ABC):
    # list, get, search, tree, put, mkdir, move, delete, health

# Fase 2+ — extensies
class Organizable(ABC):     # tag, relate, version
class Watchable(ABC):       # watch (change events)
class Reconcilable(ABC):    # reconcile, drift_report

# Adapter implementeert wat relevant is:
class GoogleDriveAdapter(StorageInterface, Organizable, Watchable): ...
class LocalAdapter(StorageInterface): ...
```

## Mappenstructuur (uv workspaces)

```
alsdan-devhub/                          # uv workspace root
├── pyproject.toml                      # workspace definitie
├── uv.lock                             # gedeelde lockfile
├── packages/
│   ├── devhub-core/                    # huidige devhub/ → herstructureerd
│   │   ├── pyproject.toml
│   │   ├── devhub_core/
│   │   │   ├── contracts/              # NodeInterface, dev_contracts, security
│   │   │   ├── adapters/              # BorisAdapter
│   │   │   ├── agents/                # orchestrator, docs, qa
│   │   │   └── registry.py
│   │   └── tests/
│   ├── devhub-vectorstore/             # Weaviate/ChromaDB stack
│   │   ├── pyproject.toml
│   │   ├── devhub_vectorstore/
│   │   └── tests/
│   ├── devhub-storage/                 # bestandsopslag (Drive, SP, lokaal)
│   │   ├── pyproject.toml
│   │   ├── devhub_storage/
│   │   └── tests/
│   ├── devhub-agents/                  # plugin agents
│   ├── devhub-skills/                  # plugin skills
│   └── devhub-governance/              # governance checks
├── plugin/                             # Claude Code plugin definitie
├── config/nodes.yml
├── projects/buurts-ecosysteem/         # BORIS submodule
├── docs/
└── knowledge/
```

## Tracks & fasering

### Track A: uv workspace + package-splitsing (eerst)

| Stap | Wat | Zonering |
|------|-----|----------|
| A1 | uv installatie, workspace config, `devhub/` → `packages/devhub-core/` | GROEN |
| A2 | Alle imports updaten, 218+ tests groen | GROEN |
| A3 | Agents, skills, governance als aparte packages | GEEL |
| A4 | PEX packaging valideren | GROEN |

### Track B: StorageInterface (na Track A)

| Stap | Wat | Zonering |
|------|-----|----------|
| B1 | ABC + frozen dataclasses + LocalAdapter | GROEN |
| B2 | Google Drive adapter + auth | GEEL |
| B3 | Organizable/Watchable mixins | GEEL |
| B4 | Reconciliation engine (drift-rapportage) | GEEL |
| B5 | Reconciliation (correctieve acties) | ROOD |

### Track C: devhub-vectorstore (na Track A, parallel met B)

| Stap | Wat | Zonering |
|------|-----|----------|
| C1 | ABC + contracts + frozen dataclasses | GROEN |
| C2 | ChromaDB adapter (dev/test) | GROEN |
| C3 | Weaviate adapter (zones, CRUD) | GEEL |
| C4 | Multi-tenancy (per_zone + per_kwp) | GEEL |
| C5 | Embedding providers (MiniLM, later bge-m3) | GROEN |
| C6 | Migratie-tooling (ChromaDB → Weaviate) | GEEL |
| C7 | DevHub eigen Weaviate-instantie (KWP DEV) | GEEL |
| C8 | BORIS migreert naar devhub-vectorstore | ROOD (Fase 4) |

Track B en C zijn onafhankelijk van elkaar, beide afhankelijk van Track A.

## Test-strategie

Elke fase: bestaande 218+ tests groen (Art. 3), nieuwe tests ≥80% coverage, Ruff clean, frozen dataclasses, geen secrets in code (Art. 8).

**Per track:**
- **Track A:** Smoke tests (alle imports resolven), PEX packaging test
- **Track B:** Unit tests per adapter, contract tests (adapter voldoet aan ABC), property-based tests (path traversal)
- **Track C:** Mock-based tests (geen running Weaviate in CI, conform BORIS-patroon), contract tests, embedding-validatie

## Kennisgradering

| Claim | Gradering | Bron |
|-------|-----------|------|
| DevHub ~2.000 regels Python, 18 tests, 1 dep (PyYAML) | **Geverifieerd** | Codebase gelezen deze sessie |
| Pants 2.31 is laatste release (feb 2026) | **Geverifieerd** | pantsbuild.org |
| uv workspaces mist affected-test detection | **Geverifieerd** | GitHub issue #6356 |
| BORIS Weaviate 1.27.6, 5 collecties, MiniLM-L12-v2 | **Geverifieerd** | BORIS repo gelezen deze sessie |
| BORIS multi-tenancy per KWP, ChromaDB fallback | **Geverifieerd** | BORIS repo gelezen deze sessie |
| uv + pex combinatie werkt voor distributie | **Aangenomen** | FOSDEM 2026 talk, niet lokaal gevalideerd |

## Bronnen

- [Pants 2.31.0 release](https://www.pantsbuild.org/blog/2026/02/19/pants-2-31)
- [FOSDEM 2026 — Modern Python monorepo with uv](https://fosdem.org/2026/schedule/event/WE7NHM-modern-python-monorepo-apache-airflow/)
- [uv Workspaces](https://gist.github.com/Yuzu02/0f53c6f73a471077c3268c4a42aef60a)
- [uv affected-test discussion — GitHub #6356](https://github.com/astral-sh/uv/issues/6356)
- BORIS repo: `projects/buurts-ecosysteem/` (Weaviate-integratie, ADR-006)
