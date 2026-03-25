# IDEA: n8n PR Quality Gate Workflow

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow die automatisch triggert bij elke nieuwe Pull Request op de DevHub-repository. De workflow draait de `devhub-review` checks (12-punts code review + 6-punts doc review), voert tests en lint uit, en post het resultaat als PR comment. Bij RED-severity (blokkerend) wordt de PR gelabeld en Niels gemaild. Dit creëert een geautomatiseerde quality gate die elke wijziging beoordeelt voordat Niels tijd besteedt aan handmatige review.

**Context**: Niels werkt solo, voornamelijk in avonduren en weekenden. Een automated quality gate is extra waardevol voor solo developers: er is geen tweede paar ogen, dus de workflow fungeert als virtuele reviewer die altijd beschikbaar is — ook als Niels om 23:00 een PR opent.

## Motivatie

De `devhub-review` skill en het QA Agent bestaan al, maar draaien alleen on-demand. Bij een solo developer zonder CI/CD pipeline is er geen automatisch vangnet. Een PR quality gate zorgt ervoor dat:
- code-problemen worden gevangen vóórdat ze naar main mergen
- de review consistent is (altijd dezelfde 12+6 checks)
- Niels direct ziet of een PR klaar is om te mergen, of eerst werk nodig heeft

Dit sluit aan bij:
- **Art. 2 (Verificatieplicht)**: automatische verificatie bij elke code-wijziging
- **Art. 3 (Codebase-integriteit)**: bewaking vóór merge, niet achteraf
- **Art. 7 (Impact-zonering)**: GREEN PR's zijn merge-klaar, YELLOW/RED vereisen actie
- **5-laags check-architectuur** (uit SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR): Laag C (Review)

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | devhub-review skill, QA Agent, PR workflow, code kwaliteit |
| **Grootte** | Middel-Groot — nieuwe n8n-workflow + integratie met bestaande review-checks |
| **Risico** | YELLOW — schrijft PR comments en labels (niet-destructief, maar zichtbaar op GitHub) |

## n8n Workflow Specificatie

### Architectuur

```
githubTrigger (event: pull_request, action: opened/synchronize)
    │     owner: ALS-DAN, repo: alsdan-devhub (PAT auth)
    │
    ├─→ github: Get PR diff (changed files)
    │
    ├─→ executeCommand: cd $DEVHUB_REPO_PATH && git fetch && git checkout PR-branch
    ├─→ executeCommand: pytest --tb=short -q (test suite op PR-branch)
    ├─→ executeCommand: ruff check . (lint op PR-branch)
    ├─→ executeCommand: pip-audit --format=json (CVE check)
    │
    ▼
    code: Analyseer resultaten + bepaal severity
    │
    ├─→ [GREEN] Alle checks OK
    │     └─→ github: Post PR comment (✅ review rapport)
    │     └─→ github: Add label "quality-gate-passed"
    │
    ├─→ [YELLOW] Warnings (lint, minor issues)
    │     └─→ github: Post PR comment (⚠️ review rapport + aanbevelingen)
    │     └─→ github: Add label "needs-attention"
    │
    └─→ [RED] Blokkerend (test failures, CVE's)
          └─→ github: Post PR comment (❌ review rapport + blokkades)
          └─→ github: Add label "blocked"
          └─→ emailSend: notificatie naar Niels
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.githubTrigger` (v1) | Trigger | `owner: ALS-DAN, repository: alsdan-devhub, events: [pull_request]` (PAT auth) |
| **2. PR info** | `n8n-nodes-base.github` (v1.1) | Input | `resource: review, operation: get` — changed files + diff |
| **3a. Checkout** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git fetch origin pull/{PR_ID}/head:pr-{PR_ID} && git checkout pr-{PR_ID}"` |
| **3b. Tests** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && python -m pytest --tb=short -q 2>&1"` |
| **3c. Lint** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && ruff check . 2>&1"` |
| **3d. CVE** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && pip-audit --format=json 2>&1"` |
| **4. Analyse** | `n8n-nodes-base.code` | Transform | JS: parse resultaten, bepaal severity, bouw review-rapport |
| **5. Severity route** | `n8n-nodes-base.switch` | Transform | Route op basis van severity: GREEN / YELLOW / RED |
| **6a. PR Comment** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: createComment` (PR = issue in GitHub API) |
| **6b. Label** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: edit, labels: [quality-gate-*]` |
| **6c. Cleanup** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git checkout main && git branch -D pr-{PR_ID}"` |
| **7. Email (RED)** | `n8n-nodes-base.emailSend` | Output | Alleen bij RED: "PR #{PR_ID} geblokkeerd" + samenvatting |

### PR Comment Template

```markdown
## 🔍 DevHub Quality Gate — PR #{number}

**Severity:** {GREEN ✅ / YELLOW ⚠️ / RED ❌}
**Branch:** `{branch}` → `main`
**Gegenereerd door:** n8n PR Quality Gate (automated)

### Resultaten

| Check | Status | Details |
|-------|--------|---------|
| Tests | {✅/❌} | {X passed, Y failed} |
| Lint | {✅/⚠️} | {X errors, Y warnings} |
| CVE Scan | {✅/🔴} | {X vulnerabilities} |
| Changed files | — | {X files, Y additions, Z deletions} |

### {Aanbevelingen / Blokkades}

{Per finding: wat, waar, waarom, suggestie}

---
*Impact-zone: {GREEN/YELLOW/RED} — Art. 7 DEV_CONSTITUTION*
*Solo-tip: bij GREEN kun je direct mergen. Bij YELLOW, review de warnings eerst.*
```

### Severity-logica (Code node)

```javascript
const testsFailed = results.tests.exitCode !== 0;
const cveFound = JSON.parse(results.audit.stdout).length > 0;
const lintErrors = results.lint.exitCode !== 0;
const lintOutput = results.lint.stdout;
const errorCount = (lintOutput.match(/error/gi) || []).length;
const warningCount = (lintOutput.match(/warning/gi) || []).length;

// Severity bepaling
const severity = testsFailed || cveFound ? 'RED' :
                 errorCount > 0 ? 'YELLOW' :
                 warningCount > 3 ? 'YELLOW' : 'GREEN';

// Labels
const labelMap = {
  GREEN: 'quality-gate-passed',
  YELLOW: 'needs-attention',
  RED: 'blocked'
};

// Verwijder oude quality-gate labels eerst
const oldLabels = ['quality-gate-passed', 'needs-attention', 'blocked'];
```

## Relatie bestaand

- **devhub-review skill**: de checks komen uit dezelfde methodiek; workflow automatiseert de trigger
- **QA Agent (12+6 checks)**: toekomstige integratie — nu draaien we tests/lint/CVE; later de volledige QA Agent pipeline
- **SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR**: implementeert Laag C (Review) van de 5-laags architectuur
- **Health Check Workflow (IDEA 1)**: complementair — health checkt dagelijks, quality gate checkt per PR

## BORIS-impact

**Nee** — draait puur op de DevHub-repository. Een equivalent voor buurts-ecosysteem kan later via een tweede workflow-instantie, maar dat is een apart voorstel.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Notificatie | PR comment altijd + email bij RED |
| Impact-zone | YELLOW (schrijft naar GitHub, maar niet-destructief) |

| Email SMTP | Gmail met App Password |
| Branch protection | Aan met bypass — quality gate als recommended (niet required) check |
| Commit conventie | Conventional Commits + impact-tag |
| Milestones | PR's gekoppeld aan sprint-milestone |
| Re-trigger | Edit bestaand comment bij `synchronize` event (voorkomt spam) |

## Open punten (resterend — Claude Code scope)

1. **Git checkout race condition**: gebruik `git worktree` i.p.v. checkout om conflicten met lokaal werk te voorkomen. Claude Code implementeert dit.
2. **QA Agent integratie**: nu basis-checks (test/lint/CVE). Volledige QA Agent (12+6 checks) als vervolgstap in Fase 2.
