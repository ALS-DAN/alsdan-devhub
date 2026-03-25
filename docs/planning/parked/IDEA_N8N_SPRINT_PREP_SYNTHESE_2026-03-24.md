# IDEA: n8n Sprint-Prep Synthese Workflow

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow (lokaal, Docker) die automatisch een sprint-voorbereiding samenstelt vóór een weekendsessie. De workflow verzamelt health-status, open inbox-items, recente beslissingen (ADR's), open GitHub Issues en recente git-activiteit. Het resultaat is een gestructureerd synthese-rapport dat wordt gecommit als `SPRINT_PREP_SYNTHESE_{datum}.md` in de inbox, klaar voor de planner-agent en Niels om een sprint te scopen.

De workflow draait op twee manieren: scheduled (vrijdagavond 18:00 — zodat het rapport klaarligt voor de weekendsessie) én handmatig via webhook (voor ad-hoc planning). De "Aanbevolen Focus" sectie gebruikt een hybride aanpak: deterministische ranking op prioriteit, aangevuld met een korte AI-samenvatting via n8n's LangChain agent voor context.

**Context**: Niels werkt solo, voornamelijk avonduren en weekenden. Het rapport vrijdagavond klaarzetten betekent dat Niels zaterdagochtend direct kan beginnen met sprint-scoping zonder eerst handmatig data te verzamelen.

## Motivatie

De `devhub-sprint-prep` skill doet dit al handmatig, maar vereist dat iemand hem aanroept en de juiste context meegeeft. Vóór een sprint moet je:
- weten of de codebase gezond is (health)
- weten welke intakes/ideeën klaarliggen (inbox)
- weten of er blokkerende issues zijn (GitHub)
- weten welke architectuurbeslissingen recent zijn genomen (ADR's)

Dat is precies het soort synthese dat n8n kan automatiseren als voorbereiding op een planningsgesprek.

Dit sluit aan bij:
- **Shape Up methodiek**: appetite-bepaling vereist een helder beeld van de huidige staat
- **Art. 1 (Menselijke regie)**: Niels krijgt een compleet overzicht om te beslissen
- **planner-agent**: krijgt gestructureerde input in plaats van blanco canvas

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | devhub-sprint-prep skill, planner-agent, sprint lifecycle |
| **Grootte** | Middel — nieuwe n8n-workflow, hergebruikt bestaande data-bronnen |
| **Risico** | GREEN (read-only aggregatie, schrijft alleen naar inbox/) |

## n8n Workflow Specificatie

### Architectuur

```
Trigger: scheduleTrigger (vrijdag 18:00 — vóór weekendsessie)
    │     OF: webhook /sprint-prep (handmatig, voor ad-hoc planning)
    │
    ├─→ executeCommand: cd $DEVHUB_REPO_PATH && pytest --tb=line -q
    ├─→ executeCommand: ls $DEVHUB_REPO_PATH/docs/planning/inbox/*.md
    ├─→ github: Get Issues (open, labels: P1/P2/health-check) (PAT auth)
    ├─→ executeCommand: ls $DEVHUB_REPO_PATH/docs/architecture/decisions/
    └─→ executeCommand: cd $DEVHUB_REPO_PATH && git log --oneline -20
          │
          ▼
    code: Aggregeer alle bronnen + deterministische ranking
          │
          ▼
    langchain.agent: Korte AI-samenvatting van top-3 focus-items (optioneel)
          │
          ▼
    code: Genereer SPRINT_PREP_SYNTHESE markdown
          │
          ▼
    github: Commit naar docs/planning/inbox/ (PAT auth)
          │
          ▼
    emailSend: notificatie naar Niels dat rapport klaarligt
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1a. Schedule** | `n8n-nodes-base.scheduleTrigger` (v1.3) | Trigger | `rule.interval[0].triggerAtDay: 5` (vrijdag), `triggerAtHour: 18` |
| **1b. Manual** | `n8n-nodes-base.webhook` | Trigger | `path: /sprint-prep`, `method: POST` |
| **2a. Health** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && python -m pytest --tb=line -q 2>&1 \| tail -5"` |
| **2b. Inbox** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "ls -la $DEVHUB_REPO_PATH/docs/planning/inbox/*.md 2>/dev/null"` |
| **2c. Issues** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: getAll, state: open, labels: P1,P2` (PAT auth) |
| **2d. ADR's** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "ls $DEVHUB_REPO_PATH/docs/architecture/decisions/*.md 2>/dev/null"` |
| **2e. Git log** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && git log --oneline --since='2 weeks ago' -20"` |
| **3. Aggregatie** | `n8n-nodes-base.code` | Transform | JS: combineer alle data + deterministische ranking (P1 → Hoog → Middel) |
| **4. AI-context** | `@n8n/n8n-nodes-langchain.agent` | Transform | Optioneel: korte samenvatting top-3 items. Bij falen: graceful fallback naar puur data-driven |
| **5. Rapport** | `n8n-nodes-base.code` | Transform | JS: genereer markdown synthese-rapport |
| **6. Commit** | `n8n-nodes-base.github` (v1.1) | Input | `resource: file, operation: create` (PAT auth) |
| **7. Email** | `n8n-nodes-base.emailSend` | Output | "Sprint-Prep Synthese klaar — {datum}" + link naar rapport |

### Synthese-rapport Template

```markdown
# Sprint-Prep Synthese — {datum}

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | n8n Sprint-Prep Workflow (automated) |
| **Datum** | {datum} |
| **Health status** | {GREEN/YELLOW/RED} |

---

## 1. Codebase Health

| Check | Status | Detail |
|-------|--------|--------|
| Tests | {✅ 299 pass / ❌ X fail} | {samenvatting} |
| Open P1 Issues | {0/X} | {titels} |
| Open P2 Issues | {0/X} | {titels} |

## 2. Inbox Items ({X} items)

| Bestand | Type | Fase | Prioriteit |
|---------|------|------|-----------|
{voor elk .md bestand in inbox/: naam, type (IDEA/INTAKE/RESEARCH), fase, prioriteit}

## 3. Recente Beslissingen

| ADR | Titel | Datum |
|-----|-------|-------|
{voor elk ADR bestand: nummer, titel, datum}

## 4. Recente Activiteit (laatste 2 weken)

```
{git log --oneline output}
```

## 5. Aanbevolen Focus (hybride: data-ranking + AI-context)

**Ranking** (deterministisch):

1. **Blokkades**: {open P1 issues of health-failures die eerst opgelost moeten}
2. **Kritiek pad**: {hoogste prioriteit inbox-item op basis van fase + prioriteit-label}
3. **Quick wins**: {items die in 1-2 avondsessies af kunnen — solo developer context}

**AI-samenvatting** (optioneel, via LangChain agent):

> {Korte contextualiseering: waarom deze top-3 nu relevant is, wat de onderlinge samenhang is, en welk item het meeste momentum geeft voor de weekendsessie.}
> *Gegenereerd door n8n LangChain agent. Bij falen van deze stap is het rapport alsnog bruikbaar op basis van de deterministische ranking.*

---

*Gebruik dit rapport als input voor sprint-scoping (Art. 1: menselijke regie). Solo-context: plan maximaal 1 sprint-item per weekendsessie.*
```

### Aggregatie-logica (Code node)

```javascript
// Combineer alle parallel-outputs
const health = $('Health Check').first().json;
const inbox = $('Inbox Scan').first().json;
const issues = $('GitHub Issues').all();
const adrs = $('ADR Scan').first().json;
const gitlog = $('Git Log').first().json;

// Parse health status
const testsOk = !health.stdout.includes('FAILED');
const healthStatus = testsOk ? 'GREEN' : 'RED';

// Parse inbox items
const inboxFiles = inbox.stdout.split('\n')
  .filter(line => line.endsWith('.md'))
  .map(line => {
    const name = line.split('/').pop();
    const type = name.startsWith('SPRINT_INTAKE') ? 'INTAKE' :
                 name.startsWith('IDEA') ? 'IDEA' :
                 name.startsWith('RESEARCH') ? 'RESEARCH' : 'OVERIG';
    return { name, type };
  });

// Categorize issues
const p1Issues = issues.filter(i => i.json.labels?.some(l => l.name === 'P1'));
const p2Issues = issues.filter(i => i.json.labels?.some(l => l.name === 'P2'));

return [{
  json: { healthStatus, testsOk, inboxFiles, p1Issues, p2Issues, adrs, gitlog }
}];
```

## Relatie bestaand

- **devhub-sprint-prep skill**: deze workflow automatiseert de data-verzameling die de skill nu handmatig doet
- **planner-agent**: ontvangt het synthese-rapport als startpunt voor sprint-scoping
- **devhub-health skill**: health-check resultaten worden hergebruikt
- **Health Check Workflow** (IDEA 1): indien actief, kunnen we de laatste health-issue lezen i.p.v. opnieuw tests draaien

## BORIS-impact

**Nee** — focust op DevHub-repository. BORIS sprint-planning valt onder BORIS' eigen governance. Wel kan de synthese in de toekomst via BorisAdapter ook BORIS-status meenemen (Fase 4+).

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Trigger-tijd | Vrijdag 18:00 (vóór weekendsessie) + webhook voor ad-hoc |
| Notificatie | Email wanneer rapport klaarligt |
| Aanbevolen Focus | Hybride: deterministische ranking + optionele AI-samenvatting (graceful fallback) |

| Email SMTP | Gmail met App Password |
| Milestones | Ja — sprint-data via GitHub Milestones API |
| LangChain model | Haiku (snel, goedkoop, voldoende voor korte samenvatting) |
| Inbox-parsing | Frontmatter lezen (weinig bestanden, extra context waard) |

## Open punten (resterend — Claude Code scope)

1. **Health Check hergebruik**: als IDEA 1 al actief is, kan sprint-prep de laatste health-issue lezen i.p.v. opnieuw tests draaien. Claude Code bepaalt dit bij implementatie.
