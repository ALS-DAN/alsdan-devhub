---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 3
---

# Sprint Intake: Diátaxis+ Documentatie-Taxonomie & Proof-of-Concept

## Doel

Ontwerp en implementeer een uitgebreide documentatie-taxonomie (Diátaxis+) als configuratie in devhub-documents, en genereer het eerste document ("Wat is DevHub?") als proof-of-concept voor de kennisbank.

## Probleemstelling

DevHub heeft een werkende document-generatie pipeline (devhub-documents met Markdown + ODF adapters), een DocsAgent met basis Diátaxis-templates, en een operationele kennispipeline (vectorstore, embeddings, curator). Maar er ontbreekt een **gestructureerde documentatie-taxonomie** die verder gaat dan de standaard vier Diátaxis-categorieën.

Niels wil een kennisbank aanleggen over "perfecte productontwikkeling" — een expert database die door het dev-team van agents wordt gebruikt om producten te maken. De standaard Diátaxis-categorieën dekken productdocumentatie, maar niet het **ontwikkelproces zelf**: gevonden patronen, analyses, developer journey, methodieken, SOTA-onderzoek.

**Waarom nu:** Fase 3 (Knowledge & Memory) is grotendeels afgerond — de pipeline staat. Maar de pipeline produceert nog geen output. Dit is het eerste stuk dat daadwerkelijk kennis **publiceert**. Bovendien: dit wordt de blauwdruk voor hoe BORIS (en toekomstige projecten) documentatie genereert.

**Fase-context:** Fase 3 — kennisproductie als logisch vervolg op de kennispipeline.

## Deliverables

- [ ] **Diátaxis+ taxonomie als YAML-config** in `config/documents.yml` — uitgebreid met:
  - Laag 1 (Diátaxis standaard): `tutorial`, `howto`, `reference`, `explanation`
  - Laag 2 (procesgericht): `pattern`, `analysis`, `decision`, `retrospective`
  - Laag 3 (kennisbank): `methodology`, `best_practice`, `sota_review`, `playbook`
- [ ] **Template per categorie** in DocsAgent — uitbreiding van bestaande `DIATAXIS_TEMPLATES` dict met de 8 nieuwe categorieën
- [ ] **DocumentMetadata uitbreiding** — `category` veld toevoegen (naast bestaande `grade`) zodat elk document zijn taxonomie-type draagt
- [ ] **Proof-of-Concept document: "Wat is DevHub?"** — categorie `explanation`, gegenereerd via de pipeline:
  - Drie-lagen architectuur uitleg
  - Relatie DevHub ↔ projecten (BORIS)
  - Kernprincipes (DEV_CONSTITUTION)
  - Werkwijze (Shape Up, DoR, impact-zonering)
  - EVIDENCE-grading: SILVER (gebaseerd op eigen architectuur + ADRs)
- [ ] **Output in Markdown + ODF** — beide adapters testen met het PoC-document
- [ ] **Google Drive mappenstructuur** — handmatig aanmaken en document uploaden als validatie:
  ```
  /DevHub/
    /explanation/
    /tutorial/
    /howto/
    /reference/
    /pattern/
    /analysis/
    /decision/
    /methodology/
    /best_practice/
    /sota_review/
    /playbook/
    /retrospective/
  ```
- [ ] **Taxonomie-documentatie** — een `reference`-document dat de taxonomie zelf beschrijft (meta: de kennisbank documenteert zichzelf)

## Afhankelijkheden

- **Geblokkeerd door:** geen — alle benodigde packages bestaan (devhub-documents, devhub-core/DocsAgent)
- **BORIS-impact:** ja — deze taxonomie wordt de blauwdruk voor BORIS documentatie-output. Geen directe BORIS-wijziging nodig, maar het ontwerp moet generiek genoeg zijn om door BorisAdapter hergebruikt te worden.

## Fase-context

Fase 3 — Knowledge & Memory. Past direct: de kennispipeline (Track K) is operationeel, dit is het eerste stuk dat de pipeline daadwerkelijk kennis publiceert als documenten. Het verbindt devhub-vectorstore (kennis erin) met devhub-documents (kennis eruit).

## Open vragen voor Claude Code

1. **DocumentMetadata.category** — frozen dataclass uitbreiden met nieuw veld. Backward-compatible? Of een apart `DocumentCategory` enum naast `DocumentFormat`?
2. **Templates in DocsAgent vs devhub-documents** — de templates zitten nu hardcoded in `docs_agent.py`. Moeten ze naar een apart template-systeem in devhub-documents verhuizen? (scheiding concerns)
3. **YAML-config structuur** — hoe modelleer je de drie lagen in `documents.yml`? Suggestie:
   ```yaml
   taxonomy:
     layers:
       product: [tutorial, howto, reference, explanation]
       process: [pattern, analysis, decision, retrospective]
       knowledge: [methodology, best_practice, sota_review, playbook]
   ```
4. **ODF styling** — het PoC-document moet er professioneel uitzien. Welke ODF-styling opties biedt odfpy? Headers, kleuren, DevHub-branding?
5. **Relatie met KnowledgeCurator** — moet het gegenereerde document ook terug de vectorstore in als doorzoekbare kennis? (kennisbank documenteert zichzelf)

## Prioriteit

**Hoog** — dit is het fundament voor alle toekomstige documentatie-output. Zonder taxonomie is de kennispipeline een motor zonder wielen. Bovendien: blauwdruk voor BORIS (Fase 4 voorbereiding).

## Technische richting (suggestie — Claude Code mag afwijken)

- Gebruik bestaande `DocumentFormat` enum als patroon voor een nieuwe `DocumentCategory` enum in contracts.py
- Breid `documents.yml` uit met `taxonomy` sectie
- Genereer het PoC-document via DocsAgent → DocumentRequest → MarkdownAdapter + ODFAdapter
- Mappenstructuur: `output/documents/{category}/` lokaal, `/DevHub/{category}/` in Drive

## DEV_CONSTITUTION impact

- **Art. 4 (Transparantie):** taxonomie als config = traceerbaar
- **Art. 5 (Kennisintegriteit):** EVIDENCE-grading op elk document = direct toegepast
- **Art. 6 (Project-soevereiniteit):** taxonomie moet generiek zijn, projecten kiezen zelf welke categorieën ze gebruiken

## BORIS-blauwdruk notitie

Dit is expliciet bedoeld als blauwdruk. Ontwerpcriteria:
1. Taxonomie moet configureerbaar zijn per node (BORIS gebruikt misschien niet alle categorieën)
2. Templates moeten project-agnostisch zijn (geen DevHub-specifieke content in de template-structuur)
3. De mappenstructuur moet via config aanpasbaar zijn (niet hardcoded `/DevHub/`)
