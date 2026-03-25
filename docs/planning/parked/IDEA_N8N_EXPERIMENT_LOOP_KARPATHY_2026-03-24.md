# IDEA: n8n Experiment Loop (Karpathy-stijl)

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 5 (Uitbreiding) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow die een Karpathy-geïnspireerde experiment-loop implementeert: automatisch hypotheses genereren over code-/prompt-/config-verbeteringen, deze in een geïsoleerde git branch testen, resultaten vergelijken met een baseline, en bij verbetering automatisch een PR aanmaken. De kern is het "generate → isolate → test → compare → commit" patroon dat Andrej Karpathy beschrijft voor AI-gestuurde software-evolutie.

Dit is Feedback Loop 5 uit het RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM: het evolutieniveau. Waar Loop 2 (prompt evolution) individuele prompts optimaliseert, experimenteert Loop 5 met het systeem als geheel — code, configuratie, architectuur.

**Context**: Niels werkt solo, avonduren en weekenden. Deze loop draait volledig autonoom op momenten dat Niels niet werkt (bijvoorbeeld doordeweeks overdag). Niels reviewt de PR's wanneer hij aan zijn bureau zit.

**Fase-label**: dit is expliciet Fase 5 (Uitbreiding). Het vereist dat het volledige feedback-systeem (Loops 1-4) stabiel is en dat er voldoende test-coverage is om experimenten betrouwbaar te evalueren. Dit is het meest ambitieuze voorstel van alle 9 workflows.

## Motivatie

Traditionele software-ontwikkeling is sequentieel: een mens bedenkt een verbetering, implementeert die, test, en committeert. De experiment-loop keert dit om: het systeem genereert zelf verbeteringsideeën, test ze autonoom, en presenteert alleen succesvolle experimenten aan de mens. Dit vermenigvuldigt de ontwikkelsnelheid van een solo developer — het systeem experimenteert 24/7, Niels reviewt de winnaars.

Karpathy's kernidee: "The best way to improve AI systems is to let them improve themselves through automated experimentation." Dit past perfect bij DevHub's missie als "Second Development Brain."

Dit sluit aan bij:
- **Art. 1 (Menselijke regie)**: experimenten zijn voorstellen — Niels beslist via PR-review
- **Art. 2 (Verificatieplicht)**: elk experiment wordt geverifieerd via de bestaande test suite
- **Art. 3 (Codebase-integriteit)**: experimenten draaien in geïsoleerde branches
- **Feedback Loop 5** (zelfverbeterend systeem): Experiment Loop — evolutieniveau

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | devhub/ (Python), agents/, skills/, config/, test-coverage |
| **Grootte** | Groot — meest complexe workflow, vereist robuuste test suite + isolatie |
| **Risico** | RED — genereert code-wijzigingen autonoom. Veilig door branch-isolatie + PR-gate, maar vereist expliciete Niels-goedkeuring (Art. 1, Art. 7) |

## n8n Workflow Specificatie

### Architectuur

```
Trigger: scheduleTrigger (woensdag 10:00, wekelijks — doordeweeks, Niels werkt niet)
    │
    ▼
code: Selecteer experiment-domein
    │ → round-robin: [code-optimalisatie, config-tuning, test-coverage, refactoring]
    │
    ▼
langchain.agent: Genereer hypothese
    │ → input: codebase-context + health-data + retro-learnings + open issues
    │ → output: hypothese + verwacht resultaat + implementatie-plan
    │
    ▼
executeCommand: git worktree add experiment-{id} main
    │ → isoleer experiment in aparte worktree
    │
    ▼
langchain.agent: Implementeer experiment
    │ → input: hypothese + implementatie-plan + codebase
    │ → output: gewijzigde bestanden in experiment worktree
    │ → constraint: maximaal 50 regels gewijzigd (kleine, veilige experimenten)
    │
    ▼
executeCommand: Draai test suite in experiment worktree
    │ → pytest + ruff + pip-audit
    │
    ├─→ [TESTS FALEN] → cleanup worktree → log mislukt experiment
    │
    └─→ [TESTS SLAGEN]
          │
          ▼
    code: Vergelijk met baseline
    │ → test-runtime verschil
    │ → test-coverage verschil
    │ → lint-score verschil
    │ → code-complexiteit verschil (radon/pylint)
    │
    ├─→ [GEEN VERBETERING] → cleanup worktree → log neutraal experiment
    │
    └─→ [VERBETERING]
          │
          ▼
    executeCommand: git commit + git push experiment branch
          │
          ▼
    github: Create PR
    │ → title: "🧪 Experiment: {hypothese-samenvatting}"
    │ → body: hypothese + metrics vergelijking + AI-motivatie
    │ → labels: [experiment, automated, needs-review]
    │ → reviewers: nielspostma
          │
          ▼
    readWriteFile: Log experiment in experiments_history.json
          │
          ▼
    emailSend: "Experiment #{id} succesvol — PR klaar voor review"
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.scheduleTrigger` (v1.3) | Trigger | Wekelijks wo 10:00 (doordeweeks, Niels werkt overdag niet aan DevHub) |
| **2. Domein** | `n8n-nodes-base.code` | Transform | JS: selecteer experiment-type (round-robin) |
| **3. Hypothese** | `@n8n/n8n-nodes-langchain.agent` | Transform | Genereer hypothese + implementatie-plan |
| **4. Isolatie** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git worktree add /tmp/experiment-{id} main"` |
| **5. Implementatie** | `@n8n/n8n-nodes-langchain.agent` | Transform | Implementeer experiment (max 50 regels) met executeCommandTool |
| **6a. Tests** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd /tmp/experiment-{id} && python -m pytest -q 2>&1"` |
| **6b. Lint** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd /tmp/experiment-{id} && ruff check . 2>&1"` |
| **7. Vergelijking** | `n8n-nodes-base.code` | Transform | JS: vergelijk experiment metrics vs. baseline |
| **8. Commit** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd /tmp/experiment-{id} && git add -A && git commit && git push"` |
| **9. PR** | `n8n-nodes-base.github` (v1.1) | Input | `resource: review, operation: create` (PAT auth) |
| **10. Log** | `n8n-nodes-base.readWriteFile` | Output | Append naar `knowledge/experiments/experiments_history.json` |
| **11. Cleanup** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git worktree remove /tmp/experiment-{id}"` |
| **12. Email** | `n8n-nodes-base.emailSend` | Output | Samenvatting + PR link |

### Experiment-domeinen

```javascript
const DOMAINS = [
  {
    name: 'code-optimalisatie',
    description: 'Verbeter performance of leesbaarheid van Python code',
    scope: ['devhub/**/*.py'],
    maxChangedLines: 30,
    metrics: ['test_runtime', 'pylint_score']
  },
  {
    name: 'config-tuning',
    description: 'Optimaliseer configuratie-bestanden',
    scope: ['config/*.yml', 'config/*.json'],
    maxChangedLines: 20,
    metrics: ['test_pass_rate']
  },
  {
    name: 'test-coverage',
    description: 'Voeg ontbrekende tests toe of verbeter bestaande',
    scope: ['tests/**/*.py'],
    maxChangedLines: 50,
    metrics: ['coverage_percentage', 'test_count']
  },
  {
    name: 'refactoring',
    description: 'Reduceer code-complexiteit of duplicatie',
    scope: ['devhub/**/*.py'],
    maxChangedLines: 40,
    metrics: ['cyclomatic_complexity', 'pylint_score']
  }
];
```

### Safety Guards

```javascript
// Veiligheidsmaatregelen — NIET onderhandelbaar
const SAFETY = {
  maxChangedLines: 50,           // Meer → afbreken
  maxChangedFiles: 5,            // Meer → afbreken
  forbiddenPaths: [              // NOOIT wijzigen
    'governance/',
    'docs/compliance/DEV_CONSTITUTION.md',
    '.claude/CLAUDE.md',
    '.secrets.baseline',
    'config/nodes.yml'
  ],
  requireAllTestsPass: true,     // 1 failure → afbreken
  requireNoNewLintErrors: true,  // Nieuwe lint errors → afbreken
  requireNoSecrets: true,        // detect-secrets scan → afbreken bij hit
  branchPrefix: 'experiment/',   // Herkenbaar als experiment
  prLabelRequired: 'needs-review' // Niels moet altijd reviewen
};
```

### Experiment PR Template

```markdown
## 🧪 Experiment: {hypothese_samenvatting}

**Experiment ID:** {id}
**Domein:** {code-optimalisatie / config-tuning / test-coverage / refactoring}
**Gegenereerd door:** n8n Experiment Loop (automated)

### Hypothese

{Wat werd verwacht te verbeteren en waarom}

### Implementatie

{Samenvatting van de wijzigingen}

**Gewijzigde bestanden:** {X} bestanden, {Y} regels
**Safety guards:** ✅ alle checks geslaagd

### Resultaten vs. Baseline

| Metric | Baseline | Experiment | Verschil |
|--------|----------|------------|----------|
| Test pass rate | {X}% | {Y}% | {+Z}% |
| Test runtime | {X}s | {Y}s | {-Z}s |
| Lint score | {X} | {Y} | {+Z} |
| Coverage | {X}% | {Y}% | {+Z}% |

### AI-motivatie

{Waarom dit experiment waardevol is + mogelijke risico's}

---

*⚠️ Dit is een automatisch gegenereerd experiment. Review alle wijzigingen vóór merge (Art. 1: menselijke regie).*
*Impact-zone: RED — code-wijziging vereist expliciete goedkeuring (Art. 7)*

Labels: `experiment`, `automated`, `needs-review`
```

### Experiments History (JSON)

```json
{
  "experiments": [
    {
      "id": "exp-001",
      "date": "2026-05-14",
      "domain": "code-optimalisatie",
      "hypothesis": "Vervang list comprehension door generator in registry.py voor memory-efficiëntie",
      "result": "SUCCESS",
      "improvement": { "test_runtime": "-8%", "memory": "-12%" },
      "pr": "https://github.com/ALS-DAN/alsdan-devhub/pull/42",
      "merged": true
    }
  ],
  "stats": {
    "total": 1,
    "successful": 1,
    "failed": 0,
    "neutral": 0,
    "mergedRate": "100%"
  }
}
```

## Relatie bestaand

- **Alle Feedback Loops (1-4)**: Loop 5 bouwt voort op data van alle vorige loops
- **Sprint Retrospective (IDEA 7)**: retro-learnings voeden hypothese-generatie
- **Prompt Evolution (IDEA 8)**: complementair — prompts vs. code/config
- **PR Quality Gate (IDEA 4)**: experiment-PR's doorlopen dezelfde quality gate
- **Self-Healing (IDEA 6)**: vangt op als de experiment-loop zelf faalt
- **Test suite (218+ tests)**: de bestaande tests zijn het vangnet voor experimenten

## BORIS-impact

**Nee** — experimenteert alleen op DevHub's eigen codebase. BORIS is expliciet uitgesloten via `forbiddenPaths` en `scope` constraints. Pas bij Fase 4+ kan dit worden uitgebreid naar BorisAdapter-scope.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Trigger | Wekelijks wo 10:00 (doordeweeks overdag, Niels werkt niet) |
| Isolatie | git worktree in /tmp/ (niet in de werkende repo) |
| Wijzigingen | Via PR — altijd `needs-review` label, nooit direct merge |
| Safety | Max 50 regels, max 5 bestanden, forbidden paths, alle tests moeten slagen |
| AI-model | Sonnet voor hypothese + implementatie (complex redeneerwerk) |
| Impact-zone | RED — expliciete Niels-goedkeuring vereist (Art. 1, Art. 7) |

| Email SMTP | Gmail met App Password |
| Milestones | N.v.t. (niet sprint-gebonden) |
| Branch protection | Experiment-PR's doorlopen dezelfde gate als handmatige PR's |
| Commit conventie | `experiment(scope): [RED] {hypothese}` — altijd RED impact-tag |

## Open punten (resterend — Claude Code scope)

1. **Docker + git worktree**: Claude Code configureert git in de n8n Docker container + volume mount met schrijfrechten.
2. **API-kosten**: ~$0.10-0.50 per wekelijkse run (Sonnet). Claude Code implementeert kosten-tracker.
3. **pytest-cov + radon**: Claude Code checkt en installeert als dependencies. radon optioneel als Fase 5+ toevoeging.
4. **Rollback**: `git revert` + experiment history als audit trail. Claude Code implementeert dit.
5. **Afhankelijkheidsketen**: Fase 5 — NIET starten vóór Loops 1-4 stabiel + test-coverage >80%.
