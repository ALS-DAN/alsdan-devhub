# IDEA: n8n Sprint Retrospective Loop

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2-3 (Skills + Governance → Knowledge + Memory) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow die na elke sprint-close automatisch een retrospective genereert. De workflow verzamelt sprint-data (commits, PR's, issues gesloten, tijd besteed), vergelijkt die met de oorspronkelijke sprint-scope, detecteert patronen (scope creep, recurrente blokkades, onderschatting) en slaat de learnings op in `knowledge/retrospectives/`. Over meerdere sprints bouwt dit een dataset op die de planner-agent kan gebruiken voor betere schattingen.

Dit is Feedback Loop 1 uit het RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM: het reflectieniveau dat DevHub in staat stelt van zijn eigen sprints te leren.

**Context**: Niels werkt solo, avonduren en weekenden. Retrospectives worden makkelijk overgeslagen als je alleen werkt — er is geen team dat erop aandringt. Deze workflow maakt reflectie automatisch en laagdrempelig: het rapport ligt klaar, Niels hoeft alleen te lezen en eventueel annotaties toe te voegen.

## Motivatie

Zonder retrospective herhaalt een solo developer dezelfde fouten: te veel scope in een sprint, steeds dezelfde type bugs, onderschatting van complexiteit. De `devhub-sprint` skill heeft al een close-fase, maar de analyse ná close is handwerk. Door dit te automatiseren ontstaat een feedbackloop die elke sprint beter maakt dan de vorige.

Dit sluit aan bij:
- **Shape Up methodiek**: appetite vs. reality — systematisch meten of de appetite klopt
- **Art. 5 (Kennisintegriteit)**: retrospective-learnings worden BRONZE-kennis (ervaring-gebaseerd)
- **Feedback Loop 1** (zelfverbeterend systeem): Sprint Retrospective — reflectieniveau
- **planner-agent**: krijgt historische data voor betere sprint-sizing

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | sprint lifecycle, planner-agent, knowledge base, schattingsnauwkeurigheid |
| **Grootte** | Middel — nieuwe n8n-workflow + nieuw kennispad `knowledge/retrospectives/` |
| **Risico** | GREEN (read-only data-verzameling, schrijft alleen analyse-bestanden) |

## n8n Workflow Specificatie

### Architectuur

```
Trigger: webhook /sprint-retro (handmatig, na sprint-close)
    │     OF: githubTrigger (milestone closed)
    │
    ├─→ github: Get milestone details (sprint scope, titel, due date)
    ├─→ github: Get issues in milestone (planned vs. completed vs. carried over)
    ├─→ github: Get commits in sprint period
    ├─→ github: Get PRs merged in sprint period
    ├─→ executeCommand: git log --shortstat (insertions/deletions)
    │
    ▼
code: Sprint metrics berekenen
    │ → velocity (issues completed / planned)
    │ → scope creep (issues added na sprint-start)
    │ → carry-over ratio (niet-afgerond / totaal)
    │ → gemiddelde PR-grootte
    │ → commit-frequentie per dag
    │
    ▼
langchain.agent: Patroonherkenning + advies
    │ → input: huidige sprint metrics + vorige retrospectives
    │ → output: patronen, verbeterpunten, concrete aanbevelingen
    │
    ▼
code: Genereer RETROSPECTIVE markdown
    │
    ├─→ github: Commit naar knowledge/retrospectives/RETRO_{sprint}_{datum}.md
    └─→ readWriteFile: Append metrics naar knowledge/retrospectives/metrics_history.json
          │
          ▼
    emailSend: "Sprint retrospective klaar" + samenvatting
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1a. Manual** | `n8n-nodes-base.webhook` | Trigger | `path: /sprint-retro`, `method: POST`, body: `{ sprintName, startDate, endDate }` |
| **1b. Milestone** | `n8n-nodes-base.githubTrigger` (v1) | Trigger | `events: [milestone]`, action: closed |
| **2a. Milestone info** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: getAll, milestone: {id}` (PAT auth) |
| **2b. Commits** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git log --oneline --after={startDate} --before={endDate}"` |
| **2c. PR's** | `n8n-nodes-base.github` (v1.1) | Input | `resource: review, operation: getAll, state: closed, since: {startDate}` (PAT auth) |
| **2d. Stats** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git log --shortstat --after={startDate} --before={endDate}"` |
| **3. Metrics** | `n8n-nodes-base.code` | Transform | JS: bereken velocity, scope creep, carry-over, PR-grootte |
| **4. Geschiedenis** | `n8n-nodes-base.readWriteFile` | Input | Lees `knowledge/retrospectives/metrics_history.json` (vorige sprints) |
| **5. AI-analyse** | `@n8n/n8n-nodes-langchain.agent` | Transform | Patroonherkenning over meerdere sprints + concrete aanbevelingen |
| **6. Rapport** | `n8n-nodes-base.code` | Transform | JS: genereer RETROSPECTIVE markdown |
| **7a. Commit** | `n8n-nodes-base.github` (v1.1) | Input | `resource: file, operation: create` (PAT auth) |
| **7b. Metrics opslaan** | `n8n-nodes-base.readWriteFile` | Output | Append huidige sprint metrics naar `metrics_history.json` |
| **8. Email** | `n8n-nodes-base.emailSend` | Output | Samenvatting + link naar retrospective |

### Sprint Metrics (Code node)

```javascript
const planned = milestoneIssues.filter(i => i.createdBefore(sprintStart));
const added = milestoneIssues.filter(i => i.createdAfter(sprintStart));
const completed = milestoneIssues.filter(i => i.state === 'closed');
const carriedOver = milestoneIssues.filter(i => i.state === 'open');

const metrics = {
  sprintName,
  startDate,
  endDate,
  durationDays: daysBetween(startDate, endDate),

  // Velocity
  planned: planned.length,
  completed: completed.length,
  velocity: (completed.length / planned.length * 100).toFixed(1) + '%',

  // Scope creep
  addedDuringSprint: added.length,
  scopeCreepRatio: (added.length / planned.length * 100).toFixed(1) + '%',

  // Carry-over
  carriedOver: carriedOver.length,
  carryOverRatio: (carriedOver.length / milestoneIssues.length * 100).toFixed(1) + '%',

  // Code metrics
  totalCommits: commits.length,
  totalInsertions: stats.insertions,
  totalDeletions: stats.deletions,
  avgPRSize: prs.reduce((sum, pr) => sum + pr.additions + pr.deletions, 0) / prs.length,

  // Werkpatroon (solo-relevant)
  commitsByDayOfWeek: groupCommitsByDay(commits),
  peakHours: detectPeakHours(commits), // wanneer werkt Niels het meest productief?
};
```

### Retrospective Template

```markdown
# Sprint Retrospective — {sprintName}

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | n8n Sprint Retrospective Loop (automated) |
| **Sprint** | {sprintName} |
| **Periode** | {startDate} — {endDate} ({durationDays} dagen) |
| **Datum** | {nu} |

---

## Metrics

| Metric | Waarde | Trend vs. vorige sprint |
|--------|--------|------------------------|
| Velocity | {X}% ({completed}/{planned}) | {↑/↓/→} |
| Scope creep | {X}% ({added} items toegevoegd) | {↑/↓/→} |
| Carry-over | {X}% ({carriedOver} items) | {↑/↓/→} |
| Commits | {X} | {↑/↓/→} |
| Gem. PR-grootte | {X} regels | {↑/↓/→} |

## Werkpatroon

| Dag | Commits |
|-----|---------|
{per dag van de week: activiteit}

**Piek-uren**: {wanneer Niels het meest productief was}

## AI-Analyse

### Patronen gedetecteerd

{AI-output: terugkerende patronen over meerdere sprints}

### Wat ging goed

{AI-output: positieve trends}

### Verbeterpunten

{AI-output: concrete, actionable aanbevelingen}

### Aanbeveling voor volgende sprint

{AI-output: sizing-advies op basis van historische velocity}

---

*EVIDENCE-grading: BRONZE (ervaring-gebaseerd, 1 sprint). Wordt SILVER na 3+ sprints met consistent patroon.*
*Feedback Loop 1 — Art. 5 DEV_CONSTITUTION*
```

### Metrics History (JSON)

```json
{
  "sprints": [
    {
      "name": "FASE1_BOOTSTRAP",
      "date": "2026-03-20",
      "velocity": 85.7,
      "scopeCreep": 14.3,
      "carryOver": 7.1,
      "commits": 47,
      "avgPRSize": 234
    }
  ],
  "patterns": {
    "avgVelocity": 85.7,
    "velocityTrend": "stable",
    "commonBlockers": ["dependency conflicts", "test coverage gaps"]
  }
}
```

## Relatie bestaand

- **devhub-sprint skill**: close-fase triggert de retrospective
- **planner-agent**: gebruikt historische metrics voor betere sizing
- **devhub-mentor skill**: werkpatroon-data kan coaching-advies verrijken
- **Knowledge Decay Scan (IDEA 2)**: retrospectives zijn kennisbestanden die ook verouderen
- **Sprint-Prep Synthese (IDEA 3)**: kan carry-over items uit vorige retro meenemen

## BORIS-impact

**Nee** — analyseert alleen DevHub-sprints. BORIS sprint-retrospectives vallen onder BORIS' eigen governance.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Trigger | Webhook (handmatig na sprint-close) + optioneel milestone-trigger |
| Opslag | `knowledge/retrospectives/` + `metrics_history.json` |
| AI-model | Haiku voor patroonherkenning (snel, goedkoop, voldoende voor reflectie) |
| EVIDENCE-grading | BRONZE (1 sprint) → SILVER (na 3+ consistente sprints) |

| Email SMTP | Gmail met App Password |
| Milestones | Ja — sprint-retrospective haalt data uit GitHub Milestones API |

## Open punten (resterend — Claude Code scope)

1. **Metrics history pad**: Claude Code maakt `knowledge/retrospectives/metrics_history.json` aan bij eerste run.
2. **Privacy werkpatroon**: piek-uren en dag-analyse niet in publieke commits (Art. 8). Claude Code zet dit in een `.gitignore`'d lokaal bestand of in de metrics_history.json die niet gepusht wordt.
3. **Minimum data**: eerste retrospective is puur metrics, AI-patroonherkenning start pas na 2-3 sprints. Claude Code implementeert een `if (sprints.length < 3)` guard.
