# Sprint Intake: devhub-storage — StorageInterface Package

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 3 (Track B)
prioriteit: P3
sprint_type: FEAT (stap 1-2), SPIKE→FEAT (stap 3-5)
---

## Doel

DevHub krijgt een vendor-neutraal storage-package (`devhub-storage`) voor bestandsopslag op Google Drive, SharePoint, S3 en lokaal filesystem, met een reconciliation engine voor declaratief mappenbeheer.

## Probleemstelling

DevHub heeft geen eigen opslaglaag. Research-documenten, kennisbibliotheek, governance-archieven en dev-docs staan nu als losse bestanden in de git-repo of lokaal op schijf. Er is geen gestructureerde manier om bestanden naar cloud storage te synchroniseren, te doorzoeken of drift te detecteren. Wanneer DevHub producten als BORIS aflevert, moeten die producten dezelfde storage-abstractie kunnen gebruiken voor hun eigen MS365/Drive-koppelingen.

**Waarom nu (fase-context):** Track B start na Track A (uv workspace). De package-structuur moet staan voordat devhub-storage als package kan bestaan. Niet blokkerend voor Track C (vectorstore).

## Deliverables

### Stap 1: Interface + LocalAdapter (GROEN)
- [ ] `packages/devhub-storage/` aanmaken in uv workspace
- [ ] `StorageInterface` ABC met 9 kernoperaties: list, get, search, tree, put, mkdir, move, delete, health
- [ ] Frozen dataclasses: `StorageItem`, `StorageTree`, `StorageHealth`, `WriteResult`
- [ ] `LocalAdapter(StorageInterface)` — filesystem-backend
- [ ] Unit tests voor LocalAdapter (CRUD + edge cases: path traversal, symlinks)
- [ ] Property-based tests voor beveiligingsrandgevallen

### Stap 2: Extensie-mixins (GROEN)
- [ ] `Organizable` mixin: tag, relate, version
- [ ] `Watchable` mixin: watch (change events)
- [ ] `Reconcilable` mixin: reconcile, drift_report
- [ ] Mixins zijn optioneel per adapter — niet elke backend hoeft alles te implementeren

### Stap 3: Google Drive adapter (GEEL)
- [ ] `GoogleDriveAdapter(StorageInterface, Organizable, Watchable)`
- [ ] Google Drive API v3 SDK integratie
- [ ] Auth via service account (environment-based secrets, Art. 8)
- [ ] Rate limiter (1.000 req/100s quota)
- [ ] Mock-based tests + optioneel live integratietest

### Stap 4: SharePoint adapter (GEEL)
- [ ] `SharePointAdapter(StorageInterface, Organizable)`
- [ ] Microsoft Graph SDK integratie
- [ ] EntraID auth-flow
- [ ] Mock-based tests

### Stap 5: Reconciliation engine (GEEL → ROOD voor correctieve acties)
- [ ] YAML spec-parser voor gewenste mappenstructuur
- [ ] Observer: actuele staat via StorageInterface
- [ ] Comparator: diff gewenst vs. actueel
- [ ] `drift_report()` — read-only (GEEL)
- [ ] `reconcile()` — correctieve acties (ROOD, Niels-goedkeuring per actie)
- [ ] Idempotentie-tests: reconcile(reconcile(x)) == reconcile(x)

## Grenzen (wat we NIET doen)

- Geen volledige filesystem-abstractie à la fsspec — elk backend gebruikt native SDK
- Geen realtime sync — reconciliation is periodiek of on-demand
- Geen eigen file viewer/editor — alleen CRUD + metadata
- Geen BORIS-specifieke logica — BORIS implementeert eigen adapters als dat nodig is
- Object stores (S3/GCS/Azure Blob via obstore) zijn **optioneel** en niet in scope voor initiële sprint

## Appetite

Stap 1-2: 1 sprint (FEAT). Stap 3-4: elk 1 sprint (FEAT). Stap 5: 1 sprint (SPIKE→FEAT). Totaal: 3-4 sprints verspreid over Fase 3.

## Afhankelijkheden

- **Geblokkeerd door:** Track A (uv workspace transitie) — package-structuur moet staan
- **BORIS impact:** Indirect. BORIS kan op termijn devhub-storage consumeren voor MS365-koppeling. Niet blokkerend — BORIS heeft eigen connectors/.

## Technische richting

(Claude Code mag afwijken)

- Interface volgt NodeInterface-patroon: ABC + frozen dataclasses
- Per backend native SDK: Google Drive API v3, Microsoft Graph SDK
- Factory pattern met YAML-config (conform `config/nodes.yml` patroon)
- Auth-abstractie: environment-based secrets, nooit hardcoded (Art. 8)

## Risico's

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Scope creep (te veel operaties) | Hoog | Mixins gefaseerd, kerninterface is 9 ops |
| Google Drive rate limits | Middel | Rate limiter in observer, exponential backoff |
| SharePoint permissiemodel complexiteit | Middel | Accepteer informatieverlies in vendor-neutrale abstractie |
| Credentials in code/commits | Hoog | Art. 8 + detect-secrets pre-commit hook |

## Open vragen voor Claude Code

1. Exacte method signatures en return types voor de 9 kernoperaties?
2. Hoe integreert de factory met `config/nodes.yml` — apart config-bestand of uitbreiden?
3. Google Drive auth: service account of OAuth2 flow?
4. Reconciliation YAML spec format: welke structuur?

## DEV_CONSTITUTION impact

- **Art. 3** (Codebase-integriteit): Nieuwe package, geen bestaande code raakt. Tests moeten groen.
- **Art. 7** (Impact-zonering): Stap 1-2 GROEN, stap 3-4 GEEL, stap 5 ROOD (correctieve acties)
- **Art. 8** (Dataminimalisatie): Credentials-beheer is kernrisico
