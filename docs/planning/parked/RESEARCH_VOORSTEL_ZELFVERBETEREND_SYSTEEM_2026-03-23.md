# RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM_2026-03-23

---
gegenereerd_door: Cowork — alsdan-devhub
status: INBOX
fase: 2-5
---

## Kennislacune

- **Domein:** AI-engineering / multi-agent architectuur / governance
- **Gat:** DevHub heeft de bouwstenen voor een zelfverbeterend systeem (QA Agent, DevOrchestrator, EVIDENCE-gradering, impact-zonering) maar mist de feedback loops die deze componenten verbinden tot een lerend geheel.
- **Huidige grading:** SPECULATIVE (concept gevalideerd in academisch onderzoek en Karpathy's autoresearch, niet in development-governance context)

## Onderzoeksvraag

**Hoe kan DevHub een zelfverbeterend systeem worden dat leert van elke sprint, zijn eigen prompts optimaliseert, kennis actueel houdt, workflows repareert, en nieuwe aanpakken experimenteel test — binnen de governance-grenzen van de DEV_CONSTITUTION?**

## Theoretisch Fundament

### Drie niveaus van zelfverbetering

Gebaseerd op het Self-Evolving Agents onderzoeksveld (survey 300+ papers, Fudan/Cambridge 2025) en het metacognitieve framework (ICML 2026 position paper):

| Niveau | Naam | Beschrijving | Autonomie |
|--------|------|-------------|-----------|
| 1 | Reflectie | Systeem kijkt terug op output en leert | Laag |
| 2 | Optimalisatie | Systeem past actief prompts/workflows aan | Middel |
| 3 | Evolutie | Systeem genereert en test nieuwe aanpakken | Hoog |

### Karpathy AutoResearch (maart 2026)

Referentie-experiment: een AI agent draaide 700 experimenten in 2 dagen, ontdekte 20 optimalisaties die 11% snelheidswinst opleverden. De drie primitieven:

1. **Editable asset** — één bestand dat de agent mag wijzigen
2. **Scalar metric** — één meetpunt dat verbetering definieert
3. **Time-boxed cycle** — vaste duur per experiment

### EvoAgentX Framework (Fudan University)

Open-source framework (2.5k+ GitHub stars) voor iteratieve prompt-verbetering via TextGrad, AFlow en MIPRO. Benchmarks tonen tot 20% accuracyverbetering.

## Bevindingen: Vijf Feedback Loops

### Loop 1: Sprint Retrospective Loop (Niveau 1 — Reflectie)

**Wat:** Na elke sprint analyseert het systeem automatisch: welke commits gelukt, welke tests faalden, taakduur vs. schatting, agent-performance.

**Mechanisme:**
- Input: git log, test reports, QA reports, sprint doc
- Analyse: patroondetectie (welke agents presteren goed, bottlenecks, onderschatte taken)
- Output: `RETROSPECTIVE_REPORT.md` per sprint

**DevHub-mapping:**
- DevOrchestrator scratchpad bevat al taak-resultaten
- QA Agent reports bevatten verdicts per taak
- BorisAdapter kan git log + test output lezen

**Governance-toets:**
| Artikel | Impact | Beoordeling |
|---------|--------|-------------|
| Art. 1 (Regie) | Niels ontvangt rapport | GREEN |
| Art. 3 (Integriteit) | Alleen lezen | GREEN |
| Art. 7 (Zonering) | Geen code-wijzigingen | GREEN |

**Fase:** 2 (vereist reviewer agent uit Fase 1)
**Kennisgradering:** SILVER — bewezen patroon in agile teams, niet specifiek met AI-agents gevalideerd

---

### Loop 2: Prompt Evolution Loop (Niveau 2 — Optimalisatie)

**Wat:** Na elke sprint worden agent system prompts (dev-lead.md, coder.md, reviewer.md) automatisch geëvalueerd en verbeterd.

**Mechanisme:**
1. QA Agent beoordeelt output van andere agents
2. Patronen die tot RED-zone escalaties leiden worden gedetecteerd
3. Systeem genereert prompt-varianten
4. Test in sandbox-sprint (GREEN-zone, geen productie-impact)
5. Niels keurt prompt-wijzigingen goed (Art. 1)

**Voorbeeld:** Als coder consistent fouten maakt bij type X taken → coder.md wordt verrijkt met specifieke instructies voor dat patroon.

**Governance-toets:**
| Artikel | Impact | Beoordeling |
|---------|--------|-------------|
| Art. 1 (Regie) | Niels keurt wijzigingen | YELLOW |
| Art. 3 (Integriteit) | Sandbox-only testing | YELLOW |
| Art. 7 (Zonering) | Prompt-wijziging = YELLOW | YELLOW |

**Fase:** 3 (vereist retrospective data + KWP DEV kennisbank)
**Kennisgradering:** BRONZE — academisch gevalideerd (EvoAgentX, 20% verbetering op benchmarks), niet in productie-dev-teams getest

---

### Loop 3: Knowledge Decay & Refresh Loop (Niveau 1 — Reflectie)

**Wat:** Automatische bewaking van Art. 5.4 (GOLD-kennis degradeert na 6 maanden naar SILVER).

**Mechanisme via n8n:**
1. `scheduleTrigger` (wekelijks) → check kennisbank op leeftijd
2. Als entry ouder dan threshold → `githubTrigger` checkt of gerelateerde code gewijzigd is
3. Code gewijzigd maar kennis niet bijgewerkt → genereer `RESEARCH_VOORSTEL_*.md`
4. Kennis nog klopt → hervalideer en reset timer

**Beschikbare n8n-nodes (geverifieerd):**
- `n8n-nodes-base.scheduleTrigger` — periodieke trigger
- `n8n-nodes-base.githubTrigger` — GitHub event trigger
- `n8n-nodes-base.github` — GitHub API interactie
- `@n8n/n8n-nodes-langchain.agent` — AI agent voor analyse

**Governance-toets:**
| Artikel | Impact | Beoordeling |
|---------|--------|-------------|
| Art. 1 (Regie) | Automatisch, adviserend | GREEN |
| Art. 3 (Integriteit) | Alleen lezen | GREEN |
| Art. 5 (Kennisintegriteit) | Direct ondersteunend | GREEN |

**Fase:** 3 (vereist KWP DEV + EVIDENCE-kopie)
**Kennisgradering:** SILVER — gebaseerd op bewezen CI/CD monitoring patterns

---

### Loop 4: Self-Healing Workflow Loop (Niveau 2 — Optimalisatie)

**Wat:** Wanneer een workflow (health check, sprint-lifecycle, agent-delegatie) faalt, diagnosticeert en repareert het systeem zichzelf.

**Mechanisme:**
1. n8n error trigger activeert error-workflow
2. Error-workflow roept Claude Code aan
3. Claude gebruikt n8n-MCP server om kapotte workflow te auditen
4. Begrijpt wat er mis ging → fixt automatisch
5. Monitoring-data voedt terug naar Loop 1

**Bewezen patroon:** Self-healing n8n workflows met Claude Code zijn gedocumenteerd en in productie bij meerdere teams (bron: n8n community, Towards Data Science).

**Governance-toets:**
| Artikel | Impact | Beoordeling |
|---------|--------|-------------|
| Art. 1 (Regie) | Binnen n8n, logs beschikbaar | YELLOW |
| Art. 3 (Integriteit) | Repareert workflows, niet code | YELLOW |
| Art. 4 (Transparantie) | Alle fixes gelogd | GREEN |

**Fase:** 2 (n8n-integratie + health check skill bestaan al)
**Kennisgradering:** SILVER — gedocumenteerd patroon, meerdere productie-cases

---

### Loop 5: Experiment Loop — "DevHub AutoResearch" (Niveau 3 — Evolutie)

**Wat:** Geïnspireerd op Karpathy's autoresearch. Het systeem genereert hypothesen, test ze in isolatie, en presenteert verbeteringen.

**Mechanisme:**
1. Systeem genereert hypothese ("Wat als reviewer agent strengere check X krijgt?")
2. Creëert geïsoleerde branch
3. Voert wijziging door (prompt of code)
4. Draait testsuite (218+ tests)
5. Vergelijkt resultaten met baseline
6. Bij verbetering → commit + PR voor Niels-review
7. Bij geen verbetering → git reset, log experiment

**Karpathy-primitieven voor DevHub:**
| Primitief | DevHub-equivalent |
|-----------|-------------------|
| Editable asset | Agent system prompts (dev-lead.md, coder.md, etc.) |
| Scalar metric | Test pass rate + QA score + sprint velocity |
| Time-boxed cycle | 5 minuten per experiment, ~12/uur, ~100 overnight |

**Governance-toets:**
| Artikel | Impact | Beoordeling |
|---------|--------|-------------|
| Art. 1 (Regie) | Niels keurt PR's goed | RED bij merge |
| Art. 3 (Integriteit) | Geïsoleerde branch | GREEN tot merge |
| Art. 7 (Zonering) | Experiment = GREEN, merge = RED | RED |

**Fase:** 5 (experimenteel, vereist volwassen systeem)
**Kennisgradering:** SILVER (Karpathy's loop is open-source en gerepliceerd, maar voor ML training, niet dev-governance)

## Samenvattende Prioritering

| Loop | Fase | Risico | Directe waarde | Aanbeveling |
|------|------|--------|----------------|-------------|
| 1. Sprint Retrospective | 2 | Laag | Hoog — data voor alle andere loops | **Eerst bouwen** |
| 4. Self-Healing | 2 | Middel | Hoog — operationele stabiliteit | **Parallel met Loop 1** |
| 3. Knowledge Decay | 3 | Laag | Middel — kennisborging | Na Fase 2 |
| 2. Prompt Evolution | 3 | Middel | Hoog — continue verbetering | Na retrospective data |
| 5. AutoResearch | 5 | Hoog | Zeer hoog (indien succesvol) | Apart bespreken met Niels |

## Bronnen

| Bron | Type | Kennisgradering |
|------|------|----------------|
| [Self-Evolving Agents Survey](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents) | Academisch survey (300+ papers) | SILVER |
| [EvoAgentX Framework](https://github.com/EvoAgentX/EvoAgentX) | Open-source framework | BRONZE |
| [Karpathy AutoResearch](https://github.com/karpathy/autoresearch) | Open-source experiment | SILVER |
| [Karpathy Loop — Fortune](https://fortune.com/2026/03/17/andrej-karpathy-loop-autonomous-ai-agents-future/) | Journalistiek | SILVER |
| [AutoResearch Builder's Playbook](https://sidsaladi.substack.com/p/autoresearch-101-builders-playbook) | Praktijkgids | BRONZE |
| [Metacognitive Learning (ICML 2026)](https://openreview.net/forum?id=4KhDd0Ozqe) | Academisch position paper | SPECULATIVE |
| [OpenAI: Self-Evolving Agents Cookbook](https://cookbook.openai.com/examples/partners/self_evolving_agents/autonomous_agent_retraining) | Praktijkgids | SILVER |
| [Self-Healing n8n + Claude Code](https://n8n.io/workflows/10779-monitor-and-debug-n8n-workflows-with-claude-ai-assistant-and-mcp-server/) | n8n template | SILVER |
| [Deploy AI to Monitor n8n](https://towardsdatascience.com/deploy-your-ai-assistant-to-monitor-and-debug-n8n-workflows-using-claude-and-mcp/) | Towards Data Science | SILVER |
| [7 Tips Self-Improving Agents](https://datagrid.com/blog/7-tips-build-self-improving-ai-agents-feedback-loops) | Praktijkgids | BRONZE |

## Evidence Doel

- **Grade:** SILVER voor loops 1 en 4 (na 1 sprint validatie), GOLD na 3 sprints
- **Vereist:** Implementatie + meting van sprint velocity, test pass rate, en time-to-fix over meerdere sprints

## Prioriteit

- **Fase:** 2-5 (gespreid over roadmap)
- **Kritiek pad:** Loop 1 (Sprint Retrospective) is voorwaarde voor alle andere loops
- **Motivatie:** Zonder feedback loops blijft DevHub een statisch systeem dat niet leert van zijn eigen output

## Open Vragen voor Claude Code

1. Hoe integreren we de retrospective loop met de bestaande DevOrchestrator scratchpad?
2. Welk datamodel gebruiken we voor experiment-resultaten in Loop 5?
3. Hoe voorkomen we dat self-healing workflows (Loop 4) onbedoeld RED-zone acties uitvoeren?
4. Wat is het minimale datavolume nodig voordat prompt evolution (Loop 2) betrouwbaar wordt?
5. Hoe meten we "agent-performance" concreet? Welke metrics zijn het meest informatief?
