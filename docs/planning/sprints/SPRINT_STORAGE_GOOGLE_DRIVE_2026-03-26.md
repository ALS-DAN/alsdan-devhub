# Sprint: Storage Google Drive Adapter (Track B S2)

## Meta
- **Track:** B (Storage), Sprint 2
- **Golf:** 2 (Uitbouw)
- **Status:** ACTIEF
- **Baseline:** 662 tests
- **Parallel met:** Track C S2 (Vectorstore Weaviate)

## Doel
Google Drive adapter voor StorageInterface — lezen/schrijven via Google Drive API. Zelfde ABC-contract als LocalAdapter. Auth-abstractie voor hergebruik door toekomstige adapters.

## Deliverables

| # | Deliverable | Pad |
|---|-------------|-----|
| D1 | StorageAuth ABC + implementaties | `packages/devhub-storage/devhub_storage/auth.py` |
| D2 | GoogleDriveAdapter klasse | `packages/devhub-storage/devhub_storage/adapters/google_drive_adapter.py` |
| D3 | StorageFactory | `packages/devhub-storage/devhub_storage/factory.py` |
| D4 | Unit tests (mocked API) | `packages/devhub-storage/tests/test_google_drive_adapter.py`, `tests/test_auth.py`, `tests/test_factory.py` |
| D5 | pyproject.toml update | `packages/devhub-storage/pyproject.toml` |

## Fasen

### Fase 1: Auth-abstractie
- StorageAuth ABC met authenticate() methode
- ServiceAccountAuth: JSON key-file pad
- OAuth2Auth: client secrets + token cache
- Credentials NOOIT in code (Art. 8)

### Fase 2: GoogleDriveAdapter
- 9 StorageInterface methoden implementeren
- Lazy import googleapiclient
- Path-model: `/folder/file.txt` met gecachte folder-ID lookups
- Resumable uploads voor grote bestanden

### Fase 3: Factory + mixins
- StorageFactory.create(backend="local"|"google_drive")
- Organizable: Drive labels als tags
- Watchable: Changes API

### Fase 4: QA + afsluiting
- Tests groen, ruff clean
- Exports bijwerken

## DoR Checklist
- [x] Scope gedefinieerd
- [x] Baseline tests slagen (662)
- [x] Afhankelijkheden afgerond (Storage S1)
- [x] Acceptatiecriteria: 9 interface-methoden + factory + auth + tests
- [x] Risico's: auth-tokens, API rate limits
- [x] n8n impact: geen

## Risico's
| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Google API auth-complexiteit | Middel | Mock-first, integratie-test apart |
| API rate limits | Laag | Exponential backoff in adapter |
