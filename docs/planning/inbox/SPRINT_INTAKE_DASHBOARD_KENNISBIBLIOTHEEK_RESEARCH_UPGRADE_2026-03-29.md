---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 4
---

# Sprint Intake: Dashboard Kennisbibliotheek & Research Management Upgrade

## Doel

Upgrade het NiceGUI dashboard van een status-overzicht naar een volledig kennismanagement- en research-platform met bibliotheekfunctie, professioneel research-formulier, synergie-detectie, en cross-paneel verbindingen.

## Probleemstelling

Het dashboard (Sprint 43) toont op dit moment vooral *tellers en statussen* — hoeveel kennis-items, welke grading-verdeling, inbox-aantallen. Er zit weinig interactie en diepte in. Drie concrete problemen:

**1. Knowledge-paneel = oppervlakkig.** Het telt bestanden en toont grading-bars, maar je kunt geen artikelen bekijken, doorzoeken, filteren of beoordelen op versheid. De kennisbank is een blackbox vanuit het dashboard.

**2. Research-formulier = te mager.** Vier velden (topic, domein, diepte, document type) zijn onvoldoende voor een serieus researchvoorstel. Bij een kennisinstituut bevat een voorstel onderzoeksvragen, scope-afbakening, verwachte gradering, gerelateerde kennis, en motivatie. Het huidige formulier leidt tot onduidelijke opdrachten voor de researcher agent.

**3. Geen ontdekkingsmechanisme.** Het systeem toont wat er is, maar vindt niet wat er *zou moeten* zijn. Er is geen automatische detectie van verbanden tussen domeinen, kennislacunes als kansen, of onverwachte synergieën — terwijl de vectorstore + embeddings hier perfect voor gebouwd zijn.

**Waarom nu:** Het dashboard is vers (Sprint 43), de componentenbibliotheek (kpi_card, status_badge, research_card, trend_chart) staat klaar, en de Kennisketen sprint (die de vectorstore vult) gaat binnenkort draaien. Dit is het ideale moment om het dashboard te verrijken vóórdat de kennispipeline data begint te leveren.

**Fase-context:** Fase 4 — Verbindingen. Dit is een dashboard-upgrade die bestaande pagina's verrijkt en nieuwe interacties toevoegt. Het sluit aan bij het verbindingen-thema: kennis, research en agents worden zichtbaar verbonden.

## SOTA-onderbouwing

### Kennisbibliotheek

- **Catalogusview-patroon** (UX Bulletin, Pencil & Paper): kennisbanken gebruiken article cards met metadata, freshness-indicator, en DRI (Directly Responsible Individual). Versheid correleert direct met gebruikswaarde.
- **Diátaxis-taxonomie**: DevHub heeft dit al als DocumentCategory (3 lagen: product/proces/kennisbank). De bibliotheek kan hierop filteren.
- **Knowledge decay** (KMInsider 2025): actieve freshness-monitoring voorkomt dat verouderde kennis als actueel wordt behandeld.

### Research Management

- **SCOPE-framework** (INORMS, peer-reviewed 2024): vijf stappen voor verantwoord research assessment — Start with what you value → Context → Options → Probe → Evaluate your evaluation.
- **Evaluatiecriteria** (Insight7, Scribbr): significance, innovation, approach, qualifications als vier assen.
- **Structured proposals** (USC Libguides): achtergrond, RQs met scope-afbakening, methodologie, verwachte output, tijdlijn.

### Synergie-detectie

- **Literature-Based Discovery** (Swanson 1986, Wikipedia LBD): het ABC-paradigma — als A↔B en B↔C verbonden zijn, is A↔C een onontdekte verbinding. Klassiek voorbeeld: fish oil ↔ blood viscosity ↔ Raynaud syndrome.
- **Discovery Engine** (ArXiv 2505.17500): framework voor AI-gestuurde synthese en navigatie van kennislandschappen. Transformeert ontdekking van serendipiteit naar systematische exploratie.
- **Embedding-gebaseerde clustering** (ResearchGate, Springer): cosine-similarity op embeddings vindt thematische clusters en outliers die op onverwachte verbanden wijzen.
- **Knowledge gap analysis** (Academia.edu): unsupervised clustering op kennisartikelen identificeert onderbediende gebieden en genereert automatisch research-suggesties.

## Deliverables

### Sprint 1: Bibliotheek + Research Formulier Upgrade

#### A. Kennisbibliotheek (Knowledge-pagina verrijking)

- [ ] **Catalogusview met artikelkaarten** — vervangt de huidige teller-view
  - Per artikel: titel, domein-badge (ring 1/2/3 kleurcodering), grading-badge (GOLD/SILVER/BRONZE/SPECULATIVE), publicatiedatum, auteur
  - Samenvatting: eerste 2-3 zinnen automatisch uit content geëxtraheerd
  - Freshness-indicator: groen (<30 dagen), oranje (30-90 dagen), rood (>90 dagen)
  - Data: parse YAML frontmatter uit `knowledge/**/*.md` bestanden
  - NiceGUI componenten: `ui.card()` per artikel, `ui.badge()` voor tags

- [ ] **Filter- en sorteerbalk**
  - Filter op: ring (core/agent/project), domein (KnowledgeDomain enum), grade, freshness
  - Sorteer op: datum (nieuwst/oudst), grade (hoogst/laagst), domein
  - NiceGUI: `ui.select()` dropdowns + `ui.switch()` voor toggles

- [ ] **Domein-dekkingsmatrix**
  - Visueel grid: 3 ringen × N domeinen
  - Per cel: aantal artikelen + gemiddelde grade + freshness-score
  - Kleurcodering: groen (goed gedekt), oranje (matig), rood (lacune)
  - Toont welke domeinen aandacht nodig hebben
  - Data: `KnowledgeDomain.by_ring()` + file scan

- [ ] **Artikel-detailpagina** (`/knowledge/{article_id}`)
  - Volledige content als markdown-rendered tekst (NiceGUI `ui.markdown()`)
  - Metadata-sidebar: bronnen, verificatie-%, RQ-tags, entity_refs
  - Gerelateerde artikelen (op basis van domein + tags)
  - "Start Research" knop als artikel verouderd is (pre-fills research-formulier)

- [ ] **Versheids-dashboard (knowledge decay)**
  - Heatmap per domein: actueel / verouderend / verlopen
  - Totaal freshness-score als KPI op overview-pagina
  - Bouwt op `ObservationType.FRESHNESS_ALERT` uit curator_contracts

#### B. Research Formulier Upgrade (Research-pagina verrijking)

- [ ] **Uitgebreid indienformulier** — vervangt het huidige 4-velden formulier
  - Topic (met suggestie-autocomplete op basis van bestaande kennislacunes)
  - Achtergrond/motivatie (textarea): waarom is dit onderzoek nodig?
  - Onderzoeksvragen (RQs): dynamisch formulier, toevoegen/verwijderen van genummerde RQs
  - Scope-afbakening: wat valt er wél en niet onder? (textarea)
  - Verwachte gradering: dropdown met tooltip (GOLD = peer-reviewed nodig, SILVER = docs, BRONZE = ervaring)
  - Domein + Ring: visuele indicatie core/agent/project
  - Diepte: met tooltips die QUICK/STANDARD/DEEP concreet uitleggen
  - Gerelateerde kennis: multi-select dropdown met bestaande artikelen
  - Prioriteit: 1-10 slider met motivatie-veld
  - Deadline (optioneel): datepicker
  - Document type (bestaand): DocumentCategory enum

- [ ] **ResearchQueueItem uitbreiden** met nieuwe velden
  - `background: str` — motivatie/achtergrond
  - `research_questions: list[str]` — expliciete RQs
  - `scope_in: str` — wat valt erin
  - `scope_out: str` — wat valt erbuiten
  - `expected_grade: str` — verwachte EVIDENCE-niveau
  - `related_articles: list[str]` — IDs van gerelateerde kennis
  - `deadline: str` — optionele deadline (ISO 8601)
  - Backwards-compatible: bestaande items met lege velden werken nog

- [ ] **Voorstel-detailpagina** (`/research/{item_id}`)
  - Statusflow-visualisatie: PENDING → APPROVED → IN_PROGRESS → REVIEW → COMPLETED (of REJECTED)
  - Per stap: wie, wanneer, metadata
  - Onderzoeksvragen met per-RQ status (beantwoord/open)
  - Bronnenlijst wanneer beschikbaar
  - Timeline-weergave van de research lifecycle

- [ ] **Review-paneel voor afgerond onderzoek**
  - Beantwoorde RQs met per-RQ gradering
  - Gap-analyse: welke vragen onbeantwoord
  - "Publiceer naar kennisbank" actie
  - Koppeling naar resulterende kennisartikelen

### Sprint 2: Synergie-detectie & Cross-paneel Intelligentie

*Geblokkeerd door: Sprint 1 + Kennisketen End-to-End sprint (vectorstore moet gevuld zijn)*

#### C. Discovery Engine (nieuw paneel of sub-tab)

- [ ] **ABC-verbindingendetector** (Swanson-patroon)
  - Implementatie: voor elk paar domeinen A en C, zoek gedeelde concepten B via embedding-similarity
  - Voorbeeld: als "testing_qa" ↔ "security_appsec" een B-concept delen maar geen directe link hebben → suggestie
  - Output: kaarten met "Onontdekte verbinding: A ↔ C via B" met confidence-score
  - Data: cosine-similarity op vectorstore embeddings via `VectorStoreAdapter.query()`

- [ ] **Kennislacune-scanner**
  - Automatische gap-analyse per domein:
    - Welke domeinen < N artikelen?
    - Welke domeinen 100% SPECULATIVE/BRONZE?
    - Welke ring 1 (core) domeinen niet gedekt?
  - Output: geprioriteerde lijst van research-suggesties
  - "Neem over als research-voorstel" knop (pre-fills formulier)

- [ ] **Thematische clusters**
  - Unsupervised clustering op embeddings (k-means of HDBSCAN)
  - Visualisatie: scatter plot met clusters, outliers gemarkeerd
  - Per cluster: dominant thema, aantal artikelen, gemiddelde grade
  - Outliers = potentieel nieuwe onderzoeksrichtingen
  - NiceGUI: Plotly scatter plot (bestaand patroon, zie growth_page)

- [ ] **Trending topics en serendipiteitsindex**
  - Track welke domeinen/topics het snelst groeien
  - "Serendipiteitsindex": hoeveel cross-domein verbindingen een artikel heeft (hoe hoger, hoe meer verrassingswaarde)
  - Weekly digest: "Deze week ontdekt: 3 nieuwe verbanden, 2 kennislacunes"

#### D. Cross-paneel Verbindingen

- [ ] **Globale zoekfunctie** (header-balk)
  - Zoekbalk in `_nav_header()` die over kennis, research-voorstellen, en sprints zoekt
  - Semantisch zoeken via vectorstore embeddings (niet alleen keyword)
  - Resultaten gegroepeerd per type met directe links
  - NiceGUI: `ui.input()` met debounce + dropdown resultaten

- [ ] **Event Log / Activity Feed** (nieuw paneel of overview sub-sectie)
  - Chronologisch overzicht van systeem-activiteit via Event Bus
  - Types: sprint afgerond, kennis toegevoegd, research gestart, governance-check gedraaid
  - Filterable op type en tijdsperiode
  - "Heartbeat" van het hele DevHub-systeem

- [ ] **Knowledge ↔ Research bruggen**
  - Op Knowledge-pagina bij verouderde/lacune-domeinen: directe "Start Research" knop
  - Op Research-pagina bij completed research: "Bekijk in kennisbank" link
  - Op Planning-pagina: tonen welke kennisartikelen een sprint heeft opgeleverd

- [ ] **Sprint-impact op Knowledge**
  - Bij elke sprint in de planning-view: badge met "N kennis-items aangemaakt/bijgewerkt"
  - Maakt de waardecreatie van sprints voor de kennisbank zichtbaar

## Afhankelijkheden

| Afhankelijkheid | Impact | Status |
|-----------------|--------|--------|
| Kennisketen End-to-End sprint | Sprint 2 vereist gevulde vectorstore voor embedding-queries en synergie-detectie | INBOX |
| `knowledge/**/*.md` bestanden | Sprint 1 leest direct van filesystem; werkt met huidige 10 bestanden | ✅ Beschikbaar |
| `KnowledgeArticle` dataclass | Bevat alle benodigde metadata (grade, domain, rq_tags, entity_refs) | ✅ In devhub-core |
| `ResearchQueueManager` | Uitbreiden met nieuwe velden; backwards-compatible | ✅ In devhub-dashboard |
| `VectorStoreAdapter.query()` | Sprint 2 gebruikt dit voor semantisch zoeken en similarity | ✅ Interface bestaat |
| `EmbeddingProvider` | Sprint 2 vereist werkende embedding-generatie | ✅ Interface bestaat |
| Event Bus | Sprint 2 Activity Feed leest events | ✅ Gebouwd in Sprint 42 |
| BORIS-impact | Geen directe BORIS-impact — dit is pure DevHub-dashboard code | n.v.t. |

## Fase-context

Fase 4 — Verbindingen. Deze sprint verbindt alle bestaande systemen (kennisbank, research queue, vectorstore, event bus) tot een coherent, interactief dashboard. Het is de "gebruikersinterface op de verbindingen" — precies het fase 4 thema.

## Technische richting (suggesties — Claude Code mag afwijken)

### Sprint 1 architectuur
- **KnowledgeProvider** — nieuwe data provider in `devhub_dashboard/data/` die `knowledge/` directory scant, frontmatter parsed, en artikelkaarten levert. Pattern: volg bestaande `HealthProvider`/`PlanningProvider`.
- **Pagina-structuur**: Knowledge-pagina refactor met tabs (Catalogus | Dekking | Versheid). Research-pagina refactor met tabs (Nieuw Voorstel | Mijn Verzoeken | Agent-voorstellen | Auto-kennis).
- **ResearchQueueItem v2**: nieuwe velden met default empty strings voor backwards-compatibiliteit. Bestaande JSON-bestanden blijven werken.
- **Nieuwe NiceGUI pagina**: `/knowledge/{article_id}` via `@ui.page("/knowledge/{article_id}")` — NiceGUI ondersteunt path parameters.

### Sprint 2 architectuur
- **DiscoveryService** — nieuwe service in `devhub_dashboard/data/` of in `devhub-core` die embedding-queries uitvoert en ABC-verbindingen berekent.
- **Clustering**: scipy of scikit-learn voor k-means/HDBSCAN op embeddings. Lightweight, geen zware dependencies.
- **Zoekfunctie**: `VectorStoreAdapter.query()` met `RetrievalRequest` voor semantisch zoeken. Resultaten combineren met filesystem-scan voor niet-geëmbedde items.

### Componentenbibliotheek uitbreiden
- `knowledge_card.py` — artikelkaart (herbruikbaar op catalogus + zoekresultaten)
- `research_form.py` — uitgebreid formulier als apart component
- `discovery_card.py` — verbinding/synergie-suggestie kaart
- `status_flow.py` — horizontale statusflow-visualisatie (PENDING → ... → COMPLETED)
- `search_bar.py` — globale zoekbalk component

## DEV_CONSTITUTION impact

| Artikel | Impact |
|---------|--------|
| Art. 1 (Menselijke regie) | Dashboard is Niels' primaire interface voor regie — versterkt Art. 1 |
| Art. 5 (Kennisintegriteit) | Grading en freshness worden zichtbaar gemaakt — transparantie op Art. 5 |
| Art. 7 (Impact-zonering) | GREEN: alle wijzigingen in devhub-dashboard package, geen externe impact |
| Art. 9 (Planning) | Geen impact op SPRINT_TRACKER — leest alleen |

## Open vragen voor Claude Code

1. **Frontmatter-parsing**: sommige `knowledge/` bestanden gebruiken `---` YAML frontmatter, andere hebben markdown headers met inline metadata. Hoe uniform maken? Stricte parser of fuzzy?
2. **NiceGUI path parameters**: wordt `/knowledge/{article_id}` goed ondersteund in de huidige NiceGUI versie? Alternatief: query parameters (`/knowledge?id=X`).
3. **ResearchQueueItem v2 migratie**: nieuwe velden toevoegen aan bestaande JSON-bestanden automatisch bij eerste read, of alleen voor nieuwe items?
4. **Sprint 2 embedding-queries**: direct via VectorStoreAdapter of via een nieuwe abstractie laag (DiscoveryService)? Voorkeur voor separation of concerns.
5. **Clustering-libraries**: scikit-learn toevoegen als dependency of lightweight alternatief?
6. **Test-strategie**: snapshot tests voor NiceGUI components, of integration tests die pagina's renderen?

## Prioriteit

**Hoog** — Het dashboard is Niels' primaire window op het DevHub-systeem. Een informatierijk, interactief dashboard met discovery-capabilities maakt het verschil tussen een passief statusbord en een actief kennismanagement-platform. De timing is optimaal: de Kennisketen sprint gaat de data leveren, dit dashboard zorgt dat die data zichtbaar en bruikbaar wordt.

## Risico's en mitigatie

| Risico | Kans | Impact | Mitigatie |
|--------|------|--------|-----------|
| Sprint 2 geblokkeerd als Kennisketen niet eerst draait | Middel | Hoog | Sprint 1 werkt onafhankelijk op filesystem; Sprint 2 expliciet geblokkeerd |
| Weinig kennisartikelen (10 stuks) maakt bibliotheek leeg | Hoog | Laag | Bibliotheek is nuttig vanaf dag 1 als "wat hebben we?"; groeit mee |
| Clustering onzinnig bij <50 embeddings | Middel | Laag | Minimum-threshold: toon cluster-view alleen bij >20 artikelen |
| NiceGUI performance bij veel componenten | Laag | Middel | Paginering en lazy loading als standaard |
