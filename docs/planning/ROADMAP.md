# DevHub Roadmap — Geconsolideerd

---
laatst_bijgewerkt: 2026-03-28
gegenereerd_door: "Cowork Architect — alsdan-devhub"
---

## Huidige positie

```
Fase 0 ✅  Fundament (2 sprints)
Fase 1 ✅  Kernagents + Infra (2 sprints)
Fase 2 ✅  Skills + Governance incl. 2b red-team (4 sprints)
Fase 3 ✅  Knowledge + Memory + Infrastructure (22 sprints, 395→1191 tests)
           Provider Pattern + Claude Research (2 sprints, 673 tests na adapter-migratie)
           ↑ WE ZIJN HIER — 673 tests, 11 agents, 10 skills, alle tracks afgerond
Fase 4 🔲  DevHub Production-Ready (4 golven)
Fase 5 🔲  BORIS Upgrade + Uitbreiding
```

---

## Fase 0-3: Wat er al staat (AFGEROND)

31 sprints hebben het volgende opgeleverd:

**4 Python packages** — allemaal volledig geïmplementeerd en getest:
- devhub-core v0.2.0: 13 contracts, 11 agents, NodeRegistry
- devhub-storage v0.3.0: Local, Google Drive, SharePoint adapters + reconciliation
- devhub-vectorstore v0.3.0: ChromaDB, Weaviate, embedding providers
- devhub-documents v0.1.0: Markdown, ODF adapters

**Plugin-laag:**
- 7 plugin agents (dev-lead, coder, reviewer, researcher, planner, red-team, knowledge-curator)
- 10 skills (sprint, health, mentor, sprint-prep, review, research-loop, governance-check, redteam, growth, analyse)

**Governance:** DEV_CONSTITUTION (8 artikelen), 3 ADRs, 6 golden paths, 3 runbooks

**Integratie:** BorisAdapter (1.266 regels), NodeRegistry, config/nodes.yml

**Tests:** 673 tests, 54 testbestanden, 12.319 regels testcode

Alle onderdelen zijn gebouwd. Wat mist zijn de **verbindingen** en **mechanismen** die DevHub van een verzameling tools naar een zelfstandig lerend ontwikkelsysteem tillen.

---

## Fase 4: DevHub Production-Ready

**Start NOOIT zonder expliciete Niels-goedkeuring.**

DevHub heeft alle onderdelen, maar ze zijn nog niet verbonden tot een werkend geheel. Fase 4 maakt van losse componenten een samenhangend systeem dat zelfstandig kan draaien, leren en distribueerbaar is.

### Golf 1: Fundament versterken

> DevHub betrouwbaar en up-to-date maken. Voorwaarde voor alles wat volgt.

#### 1A — Housekeeping & documentatie

**Waarom:** CLAUDE.md bevat verouderde informatie (versienummers "v0.1.0" terwijl packages op v0.3.0 staan, "stub" labels die niet meer kloppen). De architectuur-documenten zijn net geschreven maar CLAUDE.md verwijst er nog niet naar.

**Wat:**
- CLAUDE.md bijwerken met correcte versienummers en status
- Verwijzingen naar architectuur-documenten toevoegen
- Verouderde referenties naar MIGRATION_PLAN verwijderen

**Bestanden:** `.claude/CLAUDE.md`

#### 1B — Agent unit tests

**Waarom:** De 11 agents in devhub-core zijn gebouwd en werken (bewezen via integratie-tests), maar hebben geen eigen unit tests. Als er iets breekt in een agent, is het moeilijk te lokaliseren.

**Wat:** Dedicated unit tests schrijven voor:
- DevOrchestrator, QAAgent, DocsAgent
- KnowledgeCurator, AnalysisPipeline, ResearchAdvisor
- SecurityScanner, GrowthReportGenerator
- ChallengeEngine, ScaffoldingManager

**Bestanden:** `packages/devhub-core/tests/test_<agent>.py` (10 nieuwe testbestanden)

#### 1C — Kennispipeline event-triggers

**Waarom:** De kennispipeline is code-compleet (KnowledgeCurator, AnalysisPipeline, ResearchAdvisor), maar niet aangesloten op events. Als een sprint eindigt, moet kennis automatisch geëxtraheerd worden — dat gebeurt nu niet.

**Wat:**
- Sprint-closure trigger: bij sprint-afsluiting → kennisextractie starten
- Retrospective-learnings automatisch opslaan in vectorstore
- Kennis categoriseren (GOLD/SILVER/BRONZE/SPECULATIVE gradering)
- Event-bus of hook-mechanisme voor triggers

**Bestanden:** Nieuwe module in `packages/devhub-core/devhub_core/events/` of integratie in bestaande agents

---

### Golf 2: Intelligentie toevoegen

> DevHub leert van wat het bouwt. Dit is de kern van het zelfverbeterend systeem.

**Afhankelijk van:** Golf 1C (kennispipeline moet actief zijn)

#### 2A — Feedback loop engine

**Waarom:** DevHub bouwt projecten maar leert er niet van. Als BORIS een slim patroon gebruikt dat beter is dan wat DevHub zelf doet, merkt DevHub dat niet op. De feedback loop is het hart van de visie: kennis stroomt in twee richtingen.

**Wat:**
- Patroon-vergelijking: project-code analyseren tegen DevHub-patronen
- Detectie: "dit project doet X beter dan DevHub"
- Voorstel-generatie: concrete verbetervoorstellen voor DevHub zelf
- Contracts bestaan al (`GrowthReport.strategic_insights`, `DevelopmentChallenge.feedback`) maar er is geen engine

**Bestanden:** Nieuwe agent of module, bijv. `packages/devhub-core/devhub_core/agents/feedback_engine.py`

#### 2B — Zelfverbeterend systeem (eerste versie)

**Waarom:** Ontgrendeld door Fase 3. DevHub moet niet alleen detecteren dat iets beter kan, maar ook voorstellen om zichzelf aan te passen. Dit is de stap van "signaleren" naar "handelen".

**Wat:**
- Verbetervoorstellen vertalen naar concrete acties (skill-update, agent-aanpassing, patroon-adoptie)
- Niels-goedkeuring voor elke zelfverbetering (Art. 1 DEV_CONSTITUTION)
- Audit trail van alle zelfverbeteringen

**Afhankelijk van:** 2A (feedback loop)

#### 2C — Knowledge decay detectie

**Waarom:** Kennis veroudert. Wat 3 maanden geleden GOLD-kennis was, kan nu achterhaald zijn. DevHub moet dit signaleren.

**Wat:**
- Periodieke scan van opgeslagen kennis
- Vergelijking met actuele bronnen
- Signalering van verouderde of tegenstrijdige kennis
- Hergradering (GOLD → BRONZE als bewijs veroudert)

**Triage-item:** `IDEA_N8N_KNOWLEDGE_DECAY_SCAN` (ontgrendeld)

---

### Golf 3: Automatisering

> DevHub draait zelfstandig, niet alleen als iemand het aanroept.

**Afhankelijk van:** Golf 1C (triggers), Golf 2 (feedback loop beschikbaar)

#### 3A — n8n workflows voor DevHub

**Waarom:** DevHub heeft runbooks die beschrijven HOE dingen moeten draaien, maar alles moet handmatig getriggerd worden. n8n kan dit automatiseren.

**Wat:**
- Prompt Evolution Loop — prompts automatisch verbeteren op basis van resultaten
- Sprint Retrospective Loop — automatisch learnings extraheren na sprint-closure
- Knowledge Decay Scan — periodiek kennis controleren op veroudering
- Sprint Prep Synthese — voorbereiding automatiseren

**Triage-items (alle ontgrendeld):**
- `IDEA_N8N_PROMPT_EVOLUTION_LOOP`
- `IDEA_N8N_SPRINT_RETROSPECTIVE_LOOP`
- `IDEA_N8N_KNOWLEDGE_DECAY_SCAN`
- `IDEA_N8N_SPRINT_PREP_SYNTHESE`

**Bestanden:** n8n workflow JSONs + setup-configuratie

#### 3B — Event-driven sprint lifecycle

**Waarom:** Nu is sprint-closure een handmatig proces. Met event-triggers kan sprint-closure automatisch kennisextractie, retrospective en HERALD-sync triggeren.

**Wat:**
- Sprint-closure → kennisextractie (Golf 1C)
- Sprint-closure → retrospective-loop (3A)
- Sprint-start → prep-synthese (3A)
- Health check op schema (wekelijks/dagelijks)

---

### Golf 4: Distributie

> DevHub wordt installeerbaar voor elk project, niet alleen vanuit de monorepo.

#### 4A — Plugin bundling

**Waarom:** DevHub werkt nu alleen als je in de monorepo zit. Zonder installeerbare plugin kan DevHub alleen BORIS bedienen.

**Wat:**
- `.claude-plugin/plugin.json` uitbreiden (nu minimale metadata)
- Plugin bundling: agents + skills + configuratie als één installeerbaar pakket
- Versioning strategie (semver)
- Installatie-instructies

**Bestanden:** `.claude-plugin/plugin.json`, nieuwe build-configuratie

#### 4B — Package distributie (Track A3-A4)

**Waarom:** Doorgeschoven uit Fase 3. Als projecten DevHub-contracts willen implementeren (NodeInterface), moeten ze `devhub-core` kunnen installeren via pip.

**Wat:**
- `devhub-core[contracts]` als pip-installeerbaar micro-package
- Agents en skills als aparte packages (optioneel)
- PEX packaging valideren

**Bestanden:** `packages/devhub-core/pyproject.toml`, packaging configuratie

#### 4C — Multi-project validatie

**Waarom:** DevHub is gebouwd voor meerdere projecten maar heeft alleen BORIS als referentie. Een tweede project (proof-of-concept) valideert dat het systeem echt node-agnostisch werkt.

**Wat:**
- Tweede project registreren in `config/nodes.yml`
- Minimale NodeInterface adapter schrijven
- DevHub skills testen met tweede project
- Multi-project data laag activeren

**Triage-item:** `RESEARCH_DEVHUB_MULTI_PROJECT_DATA_LAAG` (ontgrendeld)

---

## Fase 5: BORIS Upgrade + Uitbreiding

DevHub is production-ready. Nu kan het doen waarvoor het gebouwd is: BORIS upgraden met SOTA-kennis, zonder de ziel van de Gems te verliezen.

### 5A — BORIS bekijken met DevHub-bril

**Wat:** DevHub analyseert BORIS volledig — code-kwaliteit, architectuur, test coverage, patronen, security. Niet om te slopen, maar om te begrijpen waar verbetering mogelijk is.

**Resultaat:** Upgrade-rapport met concrete voorstellen, geprioriteerd op impact.

### 5B — Gem-identiteit bewaren, code upgraden

**Wat:** Per Gem (VERA, LUMEN, CLAIR, SCOUT, HERALD, CURATOR, ATLAS, SCRIPTOR):
- Essentie documenteren (wat maakt deze Gem uniek?)
- Code-kwaliteit verbeteren (tests, typing, error handling)
- Patronen upgraden naar DevHub SOTA-niveau
- Identiteit behouden — de Gem blijft herkenbaar

### 5C — BORIS skills upgraden

**Wat:** De bestaande BORIS skills (buurts-sprint, buurts-health, buurts-review, mentor-dev, boris-sprint-prep) upgraden met kennis uit DevHub:
- Betere workflows
- DevHub-integratie waar zinvol
- Behoud van BORIS-specifieke context en domeinkennis

### 5D — Agent Teams

**Wat:** Multi-agent orchestratie — agents die samenwerken aan complexe taken. DevHub's plugin agents coördineren met BORIS runtime agents.

### 5E — Karpathy Experiment Loop

**Wat:** Geautomatiseerde experiment-loop voor continue verbetering. DevHub stelt hypotheses op, test ze, en leert van de resultaten.

**Triage-item:** `IDEA_N8N_EXPERIMENT_LOOP_KARPATHY`

---

## Afhankelijkheden-diagram

```
Golf 1: Fundament
├── 1A Housekeeping ──────────────────────── (geen deps)
├── 1B Agent tests ───────────────────────── (geen deps)
└── 1C Kennispipeline triggers ───────────── (geen deps)
         │
Golf 2: Intelligentie
├── 2A Feedback loop engine ──────────────── (vereist 1C)
├── 2B Zelfverbeterend systeem ───────────── (vereist 2A)
└── 2C Knowledge decay ──────────────────── (vereist 1C)
         │
Golf 3: Automatisering
├── 3A n8n workflows ─────────────────────── (vereist 1C, profiteert van 2A)
└── 3B Event-driven lifecycle ────────────── (vereist 1C + 3A)
         │
Golf 4: Distributie
├── 4A Plugin bundling ───────────────────── (geen deps)
├── 4B Package distributie ───────────────── (geen deps)
└── 4C Multi-project validatie ───────────── (vereist 4A of 4B)
         │
Fase 5: BORIS Upgrade
├── 5A Analyse met DevHub-bril ───────────── (vereist Fase 4 af)
├── 5B Gem-code upgraden ─────────────────── (vereist 5A)
├── 5C Skills upgraden ───────────────────── (vereist 5A)
├── 5D Agent Teams ───────────────────────── (vereist 5B)
└── 5E Karpathy Loop ────────────────────── (vereist 2B + 3A)
```

---

## Volgorde-samenvatting

```
DONE:    Fase 0-3 — Alle onderdelen gebouwd (31 sprints, 673 tests)
GATE:    Fase 4 Golf 1 — Fundament versterken (housekeeping, tests, triggers)
DAN:     Fase 4 Golf 2 — Intelligentie (feedback loop, zelfverbetering)
DAN:     Fase 4 Golf 3 — Automatisering (n8n, event-driven)
DAN:     Fase 4 Golf 4 — Distributie (plugin, packaging, multi-project)
LATER:   Fase 5 — BORIS Upgrade + Uitbreiding
```

**Architectuurmodel:** `docs/architecture/OVERVIEW.md`
**Upgrade-model:** `docs/architecture/UPGRADE_MODEL.md`
**Fase 3 retrospective:** `knowledge/retrospectives/RETRO_FASE3_KNOWLEDGE_MEMORY.md`
