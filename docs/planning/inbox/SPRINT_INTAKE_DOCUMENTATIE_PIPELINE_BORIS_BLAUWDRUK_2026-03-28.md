---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 3
---

# Sprint Intake: Documentatie-productie Pipeline & BORIS-blauwdruk

## Doel

Bouw een werkende documentatie-productie pipeline die kennis uit de vectorstore omzet naar gepubliceerde documenten in Google Drive, en documenteer deze pipeline als herbruikbare blauwdruk voor BORIS en toekomstige projecten.

## Probleemstelling

Na Sprint 1 (Diátaxis+ Taxonomie PoC) bestaan de taxonomie, templates en een eerste document. Maar het productieproces is nog **handmatig**: een agent genereert lokaal, iemand uploadt naar Drive. Dat schaalt niet en is niet overdraagbaar naar andere projecten.

De ambitie is groter: DevHub moet een **kennisgestuurde productiefabriek** zijn. De workspace packages (devhub-core, devhub-storage, devhub-documents, devhub-vectorstore) zijn de composable bouwblokken. Wat ontbreekt is de **orkestratielaag** die ze verbindt: kennis erin (vectorstore) → agent selecteert en verwerkt → document eruit (devhub-documents) → publicatie (devhub-storage → Google Drive).

**Waarom nu:** Sprint 1 valideert het *wat* (taxonomie, content-kwaliteit). Sprint 2 bouwt het *hoe* (pipeline, automatisering). Samen vormen ze de blauwdruk die Niels wil hergebruiken in BORIS.

**Fase-context:** Fase 3 — afronding Knowledge & Memory. Dit is het sluitstuk: de kennispipeline produceert daadwerkelijk output.

## Deliverables

### Pipeline

- [ ] **DocumentService orchestrator** — nieuwe service die de keten verbindt:
  1. Query vectorstore voor relevante kennis (devhub-vectorstore)
  2. Selecteer template op basis van DocumentCategory (uit Sprint 1)
  3. Genereer document via DocumentInterface (devhub-documents)
  4. Publiceer naar storage backend (devhub-storage)
  - Input: `DocumentProductionRequest` (topic, category, target_node, output_format)
  - Output: `DocumentProductionResult` (document_result + storage_path + publish_status)
- [ ] **Google Drive via LocalAdapter** — geen API, geen OAuth. Drive voor Desktop sync pad configureerbaar in `documents.yml`. LocalAdapter schrijft naar het lokale Drive-pad, Google Drive voor Desktop synct automatisch naar de cloud.
- [ ] **Automatische mappenroutering** — document.category → juiste Drive-map (configureerbaar per node in `documents.yml`)
- [ ] **Minimaal 3 documenten genereren** — elk uit een andere Diátaxis+ categorie:
  - 1× `pattern` — een gevonden development-patroon (bijv. "ABC + Adapter pattern in DevHub")
  - 1× `methodology` — een methodiek-beschrijving (bijv. "Shape Up in DevHub")
  - 1× `tutorial` — een leerdocument (bijv. "Je eerste sprint intake maken")
- [ ] **End-to-end test** — van vectorstore-query tot document in Drive

### BORIS-blauwdruk

- [ ] **Blauwdruk-document** (categorie: `methodology`) — "Hoe een project de DevHub documentatie-pipeline overneemt":
  - Welke packages nodig zijn
  - Hoe `documents.yml` per node geconfigureerd wordt
  - Hoe de taxonomie per project aanpasbaar is (niet alle categorieën verplicht)
  - Hoe Drive-mappenstructuur per project verschilt
  - Voorbeeld: BORIS-configuratie (welke categorieën, welke output)
- [ ] **Node-specifieke config** in `documents.yml`:
  ```yaml
  nodes:
    devhub:
      taxonomy: [tutorial, howto, reference, explanation, pattern, analysis, decision, retrospective, methodology, best_practice, sota_review, playbook]
      drive_root: "/DevHub/"
    boris-buurts:
      taxonomy: [tutorial, howto, reference, explanation, pattern, decision]
      drive_root: "/BORIS/"
  ```
- [ ] **BorisAdapter documentatie-integratie** — read-only verificatie dat BORIS' eigen docs-structuur compatible is met de pipeline

## Afhankelijkheden

- **Geblokkeerd door:** Sprint 1 (Diátaxis+ Taxonomie PoC) — taxonomie, templates en PoC-document moeten bestaan
- **BORIS-impact:** ja — de blauwdruk definieert hoe BORIS documentatie zal produceren. Geen directe BORIS-wijziging in deze sprint, maar het ontwerp raakt BorisAdapter-scope. De blauwdruk wordt input voor een toekomstige BORIS-sprint (Fase 4).

## Fase-context

Fase 3 — Knowledge & Memory, afronding. Dit is het sluitstuk van de hele kennisketen die in Track K (Golf 1-3) gebouwd is. Na deze sprint is Fase 3 conceptueel compleet: kennis gaat erin (researcher + curator), wordt beheerd (vectorstore + grading), en komt eruit (documents + Drive).

De BORIS-blauwdruk is expliciet Fase 3 — het documenteert hoe het systeem werkt, het implementeert niets in BORIS. Fase 4 (migratie) blijft een apart traject.

## Open vragen voor Claude Code

1. **DocumentService locatie** — nieuw bestand in devhub-core (agents/)? Of een aparte orchestrator in devhub-documents? Het verbindt meerdere packages, dus misschien een nieuw top-level module?
2. **Drive sync pad configuratie** — het lokale Google Drive pad verschilt per machine en bevat het e-mailadres (Art. 8). Aanpak: environment variable `DEVHUB_DRIVE_ROOT` als primair, later uitbreidbaar naar `~/.devhub/local.yml` als er meer lokale config bijkomt. Code moet graceful falen als de variabele niet gezet is.
3. **Vectorstore query-strategie** — hoe selecteert de DocumentService relevante kennis voor een topic? Semantic search op topic + category filter? Of een apart `DocumentKnowledgeQuery` contract?
5. **Idempotentie** — wat als hetzelfde document opnieuw gegenereerd wordt? Overschrijven? Versioning? Hoe gaat `DocumentMetadata.version` hiermee om?
6. **Batching** — moet de pipeline één document tegelijk produceren, of een batch (bijv. "genereer alle verouderde docs opnieuw")? Relatie met KnowledgeCurator freshness monitoring.

## Prioriteit

**Hoog** — directe opvolger van Sprint 1. Samen vormen ze de kerndeliverable van de documentatie-visie. De BORIS-blauwdruk is essentieel als voorbereiding op Fase 4.

## Technische richting (suggestie — Claude Code mag afwijken)

- DocumentService als nieuw contract in devhub-core/contracts/ + implementatie in devhub-core/agents/ (het is een orchestrator, vergelijkbaar met DevOrchestrator)
- `DocumentProductionRequest` en `DocumentProductionResult` als frozen dataclasses
- Drive sync pad via environment variable `DEVHUB_DRIVE_ROOT` of `~/.devhub/local.yml` (niet in repo)
- LocalAdapter als storage backend (schrijft naar Drive-map, Drive synct automatisch)
- Pipeline als async flow: query → generate → publish (elk stap apart testbaar)
- E2E test met tmp-dir als fallback voor CI (echte Drive-sync alleen lokaal)

## DEV_CONSTITUTION impact

- **Art. 4 (Transparantie):** pipeline-stappen traceerbaar (logging per stap)
- **Art. 5 (Kennisintegriteit):** documenten erven EVIDENCE-grading uit vectorstore-bronnen
- **Art. 6 (Project-soevereiniteit):** node-specifieke config = elk project kiest eigen taxonomie
- **Art. 8 (Dataminimalisatie):** Drive-pad bevat e-mailadres — NOOIT in repo hardcoden, altijd via lokale config/environment. Geen PII in gegenereerde docs

## BORIS-blauwdruk criteria

De blauwdruk is geslaagd als een nieuw project (BORIS of hypothetisch 2e project) de pipeline kan overnemen door:
1. Zichzelf als node te registreren in `nodes.yml`
2. Een taxonomie-selectie te maken in `documents.yml`
3. Een lokaal Drive sync pad te configureren (environment variable of `~/.devhub/local.yml`)
4. Documenten te genereren via dezelfde DocumentService

Geen fork, geen copy-paste — configuratie.
