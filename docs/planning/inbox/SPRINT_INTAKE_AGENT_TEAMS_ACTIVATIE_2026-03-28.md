# SPRINT_INTAKE_AGENT_TEAMS_ACTIVATIE_2026-03-28

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: SPIKE
fase: 4
cynefin: complex
---

## Doel

Onderzoek en valideer hoe Claude Code Agent Teams geactiveerd en geconfigureerd kan worden zodat DevHub's bestaande 7 agents (dev-lead, coder, reviewer, researcher, planner, red-team, knowledge-curator) als gecoördineerd team kunnen samenwerken in plaats van als solo-workers.

## Probleemstelling

### Waarom nu

DevHub heeft 7 plugin agents en 3 project-level agents, maar ze werken uitsluitend als solo-workers. De dev-lead delegeert via subagents (één voor één, synchroon), niet via Agent Teams (parallel met onderlinge communicatie). Dit betekent:

1. **Geen parallelle uitvoering:** Coder en reviewer kunnen niet tegelijk werken aan gescheiden file-sets. Research en implementatie zijn strikt sequentieel.
2. **Geen onderlinge communicatie:** De reviewer kan de coder niet direct vragen stellen over een implementatiekeuze — alles gaat via de dev-lead als bottleneck.
3. **Geen shared task list:** Er is geen gedeeld overzicht van wie wat doet, met dependency tracking. De scratchpad JSON-queues zijn eenrichtingsverkeer (orchestrator → agent).
4. **Context-isolatie mist:** Alle agents delen impliciet dezelfde context. Agent Teams geeft elke teammate een eigen context window — betere resultaten op complexe taken.

### SOTA-onderbouwing

- **Claude Code Agent Teams** (Anthropic, feb 2026): Team lead + 2-16 teammates, mailbox-systeem, shared task list met dependency tracking, 13 TeammateTool operaties. Vijf orchestratiepatronen: Leader, Swarm, Pipeline, Council, Watchdog.
- **Kennisgradering:** SILVER — Anthropic-gedocumenteerd, breed geadopteerd (bron: [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams)), upgrade van SPECULATIVE (maart 2026 assessment).
- **90.2% betere resultaten** op complexe taken vs. single-agent (bron: [multi-agent benchmarks](https://www.codewithseb.com/blog/claude-code-sub-agents-multi-agent-systems-guide)).
- **Swarm Orchestration Skill** als referentie-implementatie (bron: [Gist](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea)).
- **AG2 (AutoGen v0.4)** herschreven rond async event-driven actor model — bevestigt dat event-driven + teams het dominante patroon is (bron: [AG2 architecture](https://arxiv.org/html/2601.13671v1)).
- **Google A2A protocol** (150+ organisaties) — Agent Cards als forward-compatible patroon voor agent discovery.

### Fase-context

Fase 4 Golf 1 (Fundament versterken). Dit is de eerste stap in het verbinden van de losse componenten tot een samenhangend systeem. Agent Teams activatie is de laagste drempel met de hoogste impact — het vereist voornamelijk configuratie en skill-aanpassing, geen nieuwe Python-code.

### Root cause analyse

DevHub's agent-architectuur is gebouwd vóór Agent Teams stabiel was (Fase 0-1, dec 2025 - jan 2026). De agents zijn ontworpen als subagent-delegatie: dev-lead spawnt een subagent, wacht op resultaat, spawnt de volgende. Agent Teams was toen SPECULATIVE. Nu het SILVER is, kan de bestaande architectuur ge-upgrade worden zonder de agents zelf te herschrijven.

## Onderzoeksvragen (SPIKE scope)

### V1: Configuratie & activatie

- Hoe wordt `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` geactiveerd in DevHub's plugin-context?
- Werkt dit via `settings.json`, environment variable, of plugin.json configuratie?
- Versie-check: vereist Claude Code v2.1.32+ — hoe borgen we dit?

### V2: Agent-mapping op TeammateTool

- Welk orchestratiepatroon past het best bij DevHub? **Hypothese:** Leader-patroon (dev-lead = team lead, rest = teammates).
- Hoe mappen de 7 agents op teammates? Welke zijn altijd actief, welke on-demand?
- File-ownership verdeling: coder owns `packages/`, reviewer owns `tests/`, researcher owns `knowledge/`, planner owns `docs/planning/`?

### V3: Compatibiliteit met bestaande delegatie

- Kan Agent Teams naast de huidige subagent-flow bestaan? Of vervangt het die volledig?
- Hoe interageert de mailbox met de bestaande scratchpad JSON-queues?
- Kan de DevOrchestrator (Python) Agent Teams triggeren, of zijn dat gescheiden werelden?

### V4: dev-lead skill-aanpassing

- Welke wijzigingen zijn nodig in `agents/dev-lead.md` om van subagent-delegatie naar team lead te gaan?
- Moet de dev-lead een nieuw "team orchestration" blok krijgen, of is TeammateTool voldoende?
- Hoe handelt de dev-lead het Council-patroon af (bijv. coder + reviewer + red-team consensus)?

### V5: Kosten en performance

- Agent Teams gebruikt ~7x tokens vs. single session. Wat is de sweet spot voor DevHub? Altijd teams, of alleen voor complexe taken (FEAT sprints)?
- Hoe voorkom je dat teammates elkaars bestanden overschrijven?

## Deliverables

- [ ] **Analyse-rapport:** Agent Teams activatie in DevHub-context (configuratie, versie-eisen, beperkingen)
- [ ] **Agent-team mapping:** Welke agents als teammates, welk patroon, file-ownership verdeling
- [ ] **PoC:** Minimale Agent Teams sessie met dev-lead + coder + reviewer op een concrete DevHub-taak
- [ ] **dev-lead.md concept v2:** Voorgestelde wijzigingen voor team lead-rol
- [ ] **Compatibiliteitsanalyse:** Agent Teams vs. bestaande subagent-flow vs. DevOrchestrator
- [ ] **Aanbeveling:** Welke taken wel/niet via Agent Teams, kosten-batenanalyse

## Grenzen (wat we NIET doen)

- NIET de Python-laag wijzigen (DevOrchestrator, agents in devhub-core)
- NIET alle 7 agents tegelijk als teammates configureren — PoC met 2-3 agents
- NIET de event bus bouwen (dat is Sprint 2)
- NIET n8n-integratie (dat is Sprint 3)
- NIET BORIS-gerelateerde wijzigingen
- NIET de bestaande subagent-flow verwijderen — naast elkaar laten bestaan

## Afhankelijkheden

| Type | Beschrijving |
|------|-------------|
| Geblokkeerd door | Geen — SPIKE kan direct starten |
| Blokkeert | Sprint 2 (Event Bus) profiteert van inzichten maar is niet hard geblokkeerd |
| BORIS impact | Nee — raakt alleen DevHub plugin-laag |
| Raakt agents | dev-lead.md (primair), coder.md, reviewer.md (als eerste teammates) |
| Raakt skills | devhub-sprint (mogelijk team-modus), dev-lead orchestratie |
| Externe deps | Claude Code v2.1.32+, CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS |

## Open vragen voor Claude Code

1. Werkt TeammateTool correct als het vanuit een plugin-agent (dev-lead.md) wordt aangeroepen, of alleen vanuit een directe Claude Code sessie?
2. Kunnen teammates elkaars agent-memory lezen (`.claude/agent-memory/`), of is dat geïsoleerd per context window?
3. Hoe interageert de shared task list met DevHub's bestaande SPRINT_TRACKER.md?
4. Is er een manier om teammate-resultaten automatisch te loggen voor de kennispipeline?
5. Kan een teammate een skill aanroepen (bijv. reviewer roept `/devhub-review` aan)?

## Prioriteit

**Hoog** — Dit is de eerste stap in Fase 4 en heeft de laagste drempel: voornamelijk configuratie, geen nieuwe Python-code. De inzichten uit deze SPIKE bepalen hoe Sprint 2 (Event Bus) en Sprint 3 (n8n) vormgegeven worden.

## DEV_CONSTITUTION impact

| Artikel | Geraakt | Toelichting |
|---------|---------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Team lead (dev-lead) behoudt orchestratie — Niels beslist architectuur |
| Art. 3 (Codebase Integriteit) | Ja | File-ownership voorkomt conflicten tussen teammates |
| Art. 4 (Transparantie) | Ja | Shared task list + mailbox = traceerbare coördinatie |
| Art. 7 (Impact-zonering) | GEEL | Nieuw concept, vereist review van PoC resultaten |

## Technische richting (Claude Code mag afwijken)

De SPIKE zou het beste werken als:
1. Eerst Agent Teams activeren in een test-setting
2. Dan een concrete DevHub-taak uitvoeren met dev-lead + coder + reviewer als team
3. Resultaten documenteren: wat werkt, wat niet, waar zijn de grenzen
4. Aanbeveling formuleren voor structurele adoptie

Verwachte output: analyse-rapport + concept dev-lead.md v2 als input voor een FEAT-sprint die de structurele wijzigingen implementeert.

## Relatie met andere sprints

```
Sprint 1: Agent Teams SPIKE (deze)
    ↓ inzichten
Sprint 2: Event Bus FEAT — profiteert van team-coördinatie inzichten
    ↓ event-triggers
Sprint 3: n8n Scheduler SPIKE — bouwt voort op event bus
```
