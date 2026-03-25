# IDEA: n8n Governance Check on Merge

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow die triggert bij elke push naar `main` (merge van PR of directe push). De workflow valideert of de gemergte wijzigingen voldoen aan de DEV_CONSTITUTION — specifiek Art. 2 (verificatieplicht), Art. 5 (kennisintegriteit), Art. 7 (impact-zonering) en Art. 8 (dataminimalisatie). Bij schendingen wordt een GitHub Issue aangemaakt en Niels gemaild.

Dit is de "bewaker na de poort" — waar de PR Quality Gate (IDEA 4) de bewaker vóór merge is, vangt deze workflow alles op dat tóch doorkomt: directe pushes naar main, merges zonder quality gate, of regels die de quality gate niet checkt (zoals secrets in commits of missende EVIDENCE-graderingen).

**Context**: Niels werkt solo, vaak laat op de avond. Juist dan is de kans groter dat er iets direct naar main wordt gepusht zonder PR. Deze workflow vangt dat op zonder dat Niels het zelf hoeft te onthouden.

## Motivatie

De DEV_CONSTITUTION is het fundament van DevHub's governance, maar naleving is nu volledig afhankelijk van menselijke discipline en handmatige checks via de `devhub-governance-check` skill. Zonder automatische bewaking kan een haastige commit op een late avond ongemerkt een schending introduceren.

Dit sluit aan bij:
- **Art. 2 (Verificatieplicht)**: automatische verificatie van elke merge
- **Art. 4 (Transparantie)**: alle wijzigingen traceerbaar via commits + besluitvorming
- **Art. 7 (Impact-zonering)**: achteraf-validatie als vangnet
- **Art. 8 (Dataminimalisatie)**: actieve detectie van secrets/credentials/PII
- **devhub-governance-check skill (Fase 2.3)**: deze workflow automatiseert de trigger

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | governance, DEV_CONSTITUTION compliance, codebase-integriteit |
| **Grootte** | Middel — nieuwe n8n-workflow, bouwt op bestaande governance-structuur |
| **Risico** | GREEN (read-only checks, schrijft alleen issues/comments) |

## n8n Workflow Specificatie

### Architectuur

```
githubTrigger (event: push, branch: main)
    │     owner: ALS-DAN, repo: alsdan-devhub (PAT auth)
    │
    ├─→ github: Get commit details (files changed, commit message, author)
    │
    ├─→ executeCommand: detect-secrets scan (Art. 8 — dataminimalisatie)
    │     cd $DEVHUB_REPO_PATH && detect-secrets scan --baseline .secrets.baseline
    │
    ├─→ executeCommand: check gewijzigde .md bestanden op EVIDENCE frontmatter (Art. 5)
    │
    ├─→ code: Analyseer commit message op impact-zone labels (Art. 7)
    │     [GREEN], [YELLOW], [RED] → juist gelabeld?
    │
    ├─→ code: Check of gewijzigde bestanden in RED-zone paden zitten
    │     (governance/, DEV_CONSTITUTION.md, .claude/, config/)
    │
    ▼
    code: Aggregeer alle checks → compliance rapport
    │
    ├─→ [COMPLIANT] Alle checks OK
    │     └─→ (geen actie — stil succes)
    │
    └─→ [SCHENDING] Een of meer checks gefaald
          │
          ├─→ github: Create Issue (label: governance-violation, automated)
          ├─→ github: Add commit comment met details
          └─→ emailSend: notificatie naar Niels
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.githubTrigger` (v1) | Trigger | `owner: ALS-DAN, repository: alsdan-devhub, events: [push]` (PAT auth) |
| **2. Commit info** | `n8n-nodes-base.github` (v1.1) | Input | `resource: repository, operation: getCommit` — files, message, author |
| **3a. Secrets scan** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && detect-secrets scan --list-all-secrets 2>&1"` |
| **3b. Frontmatter** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && for f in {changed_md_files}; do head -10 $f; done"` |
| **3c. Impact-zone** | `n8n-nodes-base.code` | Transform | JS: parse commit message voor [GREEN]/[YELLOW]/[RED] labels |
| **3d. RED-zone paden** | `n8n-nodes-base.code` | Transform | JS: check of gewijzigde bestanden in beschermde paden zitten |
| **4. Aggregatie** | `n8n-nodes-base.code` | Transform | JS: combineer alle checks tot compliance-rapport |
| **5. Conditie** | `n8n-nodes-base.if` | Transform | Check: `violations.length > 0` |
| **6a. Issue** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: create, labels: [governance-violation, automated]` (PAT auth) |
| **6b. Commit comment** | `n8n-nodes-base.github` (v1.1) | Input | `resource: repository` — commit comment via API |
| **7. Email** | `n8n-nodes-base.emailSend` | Output | "Governance schending gedetecteerd" + samenvatting |

### Governance Checks (Code node)

```javascript
const violations = [];

// Art. 8: Dataminimalisatie — secrets detectie
const secretsScan = $('Secrets Scan').first().json;
if (secretsScan.stdout && !secretsScan.stdout.includes('No secrets found')) {
  violations.push({
    article: 'Art. 8',
    severity: 'RED',
    description: 'Mogelijke secrets/credentials gedetecteerd in commit',
    detail: secretsScan.stdout
  });
}

// Art. 5: Kennisintegriteit — frontmatter check
const changedMdFiles = commit.files.filter(f => f.filename.endsWith('.md'));
const knowledgeFiles = changedMdFiles.filter(f =>
  f.filename.startsWith('knowledge/') || f.filename.startsWith('docs/')
);
for (const file of knowledgeFiles) {
  const frontmatter = parseFrontmatter(file.content);
  if (!frontmatter.evidence_grade) {
    violations.push({
      article: 'Art. 5',
      severity: 'YELLOW',
      description: `Kennisbestand zonder EVIDENCE-grading: ${file.filename}`,
      detail: 'Voeg evidence_grade toe aan frontmatter'
    });
  }
}

// Art. 7: Impact-zonering — RED-zone bestanden zonder expliciete goedkeuring
const RED_ZONE_PATHS = [
  'governance/', 'docs/compliance/DEV_CONSTITUTION.md',
  '.claude/', 'config/', 'agents/'
];
const redZoneChanges = commit.files.filter(f =>
  RED_ZONE_PATHS.some(path => f.filename.startsWith(path))
);
if (redZoneChanges.length > 0) {
  const commitMsg = commit.message.toLowerCase();
  if (!commitMsg.includes('[red]') && !commitMsg.includes('approved by niels')) {
    violations.push({
      article: 'Art. 7',
      severity: 'RED',
      description: `RED-zone bestanden gewijzigd zonder expliciete goedkeuring`,
      detail: redZoneChanges.map(f => f.filename).join(', ')
    });
  }
}

// Art. 4: Transparantie — commit message kwaliteit
if (commit.message.length < 10 || commit.message === 'update') {
  violations.push({
    article: 'Art. 4',
    severity: 'YELLOW',
    description: 'Commit message niet beschrijvend genoeg',
    detail: `"${commit.message}" — voeg context toe over wat en waarom`
  });
}

return [{ json: { violations, compliant: violations.length === 0 } }];
```

### Governance Issue Template

```markdown
## ⚖️ Governance Check — Schending gedetecteerd

**Commit:** {sha} ({korte message})
**Branch:** main
**Gegenereerd door:** n8n Governance Check (automated)

### Schendingen

| # | Artikel | Severity | Beschrijving |
|---|---------|----------|-------------|
{voor elke violation: nummer, artikel, severity, beschrijving}

### Details

{per schending: volledige detail + aanbevolen actie}

### Aanbevolen acties

- [ ] {per schending: concrete fix}

---
*DEV_CONSTITUTION compliance — Art. 2 (Verificatieplicht)*
*Solo-tip: overweeg branch protection op main om directe pushes te voorkomen.*
```

## Relatie bestaand

- **devhub-governance-check skill (Fase 2.3)**: deze workflow automatiseert wat de skill handmatig doet
- **PR Quality Gate (IDEA 4)**: complementair — gate vóór merge, governance check ná merge
- **DEV_CONSTITUTION.md**: directe implementatie van Art. 2, 4, 5, 7, 8
- **detect-secrets**: vereist als dependency (pip install detect-secrets)

## BORIS-impact

**Nee** — draait puur op DevHub. BORIS heeft eigen governance (AI_CONSTITUTION). Bij Fase 4 kan een equivalent worden opgezet voor buurts-ecosysteem.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Notificatie | GitHub Issue + commit comment + email bij elke schending |
| Stil succes | Geen actie bij compliance (geen ruis) |

| Email SMTP | Gmail met App Password |
| Commit conventie | Conventional Commits + impact-tag — governance check parset `type(scope): [IMPACT]` |
| Branch protection | Aan met bypass — deze workflow is het vangnet voor bypassed pushes |

## Open punten (resterend — Claude Code scope)

1. **detect-secrets installatie**: Claude Code checkt of `detect-secrets` in de DevHub venv zit, voegt toe indien nodig.
2. **Baseline-bestand**: `.secrets.baseline` moet eenmalig worden aangemaakt en gecommit door Claude Code.
3. **RED-zone paden verfijnen**: Claude Code stelt definitieve lijst vast op basis van de repo-structuur.
