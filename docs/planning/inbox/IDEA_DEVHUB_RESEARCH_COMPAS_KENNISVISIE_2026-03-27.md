# IDEA: DevHub Research Compas & Kennisvisie

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 3
type: visiedocument (overkoepelend — raakt meerdere bestaande intakes)
---

## Kernidee

DevHub adopteert het **Research Compas** — een vertaling van BORIS' MEC-methode (Master Evidence Core, ADR-037) naar de development-context. Zes Research Questions (RQ1–RQ6) vormen de universele structuur waarmee elk kennisdomein systematisch wordt onderzocht, ongeacht of het over AI-engineering, sprint-methodiek of security gaat. Dit compas wordt gecombineerd met een **drie-ringen domeinstructuur**, **agent knowledge profiles**, een **auto-bootstrap mechanisme**, en een **real-time monitoring pipeline** die DevHub's kennisbank levend houdt.

Dit document is een visiedocument: het beschrijft het eindplaatje en de architecturale keuzes. Het vervangt geen bestaande sprint-intakes maar verrijkt en verbindt ze.

## Motivatie

### Waarom dit waardevol is voor DevHub

1. **Eén onderzoekstaal over alle projecten.** BORIS gebruikt RQ1–RQ6 voor zorgdomeinen. DevHub gebruikt hetzelfde compas voor development-domeinen. Elk toekomstig project spreekt dezelfde taal. Dit maakt cross-project kennisuitwisseling mogelijk en verlaagt de cognitieve belasting.

2. **Agents die zelf weten wat ze niet weten.** Nu wordt de researcher alleen handmatig getriggerd. Met knowledge profiles weet elke agent welke kennis hij nodig heeft, kan hij lacunes detecteren, en kan hij zelfstandig ResearchRequests genereren. Het systeem wordt zelfsturend.

3. **Kennis die niet veroudert.** AI-engineering beweegt zo snel dat kennis van drie maanden geleden al achterhaald kan zijn. Een monitoring pipeline die dagelijks Anthropic-releases checkt en wekelijks het bredere veld scant, houdt de kennisbank actueel zonder handmatig werk.

4. **Professionele ontwikkeling als integraal onderdeel.** RQ3 (Transmissie) vertaalt zich naar leerpaden en drempelconcepten — precies wat de mentor-agent nodig heeft om Niels' groei te sturen. De kennisbank voedt niet alleen de agents, maar ook de architect.

5. **Vendor-agnostisch en toekomstbestendig.** Door het compas als abstractie te gebruiken (niet gebonden aan een specifieke vectorstore of opslaglaag) kan de implementatie evolueren terwijl de kennisstructuur stabiel blijft.

---

## Deel 1: Het DevHub Research Compas (RQ1–RQ6)

### Herkomst

Het Research Compas is afgeleid van BORIS' MEC-methode (Master Evidence Core), vastgelegd in ADR-037. De MEC-methode definieert zes complementaire lenzen waarmee elk kennisdomein systematisch wordt onderzocht. In BORIS zijn deze lenzen gericht op zorgdomeinen (autisme, GGZ, LVB). In DevHub vertalen we ze naar development-domeinen.

**Bronvermelding:** BORIS ADR-037 (Accepted, 2026-03-18, beslisser: Niels). De vertaling naar DevHub is een nieuwe toepassing, niet een kopie — DevHub respecteert BORIS' project-soevereiniteit (Art. 6 DEV_CONSTITUTION).

### De zes Research Questions

#### RQ1 — Taxonomie
*"Wat is de moleculaire structuur en ontologie van dit domein?"*

**BORIS-context:** Classificatie en conceptstructuur van zorgdomeinen. Hoe is autisme opgebouwd als kennisdomein? Welke subtypes, comorbiditeiten, diagnostische criteria bestaan er?

**DevHub-vertaling:** Hoe is een development-domein opgebouwd? Wat zijn de categorieën, subcategorieën, en relaties?

**Voorbeeld — domein "multi-agent architectuur":**
- Welke architectuurpatronen bestaan er? (orchestrator, blackboard, hierarchy, swarm, pipeline)
- Hoe verhouden die patronen zich tot elkaar? (complementair, exclusief, hiërarchisch)
- Welke taxonomie gebruiken de belangrijkste bronnen? (Anthropic, LangChain, CrewAI, AutoGen)
- Waar zijn de grenzen van het domein? (wanneer is iets "multi-agent" vs. "tool use" vs. "workflow"?)

**Voorbeeld — domein "sprint-methodiek":**
- Welke sprint-frameworks bestaan er? (Scrum, Kanban, Shape Up, XP, hybrid)
- Hoe classificeer je sprint-typen? (FEAT, SPIKE, CHORE, PATCH — DevHub's eigen Cynefin-mapping)
- Welke rollen en ceremonies horen bij elk framework?
- Waar overlap en waar divergeren de frameworks?

**Output-type:** Conceptkaarten, taxonomie-bomen, domeinmodellen, glossaria.

**Waarde voor agents:** De planner gebruikt RQ1-kennis om sprint-typen correct te classificeren. De researcher gebruikt het om zoekscope af te bakenen. De dev-lead gebruikt het om werk te categoriseren.

#### RQ2 — Modulariteit
*"Hoe deconstrueren we dit in hiërarchische informatie-eenheden?"*

**BORIS-context:** Hoe breek je complexe zorgkennis op in leerbare, herbruikbare eenheden voor professionals en cliënten?

**DevHub-vertaling:** Hoe structureer je development-kennis in bruikbare, doorzoekbare, combineerbare eenheden?

**Voorbeeld — domein "prompt engineering":**
- "Prompt engineering" als één artikel is te breed en onbruikbaar
- Modulair wordt: system prompts → few-shot patterns → chain-of-thought → tool use patterns → context window management → temperature/sampling → evaluation
- Elk module is een zelfstandig kennisartikel dat los gelezen kan worden, maar ook in combinatie
- Granulariteit: een module behandelt één concept met voldoende diepte om het toe te passen

**Voorbeeld — domein "testing":**
- Unit testing → integration testing → e2e testing → property-based testing → mutation testing
- Per categorie: wanneer inzetten, trade-offs, tooling, patronen
- Cross-referenties: property-based testing raakt ook "Python/architectuur" (Hypothesis library)

**Output-type:** Kennisartikelen met duidelijke scope, cross-referenties naar gerelateerde modules.

**Waarde voor agents:** De coder zoekt specifieke modules ("hoe schrijf ik property-based tests voor dataclasses?"). De curator valideert of artikelen de juiste granulariteit hebben — niet te breed (onbruikbaar), niet te smal (fragmentatie).

#### RQ3 — Transmissie
*"Welke drempelconcepten zijn nodig voor maximale retentie?"*

**BORIS-context:** Welke kernconcepten moet een professional begrijpen om effectief met een zorgdomein te werken? Wat zijn de prerequisites?

**DevHub-vertaling — tweeledig:**

**3a. Drempelconcepten voor de architect (mentor-functie):**
Welke concepten moet Niels begrijpen om een technologie effectief toe te passen? Dit is de directe koppeling met het mentor-systeem (Track M).

- **Voorbeeld — "RAG-architectuur" vereist als drempelconcepten:** embeddings (wat zijn het, hoe werken ze), similarity search (cosine vs. dot product), chunking strategieën, retrieval vs. generation trade-off
- **Voorbeeld — "multi-agent governance" vereist:** agent boundaries, capability delegation, trust zones, observation patterns
- **Leerpad-implicatie:** Als de mentor detecteert dat Niels op Dreyfus-niveau 2 zit voor embeddings, maar een sprint vereist RAG-kennis, dan triggert RQ3 een leerpad: eerst embeddings begrijpen, dan chunking, dan pas RAG-architectuur
- **Scaffolding-koppeling:** RQ3 bepaalt hoeveel scaffolding de mentor biedt. Dreyfus 1-2: HIGH scaffolding met stap-voor-stap uitleg. Dreyfus 3-4: LOW scaffolding, alleen de uitdaging. Dreyfus 5: REVERSE — documenteer het als ADR

**3b. Drempelconcepten voor agents (effectiviteit):**
Welke achtergrondkennis moet een agent hebben om zijn taak goed uit te voeren? Dit is een nieuw perspectief dat niet in de huidige intakes zit.

- **Voorbeeld — de reviewer** moet anti-patronen kennen om ze te detecteren. Zonder RQ3-kennis over "wat zijn de meest voorkomende anti-patronen in Python async code?" kan de reviewer ze niet herkennen
- **Voorbeeld — de planner** moet estimation-technieken begrijpen (planning poker, Monte Carlo, t-shirt sizing) om de juiste te kiezen voor een gegeven context
- **Implicatie:** De auto-bootstrap (zie Deel 4) zaait RQ3-kennis specifiek voor de domeinen die een agent nodig heeft

**Output-type:** Leerpaden met prerequisites, concept-dependency graphs, drempelconceptlijsten per domein.

**Waarde voor agents:** De mentor bouwt leerpaden op basis van RQ3. De planner weet welke concepten hij moet begrijpen voordat hij een bepaald type sprint kan plannen. De researcher structureert bronnen op basis van prerequisite-relaties.

#### RQ4 — Gevalideerde Interventies
*"Welke actie-reactie patronen zijn empirisch bewezen?"*

**BORIS-context:** Welke behandelingen, interventies en benaderingen hebben wetenschappelijk bewezen effectiviteit?

**DevHub-vertaling:** Welke development-praktijken, patronen en aanpakken zijn empirisch gevalideerd — niet alleen populair of aanbevolen, maar daadwerkelijk bewezen effectief?

**Voorbeeld — domein "code review":**
- GOLD: "Code review vindt meer defecten dan testing alleen" (IEEE TSE, meerdere meta-analyses)
- SILVER: "Kleine PRs (<200 regels) krijgen betere reviews" (Google Engineering Practices, breed geadopteerd)
- BRONZE: "Pair programming als real-time review vervangt async review voor complexe code" (praktijkervaring, beperkt onderzoek)
- SPECULATIVE: "AI-assisted review is even effectief als menselijke review voor standaard patronen" (vroege resultaten, niet gerepliceerd)

**Voorbeeld — domein "estimation":**
- GOLD: "Planning Poker levert betere schattingen dan individuele expert-inschatting" (meerdere studies)
- SILVER: "Reference class forecasting verbetert projectschattingen" (Kahneman, breed gevalideerd buiten software)
- BRONZE: "Story points zijn beter dan uren voor relatieve inschatting" (brede adoptie, beperkt onderzoek)
- SPECULATIVE: "AI-assisted estimation op basis van historische data overtreft menselijke inschatting" (vroeg stadium)

**Voorbeeld — domein "AI-engineering":**
- GOLD: "RAG verbetert factual accuracy van LLMs significant" (meerdere benchmark-studies)
- SILVER: "Chain-of-thought prompting verbetert redeneerperformance" (Google/Anthropic, peer-reviewed)
- BRONZE: "Multi-agent systemen presteren beter dan single-agent voor complexe taken" (case studies, beperkt gecontroleerd onderzoek)
- SPECULATIVE: "Self-improving agent systems bereiken superhuman performance op specifieke taken" (theoretisch, vroege experimenten)

**Output-type:** Evidence-based practice guides met expliciete gradering, bronvermelding, en toepassingscontext.

**Waarde voor agents:** De coder kiest design patterns op basis van bewezen effectiviteit, niet populariteit. De reviewer toetst code tegen gevalideerde best practices. De planner gebruikt bewezen estimation-technieken. De red-team agent kent gevalideerde attack vectors.

**Kritisch onderscheid:** RQ4 dwingt het systeem om onderscheid te maken tussen "veel mensen doen dit" (populariteit) en "dit werkt aantoonbaar" (evidence). Dit is waar de GOLD/SILVER/BRONZE/SPECULATIVE grading het meest waardevol is.

#### RQ5 — Epistemologisch Fundament
*"Welke fundamentele theorieën liggen hieraan ten grondslag?"*

**BORIS-context:** Welke wetenschappelijke theorieën vormen de basis van de zorgpraktijk? Waarom werkt een interventie — niet alleen dát het werkt, maar het mechanisme erachter.

**DevHub-vertaling:** Welke theoretische fundamenten ondersteunen onze development-keuzes? Waarom werkt Shape Up? Wat is de wiskundige basis van embeddings? Welk cognitief model verklaart waarom code review effectief is?

**Voorbeeld — domein "Shape Up (development-methodiek)":**
- Theoretisch fundament: Lean product development (Toyota Production System), Theory of Constraints (Goldratt), Bounded Rationality (Simon)
- Waarom "appetite" werkt: Theory of Constraints — de bottleneck bepaalt de throughput, niet de wenslijst
- Waarom "shaping" werkt: Bounded Rationality — mensen maken betere beslissingen met gestructureerde, afgebakende keuzes dan met open velden
- Waarom "cool-down" werkt: cognitieve hersteltijd na intense focus (Ericsson's deliberate practice pauzes)

**Voorbeeld — domein "embeddings (AI-engineering)":**
- Theoretisch fundament: Distributional Hypothesis (Harris 1954, Firth 1957), dimensionality reduction (Johnson-Lindenstrauss lemma), attention mechanisms (Vaswani 2017)
- Waarom semantic search werkt: woorden die in vergelijkbare contexten voorkomen, hebben vergelijkbare betekenissen → vergelijkbare vectorrepresentaties
- Beperkingen: de theorie voorspelt dat out-of-distribution data slecht embedded wordt → implicatie voor domein-specifieke kennis

**Voorbeeld — domein "governance (DEV_CONSTITUTION)":**
- Theoretisch fundament: Constitutionalism (juridisch), Principal-Agent Theory (economisch), Institutional Design (Ostrom)
- Waarom een constitution werkt voor AI-systemen: Principal-Agent probleem — de agent (AI) handelt namens de principal (Niels), een constitution minimaliseert agency-kosten door duidelijke constraints
- Waarom Art. 7 (impact-zonering) werkt: Tiered Trust (security principle) — niet alles verdient hetzelfde niveau van controle

**Output-type:** Theoretische fundamenten per domein met bronvermelding, mechanisme-uitleg, en implicaties voor de praktijk.

**Waarde voor agents:** De dev-lead maakt architectuurbeslissingen gebaseerd op theoretische principes, niet op trends. De researcher kan dieper zoeken wanneer hij het "waarom" begrijpt. De mentor kan concepten uitleggen vanuit eerste principes in plaats van oppervlakkige regels.

**Koppeling met mentor:** RQ5-kennis is essentieel voor Dreyfus-niveau 4-5 (Proficient/Expert). Een Novice leert "wat" (RQ1), een Competent leert "hoe" (RQ4), een Expert begrijpt "waarom" (RQ5). Het mentor-systeem gebruikt deze progressie om leerpaden te structureren.

#### RQ6 — Systemische Ecologie
*"Welke randvoorwaarden bepalen de werking van de kern?"*

**BORIS-context:** Welke contextuele factoren bepalen of een interventie werkt? Huisvesting, inkomen, sociaal netwerk — factoren buiten het zorgdomein die de uitkomsten bepalen.

**DevHub-vertaling:** Welke contextfactoren bepalen of een development-aanpak, tool of methodiek werkt in *deze specifieke situatie*?

Dit is de meest onderscheidende RQ voor DevHub. Het verschil tussen generieke kennis ("RAG is effectief") en toepasbare kennis ("RAG is effectief in deze context, maar niet in die context") zit volledig in RQ6.

**Contextfactoren voor DevHub:**

| Factor | Spectrum | Niels' positie | Implicatie |
|--------|----------|---------------|------------|
| Teamgrootte | Solo ↔ Enterprise | Solo developer | Geen PR-reviews, geen pair programming, alles via AI-agents |
| Beschikbare uren | Fulltime ↔ Avonduren | Avonduren + weekenden | Kortere sprints, minder context-switches, focus op high-impact werk |
| AI-tooling | Geen ↔ Volledig geïntegreerd | Claude Code + Cowork + MCP | Agents als teamleden, niet als tools |
| Governance-niveau | Informeel ↔ Gereguleerd | DEV_CONSTITUTION (8 art.) | Hogere overhead, maar ook hogere consistentie en traceerbaarheid |
| Projectcomplexiteit | Single app ↔ Multi-project ecosysteem | DevHub + BORIS + toekomstige projecten | Cross-project patronen, abstracties nodig |
| Domeinkennis | Generalist ↔ Specialist | T-shaped (diep: AI-engineering, breed: overig) | ZPD verschilt per domein |
| Infrastructuur | Lokaal ↔ Cloud | Hybrid (lokaal dev, n8n, Drive) | Vendor lock-in risico, offline-capability vereist |

**Voorbeeld — "Is Scrum geschikt?":**
- RQ4 zegt: "Scrum is empirisch gevalideerd voor teams van 5-9"
- RQ6 zegt: "Niels is een solo developer. Scrum's ceremonies (standup, planning, review, retro) zijn ontworpen voor teamsynchronisatie. Voor solo: overhead zonder meerwaarde. Shape Up's shaping-cycle + appetite past beter bij de solo + avonduren context."
- Conclusie: RQ4-kennis (Scrum werkt) wordt gecorrigeerd door RQ6-kennis (niet in deze context)

**Voorbeeld — "Moet DevHub microservices gebruiken?":**
- RQ4: "Microservices verbeteren schaalbaarheid en deployment-frequentie" (GOLD voor organisaties >50 developers)
- RQ6: "Solo developer, beperkte uren, geen operations-team. Microservices introduceren operationele complexiteit die de voordelen teniet doet. Monorepo met packages (uv workspace) geeft modulariteit zonder deployment-overhead."

**Voorbeeld — "Is Weaviate de juiste vectorstore?":**
- RQ4: "Weaviate scoort hoog op feature-completeness en community" (SILVER)
- RQ6: "Solo developer, moet lokaal draaien, geen dedicated infra-team. Weaviate's resource-requirements (Docker, RAM) passen, maar ChromaDB is lichter voor dev/test. Hybride aanpak: ChromaDB lokaal, Weaviate productie."

**Output-type:** Contextanalyses, situationele aanbevelingen, "werkt/werkt niet" matrices per context.

**Waarde voor agents:** Elke agent gebruikt RQ6 om generieke kennis te vertalen naar de specifieke DevHub-context. De planner past estimation aan voor solo-developer ritme. De coder kiest patterns die passen bij de monorepo-structuur. De reviewer weegt complexiteit anders voor avonduren-sprints.

### Samenvatting: Het Compas als Systeem

```
RQ1 (Taxonomie)          → WAT bestaat er?
RQ2 (Modulariteit)       → HOE structureren we het?
RQ3 (Transmissie)        → WAT moet je begrijpen om het toe te passen?
RQ4 (Gevalideerde Int.)  → WAT werkt bewezen?
RQ5 (Epistemologisch F.) → WAAROM werkt het?
RQ6 (Systemische Ecol.)  → WERKT het in DEZE context?
```

De zes RQ's zijn niet onafhankelijk — ze vormen een progressie:
- RQ1 → RQ2: van overzicht naar structuur
- RQ3 → RQ4: van begrip naar toepassing
- RQ5 → RQ6: van theorie naar context

En ze vormen een cyclus: RQ6-inzichten (contextfactoren) beïnvloeden RQ1 (welke categorieën zijn relevant in deze context), wat de cyclus herstart.

### Vergelijking BORIS ↔ DevHub

| Aspect | BORIS | DevHub |
|--------|-------|--------|
| Doeldomein | Zorg (autisme, GGZ, LVB, etc.) | Development (AI-eng, methodiek, security, etc.) |
| RQ1–RQ6 | Identiek compas | Identiek compas, andere voorbeelden |
| Evidence Matrix | GOLD/SILVER/BRONZE/SPECULATIVE | Identiek (hergebruik) |
| Research Orchestrator | ATLAS (A8) — bouw + query modus | Researcher agent — demand-driven + monitoring |
| Curator | CURATOR (A5) — output-curatie | KnowledgeCurator — input-curatie + freshness |
| Kennisbronnen | Webcrawl, SharePoint, interactiedata | WebSearch, API docs, papers, Anthropic releases |
| Query-isolatie | Ja (geen live web in zorgadviezen) | Nee (web search is een research-bron) |
| KWP's | 12 werkplaatsen (autisme, ggz, etc.) | Drie ringen (kern, agent-specifiek, project-specifiek) |
| Mentor-koppeling | Niet aanwezig | RQ3 → mentor leerpaden, RQ5 → Dreyfus-progressie |

**Project-soevereiniteit (Art. 6):** DevHub's Research Compas is een *vertaling*, niet een overschrijving. BORIS behoudt zijn eigen MEC-implementatie, eigen ATLAS, eigen curator. DevHub bouwt een onafhankelijke implementatie die hetzelfde conceptuele framework deelt. Dit maakt cross-project analyse mogelijk (Fase 4+) zonder projectgrenzen te schenden.

---

## Deel 2: Drie-Ringen Domeinstructuur

### Waarom de huidige vier domeinen niet volstaan

De huidige `config/knowledge.yml` definieert vier domeinen:
- ai_engineering (freshness: 3 maanden)
- claude_specific (freshness: 6 maanden)
- python_architecture (freshness: 12 maanden)
- development_methodology (freshness: 12 maanden)

**Bron:** `config/knowledge.yml` (geverifieerd deze sessie).

Dit is te smal als agents zelf kennis mogen aanvragen. De planner heeft kennis nodig over estimation en backlog management — dat valt niet in "development_methodology." De reviewer heeft kennis nodig over anti-patronen — dat valt niet in "python_architecture." De red-team agent heeft OWASP-kennis nodig — dat bestaat niet als domein.

### De drie ringen

#### Ring 1: Kern (altijd actief)

Domeinen die elk DevHub-project en elke agent raakt. Deze worden bij bootstrap als eerste gevuld.

| Domein | Freshness | Beschrijving | RQ-focus |
|--------|-----------|-------------|----------|
| `ai_engineering` | 3 mnd | Prompt engineering, agent architectuur, RAG, tool use, context management | RQ1 (patronen), RQ4 (wat werkt), RQ5 (waarom) |
| `claude_anthropic` | 1 mnd | Model capabilities, Claude Code, MCP, API changes, Anthropic releases | RQ1 (wat bestaat), RQ4 (bewezen features), RQ6 (onze context) |
| `python_architecture` | 12 mnd | Design patterns, uv, Pydantic v2, typing, async | RQ2 (modulair), RQ4 (patronen), RQ5 (principes) |
| `development_methodology` | 12 mnd | Shape Up, Cynefin, DORA metrics, trunk-based development | RQ4 (wat werkt), RQ5 (waarom), RQ6 (solo context) |
| `governance_compliance` | 6 mnd | DEV_CONSTITUTION patronen, AI governance, EU AI Act, ethiek | RQ5 (theoretische basis), RQ6 (regelgeving-context) |

**Wijziging t.o.v. huidig:** `claude_specific` → `claude_anthropic` met freshness naar 1 maand (was 6). Nieuw: `governance_compliance`. Totaal: 5 kerndomeinen.

#### Ring 2: Agent-specifiek (geactiveerd per agent)

Domeinen die relevant zijn voor specifieke agent-rollen. Worden geactiveerd wanneer een agent een knowledge profile heeft dat dit domein vereist.

| Domein | Freshness | Primaire agent(s) | Beschrijving |
|--------|-----------|-------------------|-------------|
| `sprint_planning` | 6 mnd | planner | Estimation, backlog management, velocity, sprint health |
| `code_review` | 6 mnd | reviewer | Review best practices, anti-patronen, static analysis |
| `security_appsec` | 3 mnd | red-team | OWASP ASI, supply chain, threat modeling, secrets management |
| `testing_qa` | 6 mnd | coder, reviewer | Test strategieën, property-based testing, mutation testing, coverage |
| `knowledge_methodology` | 12 mnd | researcher, curator | Bronmethodiek, EVIDENCE-grading, systematische reviews, meta-analyse |
| `coaching_learning` | 12 mnd | mentor | Vygotsky ZPD, Dreyfus model, deliberate practice, scaffolding |
| `documentation` | 12 mnd | docs-agent | Diátaxis, technical writing, API docs, architecture decision records |
| `product_ownership` | 6 mnd | planner, dev-lead | Prioritering, stakeholder management, roadmap-methodiek, value mapping |

**Totaal:** 8 agent-specifieke domeinen.

#### Ring 3: Project-specifiek (geactiveerd per node)

Domeinen die relevant zijn voor specifieke geregistreerde projecten. Worden geactiveerd wanneer een project-node in `config/nodes.yml` een knowledge profile heeft.

| Domein | Freshness | Project(en) | Beschrijving |
|--------|-----------|-------------|-------------|
| `healthcare_ict` | 6 mnd | boris-buurts | Zorg-ICT standaarden, HL7 FHIR, NEN-normen, interoperabiliteit |
| `privacy_avg` | 6 mnd | boris-buurts | AVG/GDPR, DPIA, data minimalisatie, consent management |
| `multi_tenancy` | 12 mnd | boris-buurts | Tenant isolation, shared vs. dedicated resources, data partitioning |
| *(toekomstig)* | — | *(2e project)* | *(wordt gedefinieerd bij project-registratie)* |

**Totaal:** 3 project-specifieke domeinen (groeit met elk nieuw project).

### Domein-activering

Niet alle domeinen zijn altijd actief. Activering werkt als volgt:

```
Ring 1 (Kern):            ALTIJD actief voor alle agents en projecten
Ring 2 (Agent-specifiek): Actief wanneer de bijbehorende agent een taak uitvoert
Ring 3 (Project-specifiek): Actief wanneer in een project-context wordt gewerkt
```

Dit voorkomt dat de researcher kennis opbouwt die niemand gebruikt (scope governance), terwijl het systeem dynamisch kan uitbreiden wanneer nieuwe agents of projecten worden toegevoegd.

### Configuratie-uitbreiding

De huidige `config/knowledge.yml` wordt uitgebreid:

```yaml
# config/knowledge.yml — uitgebreid met drie-ringen structuur

knowledge:
  rings:
    core:
      description: "Altijd actief — raakt elk project en elke agent"
      domains:
        ai_engineering:
          freshness_months: 3
          description: "Prompt engineering, agent architectuur, RAG, tool use, context management"
          rq_focus: [RQ1, RQ4, RQ5]
          bootstrap_priority: 1
        claude_anthropic:
          freshness_months: 1
          description: "Model capabilities, Claude Code, MCP, API changes, Anthropic releases"
          rq_focus: [RQ1, RQ4, RQ6]
          bootstrap_priority: 1
          monitored_sources:
            - type: changelog
              url: "https://docs.anthropic.com/en/docs/about-claude/models"
              check_interval: daily
            - type: blog
              url: "https://www.anthropic.com/news"
              check_interval: daily
            - type: github_releases
              repo: "anthropics/claude-code"
              check_interval: daily
        python_architecture:
          freshness_months: 12
          description: "Design patterns, uv, Pydantic v2, typing, async"
          rq_focus: [RQ2, RQ4, RQ5]
          bootstrap_priority: 2
        development_methodology:
          freshness_months: 12
          description: "Shape Up, Cynefin, DORA metrics, trunk-based development"
          rq_focus: [RQ4, RQ5, RQ6]
          bootstrap_priority: 2
        governance_compliance:
          freshness_months: 6
          description: "DEV_CONSTITUTION patronen, AI governance, EU AI Act, ethiek"
          rq_focus: [RQ5, RQ6]
          bootstrap_priority: 3

    agent_specific:
      description: "Geactiveerd per agent op basis van knowledge_profile"
      domains:
        sprint_planning:
          freshness_months: 6
          description: "Estimation, backlog management, velocity, sprint health"
          rq_focus: [RQ4, RQ5, RQ6]
          primary_agents: [planner]
        code_review:
          freshness_months: 6
          description: "Review best practices, anti-patronen, static analysis"
          rq_focus: [RQ1, RQ4]
          primary_agents: [reviewer]
        security_appsec:
          freshness_months: 3
          description: "OWASP ASI, supply chain, threat modeling, secrets management"
          rq_focus: [RQ1, RQ4, RQ6]
          primary_agents: [red-team]
        testing_qa:
          freshness_months: 6
          description: "Test strategieën, property-based testing, coverage"
          rq_focus: [RQ2, RQ4]
          primary_agents: [coder, reviewer]
        knowledge_methodology:
          freshness_months: 12
          description: "Bronmethodiek, EVIDENCE-grading, systematische reviews"
          rq_focus: [RQ1, RQ5]
          primary_agents: [researcher, knowledge-curator]
        coaching_learning:
          freshness_months: 12
          description: "Vygotsky ZPD, Dreyfus, deliberate practice, scaffolding"
          rq_focus: [RQ3, RQ4, RQ5]
          primary_agents: [mentor]
        documentation:
          freshness_months: 12
          description: "Diátaxis, technical writing, API docs, ADRs"
          rq_focus: [RQ2, RQ3]
          primary_agents: [docs-agent]
        product_ownership:
          freshness_months: 6
          description: "Prioritering, stakeholder management, roadmap, value mapping"
          rq_focus: [RQ4, RQ5, RQ6]
          primary_agents: [planner, dev-lead]

    project_specific:
      description: "Geactiveerd per project-node"
      domains:
        healthcare_ict:
          freshness_months: 6
          description: "Zorg-ICT standaarden, HL7 FHIR, NEN-normen"
          rq_focus: [RQ1, RQ4, RQ6]
          nodes: [boris-buurts]
        privacy_avg:
          freshness_months: 6
          description: "AVG/GDPR, DPIA, data minimalisatie, consent"
          rq_focus: [RQ4, RQ5, RQ6]
          nodes: [boris-buurts]
        multi_tenancy:
          freshness_months: 12
          description: "Tenant isolation, shared vs. dedicated, partitioning"
          rq_focus: [RQ2, RQ4, RQ6]
          nodes: [boris-buurts]

  # Evidence Matrix (ongewijzigd — identiek aan BORIS ADR-037)
  evidence_matrix:
    GOLD:
      description: "Meta-analyse, systematische review, p < 0.001"
      min_verification_pct: 80
    SILVER:
      description: "Peer-reviewed onderzoek, brede sector-consensus"
      min_verification_pct: 50
    BRONZE:
      description: "Expert opinion, praktijkobservatie, pilotonderzoek"
      min_verification_pct: 20
    SPECULATIVE:
      description: "Theoretisch model zonder empirische toetsing"
      min_verification_pct: 0

  # Health audit drempels
  health:
    max_speculative_pct: 60
    max_stale_pct: 20
    max_single_source_pct: 70
    min_rq_coverage: 4  # minimaal 4 van 6 RQ's gedekt per actief domein
```

---

## Deel 3: Agent Knowledge Profiles

### Concept

Elke agent krijgt een `knowledge_profile` dat definieert welke domeinen hij nodig heeft en op welk minimum Evidence-niveau. Dit profiel wordt gebruikt voor:
1. **Pre-task knowledge scan:** Vóór een taak checkt de agent of voldoende kennis beschikbaar is
2. **Auto-generated ResearchRequests:** Bij lacunes genereert de agent automatisch een request
3. **Bootstrap-prioritering:** Domeinen die door meer agents vereist worden, krijgen hogere bootstrap-prioriteit

### Profielen per agent

#### dev-lead (orchestrator)
```yaml
knowledge_profile:
  required_domains:
    ai_engineering: { min_grade: SILVER, rq_focus: [RQ1, RQ4, RQ6] }
    development_methodology: { min_grade: SILVER, rq_focus: [RQ4, RQ5] }
    governance_compliance: { min_grade: BRONZE, rq_focus: [RQ5, RQ6] }
    product_ownership: { min_grade: BRONZE, rq_focus: [RQ4, RQ6] }
  pre_task_check: true
  auto_research: true  # mag zelfstandig ResearchRequests genereren
  research_depth_default: QUICK
```

#### planner
```yaml
knowledge_profile:
  required_domains:
    sprint_planning: { min_grade: SILVER, rq_focus: [RQ4, RQ5, RQ6] }
    development_methodology: { min_grade: SILVER, rq_focus: [RQ4, RQ6] }
    product_ownership: { min_grade: BRONZE, rq_focus: [RQ4] }
  pre_task_check: true
  auto_research: true
  research_depth_default: STANDARD
```

#### coder
```yaml
knowledge_profile:
  required_domains:
    python_architecture: { min_grade: SILVER, rq_focus: [RQ2, RQ4] }
    ai_engineering: { min_grade: BRONZE, rq_focus: [RQ4] }
    testing_qa: { min_grade: BRONZE, rq_focus: [RQ4] }
  pre_task_check: true
  auto_research: true
  research_depth_default: QUICK
```

#### reviewer
```yaml
knowledge_profile:
  required_domains:
    code_review: { min_grade: SILVER, rq_focus: [RQ1, RQ4] }
    python_architecture: { min_grade: SILVER, rq_focus: [RQ4] }
    testing_qa: { min_grade: BRONZE, rq_focus: [RQ4] }
    security_appsec: { min_grade: BRONZE, rq_focus: [RQ4] }
  pre_task_check: true
  auto_research: false  # reviewer zoekt niet zelf, signaleert lacunes aan dev-lead
  research_depth_default: QUICK
```

#### researcher
```yaml
knowledge_profile:
  required_domains:
    knowledge_methodology: { min_grade: GOLD, rq_focus: [RQ1, RQ5] }
    ai_engineering: { min_grade: SILVER, rq_focus: [RQ1, RQ2, RQ5] }
  pre_task_check: false  # researcher IS de kennis-ophaler
  auto_research: false
  research_depth_default: DEEP
```

#### knowledge-curator
```yaml
knowledge_profile:
  required_domains:
    knowledge_methodology: { min_grade: GOLD, rq_focus: [RQ1, RQ5] }
    governance_compliance: { min_grade: SILVER, rq_focus: [RQ5] }
  pre_task_check: false  # curator IS de kennis-valideerder
  auto_research: false
  research_depth_default: STANDARD
```

#### red-team
```yaml
knowledge_profile:
  required_domains:
    security_appsec: { min_grade: GOLD, rq_focus: [RQ1, RQ4, RQ6] }
    ai_engineering: { min_grade: SILVER, rq_focus: [RQ4, RQ6] }
    governance_compliance: { min_grade: SILVER, rq_focus: [RQ4, RQ5] }
  pre_task_check: true
  auto_research: true
  research_depth_default: DEEP
```

#### mentor
```yaml
knowledge_profile:
  required_domains:
    coaching_learning: { min_grade: GOLD, rq_focus: [RQ3, RQ4, RQ5] }
    ai_engineering: { min_grade: SILVER, rq_focus: [RQ3] }
    development_methodology: { min_grade: SILVER, rq_focus: [RQ3] }
  pre_task_check: true
  auto_research: true
  research_depth_default: STANDARD
  special_mode: "developer_growth"  # zie mentor-intake Track M
```

### Pre-task Knowledge Scan Flow

Wanneer een agent met `pre_task_check: true` een taak krijgt:

```
Agent ontvangt taak
  → Bepaal relevante domeinen (uit knowledge_profile + taak-context)
  → Query Weaviate: hoeveel artikelen per domein, op welk niveau?
  → Vergelijk met min_grade vereiste
  → Als voldoende: ga door met taak
  → Als lacune:
      → Als auto_research: true → genereer ResearchRequest
          → Prioriteit bepaald door: blokkeer ik hierdoor? (hoog) of kan ik met wat ik heb? (laag)
          → Depth bepaald door research_depth_default
          → Veld requesting_agent = deze agent
      → Als auto_research: false → signaleer lacune aan dev-lead
      → Ga door met taak (best-effort) + annoteer output met "kennislacune bij [domein]"
```

**Belangrijk:** De scan blokkeert de taak niet. De agent werkt altijd door met wat beschikbaar is (best-effort), maar signaleert de lacune. Dit voorkomt dat een solo developer 's avonds vastzit omdat de researcher nog niet klaar is.

---

## Deel 4: Auto-Bootstrap Mechanisme

### Concept

Bij eerste activering van een domein — of bij het toevoegen van een nieuw project dat dit domein nodig heeft — draait de researcher automatisch een bootstrap-pass. Dit levert BRONZE-niveau artikelen op: breed maar niet diep. Genoeg om agents een werkbare basis te geven.

### Bootstrap-profielen per domein

Elk domein krijgt een set **kernvragen** (seed questions) verdeeld over de RQ's. De researcher beantwoordt deze vragen op QUICK depth als eerste vulling.

#### Voorbeeld: domein `ai_engineering`

```yaml
bootstrap:
  domain: ai_engineering
  target_articles: 12  # minimaal 12 artikelen na bootstrap
  seed_questions:
    RQ1:  # Taxonomie
      - "Welke architectuurpatronen bestaan er voor multi-agent systemen?"
      - "Hoe classificeer je RAG-implementaties (naive, advanced, modular)?"
    RQ2:  # Modulariteit
      - "Hoe structureer je prompt engineering kennis in herbruikbare modules?"
      - "Welke componenten heeft een productie-ready agent systeem?"
    RQ3:  # Transmissie
      - "Welke drempelconcepten zijn nodig om RAG-architectuur te begrijpen?"
      - "Wat is het minimale begrip van embeddings dat een developer nodig heeft?"
    RQ4:  # Gevalideerde Interventies
      - "Welke prompting-technieken zijn empirisch gevalideerd voor redeneer-taken?"
      - "Welke multi-agent patronen zijn bewezen effectief vs. experimenteel?"
    RQ5:  # Epistemologisch Fundament
      - "Welke theorie verklaart waarom in-context learning werkt?"
      - "Wat is de wiskundige basis van vector similarity search?"
    RQ6:  # Systemische Ecologie
      - "Welke factoren bepalen of een multi-agent systeem beter presteert dan single-agent?"
      - "Hoe beïnvloedt model-keuze (Opus vs. Sonnet vs. Haiku) de systeemarchitectuur?"
```

#### Voorbeeld: domein `sprint_planning`

```yaml
bootstrap:
  domain: sprint_planning
  target_articles: 8
  seed_questions:
    RQ1:
      - "Welke sprint/iteratie frameworks bestaan er en hoe verhouden ze zich?"
    RQ2:
      - "Hoe structureer je een sprint-intake als modulair kennisdocument?"
    RQ3:
      - "Welke concepten moet een planner begrijpen: velocity, lead time, cycle time, throughput?"
    RQ4:
      - "Welke estimation-technieken zijn empirisch gevalideerd?"
      - "Wat zijn bewezen technieken voor sprint scope management?"
    RQ5:
      - "Welke cognitieve biases beïnvloeden estimation (anchoring, planning fallacy)?"
    RQ6:
      - "Hoe werkt sprint planning voor een solo developer met beperkte uren?"
      - "Welke metrics zijn zinvol voor een AI-assisted development workflow?"
```

#### Voorbeeld: domein `claude_anthropic`

```yaml
bootstrap:
  domain: claude_anthropic
  target_articles: 10
  seed_questions:
    RQ1:
      - "Welke Claude-modellen bestaan er en wat zijn hun capabilities?"
      - "Wat is de taxonomie van MCP (servers, tools, resources, prompts)?"
    RQ2:
      - "Hoe is de Claude Code plugin-architectuur opgebouwd (agents, skills, hooks)?"
    RQ3:
      - "Welke concepten moet een developer begrijpen om effectief met Claude Code te werken?"
    RQ4:
      - "Welke Claude-specifieke prompting-technieken zijn door Anthropic gevalideerd?"
      - "Welke MCP-patronen zijn bewezen effectief in productie?"
    RQ5:
      - "Wat is Anthropic's visie op AI safety en hoe vertaalt dat naar product-features?"
    RQ6:
      - "Welke Claude-limitaties zijn relevant voor onze specifieke use case (dev tooling)?"
      - "Hoe beïnvloeden rate limits en context windows onze architectuurkeuzes?"
```

### Bootstrap-uitvoering

```
Stap 1: Niels activeert een domein (of het systeem detecteert een nieuw vereist domein)
Stap 2: Researcher laadt het bootstrap-profiel
Stap 3: Per seed question:
  → WebSearch op de vraag (QUICK depth)
  → Syntheseer antwoord tot kennisartikel
  → Tag met RQ, domein, evidence grade (initieel BRONZE)
  → Curator valideert basisvereisten (bronvermelding, scope)
  → Sla op in Weaviate + markdown in knowledge/{domein}/
Stap 4: Health audit na bootstrap: zijn alle RQ's gedekt? Minimum artikelen bereikt?
Stap 5: Rapporteer aan Niels: "{domein} gebootstrapt: {n} artikelen, dekking RQ1-6: {percentages}"
```

**Autonomie-niveau:** Bootstrap is GREEN (nieuwe kennis toevoegen, geen bestaande kennis wijzigen). Draait automatisch zonder goedkeuring. Niels ziet het resultaat achteraf in het knowledge dashboard.

### Verdiepingsfase (na bootstrap)

Na de BRONZE-basis schakelt het systeem over naar demand-driven verdieping:

```
Agent voert taak uit
  → Pre-task knowledge scan detecteert: "domein X heeft alleen BRONZE, ik heb SILVER nodig"
  → Genereert ResearchRequest: depth=STANDARD, specifieke vraag
  → Researcher gaat dieper: meerdere bronnen, cross-referentie, peer-reviewed waar mogelijk
  → Curator valideert: is dit SILVER-waardig? Verificatie ≥50%?
  → Artikel wordt geüpgraded of nieuw artikel toegevoegd
```

---

## Deel 5: Real-Time Monitoring Pipeline

### Het probleem

AI-engineering beweegt zo snel dat kennis van drie maanden geleden al achterhaald kan zijn. Anthropic publiceert soms meerdere keren per week updates: model releases, API changes, Claude Code features, prompting best practices. Daarnaast is er het bredere veld: nieuwe frameworks, security advisories, Python releases, multi-agent research papers.

Zonder actieve monitoring wordt de kennisbank een snapshot die steeds verder van de werkelijkheid afdrijft.

### Drie monitoring-lagen

#### Laag 1: Gestructureerde bronnen (dagelijks, automatisch)

Bronnen met voorspelbare structuur die geautomatiseerd gepolld worden.

| Bron | Type | Check-interval | Domein(en) |
|------|------|----------------|------------|
| Anthropic Blog | Blog/RSS | Dagelijks | claude_anthropic |
| Anthropic Docs changelog | Changelog | Dagelijks | claude_anthropic |
| Claude Code GitHub releases | GitHub releases | Dagelijks | claude_anthropic, ai_engineering |
| OWASP updates | RSS/changelog | Wekelijks | security_appsec |
| Python insider blog | Blog/RSS | Wekelijks | python_architecture |
| uv releases | GitHub releases | Wekelijks | python_architecture |
| Pydantic releases | GitHub releases | Maandelijks | python_architecture |

**Implementatie via n8n:**
```
n8n workflow: "DevHub Knowledge Monitor — Daily"
  Trigger: cron (elke ochtend 07:00)
  Stappen:
    1. HTTP Request → Anthropic blog RSS
    2. Compare → vorige run (opgeslagen in n8n)
    3. Als nieuw:
       → Parse titel + samenvatting
       → Schrijf ResearchRequest naar queue:
         requesting_agent: "monitoring_pipeline"
         question: "Analyseer en verwerk: {titel}"
         domain: "claude_anthropic"
         depth: QUICK
         priority: 8  (hoog — directe impact mogelijk)
         context: "Bron: Anthropic blog, gepubliceerd {datum}"
    4. Log resultaat
```

#### Laag 2: Curated feeds (wekelijks, semi-automatisch)

Bredere bronnen die op relevantie gefilterd worden.

| Bron | Type | Domein-matching |
|------|------|----------------|
| arXiv cs.AI + cs.SE | RSS/API | Keywords matchen tegen domeinlijst |
| Hacker News (top stories) | RSS | AI/development gerelateerde items |
| The New Stack | RSS | AI-engineering, cloud native |
| InfoQ AI/ML | RSS | AI-engineering, architectuur |
| Semantic Scholar alerts | API | Paper-alerts op specifieke topics |

**Implementatie via n8n:**
```
n8n workflow: "DevHub Knowledge Monitor — Weekly"
  Trigger: cron (elke maandag 07:00)
  Stappen:
    1. HTTP Request → meerdere RSS feeds parallel
    2. Keyword filter → match tegen actieve domeinen in knowledge.yml
    3. Dedupliceer → verwijder al verwerkte items
    4. Rank op relevantie (keyword density + bron-gewicht)
    5. Top 5 items → elk een ResearchRequest:
         depth: STANDARD
         priority: 5  (middel — verrijkend, niet urgent)
    6. Samenvatting → notificatie naar Niels (optioneel, via webhook/email)
```

#### Laag 3: Exploratory research (periodiek, agent-gestuurd)

Brede scans op domein-niveau die niet gebonden zijn aan specifieke bronnen.

```
Frequentie: Per domein, op basis van freshness_months
  - claude_anthropic (1 mnd): maandelijkse brede scan
  - ai_engineering (3 mnd): elk kwartaal
  - security_appsec (3 mnd): elk kwartaal
  - overige (6-12 mnd): halfjaarlijks/jaarlijks

Uitvoering:
  KnowledgeCurator triggert → ResearchRequest:
    question: "Wat zijn de belangrijkste ontwikkelingen in {domein} sinds {laatste_scan_datum}?"
    depth: DEEP
    priority: 4
    context: "Periodieke verrijkingsscan"
```

### Hybride autonomie-model

Gebaseerd op Niels' keuze voor een hybride aanpak, gecombineerd met Art. 7 (Impact-zonering):

| Actie | Zone | Autonomie |
|-------|------|-----------|
| Bootstrap nieuw domein (seed questions) | GREEN | Automatisch — Niels ziet resultaat achteraf |
| Freshness update bestaand artikel | GREEN | Automatisch — curator valideert |
| Nieuw artikel uit monitoring pipeline | GREEN | Automatisch — standaard ingest-flow |
| Upgrade BRONZE → SILVER | GREEN | Automatisch — curator valideert verificatie% |
| Upgrade SILVER → GOLD | YELLOW | Niels' goedkeuring vereist — GOLD impliceert hoge betrouwbaarheid |
| Nieuw domein toevoegen aan Ring 2/3 | YELLOW | Niels' goedkeuring — verandert scope van het systeem |
| Artikel verwijderen/degraderen | YELLOW | Niels' goedkeuring — vermindering van kennisbank |
| Cross-project kennisuitwisseling | RED | Niels' expliciete goedkeuring — raakt project-soevereiniteit |

### Notificatie-model

Niels wil niet dagelijks notificaties over elke kennisupdate, maar wel weten wat er verandert. Voorstel:

**Dagelijks (alleen als relevant):** "Anthropic heeft [X] gepubliceerd. Impact: [hoog/middel/laag]. Status: [verwerkt/in queue]." Alleen bij hoog-prioriteit items (priority ≥ 7).

**Wekelijks (altijd):** Knowledge digest — samenvatting van nieuwe artikelen, freshness updates, openstaande ResearchRequests, health audit resultaat. Dit is de kern van het knowledge dashboard.

**Bij trigger:** Wanneer een agent een kennislacune detecteert die zijn taak beïnvloedt, krijgt Niels een notificatie: "De planner mist SILVER-niveau kennis over [X]. ResearchRequest ingediend, prioriteit [Y]."

---

## Deel 6: Knowledge Dashboard

### Concept

Een centraal overzicht waar Niels de gezondheid, dekking en activiteit van de kennisbank ziet. Toegankelijk via de `/devhub-health` skill (uitbreiding met kennis-dimensie) of een apart `/devhub-knowledge-status` commando.

### Dashboard-elementen

#### 1. Domein-overzicht

```
═══════════════════════════════════════════════════════════════
KNOWLEDGE STATUS — 2026-03-27
═══════════════════════════════════════════════════════════════

RING 1: KERN (altijd actief)
  ai_engineering        ████████░░  32 artikelen  GOLD:4 SILVER:12 BRONZE:14 SPEC:2  Freshness: ✅
  claude_anthropic      ██████████  28 artikelen  GOLD:2 SILVER:10 BRONZE:15 SPEC:1  Freshness: ⚠️ 3 stale
  python_architecture   ██████░░░░  18 artikelen  GOLD:1 SILVER:8  BRONZE:9  SPEC:0  Freshness: ✅
  development_method.   ████████░░  22 artikelen  GOLD:3 SILVER:9  BRONZE:8  SPEC:2  Freshness: ✅
  governance_compliance ████░░░░░░  12 artikelen  GOLD:1 SILVER:5  BRONZE:5  SPEC:1  Freshness: ✅

RING 2: AGENT-SPECIFIEK (5/8 actief)
  sprint_planning       ██████░░░░   8 artikelen  ...  Freshness: ✅
  code_review           ████████░░  10 artikelen  ...  Freshness: ✅
  security_appsec       ████░░░░░░   6 artikelen  ...  Freshness: ⚠️ update beschikbaar
  testing_qa            ██████░░░░   8 artikelen  ...  Freshness: ✅
  coaching_learning     ████████░░  10 artikelen  ...  Freshness: ✅
  knowledge_methodology ░░░░░░░░░░   (niet actief)
  documentation         ░░░░░░░░░░   (niet actief)
  product_ownership     ░░░░░░░░░░   (niet actief)

RING 3: PROJECT-SPECIFIEK (boris-buurts)
  healthcare_ict        ████░░░░░░   5 artikelen  ...  Freshness: ✅
  privacy_avg           ██████░░░░   7 artikelen  ...  Freshness: ✅
  multi_tenancy         ████░░░░░░   4 artikelen  ...  Freshness: ✅
```

#### 2. RQ-dekking per domein

```
RQ-DEKKING: ai_engineering
  RQ1 Taxonomie:            ████████░░  8 artikelen  ✅
  RQ2 Modulariteit:         ██████░░░░  5 artikelen  ✅
  RQ3 Transmissie:          ████░░░░░░  3 artikelen  ⚠️ (onder minimum)
  RQ4 Gevalideerde Int.:    ████████░░  9 artikelen  ✅
  RQ5 Epistemologisch F.:   ██████░░░░  4 artikelen  ✅
  RQ6 Systemische Ecol.:    ████░░░░░░  3 artikelen  ⚠️ (onder minimum)
```

#### 3. Activiteit

```
ACTIVITEIT (afgelopen 7 dagen)
  Nieuwe artikelen:        +5 (3 automatisch, 2 op request)
  Bijgewerkte artikelen:   +3 (freshness updates)
  ResearchRequests open:    2 (planner: estimation solo-dev, red-team: MCP security)
  ResearchRequests afgerond: 4
  Monitoring-alerts:        1 (Anthropic blog: "Claude Code hooks update")
```

#### 4. Clickable links naar bronbestanden

Elk artikel in het dashboard is een directe link naar het bronbestand. De link-resolutie werkt via de StorageInterface:

```
Artikel: "Multi-agent architectuurpatronen — RQ1 Taxonomie"
  Lokaal:  knowledge/ai_engineering/RQ1_multi_agent_patterns.md
  Drive:   https://drive.google.com/file/d/{id}/view   ← clickable link
  Weaviate: knowledge_articles/{uuid}

Artikel: "OWASP ASI 2026 — Top 10 Agentic Threats"
  Lokaal:  knowledge/security_appsec/RQ4_owasp_asi_2026.md
  Drive:   https://drive.google.com/file/d/{id}/view   ← clickable link
  Weaviate: knowledge_articles/{uuid}
```

**Vendor-agnostiek:** De StorageInterface (Track B) bepaalt waar bestanden opgeslagen worden. Als Google Drive geconfigureerd is, zijn links Drive-links. Als dat verandert naar een andere provider, veranderen de links mee. Het dashboard vraagt altijd aan de StorageInterface: "geef me de URI voor dit artikel." De specifieke URI-structuur is een implementatiedetail van de storage adapter.

#### 5. Health audit (uitbreiding van bestaande /devhub-health)

De bestaande `/devhub-health` skill doet een 6-dimensie check. Kennis wordt de 7e dimensie:

```
KNOWLEDGE HEALTH
  Overall:                 78/100  ⚠️
  Grading distributie:     OK (42% SPECULATIVE — onder 60% drempel)
  Freshness:               ⚠️ (22% stale — boven 20% drempel)
    → 3 artikelen in claude_anthropic ouder dan 1 maand
    → ResearchRequests automatisch gegenereerd
  Source-ratio:            OK (35% AI-generated — onder 70% drempel)
  Domein-dekking:          OK (geen actieve domeinen met 0 artikelen)
  RQ-dekking:              ⚠️ (ai_engineering: RQ3 en RQ6 onder minimum)
  Monitoring-pipeline:     ✅ (laatste check: vandaag 07:00)
```

---

## Deel 7: Kennisbehoefte-Mapping (Project → Domeinen)

### Concept

Per geregistreerd project in `config/nodes.yml` wordt een knowledge_profile gedefinieerd dat aangeeft welke domeinen relevant zijn en op welk niveau. Dit stuurt welke domeinen geactiveerd worden (Ring 3), welke bootstrap-prioriteit ze krijgen, en hoe de curator de health audit uitvoert.

### Configuratie-uitbreiding nodes.yml

```yaml
# config/nodes.yml — uitgebreid met knowledge_profile

nodes:
  boris-buurts:
    path: "projects/buurts-ecosysteem"
    adapter: "packages/devhub-core/devhub_core/adapters/boris_adapter.py"
    knowledge_profile:
      required_domains:
        # Ring 1 (altijd actief, maar project kan hogere eisen stellen)
        ai_engineering: { min_grade: SILVER }
        python_architecture: { min_grade: SILVER }
        governance_compliance: { min_grade: SILVER }  # BORIS heeft strikte governance
        # Ring 3 (project-specifiek)
        healthcare_ict: { min_grade: SILVER }
        privacy_avg: { min_grade: GOLD }  # AVG-compliance is kritiek voor BORIS
        multi_tenancy: { min_grade: SILVER }
      context_factors:  # RQ6-relevante factoren voor dit project
        domain: "zorg/welzijn"
        users: "zorgprofessionals + cliënten"
        compliance: "AVG, NEN 7510, Wlz"
        deployment: "multi-tenant SaaS"
        team: "solo developer + AI agents"

  # Toekomstig project (voorbeeld)
  # marketplace-project:
  #   path: "projects/marketplace"
  #   adapter: "..."
  #   knowledge_profile:
  #     required_domains:
  #       python_architecture: { min_grade: SILVER }
  #       payment_processing: { min_grade: GOLD }
  #       regulatory_compliance: { min_grade: SILVER }
  #     context_factors:
  #       domain: "e-commerce"
  #       compliance: "PSD2, PCI-DSS"
```

### Hoe de mapping werkt in de praktijk

```
Niels zegt: "Ik ga werken aan BORIS multi-tenant zone-systeem"

Dev-lead ontvangt taak
  → Detecteert project: boris-buurts
  → Laadt knowledge_profile uit nodes.yml
  → Relevante domeinen: ai_engineering, python_architecture, multi_tenancy, privacy_avg
  → Pre-task scan per domein:
      ai_engineering: 32 artikelen, SILVER+ voldoende → ✅
      python_architecture: 18 artikelen, SILVER+ voldoende → ✅
      multi_tenancy: 4 artikelen, alleen BRONZE → ⚠️ SILVER vereist
      privacy_avg: 7 artikelen, GOLD beschikbaar → ✅
  → ResearchRequest voor multi_tenancy:
      question: "Multi-tenant isolation patterns voor Python SaaS met vectorstore"
      domain: multi_tenancy
      depth: STANDARD
      priority: 7  (blokkerend voor architectuurbeslissing)
      context: "BORIS zone-systeem feature, AVG-compliance vereist"
  → Dev-lead gaat door met taak, annoteert: "multi-tenancy kennis op BRONZE, SILVER-request ingediend"
```

---

## Deel 8: Impact op Bestaand Systeem

### Huidige status (geverifieerd via git log, 2026-03-27)

De volledige kennispipeline is **operationeel**:

| Component | Status | Tests |
|-----------|--------|-------|
| Golf 1 (Research Contracts + DocumentInterface) | ✅ afgerond | +79 |
| Track C S5 (EmbeddingProviders) | ✅ afgerond | +30 |
| Golf 2A (Researcher + KnowledgeCurator) | ✅ afgerond | +53 |
| Golf 2B (KWP DEV Bootstrap) | ✅ afgerond | +29 |
| Golf 3 (Analyse Pipeline) | ✅ afgerond | +39 |
| Mentor S1+S2 (Skill Radar + Challenge Engine) | ✅ afgerond | — |
| Governance S1+S2 | ✅ afgerond | — |
| Storage Google Drive | ✅ afgerond | — |
| Vectorstore Weaviate | ✅ afgerond | — |
| **Totaal** | **1082 tests groen** | — |

Aanvullend: `packages/devhub-documents/` bestaat (DocumentInterface), research/curator contracts bestaan, `knowledge/` bevat skill_radar en retrospectives.

### Wat dit visiedocument toevoegt bovenop het bestaande

De bestaande pipeline is gebouwd op basis van de eerdere 4-domeinen scope. Dit visiedocument definieert de **volgende evolutiestap**: van een werkende pipeline naar een intelligent, zelfsturend kennissysteem. Concreet:

#### Verrijkingen van bestaande componenten

**ResearchRequest/ResearchQueue (Golf 1A, gebouwd):**
- Toevoegen: `rq_tags` veld (welke RQ's raakt dit request)
- Toevoegen: `domain_ring` veld (kern/agent/project)
- Toevoegen: query-methodes `by_domain()`, `by_rq()`
- **Impact:** GROEN — additionele velden en methodes, backward compatible

**Researcher agent (Golf 2A, gebouwd):**
- Toevoegen: RQ1-6 tagging bij artikelcreatie
- Toevoegen: auto-bootstrap mechanisme bij domein-activering
- Toevoegen: pre-task knowledge scan integratie
- **Impact:** GEEL — wijzigt bestaand gedrag van researcher

**KnowledgeCurator (Golf 2A, gebouwd):**
- Toevoegen: RQ-dekking als extra health audit dimensie
- Toevoegen: min_rq_coverage check (minimaal 4 van 6 RQ's per actief domein)
- **Impact:** GROEN — additionele audit-dimensie

**KWP DEV (Golf 2B, gebouwd):**
- Uitbreiden: van 4 naar 5+8+3 domeinen (drie ringen)
- Toevoegen: per-domein bootstrap-profielen met seed questions
- Toevoegen: domein-activering logica (Ring 2 per agent, Ring 3 per project)
- **Impact:** GEEL — significante uitbreiding van scope en configuratie

**Analyse Pipeline (Golf 3, gebouwd):**
- Toevoegen: RQ-gestructureerde analyse-templates
- Toevoegen: RQ-tags voor gerichte retrieval
- **Impact:** GROEN — template-uitbreiding, geen structuurwijziging

**Mentor (Track M S1+S2, gebouwd):**
- Koppelen: RQ3 (Transmissie) als bron voor leerpaden
- Koppelen: concept-introductie protocol via RQ3-kennis + Dreyfus-niveaus
- **Impact:** GEEL — nieuwe koppeling tussen kennissysteem en mentor

#### Volledig nieuwe componenten

**Agent knowledge profiles:**
- Nieuw configuratiebestand: `config/agent_knowledge.yml` (of uitbreiding van agents/*.md)
- Pre-task knowledge scan logica
- Auto-generated ResearchRequests vanuit agents
- **Impact:** GEEL — nieuw gedrag voor alle agents

**Drie-ringen domeinstructuur:**
- Significante uitbreiding van `config/knowledge.yml`
- Domein-activering logica in curator en researcher
- **Impact:** GEEL — configuratie-uitbreiding met runtime-gevolgen

**Monitoring pipeline:**
- n8n workflows: dagelijks (Anthropic), wekelijks (RSS), periodiek (brede scans)
- Automatische ResearchRequest-generatie vanuit monitoring
- **Impact:** GROEN voor n8n workflows (bestaande infra), GEEL voor integratie met ResearchQueue

**Knowledge dashboard:**
- Uitbreiding van `/devhub-health` skill met kennis-dimensie
- RQ-dekking visualisatie
- Clickable links via StorageInterface
- **Impact:** GEEL — skill-wijziging

### Suggestie voor implementatie-volgorde

Gegeven dat de pipeline nu operationeel is, kan dit visiedocument in fasen worden geïmplementeerd:

1. **Fase A (GROEN):** `config/knowledge.yml` uitbreiden met drie-ringen structuur + RQ-focus. Geen runtime-impact, alleen configuratie.
2. **Fase B (GROEN):** Agent knowledge profiles definiëren. Configuratie-only, nog geen runtime-integratie.
3. **Fase C (GEEL):** RQ-tagging toevoegen aan researcher output + curator health audit. Eerste runtime-wijziging.
4. **Fase D (GEEL):** Pre-task knowledge scan implementeren in agents. Agents worden kennisbewust.
5. **Fase E (GEEL):** Auto-bootstrap mechanisme voor nieuwe domeinen. Drie-ringen activering.
6. **Fase F (GROEN):** n8n monitoring workflows. Onafhankelijk van Python-runtime.
7. **Fase G (GEEL):** Knowledge dashboard in `/devhub-health`. Alles samengebracht.

### Track M (Mentor) — KOPPELING

- Mentor knowledge profile activeert domein `coaching_learning`
- RQ3 (Transmissie) wordt de primaire bron voor leerpaden
- Concept-introductie protocol gebruikt RQ3-kennis + bestaande Dreyfus-niveaus uit skill_radar
- **Impact:** GEEL — nieuwe koppeling, mentor S1+S2 zijn al gebouwd

---

## Impact

| Aspect | Impact |
|--------|--------|
| Agents | Alle 8 agents krijgen knowledge_profiles — configuratiewijziging |
| Skills | `/devhub-health` uitbreiding met kennis-dimensie |
| Governance | Research Compas wordt onderdeel van DevHub's kennisstandaard |
| Config | `knowledge.yml` significant uitgebreid (drie ringen + RQ-focus + bootstrap) |
| Config | `nodes.yml` uitgebreid met project knowledge_profiles |
| n8n | Nieuwe monitoring workflows (dagelijks + wekelijks) |
| Bestaande intakes | Golf 2A verrijkt, Golf 2B herschreven, Golf 3 verrijkt |

**Grootte:** Groot — dit is een architectureel visiedocument dat de kennisfilosofie van DevHub definieert.

## Relatie bestaand

| Component | Relatie |
|-----------|---------|
| Kennispipeline (Golf 1-3) | Dit document is de overkoepelende visie waar die golven onder vallen |
| Track M (Mentor) | RQ3 wordt de kennisbron voor leerpaden en scaffolding |
| Track C (Vectorstore) | Weaviate collections krijgen RQ-tags als metadata |
| Track B (Storage) | Links in knowledge dashboard via StorageInterface |
| BORIS MEC (ADR-037) | Conceptuele bron, onafhankelijke DevHub-implementatie |
| DEV_CONSTITUTION | Art. 5 (kennisintegriteit) wordt volledig geïmplementeerd |

## BORIS-impact

**Nee** — dit is DevHub-interne architectuur. Het hergebruikt BORIS' MEC-concept maar implementeert het onafhankelijk. BORIS behoudt zijn eigen ATLAS, CURATOR en EVIDENCE-zone. Cross-project kennisuitwisseling is pas relevant in Fase 4 (gate: expliciete Niels-goedkeuring).

## Fase-context

**Fase 3 (Knowledge & Memory).** Dit visiedocument past volledig in Fase 3 — het beschrijft hoe kennis wordt opgebouwd, gestructureerd, bewaakt en ontsloten. De monitoring pipeline raakt n8n-infrastructuur maar is conceptueel onderdeel van het kennissysteem.

**Uitzondering:** Project knowledge profiles in nodes.yml (Ring 3) voorbereiden op meerdere projecten is Fase 4-adjacent. De configuratie-structuur mag alvast bestaan, maar actieve cross-project kennisuitwisseling is Fase 4.

## Open punten

1. **Seed questions:** De voorbeelden in dit document zijn illustratief. De definitieve set kernvragen per domein moet in detail worden uitgewerkt — mogelijk als apart document of als onderdeel van de Golf 2B herschrijving.

2. **n8n workflow-details:** De monitoring pipeline is conceptueel beschreven. Specifieke n8n workflow-configuratie (nodes, credentials, error handling) moet apart worden uitgewerkt.

3. **Prioritering van domeinen:** Bij beperkte tijd — welke Ring 2 domeinen worden als eerste gebootstrapt? Voorstel: de domeinen die door de meeste agents vereist worden (sprint_planning, code_review, testing_qa).

4. **RQ-weging:** Moeten alle RQ's even zwaar wegen in de health audit, of zijn sommige RQ's belangrijker voor bepaalde domeinen? (Bijv. RQ4 is crucialer voor security_appsec dan RQ3.)

5. **Metric-definitie:** Wat is "voldoende" dekking per RQ? Minimum aantal artikelen? Minimum grading? Dit moet concreet gedefinieerd worden voor de health audit.

6. **Historisch verloop:** Moet het dashboard ook trends tonen (kennisgroei over tijd)? Dit vereist opslag van historische snapshots.

7. **Mentor-integratie timing:** De koppeling RQ3 → mentor is conceptueel beschreven maar vereist dat zowel de kennispipeline (Golf 2A+) als het mentor-systeem (Track M Sprint 3) operationeel zijn. Dit is een late-fase integratie.

---

## Bronvermelding

| Bron | Type | Relatie | Gradering |
|------|------|---------|-----------|
| BORIS ADR-037 (MEC-methode) | Architectuurdocument (geverifieerd) | RQ1-6 definitie, Evidence Matrix | Geverifieerd (gelezen deze sessie) |
| BORIS ADR-036 (ATLAS orchestrator) | Architectuurdocument (geverifieerd) | Bouw/query-modus concept | Geverifieerd (gelezen deze sessie) |
| BORIS ADR-046 (drie kennisstromen) | Architectuurdocument (geverifieerd) | Monitoring-pipeline inspiratie | Geverifieerd (gelezen deze sessie) |
| config/knowledge.yml | Configuratiebestand (geverifieerd) | Huidige 4 domeinen + health drempels | Geverifieerd (gelezen deze sessie) |
| Golf 1A-3 sprint intakes | Inbox-documenten (geverifieerd) | Bestaande kennispipeline-ontwerp | Geverifieerd (gelezen deze sessie) |
| Track M mentor intake | Inbox-document (geverifieerd) | ZPD, Dreyfus, deliberate practice | Geverifieerd (gelezen deze sessie) |
| DEV_CONSTITUTION Art. 5, 6, 7 | Governance (aangenomen) | Kennisintegriteit, soevereiniteit, zonering | Aangenomen (niet opnieuw gelezen deze sessie) |
