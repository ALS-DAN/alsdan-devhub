# SPRINT_INTAKE_N8N_EVENT_SCHEDULER_2026-03-28

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: SPIKE
fase: 4
cynefin: complex
---

## Doel

Onderzoek en valideer hoe n8n als externe event-scheduler voor DevHub kan fungeren — periodieke taken (health checks, knowledge decay scans, sprint prep) automatiseren en koppelen aan de event bus uit Sprint 2.

## Probleemstelling

### Waarom nu

DevHub's event bus (Sprint 2) maakt het systeem reactief *tijdens* een sessie. Maar veel waardevolle taken vereisen **periodieke uitvoering** los van actieve Claude Code sessies:

1. **Health checks draaien niet:** De `/devhub-health` skill bestaat en werkt, maar wordt alleen getriggerd als iemand eraan denkt. Er is geen wekelijkse of dagelijkse automatische health check. Degradatie wordt pas opgemerkt als het te laat is.

2. **Kennis veroudert ongemerkt:** Knowledge decay detectie is geïdentificeerd als essentieel (ROADMAP Golf 2C), maar er is geen mechanisme dat periodiek kennis scant op veroudering. Drie maanden oude GOLD-kennis kan nu achterhaald zijn door nieuwe Anthropic releases of framework-updates.

3. **Sprint prep is handwerk:** Elke sprint begint met handmatige prep (context ophalen, inbox scannen, afhankelijkheden checken). Dit kan grotendeels geautomatiseerd worden als een pre-sprint workflow.

4. **Prompt evolution stopt:** DevHub's agent-prompts verbeteren niet automatisch op basis van resultaten. Er is geen feedback loop die meet welke prompts beter presteren en voorstellen doet.

### SOTA-onderbouwing

- **n8n als AI-orchestrator:** n8n's AI Agent node kan Claude aansturen via MCP-tools. DevHub heeft al geverifieerde MCP-tools: `search_nodes`, `search_templates`, `validate_workflow`, `validate_node`, `get_template`. **Kennisgradering: BRONZE** — volwassen extern ecosysteem, niet getest in DevHub-context (bron: [n8n-MCP for Claude Code](https://github.com/czlonkowski/n8n-mcp)).

- **Event-driven workflows als extern brein:** "The scheduler pattern — using external orchestrators for periodic tasks while keeping the agent system focused on reactive work — is emerging as a best practice for production AI systems." **Kennisgradering: SILVER** (bron: [Multi-Agent Orchestration Patterns](https://www.ai-agentsplus.com/blog/multi-agent-orchestration-patterns-2026)).

- **Relevante n8n-nodes (geverifieerd in eerdere research):**
  - `scheduleTrigger` / `cron` — periodieke triggers
  - `githubTrigger` — start bij push/PR events
  - `GitHub` node + `GitHub Tool` (AI Agent variant) — repo-interactie
  - `GitHub Document Loader` — repository-inhoud laden

### Fase-context

Fase 4 Golf 3 (Automatisering). Dit bouwt voort op Golf 2 (event bus) en maakt DevHub autonoom: het systeem draait zelfstandig, niet alleen als iemand het aanroept. De 9 geparkeerde n8n IDEAs worden hier concreet.

### Bestaande n8n IDEAs (geparkeerd, nu ontgrendeld)

| IDEA | Relevantie | Status |
|------|-----------|--------|
| `IDEA_N8N_HEALTH_CHECK_WORKFLOW` | Primair — periodieke health checks | Geparkeerd |
| `IDEA_N8N_KNOWLEDGE_DECAY_SCAN` | Primair — kennisveroudering detectie | Geparkeerd |
| `IDEA_N8N_SPRINT_PREP_SYNTHESE` | Primair — geautomatiseerde sprint prep | Geparkeerd |
| `IDEA_N8N_PROMPT_EVOLUTION_LOOP` | Secundair — prompt verbetering | Geparkeerd |
| `IDEA_N8N_SPRINT_RETROSPECTIVE_LOOP` | Secundair — automatische learnings | Geparkeerd |
| `IDEA_N8N_GOVERNANCE_CHECK_ON_MERGE` | Secundair — merge-time governance | Geparkeerd |
| `IDEA_N8N_PR_QUALITY_GATE` | Tertiair — PR kwaliteitscheck | Geparkeerd |
| `IDEA_N8N_SELF_HEALING_WORKFLOW` | Tertiair — auto-repair | Geparkeerd |
| `IDEA_N8N_EXPERIMENT_LOOP_KARPATHY` | Fase 5 — experiment loop | Geparkeerd |

### n8n hosting beslissingen (geverifieerd, 2026-03-24)

Eerder besloten (zie auto-memory `project_n8n_decisions.md`):
- Hosting: lokaal (Docker) of n8n Cloud
- Auth: API key + webhook secrets
- Notificatie: via GitHub of webhook
- Paden: n8n leest DevHub repo via GitHub API

## Onderzoeksvragen (SPIKE scope)

### V1: Architectuur — hoe koppelt n8n aan de event bus?

- Kan n8n events publiceren op DevHub's event bus? Of is het een gescheiden wereld?
- **Hypothese:** n8n als externe producer — publiceert events via webhook of file-based trigger die de event bus oppikt bij volgende sessie-start. Geen real-time koppeling nodig.
- Alternatief: n8n triggert Claude Code CLI direct (`claude-code --skill devhub-health`) — is dit betrouwbaar?

### V2: Welke workflows eerst?

- Prioritering van de 9 IDEAs op basis van impact × haalbaarheid.
- **Hypothese:** Health Check Workflow (hoogste impact, laagste complexiteit) → Knowledge Decay Scan (hoog, middel) → Sprint Prep Synthese (middel, middel).

### V3: n8n ↔ DevHub data-flow

- Hoe leest n8n DevHub's status? Via GitHub API (repo-bestanden), via DevHub's event bus (webhook), of via een dedicated API?
- Hoe schrijft n8n resultaten terug? Als event, als bestand in repo (via git commit), of als notificatie?

### V4: Kosten en operationeel

- n8n Cloud vs. Docker lokaal — wat past bij solo developer (avonduren/weekenden)?
- Token-kosten: als n8n periodiek Claude triggert, wat kost dat per week?
- Failure handling: wat gebeurt er als een scheduled workflow faalt?

### V5: Event bus bridge

- Hoe verbindt de event bus (Sprint 2, in-memory) met n8n (extern, altijd-aan)?
- **Hypothese:** Bi-directioneel via webhooks:
  - n8n → DevHub: webhook trigger bij sessie-start leest n8n-resultaten
  - DevHub → n8n: sprint-close event triggert n8n webhook voor retrospective

## Deliverables

- [ ] **Analyse-rapport:** n8n architectuur voor DevHub (hosting, auth, data-flow, event bus bridge)
- [ ] **PoC Workflow 1:** Health Check — scheduled trigger → DevHub health check → rapportage (GitHub issue of markdown)
- [ ] **PoC Workflow 2:** Knowledge Decay Scan — scheduled trigger → kennis-scan → signalering
- [ ] **Prioriteringsmatrix:** Alle 9 n8n IDEAs gerangschikt op impact × haalbaarheid × kosten
- [ ] **Event bus bridge ontwerp:** Hoe n8n en de event bus samenwerken (webhook, file-based, CLI)
- [ ] **Operationeel voorstel:** Hosting, kosten, failure handling, monitoring

## Grenzen (wat we NIET doen)

- NIET alle 9 n8n workflows bouwen — alleen 1-2 PoC workflows
- NIET de event bus wijzigen voor n8n-integratie (de bus moet al staan via Sprint 2)
- NIET productie-grade n8n deployment — alleen PoC-level
- NIET BORIS-specifieke workflows
- NIET de Karpathy Experiment Loop (dat is Fase 5)
- NIET real-time n8n ↔ event bus koppeling in v1 — async/webhook is voldoende

## Afhankelijkheden

| Type | Beschrijving |
|------|-------------|
| Geblokkeerd door | Sprint 2 (Event Bus) — n8n moet events kunnen consumeren/produceren via de bus |
| Blokkeert | Fase 4 Golf 3B (Event-driven sprint lifecycle) — combineert event bus + n8n |
| BORIS impact | Nee — alleen DevHub-interne workflows |
| Raakt skills | devhub-health (target van eerste PoC), devhub-sprint-prep (target van PoC 2-3) |
| Externe deps | n8n (Cloud of Docker), GitHub API, webhook endpoints |
| Raakt geparkeerde items | 9 n8n IDEAs in `docs/planning/parked/` worden concreet |

## Open vragen voor Claude Code

1. Kan `claude-code` CLI non-interactief getriggerd worden vanuit n8n (bijv. `claude-code --skill devhub-health --non-interactive`)? Of moet het via MCP?
2. Hoe handelt n8n authenticatie af als het DevHub's GitHub repo moet lezen/schrijven?
3. Is er een manier om n8n workflow-resultaten als events op de bus te publiceren zonder dat Claude Code actief is? (bijv. file-based event queue die bij sessie-start wordt ingelezen)
4. Hoeveel tokens kost een gemiddelde health check run? Dit bepaalt of dagelijks of wekelijks realistisch is.
5. Kan n8n de event bus webhooks aanroepen, of moet er een intermediaire API-laag tussen?

## Prioriteit

**Middel** — Dit is de derde sprint in de reeks en geblokkeerd door Sprint 2. De PoC-resultaten bepalen of de overige 7 geparkeerde n8n IDEAs haalbaar zijn. Hoge strategische waarde (DevHub autonoom maken) maar lagere urgentie dan Sprint 1 en 2.

## DEV_CONSTITUTION impact

| Artikel | Geraakt | Toelichting |
|---------|---------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Geautomatiseerde taken vereisen duidelijke scope — alleen GREEN zone acties autonoom |
| Art. 3 (Codebase Integriteit) | Ja | n8n mag niet ongecontroleerd naar de repo schrijven |
| Art. 4 (Transparantie) | Ja | Alle n8n-acties gelogd en traceerbaar |
| Art. 7 (Impact-zonering) | GEEL | Externe dependency, nieuwe infrastructuur |
| Art. 8 (Dataminimalisatie) | Ja | n8n mag geen secrets/credentials in workflows opslaan die in repo terechtkomen |

## Technische richting (Claude Code mag afwijken)

Aanbevolen aanpak:

1. **Start met hosting-keuze** — Docker lokaal is simpeler voor solo dev, n8n Cloud is minder onderhoud
2. **Bouw PoC 1: Health Check** — simpelste workflow, hoogste impact, bewijst het patroon
3. **Ontwerp event bus bridge** — hoe praten n8n en de bus met elkaar
4. **Bouw PoC 2: Knowledge Decay** — complexer, valideert het patroon op een tweede use case
5. **Documenteer en prioriteer** — rangschik de overige 7 IDEAs op basis van PoC-learnings

## Relatie met andere sprints

```
Sprint 1: Agent Teams SPIKE
    ↓ inzicht: hoe werken teammates samen?
Sprint 2: Event Bus FEAT
    ↓ event-triggers beschikbaar
Sprint 3: n8n Scheduler SPIKE (deze)
    ↓ periodieke automatisering
────────────────────────────────
Vervolgsprints (na SPIKE validatie):
- FEAT: n8n Health Check Workflow (productie-grade)
- FEAT: n8n Knowledge Decay Workflow
- FEAT: n8n Sprint Prep Synthese
- FEAT: Event-driven Sprint Lifecycle (combineert bus + n8n)
```
