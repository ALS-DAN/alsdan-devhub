# Sprint Intake: Kennispipeline Golf 1B — DocumentInterface ABC + ODF Adapter

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
prioriteit: P2 (vereist voor document-output in analyse pipeline)
sprint_type: FEAT
cynefin: complicated (bekende patronen, volgt bestaand ABC patroon)
impact_zone: GROEN (nieuw package, raakt geen bestaande code)
kennispipeline_golf: 1
parallel_met: [KENNISPIPELINE_GOLF1A_RESEARCH_CONTRACTS, TRACK_B_S2_GOOGLE_DRIVE]
geblokkeerd_door: geen
volgende_stap: KENNISPIPELINE_GOLF3_ANALYSE_PIPELINE
---

## Doel

Bouw een vendor-agnostic DocumentInterface ABC met ODF-adapter (.odt) als primair output-formaat. Volgt hetzelfde patroon als StorageInterface en VectorStoreInterface.

## Probleemstelling

DevHub kan kennis opslaan (vectorstore) en ophalen (researcher), maar heeft geen manier om gestructureerde documenten te genereren. Voor analyse-output, rapportages en kennisexport is document-generatie essentieel. De output moet vendor-agnostic zijn — geen afhankelijkheid van Microsoft-formaten.

ODF (Open Document Format, ISO/IEC 26300) is de open standaard hiervoor. Het is native in LibreOffice en breed ondersteund.

## Deliverables

### DocumentInterface ABC

- [ ] **DI-01** — `DocumentInterface` ABC in nieuw package `packages/devhub-documents/`
  - Workspace package, volgt patroon van devhub-storage en devhub-vectorstore
  - uv workspace integratie

- [ ] **DI-02** — Document contracts (frozen dataclasses):
  - `DocumentRequest`: titel, secties, metadata, output_format, template
  - `DocumentSection`: heading, content, level, subsections
  - `DocumentMetadata`: author, date, grade, sources, tags, version
  - `DocumentResult`: path, format, size, checksum

- [ ] **DI-03** — `DocumentInterface` ABC methodes:
  - `create(request: DocumentRequest) -> DocumentResult`
  - `from_template(template_path, data) -> DocumentResult`
  - `supported_formats() -> list[str]`

### ODF Adapter

- [ ] **DI-04** — `ODFAdapter` implementatie
  - Gebruikt `odfpy` library
  - Genereert .odt bestanden
  - Ondersteunt: headings, paragrafen, tabellen, metadata, inhoudsopgave
  - Basis-styling: clean, professioneel, leesbaar

- [ ] **DI-05** — `MarkdownAdapter` implementatie (fallback)
  - Genereert .md bestanden vanuit dezelfde DocumentRequest
  - Lichtgewicht fallback wanneer ODF niet nodig is

### Factory + Config

- [ ] **DI-06** — `DocumentFactory` met YAML-config
  - Volgt patroon: `StorageFactory`, `VectorStoreFactory`
  - Config in `config/documents.yml`

### Tests

- [ ] **DI-07** — Tests voor contracts, ABC, adapters, factory
  - Minimum: 25 tests
  - Inclusief: roundtrip test (create → verify content), template test, metadata test

## Afhankelijkheden

- **Geblokkeerd door:** geen — volledig onafhankelijk package
- **BORIS impact:** nee — DevHub tooling. BORIS kan later eigen adapters toevoegen
- **Python dependency:** `odfpy` toevoegen aan devhub-documents pyproject.toml

## Fase-context

Fase 3 (Knowledge & Memory). DocumentInterface is een bouwblok voor de analyse pipeline (Golf 3) en voor toekomstige kennisexport.

## Open vragen voor Claude Code

1. Moet er een `DOCXAdapter` als optionele adapter bij, of is dat scope creep voor nu?
2. Hoe verhoudt de template-functionaliteit zich tot de bestaande Golden Paths templates?
3. Is `packages/devhub-documents/` het juiste pad, of past het beter als submodule van devhub-core?

## Technische richting (Claude Code mag afwijken)

- Nieuw workspace package: `packages/devhub-documents/`
- `odfpy` als enige externe dependency voor ODF
- Frozen dataclasses met `__slots__` voor alle contracts
- Factory pattern met YAML-config, consistent met storage en vectorstore

## DEV_CONSTITUTION impact

- **Art. 5 (Kennisintegriteit):** DocumentMetadata bevat `grade` en `sources` velden — kennisgradering doorgetrokken naar documenten
- **Art. 7 (Impact-zonering):** GROEN — nieuw package, geen bestaande code geraakt
