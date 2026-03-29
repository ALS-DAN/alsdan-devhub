# Sprint Intake: Planning-herstructurering — Drie-lagen overzicht

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: CHORE
fase: 4
---

## Doel

SPRINT_TRACKER.md herstructureren van chronologische log (500+ regels) naar drie-lagen overzicht (Strategisch → Work Streams → Detail) met Now-Next-Later navigatie, thematische stromen-indeling en ingeklapte afgeronde fasen.

## Probleemstelling

### Waarom nu

Na 45 sprints in 6 dagen is de SPRINT_TRACKER uitgegroeid tot een onnavigeerbaar document. Alle sprints staan chronologisch op hetzelfde vlak — Sprint 1 krijgt evenveel ruimte als Sprint 45. 12 van de 15 post-Fase-3 sprints staan als "Intermezzo" omdat het model geen work streams kent. Velocity- en cycle-time tabellen (120+ regels) domineren het document maar worden zelden dagelijks geraadpleegd. Het resultaat: om te weten "waar staan we en wat is het volgende?" moet je 500+ regels scrollen en mentaal drie documenten combineren (SPRINT_TRACKER + inbox + ROADMAP.md).

### Fase-context

Fase 4 (Verbindingen) is de fase waarin systeemdelen samenwerken. Een helder planningsoverzicht is voorwaarde voor effectieve coördinatie — zowel voor Niels (strategisch), voor Cowork (planning-voorstellen) als voor Claude Code (sprint-uitvoering). De SprintTrackerParser in het dashboard parst deze structuur al, dus een herstructurering verbetert ook het planning-paneel.

## Deliverables

```yaml
deliverables:
  - id: D1
    naam: "Laag 1 — Strategisch overzicht (Now-Next-Later)"
    beschrijving: |
      Bovenaan SPRINT_TRACKER, max 30-40 regels:
      - 🟢 Now: actieve sprint(s) of "geen actieve sprint"
      - 🔵 Next: geshaped intakes klaar voor uitvoering (uit inbox)
      - ⚪ Later: visie-items, Fase 5 richting, geparkeerde ideeën
    impact_zone: GREEN
    acceptatiecriteria:
      - "Now/Next/Later secties zichtbaar bovenaan tracker"
      - "Next verwijst naar bestaande inbox-bestanden"
      - "Later bevat Fase 5 items uit ROADMAP.md"
      - "Totaal max 40 regels"

  - id: D2
    naam: "Laag 2 — Work Streams categorisering"
    beschrijving: |
      Alle 45 sprints gecategoriseerd in thematische stromen:
      1. Kern-platform (packages, contracts, event bus)
      2. Kennis & Research (kennispipeline, vectorstore, Research Compas, docs)
      3. Governance & Kwaliteit (DEV_CONSTITUTION, security, guardrails)
      4. Integraties (Drive, n8n, Provider Pattern)
      5. Gebruikerservaring (dashboard, mentor, skills)
      6. Verkenning (SPIKEs, research-sprints)
      Elke stroom toont: totaal sprints, tests-delta, status actieve items.
    impact_zone: YELLOW
    reden: "herstructurering van bestaand document, raakt parser"
    acceptatiecriteria:
      - "Alle 45 sprints zijn toegewezen aan precies één stroom"
      - "Per stroom: samenvatting met sprint-count, test-delta, status"
      - "Stromen-secties vervangen chronologische intermezzo-secties"
      - "Geen data verloren — alle sprint-informatie behouden"

  - id: D3
    naam: "Laag 3 — Afgeronde fasen inklappen"
    beschrijving: |
      Fase 0-3 samengevat in één compacte tabel (~10 regels i.p.v. ~160).
      Fase 3 golfplanning verplaatst naar archief.
      Alleen Fase 4 behoudt volledig sprint-detail.
    impact_zone: GREEN
    reden: "ADR-003 schrijft dit al voor"
    acceptatiecriteria:
      - "Fase 0-3 ingeklapt tot samenvatting-tabel"
      - "Fase 3 golfplanning verplaatst naar docs/planning/archive/"
      - "Fase 4 detail volledig behouden"
      - "Verwijzing naar archief voor historisch detail"

  - id: D4
    naam: "Metrics verplaatsen naar apart bestand"
    beschrijving: |
      Velocity Log (45 rijen) en Cycle Time (45 rijen) verplaatsen naar
      docs/planning/VELOCITY_LOG.md. SPRINT_TRACKER behoudt alleen afgeleide
      metrics (5-regel samenvatting). Verwijzing naar VELOCITY_LOG voor detail.
    impact_zone: GREEN
    acceptatiecriteria:
      - "VELOCITY_LOG.md aangemaakt met volledige velocity + cycle time data"
      - "SPRINT_TRACKER bevat samenvattende metrics (~10 regels)"
      - "Verwijzing naar VELOCITY_LOG.md in tracker"

  - id: D5
    naam: "SprintTrackerParser aanpassen"
    beschrijving: |
      Dashboard's SprintTrackerParser aanpassen aan nieuwe structuur:
      - Now/Next/Later secties parsen
      - Stromen-indeling herkennen
      - Ingeklapte fasen correct verwerken
    impact_zone: YELLOW
    reden: "bestaande parser-functionaliteit wijzigt"
    acceptatiecriteria:
      - "Parser verwerkt nieuwe structuur zonder fouten"
      - "Dashboard planning-paneel toont correcte data"
      - "Bestaande tests aangepast + nieuwe tests voor stromen-parsing"

  - id: D6
    naam: "Machine-leesbaar companion-blok"
    beschrijving: |
      YAML-blok bovenaan SPRINT_TRACKER met gestructureerde data:
      - stromen met sprint-ids
      - now/next/later status
      - fase-samenvattingen als data
      Past in dual-format standaard (IDEA_DUAL_FORMAT).
    impact_zone: GREEN
    acceptatiecriteria:
      - "YAML-blok bovenaan met stromen-definitie"
      - "Parsebaar door agents en dashboard"
```

## Afhankelijkheden

```yaml
afhankelijkheden:
  geblokkeerd_door: geen
  versterkt_door:
    - "SPRINT_INTAKE_DUAL_FORMAT_MACHINE_LEESBARE_SYSTEEMBESTANDEN"
    - reden: "dual-format standaard definieert het YAML-blok formaat"
    - volgorde: "kan parallel, dual-format levert de conventie, deze sprint past toe"
  boris_impact:
    direct: nee
    indirect: nee
    toelichting: "Puur DevHub planning-structuur, raakt geen BORIS-bestanden"
  dashboard_impact:
    direct: ja
    beschrijving: "SprintTrackerParser moet aangepast worden (D5)"
    risico: "Parser-wijziging kan tijdelijk dashboard planning-paneel breken"
    mitigatie: "Parser + tracker in dezelfde sprint wijzigen, tests verifiëren"
```

## Fase-context

```yaml
fase_context:
  huidige_fase: 4
  fase_naam: "Verbindingen"
  fit: |
    Fase 4 verbindt systeemdelen. Een navigeerbaar planningsoverzicht is de
    basis voor effectieve coördinatie tussen Cowork (voorstellen), Claude Code
    (uitvoering), en het dashboard (visualisatie). De stromen-indeling maakt
    ook expliciet welke tracks parallel kunnen lopen — essentieel voor Fase 4
    waar meerdere integratiesprints tegelijk kunnen draaien.
  kritiek_pad: nee
  parallel_mogelijk_met:
    - "SPRINT_INTAKE_DUAL_FORMAT_MACHINE_LEESBARE_SYSTEEMBESTANDEN"
    - "SPRINT_INTAKE_KENNISKETEN_END_TO_END"
```

## Open vragen Claude Code

```yaml
open_vragen:
  - vraag: "Hoe parst SprintTrackerParser momenteel de SPRINT_TRACKER?"
    context: "Bepaalt scope van D5 — regex-gebaseerd? Sectie-gebaseerd? YAML-aware?"
    urgentie: hoog

  - vraag: "Zijn er andere skills/agents die SPRINT_TRACKER direct lezen?"
    context: "Impact-analyse — wie moet nog meer aangepast na herstructurering?"
    urgentie: hoog

  - vraag: "Hoeveel dashboard-tests raken de huidige tracker-structuur?"
    context: "Test-impact D5"
    urgentie: middel

  - vraag: "Wil je de Fase 3 golfplanning archiveren of inline laten als ingeklapt blok?"
    context: "Archiveren = schoner maar apart bestand; inline = alles bij elkaar"
    urgentie: laag
```

## Prioriteit

```yaml
prioriteit:
  niveau: Middel
  motivatie: |
    Niet blokkerend voor andere sprints, maar verbetert de plannings-ervaring
    significant. Hoe meer sprints er bijkomen, hoe urgenter dit wordt — het
    is efficiënter om nu te herstructureren (45 sprints) dan later (60+ sprints).
    Combineert goed met de dual-format sprint die ook systeembestanden verrijkt.
```

## Technische richting

_Claude Code mag afwijken van onderstaande richting._

```yaml
technische_richting:
  aanpak: "in-place herstructurering van SPRINT_TRACKER.md"
  volgorde:
    1: "D4 — Metrics verplaatsen (laagste risico, maakt ruimte)"
    2: "D3 — Fasen inklappen (geen parser-impact)"
    3: "D2 — Work Streams invoeren (vervang intermezzo's)"
    4: "D1 — Now-Next-Later toevoegen bovenaan"
    5: "D6 — YAML companion-blok"
    6: "D5 — Parser aanpassen (als laatste, na structuur stabiel is)"

  stromen_definitie:
    kern_platform:
      beschrijving: "Packages, contracts, event bus, runtime-infra"
      sprint_nummers: [1, 2, 5, 30, 42]
    kennis_en_research:
      beschrijving: "Kennispipeline, vectorstore, Research Compas, documentatie"
      sprint_nummers: [10, 15, 18, 19, 20, 21, 22, 29, 31, 32, 33, 34, 35]
    governance_en_kwaliteit:
      beschrijving: "DEV_CONSTITUTION, security, tests, guardrails"
      sprint_nummers: [4, 13, 17, 25, 26, 27, 36, 37]
    integraties:
      beschrijving: "Google Drive, n8n, BorisAdapter, externe systemen"
      sprint_nummers: [3, 9, 14, 24, 28, 38, 40, 41]
    gebruikerservaring:
      beschrijving: "Dashboard, mentor, skills, agent UX"
      sprint_nummers: [12, 16, 23, 43, 44, 45]
    verkenning:
      beschrijving: "SPIKEs, research-sprints, proof-of-concepts"
      sprint_nummers: [6, 31, 39]

  overige_sprints:
    niet_gecategoriseerd: [7, 8, 11]
    reden: "Quick Fixes (7), Planning Opschoning (8) en Planning & Tracking (11) zijn meta-sprints"
    voorstel: "Onderdeel van Fase-samenvatting, niet van een stroom"
```

## DEV_CONSTITUTION impact

```yaml
dev_constitution_impact:
  geen_wijzigingen: true
  toelichting: |
    Deze sprint wijzigt geen governance-regels. Het herstructureert alleen
    het planningsdocument. ADR-003 (Planning Single Source of Truth) wordt
    versterkt door het consequent toepassen van het inklap-principe.
```

## Shape Up samenvatting

```yaml
shape_up:
  probleem: |
    SPRINT_TRACKER is een 500+ regels chronologische log waar afgerond werk
    evenveel ruimte krijgt als gepland werk. Er is geen navigatie-structuur,
    geen thematische ordening, en geen zicht op toekomst. De "intermezzo"
    noodoplossing maskeert dat er impliciete work streams zijn die niet
    geëxpliciteerd worden.
  oplossing: |
    Drie-lagen herstructurering:
    Laag 1 (Strategisch): Now-Next-Later overzicht bovenaan
    Laag 2 (Stromen): Sprints gecategoriseerd in 6 thematische stromen
    Laag 3 (Detail): Alleen actieve fase volledig, rest ingeklapt
    Plus: metrics naar apart bestand, parser aanpassen, YAML companion.
  grenzen:
    wel:
      - "SPRINT_TRACKER.md herstructureren"
      - "Metrics naar VELOCITY_LOG.md"
      - "Fase 0-3 inklappen"
      - "Work Streams invoeren"
      - "Now-Next-Later toevoegen"
      - "SprintTrackerParser aanpassen"
      - "YAML companion-blok"
    niet:
      - "ROADMAP.md herschrijven (apart)"
      - "Inbox-structuur wijzigen"
      - "Nieuwe planning-tooling introduceren"
      - "GitHub Projects opzetten (apart traject indien gewenst)"
      - "Dashboard planning-paneel redesign (alleen parser-compatibiliteit)"
  appetite: "Small-Medium (1 sprint)"
```

## Three Amigos

```yaml
three_amigos:
  tech_lead:
    haalbaarheid: "Hoog — herstructurering van Markdown, geen nieuwe code behalve parser"
    architectuurrisicos:
      - risico: "SprintTrackerParser breekt door gewijzigde structuur"
        mitigatie: "Parser + tracker in zelfde sprint wijzigen, tests eerst"
      - risico: "Informatie-verlies bij inklappen"
        mitigatie: "Niets verwijderen, alleen verplaatsen naar archief/apart bestand"
    cynefin: simpel
    sprint_type: CHORE
    boris_impact: "geen"

  product_owner:
    waarde: "Directe verbetering van dagelijkse plannings-ervaring"
    roadmap_fit: "Fase 4 enabler — betere coördinatie door betere navigatie"
    probleem_of_oplossing: "Probleem-gedreven: tracker is onnavigeerbaar"
    dev_constitution_consistent: "Ja — versterkt ADR-003"

  qa_invest:
    I_independent: true    # geen blokkers
    N_negotiable: true     # Claude Code bepaalt details (stroom-namen, archief-locatie)
    V_valuable: true       # dagelijkse plannings-efficiëntie
    E_estimable: true      # 6 deliverables, concrete scope
    S_small: true          # past in 1 sprint
    T_testable: true       # parser-tests + visuele verificatie
    gate: "T = GROEN"
```

## Gate check

```yaml
gate_stap_3:
  1_devhub_brief_gelezen: true    # gelezen (verouderd) + SPRINT_TRACKER gelezen (SSoT)
  2_niet_duplicaat: true           # geen bestaande intake voor planning-herstructurering
  3_shape_up_compleet: true        # probleem + oplossing + grenzen + appetite
  4_invest_t_groen: true           # parser-tests + visuele verificatie per deliverable
  5_past_in_fase: true             # Fase 4 — Verbindingen
  6_sprint_type_cynefin: true      # simpel → CHORE
  7_claims_geverifieerd: true      # SPRINT_TRACKER zelf gelezen (505 regels, 45 sprints)
  8_auto_memory_geraadpleegd: true # MEMORY.md gelezen bij sessie-start
  9_cross_project_impact: true     # geen BORIS-impact
```
