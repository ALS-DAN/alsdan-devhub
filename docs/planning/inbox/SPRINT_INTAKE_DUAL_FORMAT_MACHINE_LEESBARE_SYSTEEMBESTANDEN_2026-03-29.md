# Sprint Intake: Dual-Format Machine-Leesbare Systeembestanden

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
node: devhub
sprint_type: FEAT
fase: 4
---

## Doel

Alle systeembestanden (governance, agent-definities, ADRs, architectuur-overzichten) verrijken met embedded machine-leesbare blokken (YAML/Mermaid) en dit als standaard borgen via DEV_CONSTITUTION Art. 4 + reviewer-agent enforcement.

## Probleemstelling

### Waarom nu

DevHub groeit: 7 agents, 8 skills, 9 DEV_CONSTITUTION-artikelen, 3+ ADRs, een volledige kennispipeline. Agents lezen deze systeembestanden dagelijks om governance te valideren, taken te classificeren en beslissingen te respecteren. Het probleem: de meeste systeembestanden zijn proza-eerst geschreven. Agents moeten hele documenten scannen en interpreteren om één regel of classificatie te vinden.

### Concrete pijn (geverifieerd 2026-03-29)

```yaml
pijnpunten:
  dev_constitution:
    omvang: "243 regels proza"
    nut_voor_agent: "~35 regels concrete regels en classificaties"
    ratio: "14% nuttige data, 86% context die agents moeten filteren"
    voorbeeld: "Art. 7 zonering — agent moet tabel + 5 regels proza parsen om zones te kennen"

  agent_definities:
    omvang: "7 bestanden, elk 60-150 regels"
    frontmatter: "name, description, model — 3 velden"
    ontbreekt: "capabilities, constraints, packages, afhankelijkheden"
    gevolg: "dev-lead kent geen formele capability-matrix, delegeert op basis van beschrijvingsproza"

  adrs:
    aantal: 3
    inconsistentie: "ADR-003 heeft YAML frontmatter-tabel + gestructureerde secties; ADR-001 heeft minimale structuur"
    gevolg: "geen uniforme ADR-queries mogelijk (bijv. 'welke ADRs zijn YELLOW-zone?')"
```

### Fase-context

Fase 4 (Verbindingen) draait om systeemdelen laten samenwerken. Machine-leesbare systeembestanden zijn de basis: als agents governance-regels niet kunnen parsen, kunnen ze ook niet betrouwbaar samenwerken. Dit is een enabler voor de governance-check skill, het NiceGUI dashboard (dat gestructureerde data wil tonen), en de kennisketen (die documenten met metadata moet genereren).

## Deliverables

```yaml
deliverables:
  retroactief:
    - id: D1
      naam: "DEV_CONSTITUTION.md — YAML-blokken per artikel"
      beschrijving: |
        Elk van de 9 artikelen krijgt een embedded YAML-blok met:
        - artikel nummer, titel
        - regels als lijst met id, tekst, type, enforcement
        - Art. 7: zones met criteria en automation_allowed
        - Handhavingsregels als gestructureerde lijst
      impact_zone: YELLOW
      reden: "governance-document wijziging"
      acceptatiecriteria:
        - "Alle 9 artikelen hebben een ```yaml blok"
        - "Bestaande proza is ONGEWIJZIGD (alleen blokken toegevoegd)"
        - "YAML is valide en parsebaar"
        - "Bestaande governance-check tests slagen nog"

    - id: D2
      naam: "Agent-definities — uitgebreide frontmatter"
      beschrijving: |
        Alle 7 agent .md bestanden krijgen uitgebreide frontmatter:
        - capabilities: [lijst van formele capabilities]
        - constraints: [lijst met art. referenties]
        - required_packages: [welke devhub packages]
        - depends_on_agents: [welke andere agents]
        - reads_config: [welke config bestanden]
        - impact_zone_default: GREEN/YELLOW/RED
      impact_zone: GREEN
      reden: "additief, breekt niets"
      acceptatiecriteria:
        - "Alle 7 agents hebben capabilities en constraints in frontmatter"
        - "Frontmatter is valide YAML"
        - "Geen bestaande functionaliteit gebroken"

    - id: D3
      naam: "ADRs — standaard frontmatter formaat"
      beschrijving: |
        ADR-001 en ADR-002 upgraden naar ADR-003 formaat:
        - Tabel met Status, Datum, Context, Impact-zone
        - Gestructureerde secties (Context, Beslissing, Consequenties)
      impact_zone: GREEN
      reden: "additief"
      acceptatiecriteria:
        - "Alle ADRs hebben identiek frontmatter-formaat"
        - "Impact-zone is aanwezig bij elke ADR"

    - id: D4
      naam: "Mermaid-diagrammen voor sleutelprocessen"
      beschrijving: |
        Toevoegen van Mermaid-diagrammen aan:
        - DEV_CONSTITUTION: flow voor zone-classificatie (Art. 7)
        - Architectuur OVERVIEW: componenten-diagram
        - Agent-interactie: delegatie-flow dev-lead → coder/reviewer
      impact_zone: GREEN
      reden: "additief"
      acceptatiecriteria:
        - "Mermaid-blokken renderen correct op GitHub"
        - "Minimaal 3 diagrammen toegevoegd"

  prospectief:
    - id: D5
      naam: "DEV_CONSTITUTION Art. 4.6 — machine-leesbaarheidsverplichting"
      beschrijving: |
        Nieuw subartikel:
        4.6. Systeembestanden (governance, agent-definities, ADRs, architectuur-overzichten)
        bevatten machine-leesbare blokken (YAML/Mermaid) naast menselijke proza.
        Nieuwe systeembestanden zonder machine-leesbare blokken worden niet geaccepteerd
        in review.
      impact_zone: YELLOW
      reden: "governance-wijziging"
      acceptatiecriteria:
        - "Art. 4.6 staat in DEV_CONSTITUTION"
        - "Versiehistorie bijgewerkt"

    - id: D6
      naam: "Reviewer-agent — machine-readability check"
      beschrijving: |
        reviewer.md krijgt een nieuwe capability: machine_readability_check.
        Bij review van systeembestanden checkt reviewer of YAML/Mermaid-blokken aanwezig zijn.
      impact_zone: GREEN
      reden: "additief aan bestaande reviewer"
      acceptatiecriteria:
        - "reviewer.md heeft machine_readability_check in capabilities"
        - "Instructie beschrijft wanneer en hoe te checken"

    - id: D7
      naam: "Conventie-document: MACHINE_READABILITY_STANDARD.md"
      beschrijving: |
        Referentiedocument in docs/architecture/ of docs/compliance/ dat de standaard beschrijft:
        - Welke bestanden MOETEN YAML-blokken hebben
        - Welke bestanden MOETEN Mermaid-diagrammen hebben
        - Formaat-conventies (marker comments, plaatsing)
        - Voorbeelden per bestandstype
      impact_zone: GREEN
      acceptatiecriteria:
        - "Document beschrijft standaard met concrete voorbeelden"
        - "Gelinkt vanuit DEV_CONSTITUTION Art. 4.6"
```

## Afhankelijkheden

```yaml
afhankelijkheden:
  geblokkeerd_door: geen
  boris_impact:
    direct: nee
    indirect: ja
    toelichting: |
      DevHub-agents die in BORIS werken profiteren van snellere governance-lookup.
      BORIS kan op termijn dezelfde standaard adopteren voor AI_CONSTITUTION —
      maar dat is een BORIS-beslissing (Art. 6 project-soevereiniteit).
  versterkt:
    - "governance-check skill (gestructureerde input)"
    - "NiceGUI dashboard (gestructureerde data voor panelen)"
    - "kennisketen (DocumentService metadata)"
    - "dev-lead delegatie (formele capability-matrix)"
```

## Fase-context

```yaml
fase_context:
  huidige_fase: 4
  fase_naam: "Verbindingen"
  fit: |
    Fase 4 verbindt systeemdelen. Machine-leesbare systeembestanden zijn de
    gemeenschappelijke taal waarmee agents, skills en het dashboard communiceren.
    Zonder gestructureerde governance-data kan het dashboard geen compliance-paneel
    tonen, kan de governance-check niet deterministisch valideren, en kan dev-lead
    niet formeel delegeren op basis van agent-capabilities.
  kritiek_pad: nee
  parallel_mogelijk_met:
    - "SPRINT_INTAKE_KENNISKETEN_END_TO_END"
    - "SPRINT_INTAKE_DEVHUB_DASHBOARD_NICEGUI"
```

## Open vragen Claude Code

```yaml
open_vragen:
  - vraag: "Hoe parst de governance-check skill momenteel de DEV_CONSTITUTION?"
    context: "Bepaalt of bestaande tests moeten worden aangepast na YAML-verrijking"
    urgentie: hoog

  - vraag: "Laden agents hun eigen .md definitie, en zo ja: parsen ze de frontmatter?"
    context: "Bepaalt of uitgebreide frontmatter direct bruikbaar is of extra parsing nodig heeft"
    urgentie: hoog

  - vraag: "Is er een YAML-parser beschikbaar in de agent-runtime?"
    context: "Als agents frontmatter moeten parsen, moet er een parser zijn"
    urgentie: middel

  - vraag: "Welke tests raken de DEV_CONSTITUTION content?"
    context: "Impact-analyse voor D1 (YELLOW-zone)"
    urgentie: middel

  - vraag: "Wil je de Mermaid-diagrammen (D4) valideren via CI?"
    context: "mermaid-cli bestaat als npm package voor CI-validatie"
    urgentie: laag
```

## Prioriteit

```yaml
prioriteit:
  niveau: Hoog
  motivatie: |
    Enabler voor meerdere Fase 4 deliverables (dashboard, governance-check, kennisketen).
    Relatief lage implementatie-effort (S-M) met brede impact op token-efficiëntie en
    betrouwbaarheid van agent-gedrag. Hoe langer dit uitgesteld wordt, hoe meer
    systeembestanden in proza-only formaat bijkomen die later alsnog geconverteerd moeten worden.
```

## Technische richting

_Claude Code mag afwijken van onderstaande richting._

```yaml
technische_richting:
  aanpak: "in-place verrijking"
  principe: "Bestaande proza NIET herschrijven, alleen YAML/Mermaid blokken TOEVOEGEN"

  yaml_blok_formaat:
    marker: "# MACHINE-LEESBAAR BLOK"
    plaatsing: "direct na de Markdown-sectie die het beschrijft"
    voorbeeld: |
      ## Artikel 7 — Impact-zonering
      **Principe:** Wijzigingen worden geclassificeerd...
      [bestaande proza intact]

      ```yaml
      # MACHINE-LEESBAAR BLOK
      artikel: 7
      titel: Impact-zonering
      zones:
        GREEN: {criteria: [...], vereiste: automatisch, automation_allowed: true}
        YELLOW: {criteria: [...], vereiste: review, automation_allowed: false}
        RED: {criteria: [...], vereiste: menselijke_goedkeuring, automation_allowed: false}
      regels:
        - {id: "7.1", tekst: "...", enforced_by: [dev-lead]}
      ```

  agent_frontmatter:
    voorbeeld: |
      ---
      name: reviewer
      description: "Code review + anti-patronen detectie"
      model: haiku
      capabilities: [code_review, anti_pattern_detection, machine_readability_check]
      constraints:
        - art_2: "claims verifiëren tegen primaire bronnen"
        - art_7: "zone-classificatie rapporteren"
      required_packages: [devhub-core]
      depends_on_agents: []
      reads_config: [nodes.yml]
      impact_zone_default: GREEN
      ---

  volgorde:
    1: "D1 — DEV_CONSTITUTION (hoogste impact, YELLOW-zone → eerst)"
    2: "D5 — Art. 4.6 toevoegen (meteen mee met D1)"
    3: "D2 — Agent frontmatter (7 bestanden, snel)"
    4: "D6 — Reviewer update (meteen mee met D2)"
    5: "D3 — ADR standaardisatie"
    6: "D4 — Mermaid diagrammen"
    7: "D7 — Conventie-document (als laatste, beschrijft wat er is)"
```

## DEV_CONSTITUTION impact

```yaml
dev_constitution_impact:
  art_4_transparantie:
    wijziging: "Nieuw subartikel 4.6 — machine-leesbaarheidsverplichting"
    impact_zone: YELLOW
  art_7_zonering:
    wijziging: "geen — dit is een wijziging AAN het document, niet aan de regels"
    verduidelijking: "D1 voegt YAML-representatie toe van BESTAANDE regels, wijzigt geen regels"
  overig: "geen andere artikelen geraakt"
```

## Shape Up samenvatting

```yaml
shape_up:
  probleem: |
    Systeembestanden zijn proza-eerst: agents moeten hele documenten interpreteren
    om governance-regels, capabilities en beslissingen te vinden. Dit kost tokens,
    is foutgevoelig, en blokkeert deterministische governance-validatie.
  oplossing: |
    Dual-format standaard: elk systeembestand behoudt menselijke proza maar krijgt
    embedded YAML-blokken en Mermaid-diagrammen. Reviewer-agent enforced de standaard
    prospectief, DEV_CONSTITUTION Art. 4.6 borgt het als governance-regel.
  grenzen:
    wel:
      - "DEV_CONSTITUTION verrijken (9 artikelen)"
      - "Agent frontmatter uitbreiden (7 agents)"
      - "ADR formaat standaardiseren (3 ADRs)"
      - "Mermaid-diagrammen toevoegen (minimaal 3)"
      - "Art. 4.6 + reviewer-update + conventie-document"
    niet:
      - "Bestaande proza herschrijven of verwijderen"
      - "JSON Schema validatie (apart SPIKE indien gewenst)"
      - "Tutorials, how-to's of explanations converteren"
      - "BORIS-bestanden wijzigen"
      - "CI-integratie voor Mermaid-validatie (apart indien gewenst)"
  appetite: "Small-Medium (1 sprint, geschatte 20-30 bestanden)"
```

## Three Amigos

```yaml
three_amigos:
  tech_lead:
    haalbaarheid: "Hoog — toevoegen van YAML-blokken en frontmatter is low-risk"
    architectuurrisicos:
      - risico: "Bestaande governance-check tests kunnen breken door gewijzigde bestandsinhoud"
        mitigatie: "YAML-blokken zijn TOEVOEGINGEN, geen vervanging — regex op bestaande proza raakt niet"
      - risico: "YAML-blokken kunnen out-of-sync raken met proza"
        mitigatie: "Reviewer-agent checkt consistentie; conventie-document schrijft voor dat YAML-blok de bron-van-waarheid is"
    cynefin: complicated
    sprint_type: FEAT
    boris_impact: "geen directe wijzigingen"

  product_owner:
    waarde: "Direct bruikbaar voor governance-check, dashboard, dev-lead delegatie"
    roadmap_fit: "Fase 4 enabler — versterkt meerdere parallelle tracks"
    probleem_of_oplossing: "Probleem-gedreven: agents moeten proza interpreteren"
    dev_constitution_consistent: "Ja — versterkt Art. 4 (transparantie)"

  qa_invest:
    I_independent: true    # geen blokkers
    N_negotiable: true     # Claude Code bepaalt volgorde en details
    V_valuable: true       # token-efficiëntie + governance-automatisering
    E_estimable: true      # 7 deliverables, concrete scope
    S_small: true          # past in 1 sprint
    T_testable: true       # elk deliverable heeft acceptatiecriteria
    gate: "T = GROEN"
```

## Gate check

```yaml
gate_stap_3:
  1_devhub_brief_gelezen: true    # gelezen — is verouderd, SPRINT_TRACKER is SSoT (ADR-003)
  2_niet_duplicaat: true           # geen bestaand intake-document voor dit onderwerp
  3_shape_up_compleet: true        # probleem + oplossing + grenzen + appetite aanwezig
  4_invest_t_groen: true           # acceptatiecriteria per deliverable
  5_past_in_fase: true             # Fase 4 — Verbindingen
  6_sprint_type_cynefin: true      # complicated → FEAT
  7_claims_geverifieerd: true      # DEV_CONSTITUTION, agents, ADRs zelf gelezen deze sessie
  8_auto_memory_geraadpleegd: true # MEMORY.md gelezen bij sessie-start
  9_cross_project_impact: true     # BORIS: indirect, geen directe wijzigingen
```
