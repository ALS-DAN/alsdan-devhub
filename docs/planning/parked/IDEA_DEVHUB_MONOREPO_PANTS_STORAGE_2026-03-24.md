# IDEA: DevHub Monorepo met Pants + StorageInterface

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: "2-3 (cross-fase: infrastructure + knowledge)"
datum: 2026-03-24
---

## Kernidee

DevHub wordt een Pants-gebaseerde Python monorepo die functioneert als Niels' centrale werkbank en dev-team. Binnen deze monorepo worden packages ontwikkeld, getest en gedistribueerd als versioned dependencies naar producten (BORIS, toekomstige projecten). Daarnaast krijgt DevHub een eigen StorageInterface voor vendor-neutrale cloud storage (Google Drive, SharePoint, S3, lokaal) met een reconciliation engine voor declaratief + discovery-gebaseerd mappenbeheer.

Dit idee omvat twee samenhangende onderdelen:
1. **Monorepo-transitie naar Pants** — de structurele basis
2. **StorageInterface + Reconciliation Engine** — een nieuw package binnen de monorepo

## Motivatie

### Waarom Pants monorepo?

DevHub groeit: meer packages (core, agents, skills, governance, storage), meer tests (218+), en straks distributie naar meerdere producten. De huidige flat structuur schaalt niet mee. Pants biedt:

- **Fine-grained caching**: alleen herbouwen/hertesten wat veranderd is
- **Dependency inference**: Pants leest imports via static analysis, geen handmatig bijhouden
- **Hermetische builds**: PEX-distributie — zelfstandige pakketten voor product-delivery
- **Parallel execution**: onafhankelijke taken concurrent
- **uv integratie**: uv als snelle dependency resolver onder Pants, `pyproject.toml` als single source of truth

### Waarom StorageInterface?

DevHub heeft eigen storage-behoeften: research-documenten, kennisbibliotheek, dev-docs, governance-archieven. Deze moeten naar cloud storage (primair Google Drive) met een gestructureerde mappenstructuur die zowel gedeclareerd als ontdekt kan worden. De interface moet vendor-neutraal zijn — dezelfde abstractie voor Drive, SharePoint, S3, lokaal.

### Waarom reconciliation engine?

Mappenstructuren driften. Een reconciliation engine (Kubernetes operator pattern: observe → compare → reconcile) detecteert afwijkingen tussen gewenste staat (declaratieve YAML spec) en actuele staat (wat er echt op Drive/SharePoint staat), en rapporteert of corrigeert drift.

## Architectuurbeslissingen

### 1. DevHub als monorepo — producent/product scheiding

DevHub **produceert** projecten zoals BORIS. BORIS draait **standalone** bij afnemers.

- Tijdens development: monorepo met projecten als submodules (alles bij de hand)
- Bij delivery: producten installeren versioned packages uit DevHub (PEX/wheels via private registry of git tags)
- Wat DevHub distribueert = **dev-tooling en maintenance**: agents, skills, governance-checks, testing utilities
- Product-functionaliteit (bijv. BORIS' eigen document-connectors) = **product-code**, niet DevHub's concern

### 2. Pants + uv als build-systeem

- **Pants** (v2.28+) voor build orchestration, caching, dependency inference, PEX packaging
- **uv** als dependency resolver onder Pants (`uv_requirements` target)
- `pyproject.toml` per package als single source of truth voor dependencies
- Trunk-based development (korte branches, frequente merges)

### 3. StorageInterface — eigen abstractie, niet fsspec

fsspec abstraheert alles als filesystem — dat is de verkeerde abstractie. Object stores (S3, GCS, Azure Blob) en collaboratieplatformen (Google Drive, SharePoint) zijn fundamenteel anders.

DevHub's `StorageInterface` ABC respecteert dit verschil:
- **Frozen dataclasses** als contracten (conform NodeInterface-patroon)
- **Per backend de beste native SDK**: Google Drive API v3, Microsoft Graph SDK, obstore (voor object stores)
- **Geen vendor-types** in het contract — alleen DevHub's eigen types

### 4. Reconciliation engine — Kubernetes operator pattern

- **Declaratieve spec** (YAML): gewenste mappenstructuur, naamconventies, lifecycle-regels
- **Observer**: leest actuele staat via StorageInterface
- **Comparator**: vergelijkt gewenst vs actueel, detecteert drift
- **Reconciler**: idempotente correctieve acties (mappen aanmaken, bestanden verplaatsen, anomalieën rapporteren)
- **Control loop**: periodiek of on-demand

### 5. Hergebruik BORIS-patronen

De technische constructen uit BORIS' `connectors/` worden hergebruikt als patroon, niet als gedeelde library:
- Frozen dataclasses (DocumentMeta, DocumentContent, ConnectorHealth, ChangeEvent)
- Factory pattern met YAML-config
- Auth-abstractie (APIKey, EntraID, GoogleDriveAuth)
- Secrets-provider (env-based, later Vault/Azure Key Vault)
- RBAC met permissie-matrix
- Event-systeem (ChangeEventType, EventReceiverInterface)

DevHub maakt deze patronen **eigen** op development-niveau. BORIS houdt zijn eigen implementatie.

## Voorgestelde packagestructuur

```
alsdan-devhub/                          # Pants workspace root
├── pants.toml                          # Pants configuratie
├── BUILD                               # root targets
├── packages/
│   ├── devhub-core/                    # Python runtime (huidige devhub/)
│   │   ├── BUILD
│   │   ├── pyproject.toml
│   │   └── devhub_core/
│   │       ├── contracts/              # NodeInterface, frozen dataclasses
│   │       ├── adapters/               # BorisAdapter
│   │       ├── agents/                 # orchestrator, docs, qa
│   │       └── registry.py
│   ├── devhub-storage/                 # NIEUW: StorageInterface
│   │   ├── BUILD
│   │   ├── pyproject.toml
│   │   └── devhub_storage/
│   │       ├── interface.py            # StorageInterface ABC
│   │       ├── contracts.py            # frozen dataclasses
│   │       ├── reconciliation/
│   │       │   ├── engine.py           # observe → compare → reconcile
│   │       │   ├── spec.py             # declaratieve layout parser
│   │       │   └── drift.py            # drift detectie + rapportage
│   │       ├── adapters/
│   │       │   ├── google_drive.py     # Google Drive API v3
│   │       │   ├── sharepoint.py       # Microsoft Graph SDK
│   │       │   ├── object_store.py     # obstore (S3/GCS/Azure Blob)
│   │       │   └── local.py            # lokaal filesystem
│   │       ├── auth/                   # auth-abstractie
│   │       ├── secrets/                # secrets-provider
│   │       └── factory.py              # YAML-driven factory
│   ├── devhub-agents/                  # dev-agents als package
│   │   ├── BUILD
│   │   └── pyproject.toml
│   ├── devhub-skills/                  # dev-skills als package
│   │   ├── BUILD
│   │   └── pyproject.toml
│   └── devhub-governance/              # governance checks
│       ├── BUILD
│       └── pyproject.toml
├── plugin/                             # Claude Code plugin definitie
│   ├── BUILD
│   └── plugin.json
├── projects/
│   └── buurts-ecosysteem/              # BORIS als submodule
├── docs/
├── uv.lock                            # gedeelde lockfile
└── pants.toml
```

## StorageInterface — operaties (volledig)

De interface dekt de volledige cyclus die DevHub (en BORIS voor zichzelf) nodig heeft:

### Lezen
- `list(folder)` → bestanden in map
- `get(doc_id)` → bestandsinhoud + metadata
- `search(query)` → zoeken in namen én inhoud
- `tree(root)` → volledige mappenstructuur

### Schrijven
- `put(content, path)` → bestand aanmaken/overschrijven
- `upload(bytes, filename, folder)` → binair bestand uploaden
- `move(source, target)` → bestand verplaatsen
- `mkdir(path)` → map aanmaken
- `delete(doc_id)` → bestand verwijderen

### Organiseren
- `tag(doc_id, tags)` → metadata/tags toevoegen (kennisgradering GOLD/SILVER/BRONZE)
- `relate(doc_id, related_ids)` → relaties leggen tussen bestanden
- `version(doc_id)` → versiegeschiedenis ophalen

### Luisteren
- `watch(callback)` → echte change events (niet snapshot-based)

### Reconciliëren
- `reconcile(spec)` → gewenste staat afdwingen
- `drift_report(spec)` → afwijkingen rapporteren zonder correctie

### Meta
- `health()` → bereikbaarheid + latency
- `quota()` → beschikbare ruimte
- `permissions(doc_id)` → toegangsrechten

## SOTA-technologiekeuzes

| Laag | Keuze | Motivatie |
|------|-------|-----------|
| Build system | Pants 2.28+ | Fine-grained caching, dep inference, PEX, Python plugin API |
| Dependency resolver | uv (onder Pants) | 10-100x sneller dan pip, `pyproject.toml` native |
| Google Drive | Google Drive API v3 | Native SDK, volledige CRUD, officiële MCP support beschikbaar |
| MS365/SharePoint | Microsoft Graph SDK (Python) | Officiële SDK, covers Drive + SharePoint + OneDrive |
| Object stores | obstore | Rust-kern, 9x sneller dan fsspec, native async, S3/GCS/Azure Blob |
| Reconciliation | Kubernetes operator pattern | Bewezen op schaal, observe → compare → reconcile, idempotent |
| Contracten | Frozen dataclasses | Conform DevHub NodeInterface patroon, immutable, vendor-free |

## Impact

| Op | Grootte | Toelichting |
|----|---------|-------------|
| DevHub structuur | **Groot** | Volledige herstructurering naar Pants monorepo |
| devhub-core | **Middel** | Verplaatsen naar packages/, BUILD bestanden toevoegen |
| Agents/Skills | **Middel** | Aparte packages worden, eigen pyproject.toml |
| Governance | **Klein** | Wordt eigen package, bestaande logica blijft |
| BORIS | **Geen** | BORIS blijft ongewijzigd, consumeert later versioned packages |
| Tests | **Klein** | Bestaande tests migreren naar package-level, Pants draait ze |

## Relatie bestaand

- **NodeInterface** (devhub-core): StorageInterface volgt hetzelfde patroon (ABC + frozen dataclasses)
- **BorisAdapter** (devhub-core): blijft bestaan, wordt onderdeel van devhub-core package
- **BORIS connectors** (projects/buurts-ecosysteem/connectors/): inspiratiebron, maar BORIS' eigen code
- **DEV_CONSTITUTION**: Art. 3 (codebase integriteit) vereist zorgvuldige migratie met tests groen

## BORIS impact

- **Direct**: Nee — BORIS' code wijzigt niet
- **Indirect**: Ja — DevHub's distributiemodel verandert. BORIS gaat op termijn versioned packages consumeren in plaats van monorepo-interne imports. Dit vereist afstemming maar is niet blokkerend.

## Risico's en mitigatie

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Pants learning curve | Middel | `pants tailor` genereert BUILD bestanden, plugin API is Python |
| Migratie breekt tests | Hoog | Stapsgewijze migratie, tests groen houden per stap |
| StorageInterface scope creep | Hoog | Eerst interface + local adapter, dan Drive, dan rest |
| Reconciliation complexiteit | Middel | Start met drift-rapportage, later pas correctieve acties |

## Open punten (voor Claude Code)

1. Hoe migreren we bestaande `devhub/` naar `packages/devhub-core/` zonder tests te breken?
2. Pants `pants.toml` configuratie: welke backends, resolves, source roots?
3. StorageInterface: exacte method signatures en return types (frozen dataclasses)?
4. Reconciliation spec format: welke YAML-structuur voor declaratieve layouts?
5. Google Drive auth: service account of OAuth2 flow voor DevHub-context?
6. Distributie-strategie: private PyPI, git tags, of PEX via releases?
7. CI-integratie: Pants remote caching setup (lokaal of cloud)?

## Fasering (voorstel)

### Stap 1: Pants monorepo basis
- Pants installatie en configuratie
- Bestaande `devhub/` → `packages/devhub-core/`
- BUILD bestanden genereren met `pants tailor`
- Alle 218+ tests groen via `pants test ::`

### Stap 2: Package-splitsing
- Agents, skills, governance als aparte packages
- Dependency inference valideren
- PEX packaging testen

### Stap 3: StorageInterface
- ABC + frozen dataclasses ontwerpen
- LocalAdapter als eerste implementatie
- Basistests

### Stap 4: Google Drive adapter
- Google Drive API v3 integratie
- Auth (service account)
- CRUD operaties + tests

### Stap 5: Reconciliation engine
- Declaratieve spec parser
- Observer + comparator
- Drift-rapportage (read-only eerst)
- Correctieve acties (met Niels-goedkeuring per actie)

### Stap 6: Distributie
- PEX packaging naar BORIS
- Versioning strategie
- CI pipeline met Pants remote caching
