# IDEA: Dual-Format Machine-Leesbare Systeembestanden

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 4
---

## Kernidee

Systeembestanden in DevHub bestaan momenteel in twee werelden: sommige zijn uitstekend machine-leesbaar (config/*.yml — GOLD-niveau), andere zijn grotendeels proza die agents moeten interpreteren (DEV_CONSTITUTION, agent-definities, ADRs). Dit idee introduceert een **dual-format standaard**: elk systeembestand heeft een menselijk leesbare versie (Markdown proza) EN een machine-parsebare companion (YAML/Mermaid/gestructureerde blokken). Waar mogelijk worden beide gecombineerd in één bestand via embedded YAML-blokken en Mermaid-diagrammen.

De standaard borgt dat agents governance-regels, capabilities en architectuurbeslissingen **direct kunnen parsen** in plaats van proza te interpreteren — wat foutgevoelig is en tokens kost.

## Motivatie

Waarom waardevol voor DevHub:

1. **Token-efficiëntie.** Agents die DEV_CONSTITUTION lezen verwerken nu 243 regels proza om 9 artikelen met ~35 regels te begrijpen. Een gestructureerde YAML-companion maakt directe lookup mogelijk: `constitution.art_7.zones.RED.vereiste` → één waarde in plaats van een heel document parsen.

2. **Governance-automatisering.** De governance-check skill (`devhub-governance-check`) moet nu proza interpreteren om te valideren. Met machine-leesbare regels kan validatie deterministisch worden — geen interpretatie, maar exacte matching.

3. **Agent-coördinatie.** Dev-lead delegeert taken aan coder/reviewer maar heeft geen gestructureerde capabilities-lijst per agent. Met een formeel agent-registry weet dev-lead exact welke agent welke packages, constraints en afhankelijkheden heeft.

4. **Consistentie afdwingen.** ADRs hebben wisselende structuur (ADR-003 is excellent, ADR-001 is basic). Een verplicht frontmatter-schema dwingt consistentie af en maakt ADR-queries mogelijk (bijv. "welke ADRs raken YELLOW-zone?").

5. **Retroactieve verbetering.** Bestaande systeembestanden worden niet herschreven maar verrijkt — de menselijke leesbaarheid blijft intact, de machine-laag wordt toegevoegd.

## Impact

```yaml
impact:
  op: [governance, agents, documentatie-pipeline, reviewer-skill]
  grootte: Middel
  raakt_packages: [devhub-core]  # governance-check, agent loading
  raakt_agents: [dev-lead, reviewer, governance-check]
  raakt_skills: [devhub-governance-check, devhub-review]
```

## Huidige staat (geverifieerd 2026-03-29)

### Wat al machine-leesbaar is (A/A+ niveau)

```yaml
excellent_bestanden:
  - pad: config/nodes.yml
    formaat: YAML
    toelichting: "Project-registry met adapter-paden, volledig parsebaar"
  - pad: config/documents.yml
    formaat: YAML
    toelichting: "Diátaxis+ taxonomie, node-routing, adapter-config"
  - pad: config/knowledge.yml
    formaat: YAML
    toelichting: "16 domeinen, drie-ringen, seed_questions, monitoring — productie-grade"
  - pad: config/challenge_templates.yml
    formaat: YAML
    toelichting: "Mentor-challenges, volledig gestructureerd"
  - pad: config/agent_knowledge.yml
    formaat: YAML
    toelichting: "Agent-domein graderingen"
```

### Wat verbetering nodig heeft (B tot C+ niveau)

```yaml
verbetering_nodig:
  - pad: docs/compliance/DEV_CONSTITUTION.md
    huidig: "243 regels proza met Markdown headings"
    probleem: "Agents moeten hele document lezen om regels te vinden"
    voorstel: "Embedded YAML-blokken per artikel met rule_id, type, zone, enforcement"
    prioriteit: Hoog
    voorbeeld_huidige_staat: |
      ## Artikel 7 — Impact-zonering
      **Principe:** Wijzigingen worden geclassificeerd naar impact...
      | Zone | Criteria | Vereiste |
      | GREEN | Tests draaien... | Automatisch toegestaan |
    voorbeeld_gewenste_staat: |
      ## Artikel 7 — Impact-zonering
      **Principe:** Wijzigingen worden geclassificeerd naar impact...
      ```yaml
      # MACHINE-LEESBAAR BLOK
      artikel: 7
      titel: Impact-zonering
      zones:
        GREEN:
          criteria: [tests_groen, geen_architectuur_impact, reversibel]
          vereiste: automatisch
          automation_allowed: true
        YELLOW:
          criteria: [architectuur_impact, meerdere_componenten, api_wijzigingen]
          vereiste: review
          automation_allowed: false
        RED:
          criteria: [destructief, security_impact, data_wijzigingen, release]
          vereiste: menselijke_goedkeuring
          automation_allowed: false
      regels:
        - id: "7.1"
          tekst: "Dev-lead classificeert elke taak naar zone VÓÓR delegatie"
          enforced_by: [dev-lead, DevOrchestrator]
        - id: "7.2"
          tekst: "Bij twijfel: kies hogere zone"
          type: escalatie_regel
        - id: "7.5"
          tekst: "RED-zone taken worden nooit geautomatiseerd"
          type: hard_constraint
      ```

  - pad: agents/*.md
    huidig: "YAML frontmatter met name/description/model — rest is proza"
    probleem: "Dev-lead kent geen formele capabilities per agent"
    voorstel: "Uitbreiden frontmatter met capabilities, constraints, packages, depends_on"
    prioriteit: Hoog
    voorbeeld_huidige_staat: |
      ---
      name: dev-lead
      description: >
        DevHub orchestrator — Second Development Brain...
      model: opus
      ---
    voorbeeld_gewenste_staat: |
      ---
      name: dev-lead
      description: >
        DevHub orchestrator — Second Development Brain...
      model: opus
      capabilities: [task_decomposition, governance_check, zone_classification, sprint_lifecycle]
      constraints:
        - art_1: "architectuurbeslissingen escaleren naar Niels"
        - art_7: "RED-zone taken niet zelfstandig uitvoeren"
      required_packages: [devhub-core, devhub-storage]
      depends_on_agents: [coder, reviewer]
      reads_config: [nodes.yml, documents.yml]
      impact_zone_default: YELLOW
      ---

  - pad: docs/adr/ADR-001-n8n-cicd-architecture.md
    huidig: "Minimale structuur, geen YAML frontmatter-tabel"
    probleem: "Inconsistent met ADR-003 formaat"
    voorstel: "Standaardiseer alle ADRs op ADR-003 formaat"
    prioriteit: Middel
    standaard_frontmatter: |
      | Veld | Waarde |
      | Status | Accepted / Proposed / Superseded / Rejected |
      | Datum | YYYY-MM-DD |
      | Context | sprint/aanleiding |
      | Impact-zone | GREEN / YELLOW / RED |

  - pad: docs/golden-paths/*.md
    huidig: "Templates als embedded markdown code blocks"
    probleem: "Niet machine-processeerbaar als templates"
    voorstel: "Companion schema.yml per template met required_fields en validatie-regels"
    prioriteit: Laag

  - pad: docs/operations/*.md
    huidig: "Proza met stappen en code-voorbeelden"
    probleem: "Niet automatiseerbaar"
    voorstel: "Runbook-stappen als YAML workflow-definities naast proza"
    prioriteit: Laag
```

## Voorgestelde standaard

### Principe: Eén bestand, twee lagen

```
┌─────────────────────────────────────┐
│  Markdown proza (mens-leesbaar)     │
│  ┌───────────────────────────────┐  │
│  │ ```yaml                       │  │
│  │ # MACHINE-LEESBAAR BLOK      │  │
│  │ ...gestructureerde data...    │  │
│  │ ```                           │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ ```mermaid                    │  │
│  │ # VISUEEL BLOK               │  │
│  │ flowchart TD                  │  │
│  │   A --> B                     │  │
│  │ ```                           │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Conventies

```yaml
conventies:
  yaml_blokken:
    marker: "# MACHINE-LEESBAAR BLOK"
    plaatsing: "direct na de Markdown-sectie die het beschrijft"
    verplichting: "VERPLICHT voor governance, agent-definities, ADR-beslissingen"
    optioneel_voor: "tutorials, how-to's, explanations"

  mermaid_blokken:
    marker: "# VISUEEL BLOK"
    gebruik: "processen, workflows, afhankelijkheden, state machines"
    verplichting: "VERPLICHT voor architectuur-overzichten, agent-interacties, pipelines"
    optioneel_voor: "korte documenten zonder procescomponent"

  frontmatter:
    agent_definities:
      verplicht: [name, description, model, capabilities, constraints]
      optioneel: [required_packages, depends_on_agents, reads_config, impact_zone_default]
    adrs:
      verplicht: [Status, Datum, Context, Impact-zone]
      optioneel: [Supersedes, Superseded-by, Related]
    governance:
      verplicht: [artikel, titel, regels_als_yaml]
      optioneel: [enforcement_agents, automation_scope]
```

## Implementatie-aanpak

```yaml
implementatie:
  strategie: "retroactief + prospectief"

  retroactief:
    stap_1:
      naam: "DEV_CONSTITUTION verrijken"
      actie: "YAML-blokken toevoegen per artikel (9 blokken)"
      impact_zone: YELLOW
      reden: "governance-document, review vereist"
      geschatte_omvang: S

    stap_2:
      naam: "Agent frontmatter uitbreiden"
      actie: "capabilities/constraints toevoegen aan 7 agent-definities"
      impact_zone: GREEN
      reden: "additief, breekt niets"
      geschatte_omvang: S

    stap_3:
      naam: "ADRs standaardiseren"
      actie: "ADR-001 en ADR-002 upgraden naar ADR-003 formaat"
      impact_zone: GREEN
      reden: "additief, bestaande content blijft intact"
      geschatte_omvang: S

    stap_4:
      naam: "Mermaid-diagrammen toevoegen"
      actie: "Architectuur-overzichten, pipeline-flows, agent-interacties"
      impact_zone: GREEN
      reden: "additief"
      geschatte_omvang: M

  prospectief:
    regel: "Elk nieuw systeembestand MOET machine-leesbare blokken bevatten"
    borging: "reviewer-agent checkt machine-readability bij review"
    waar_vastleggen: "DEV_CONSTITUTION Art. 4 uitbreiden of nieuw artikel"
```

## Borging in werkproces

```yaml
borging:
  optie_a:
    naam: "Reviewer-agent verantwoordelijkheid"
    hoe: "reviewer.md frontmatter uitbreiden met machine_readability_check capability"
    check: "bij elke review: bevat systeembestand YAML-blokken waar nodig?"
    voordeel: "past in bestaand reviewproces"
    nadeel: "alleen reactief (bij reviews)"

  optie_b:
    naam: "Governance-check skill uitbreiden"
    hoe: "devhub-governance-check krijgt extra dimensie: machine-readability score"
    check: "periodieke scan van alle systeembestanden op structuur-compliance"
    voordeel: "proactief + meetbaar"
    nadeel: "meer implementatie-effort"

  optie_c:
    naam: "Beide — reviewer reactief + governance proactief"
    hoe: "reviewer checkt bij individuele wijzigingen, governance-check scant periodiek"
    voordeel: "volledig dekkend"
    aanbeveling: "DIT — minimale extra effort, maximale dekking"

  constitutie_wijziging:
    artikel: "Art. 4 (Transparantie) uitbreiden"
    toevoeging: |
      4.6. Systeembestanden (governance, agent-definities, ADRs, architectuur-overzichten)
      bevatten machine-leesbare blokken (YAML/Mermaid) naast menselijke proza.
      Nieuwe systeembestanden zonder machine-leesbare blokken worden niet geaccepteerd
      in review (enforcement: reviewer-agent).
    impact_zone: YELLOW
    reden: "governance-wijziging vereist review"
```

## BORIS-impact

```yaml
boris_impact:
  direct: nee
  indirect: ja
  toelichting: |
    De dual-format standaard is een DevHub-intern patroon. Echter, wanneer DevHub-agents
    in BORIS werken, profiteren ze van gestructureerde governance-regels (snellere lookup,
    minder tokens). Op termijn kan BORIS dezelfde standaard adopteren voor haar eigen
    AI_CONSTITUTION — maar dat is een BORIS-beslissing (Art. 6 project-soevereiniteit).
```

## Relatie bestaand

```yaml
relatie:
  raakt_agents: [reviewer, dev-lead, governance-check]
  raakt_skills: [devhub-governance-check, devhub-review]
  raakt_config: [documents.yml]  # mogelijk nieuw veld: machine_readability_required
  raakt_governance: [DEV_CONSTITUTION Art. 4]
  versterkt: [kennispipeline]  # gestructureerde data is beter indexeerbaar
  afhankelijk_van: geen  # kan onafhankelijk geïmplementeerd worden
```

## Open punten

1. **Granulariteit YAML-blokken.** Eén groot YAML-blok per document of meerdere kleine per sectie? Aanbeveling: per sectie (artikel/component/beslissing) — dat maakt partiële reads mogelijk.

2. **Validatie-schema's.** Moeten er JSON Schema's komen voor de YAML-blokken? Zou kwaliteit borgen maar is extra onderhoudslast. Kan als apart SPIKE gepland worden.

3. **Mermaid rendering.** GitHub rendert Mermaid native, maar lokaal (VS Code, Drive) is rendering wisselend. Accepteren we dat Mermaid-blokken soms als code verschijnen?

4. **Bestaande tests.** De governance-check skill heeft tests die verwachten dat DEV_CONSTITUTION proza is. Deze moeten bijgewerkt worden na YAML-verrijking. Scope: Claude Code, niet Cowork.

5. **Migration-volgorde.** Voorstel: DEV_CONSTITUTION eerst (hoogste impact), dan agents, dan ADRs, dan rest. Of alles in één sprint?
