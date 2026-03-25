# IDEA: n8n Prompt Evolution Loop

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 3 (Knowledge + Memory) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow die systematisch de prompts van DevHub's agents en skills optimaliseert via een A/B-test cyclus. De workflow selecteert een agent/skill, genereert een prompt-variant (via AI), draait beide varianten tegen dezelfde test-cases, vergelijkt de output op kwaliteit-metrics, en slaat de winnaar op. Over tijd evolueert elke prompt naar een optimaal niveau — gedreven door data, niet door intuïtie.

Dit is Feedback Loop 2 uit het RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM: het optimalisatieniveau. Waar Loop 1 (retrospective) reflecteert op sprints, optimaliseert Loop 2 de AI-agents zelf.

**Context**: Niels werkt solo en kan niet eindeloos prompts handmatig tunen. Deze loop automatiseert het iteratieve "probeer, meet, verbeter"-proces dat normaal uren kost.

**Fase-label**: dit is expliciet Fase 3, niet Fase 2. Het vereist dat agents en skills stabiel zijn (Fase 1-2) voordat je ze gaat optimaliseren. Premature optimalisatie van prompts is waste als de agent-architectuur nog verandert.

## Motivatie

Prompts degraderen over tijd: model-updates veranderen gedrag, context groeit, en wat ooit een goede prompt was kan suboptimaal worden. Bovendien zijn prompts nu handmatig geschreven — er is geen empirische validatie dat ze optimaal zijn. Een systematische evolutie-loop lost beide problemen op.

Dit sluit aan bij:
- **Art. 5 (Kennisintegriteit)**: prompt-kwaliteit wordt meetbaar en gegradeerd
- **Feedback Loop 2** (zelfverbeterend systeem): Prompt Evolution — optimalisatieniveau
- **EvoAgentX-onderzoek** (uit RESEARCH_VOORSTEL): geautomatiseerde agent-optimalisatie

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | agents/, skills/, prompt-kwaliteit, agent-performance |
| **Grootte** | Groot — nieuwe n8n-workflow + test-framework + metrics-opslag |
| **Risico** | YELLOW — wijzigt agent-prompts (niet-destructief als variant-gebaseerd, maar review vereist) |

## n8n Workflow Specificatie

### Architectuur

```
Trigger: scheduleTrigger (zondag 14:00, tweewekelijks)
    │     OF: webhook /prompt-evolve (handmatig)
    │
    ▼
code: Selecteer agent/skill voor optimalisatie
    │ → round-robin of prioriteit op basis van performance-scores
    │
    ▼
readWriteFile: Lees huidige prompt (baseline)
    │ → agents/{agent}.md of .claude/skills/{skill}/SKILL.md
    │
    ▼
langchain.agent: Genereer prompt-variant
    │ → input: baseline prompt + performance history + verbetersuggesties
    │ → output: geoptimaliseerde variant met uitleg van wijzigingen
    │
    ▼
splitInBatches: Voor elke test-case
    │
    ├─→ [A] executeCommand: Draai baseline prompt tegen test-case
    └─→ [B] executeCommand: Draai variant prompt tegen test-case
          │
          ▼
    langchain.agent: Beoordeel output A vs B (blind evaluatie)
    │ → criteria: correctheid, volledigheid, stijl, adherence to constraints
    │ → output: score A (0-10), score B (0-10), motivatie
    │
    ▼
code: Aggregeer scores over alle test-cases
    │
    ├─→ [B wint significant]
    │     └─→ github: Commit variant als nieuwe baseline (PR, niet direct)
    │     └─→ readWriteFile: Update performance history
    │
    ├─→ [A wint of gelijk]
    │     └─→ readWriteFile: Log resultaat (geen wijziging)
    │
    └─→ emailSend: Rapport naar Niels
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.scheduleTrigger` (v1.3) | Trigger | Tweewekelijks, zo 14:00 |
| **2. Selectie** | `n8n-nodes-base.code` | Transform | JS: round-robin agent-selectie uit config |
| **3. Baseline** | `n8n-nodes-base.readWriteFile` | Input | Lees huidige agent/skill prompt |
| **4. Variant** | `@n8n/n8n-nodes-langchain.agent` | Transform | Genereer geoptimaliseerde prompt-variant |
| **5. Test-cases** | `n8n-nodes-base.readWriteFile` | Input | Lees test-cases uit `config/prompt_tests/{agent}.json` |
| **6. Batch** | `n8n-nodes-base.splitInBatches` | Transform | Itereer over test-cases |
| **7a. Run A** | `n8n-nodes-base.httpRequest` | Transform | Anthropic API: baseline prompt + test input |
| **7b. Run B** | `n8n-nodes-base.httpRequest` | Transform | Anthropic API: variant prompt + test input |
| **8. Evaluatie** | `@n8n/n8n-nodes-langchain.agent` | Transform | Blind A/B beoordeling (beoordelaar weet niet welke A/B is) |
| **9. Aggregatie** | `n8n-nodes-base.code` | Transform | JS: gemiddelde scores, significantie-check |
| **10. Compare** | `n8n-nodes-base.compareDatasets` | Transform | Vergelijk A vs B scores |
| **11a. PR** | `n8n-nodes-base.github` (v1.1) | Input | Bij B-winst: create PR met variant als nieuwe prompt |
| **11b. Log** | `n8n-nodes-base.readWriteFile` | Output | Performance history updaten |
| **12. Email** | `n8n-nodes-base.emailSend` | Output | Rapport met scores + beslissing |

### Selectie-logica (Code node)

```javascript
// Config: welke agents/skills worden geoptimaliseerd
const TARGETS = [
  { type: 'agent', name: 'dev-lead', path: 'agents/dev-lead.md', priority: 1 },
  { type: 'agent', name: 'coder', path: 'agents/coder.md', priority: 2 },
  { type: 'agent', name: 'reviewer', path: 'agents/reviewer.md', priority: 3 },
  { type: 'skill', name: 'devhub-review', path: '.claude/skills/devhub-review/SKILL.md', priority: 4 },
  { type: 'skill', name: 'devhub-health', path: '.claude/skills/devhub-health/SKILL.md', priority: 5 },
];

// Lees performance history
const history = JSON.parse(performanceFile);
const lastOptimized = history.lastOptimized || {};

// Round-robin: selecteer de agent die het langst niet is geoptimaliseerd
const target = TARGETS
  .sort((a, b) => {
    const dateA = lastOptimized[a.name] || '2000-01-01';
    const dateB = lastOptimized[b.name] || '2000-01-01';
    return new Date(dateA) - new Date(dateB);
  })[0];

return [{ json: target }];
```

### Evaluatie-criteria (AI Judge)

```javascript
const judgePrompt = `
Je bent een onpartijdige beoordelaar van AI-agent outputs.
Je krijgt twee outputs (A en B) voor dezelfde taak. Je weet NIET welke de baseline is.

Beoordeel elk op een schaal van 0-10 op:
1. Correctheid: volgt de output de instructies?
2. Volledigheid: zijn alle gevraagde onderdelen aanwezig?
3. Stijl: is de toon en formatting passend?
4. Constraints: worden de regels uit CLAUDE.md/DEV_CONSTITUTION gerespecteerd?

Output als JSON:
{
  "scoreA": { "correctheid": X, "volledigheid": X, "stijl": X, "constraints": X, "totaal": X },
  "scoreB": { "correctheid": X, "volledigheid": X, "stijl": X, "constraints": X, "totaal": X },
  "winnaar": "A" | "B" | "gelijk",
  "motivatie": "..."
}
`;
```

### Significantie-check

```javascript
// B moet minimaal 10% beter scoren om te "winnen"
// Dit voorkomt ruis-gedreven wijzigingen
const SIGNIFICANCE_THRESHOLD = 0.10;

const avgA = testResults.reduce((sum, r) => sum + r.scoreA.totaal, 0) / testResults.length;
const avgB = testResults.reduce((sum, r) => sum + r.scoreB.totaal, 0) / testResults.length;
const improvement = (avgB - avgA) / avgA;

const decision = improvement > SIGNIFICANCE_THRESHOLD ? 'ADOPT_VARIANT' :
                 improvement < -SIGNIFICANCE_THRESHOLD ? 'KEEP_BASELINE' : 'NO_CHANGE';
```

## Relatie bestaand

- **Alle agents (dev-lead, coder, reviewer, researcher, planner)**: optimalisatie-targets
- **Alle skills (sprint, health, review, etc.)**: optimalisatie-targets
- **Sprint Retrospective (IDEA 7)**: retro-learnings kunnen prompt-verbeteringen informeren
- **EvoAgentX research**: wetenschappelijke basis voor de aanpak
- **Self-Healing (IDEA 6)**: als prompt-evolutie de Anthropic API aanroept, kan self-healing API-fouten opvangen

## BORIS-impact

**Nee** — optimaliseert alleen DevHub agents/skills. BORIS' agents vallen onder BORIS' governance.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Trigger | Tweewekelijks zo 14:00 + webhook |
| Wijzigingen | Via PR (niet direct naar main) — Niels reviewt en merget (Art. 1) |
| Significantie | B moet ≥10% beter scoren dan A om te worden geadopteerd |
| AI-modellen | Variant-generator: Sonnet (creatief). Judge: Haiku (snel, objectief) |

| Email SMTP | Gmail met App Password |
| Milestones | N.v.t. (niet sprint-gebonden) |

## Open punten (resterend — Claude Code scope)

1. **Test-cases schrijven**: Claude Code maakt eerste set test-cases per agent (3-5 per agent). Daarna kan de workflow zelf test-cases genereren (Fase 5+).
2. **API-kosten**: ~15 API-calls per tweewekelijkse run. Claude Code implementeert een kosten-tracker in de performance history.
3. **Blind evaluatie**: Claude Code randomiseert A/B positie per test-case om positie-bias te voorkomen.
4. **Rollback**: git history is de natural rollback. Experiment-PR's bevatten de oude prompt in de PR description voor easy reference.
5. **Afhankelijkheid**: Fase 3 — niet starten vóór agents/skills stabiel zijn (Fase 1-2 compleet).
