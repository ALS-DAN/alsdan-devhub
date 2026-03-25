# IDEA: n8n Dagelijkse Health Check Workflow

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow (lokaal, Docker) die dagelijks (18:00 — start avondsessie) de DevHub-repository automatisch controleert op test-failures, lint-fouten, dependency-kwetsbaarheden en verouderde packages. Bij problemen wordt automatisch een GitHub Issue aangemaakt met het juiste prioriteitslabel (P1/P2), plus een email-notificatie bij RED-severity. Dit is de eerste stap naar proactieve bewaking — de bestaande `devhub-health` skill wordt nu reactief aangeroepen; deze workflow maakt hem autonoom.

**Context**: Niels werkt solo aan DevHub, voornamelijk in avonduren en weekenden. De trigger om 18:00 zorgt ervoor dat bij het starten van een avondsessie direct duidelijk is of de codebase gezond is.

## Motivatie

De `devhub-health` skill bestaat en werkt (geverifieerd: 6-dimensie check), maar draait alleen als iemand hem handmatig aanroept via Claude Code. Problemen worden pas ontdekt wanneer een developer toevallig een health check draait. Een dagelijkse geautomatiseerde check vangt regressies, CVE's en dependency-drift vroegtijdig op — voordat ze sprints blokkeren.

Dit sluit direct aan bij:
- **Art. 2 (Verificatieplicht)**: automatische verificatie van codebase-gezondheid
- **Art. 7 (Impact-zonering)**: GREEN-resultaten worden gelogd, YELLOW/RED genereren issues
- **Art. 3 (Codebase-integriteit)**: bewaking zonder destructieve operaties

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | devhub-health skill, CI/CD pipeline, development workflow |
| **Grootte** | Middel — geen code-wijzigingen in devhub/, wel nieuwe n8n-infra |
| **Risico** | GREEN (read-only checks, geen destructieve acties) |

## n8n Workflow Specificatie

### Architectuur

```
scheduleTrigger (18:00 dagelijks — vóór avondsessie)
    │
    ├─→ executeCommand: pytest (test suite)
    ├─→ executeCommand: ruff check (linting)
    ├─→ executeCommand: pip-audit (CVE scan)
    └─→ executeCommand: pip list --outdated (dependency drift)
          │    (paden via env var: $DEVHUB_REPO_PATH)
          ▼
    code: Resultaten aggregeren + severity bepalen
          │
          ├─→ [GROEN] Geen issues → log naar bestand/console
          │
          └─→ [GEEL/ROOD] Failures gevonden
                │
                ▼
          if: Bestaat er al een open issue voor dit type?
                │
                ├─→ [ja] Skip (voorkom duplicaten)
                └─→ [nee] github: Create Issue (PAT auth)
                │           ├── Labels: P1 (test/CVE) of P2 (lint/outdated)
                │           └── Body: samenvatting + details
                │
                └─→ [RED] emailSend: notificatie naar Niels
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.scheduleTrigger` (v1.3) | Trigger | `rule.interval[0].triggerAtHour: 18` |
| **2a. Tests** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && python -m pytest --tb=short -q 2>&1"` |
| **2b. Lint** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && ruff check . 2>&1"` |
| **2c. CVE** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && pip-audit --format=json 2>&1"` |
| **2d. Outdated** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && pip list --outdated --format=json 2>&1"` |
| **3. Aggregatie** | `n8n-nodes-base.code` | Transform | JS: parse outputs, bepaal severity (GREEN/YELLOW/RED) |
| **4. Conditie** | `n8n-nodes-base.if` (v2) | Transform | Check: `severity !== 'GREEN'` |
| **5. Duplicaat-check** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: getAll, filters: state=open, labels=health-check` (PAT auth) |
| **6. Issue aanmaken** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: create, owner: ALS-DAN, repository: alsdan-devhub` (PAT auth) |
| **7. Email (RED)** | `n8n-nodes-base.emailSend` | Output | Alleen bij RED-severity: samenvatting + link naar issue |

### Environment Variables (n8n Docker)

| Variable | Waarde | Doel |
|----------|--------|------|
| `DEVHUB_REPO_PATH` | `/Users/nielspostma/alsdan-devhub` | Repo-pad voor executeCommand |
| `GITHUB_PAT` | `ghp_...` (via n8n credentials) | GitHub API authenticatie |

### Issue Lifecycle

Issues met label `health-check` + `automated` volgen de stale-issue standaard:
- **14 dagen** zonder activiteit → label `stale` toegevoegd (via GitHub Actions of n8n sub-workflow)
- **28 dagen** zonder activiteit → auto-close met comment "Gesloten wegens inactiviteit. Volgende health-check maakt nieuw issue aan als probleem nog bestaat."
- Nieuwe run bij zelfde probleem → maakt nieuw issue aan (duplicaat-check kijkt alleen naar open issues)

### Severity-mapping (Code node)

```javascript
// Pseudo-logica voor de Code node
const severity = {
  testsFailed: results.tests.exitCode !== 0,        // → RED (P1)
  cveFound: results.audit.vulnerabilities.length > 0, // → RED (P1)
  lintErrors: results.lint.exitCode !== 0,            // → YELLOW (P2)
  outdated: results.outdated.length > 5               // → YELLOW (P2)
};

const level = (severity.testsFailed || severity.cveFound) ? 'RED' :
              (severity.lintErrors || severity.outdated) ? 'YELLOW' : 'GREEN';

const labels = [];
if (level === 'RED') labels.push('P1', 'health-check', 'automated');
if (level === 'YELLOW') labels.push('P2', 'health-check', 'automated');
```

### Issue Template

```markdown
## 🏥 DevHub Health Check — {datum}

**Severity:** {RED|YELLOW}
**Gegenereerd door:** n8n Health Check Workflow (automated)

### Resultaten

| Check | Status | Details |
|-------|--------|---------|
| Tests | {✅/❌} | {X failed, Y passed} |
| Lint | {✅/⚠️} | {X errors, Y warnings} |
| CVE Scan | {✅/🔴} | {X vulnerabilities found} |
| Dependencies | {✅/⚠️} | {X packages outdated} |

### Aanbevolen acties
- [ ] {actie per failure}

---
*Impact-zone: {GREEN/YELLOW/RED} — Art. 7 DEV_CONSTITUTION*
```

## Relatie bestaand

- **devhub-health skill**: deze workflow automatiseert wat de skill handmatig doet
- **QA Agent**: deelt test/lint-resultaten; workflow is complementair (scheduled vs. on-demand)
- **DEV_CONSTITUTION Art. 2, 3, 7**: directe implementatie van verificatie + integriteit + zonering

## BORIS-impact

**Nee** — deze workflow draait puur op de DevHub-repository. Indien later gewenst kan een tweede instantie voor het buurts-ecosysteem worden geconfigureerd via de BorisAdapter, maar dat is een apart voorstel.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Notificatie | GitHub Issues + email bij RED-severity |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Issue lifecycle | Stale na 14 dagen, auto-close na 28 dagen |
| Trigger-tijd | 18:00 (vóór avondsessie — solo developer, avonduren/weekenden) |

| Email SMTP | Gmail met App Password |
| Commit conventie | Conventional Commits + impact-tag: `type(scope): [IMPACT] beschrijving` |

## Open punten (resterend — Claude Code scope)

1. **Docker volume mount**: repo-pad moet als volume gemount worden in de n8n Docker container. Claude Code configureert dit bij implementatie.
