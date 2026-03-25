# IDEA: n8n Self-Healing Workflow

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n meta-workflow die triggert wanneer een andere n8n-workflow faalt (via de Error Trigger node). De workflow analyseert de fout, classificeert het type (configuratie, netwerk, dependency, logica), en probeert een geautomatiseerde diagnose te stellen via een AI Agent (LangChain). Bij eenvoudige fouten (zoals een vervallen PAT of een timeout) stelt hij een reparatie voor. Bij complexere fouten wordt een GitHub Issue aangemaakt met diagnostische context.

Dit is de "bewaker van de bewakers" — zodra de andere workflows (health check, quality gate, governance check) operationeel zijn, is er een meta-laag nodig die garandeert dat die workflows zélf blijven werken.

**Context**: Niels werkt solo en kan niet constant n8n monitoren. Als de health check workflow stilvalt door een verlopen PAT, merkt niemand dat tot Niels toevallig inlogt op n8n. Deze workflow detecteert dat automatisch.

## Motivatie

n8n-workflows zijn niet inherent zelfherstellend. Ze falen stil wanneer credentials verlopen, dependencies breken, API's wijzigen, of systeem-resources uitgeput raken. Voor een solo developer die in de avonduren werkt, is een stille failure het slechtste scenario: je denkt dat alles draait, maar er draait niets.

Dit sluit aan bij:
- **Art. 2 (Verificatieplicht)**: de monitoring-workflows zelf worden gemonitord
- **Art. 3 (Codebase-integriteit)**: bewaking van het bewakingssysteem
- **Feedback Loop 4** (uit RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM): Self-Healing Workflow
- **Cynefin**: dit is een *complex* probleem (onvoorspelbare foutmodi) → SPIKE sprint-type

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | alle n8n-workflows, n8n-betrouwbaarheid, operationele zekerheid |
| **Grootte** | Middel — meta-workflow, geen code-wijzigingen in devhub/ |
| **Risico** | YELLOW — AI-diagnose kan onnauwkeurig zijn; reparatie-voorstellen moeten door Niels worden goedgekeurd (Art. 1) |

## n8n Workflow Specificatie

### Architectuur

```
errorTrigger (triggert bij fout in ELKE geregistreerde workflow)
    │
    ▼
code: Parse error context
    │ → workflow naam, node naam, error message, timestamp
    │ → error type classificatie (zie mapping)
    │
    ▼
switch: Route op error type
    │
    ├─→ [CREDENTIAL] Verlopen token / auth failure
    │     └─→ code: Genereer specifiek herstel-advies
    │     └─→ emailSend: "⚠️ {workflow} — credential verlopen, vernieuw PAT"
    │
    ├─→ [NETWORK] Timeout / connection refused
    │     └─→ wait: 5 minuten
    │     └─→ n8n API: Retry workflow (max 2x)
    │     └─→ if: Nog steeds fout?
    │           ├─→ [ja] → GitHub Issue + email
    │           └─→ [nee] → log recovery
    │
    ├─→ [DEPENDENCY] Module niet gevonden / versie-conflict
    │     └─→ executeCommand: pip check / npm ls (diagnose)
    │     └─→ github: Create Issue met dependency-details
    │     └─→ emailSend: notificatie
    │
    └─→ [LOGIC / ONBEKEND] Onverwachte fout
          │
          ▼
    langchain.agent: AI-diagnose
          │ → input: error context + workflow structuur
          │ → output: mogelijke oorzaak + reparatie-suggestie
          │
          ▼
    github: Create Issue (label: self-healing, {error-type})
          │ → body: error details + AI-diagnose + voorgestelde fix
          │
          ▼
    emailSend: notificatie naar Niels
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.errorTrigger` | Trigger | Triggert bij fout in gekoppelde workflows |
| **2. Parse** | `n8n-nodes-base.code` | Transform | JS: parse error object, classificeer type |
| **3. Route** | `n8n-nodes-base.switch` | Transform | 4 outputs: CREDENTIAL / NETWORK / DEPENDENCY / LOGIC |
| **4a. Credential advies** | `n8n-nodes-base.code` | Transform | JS: genereer specifiek herstel-advies per credential-type |
| **4b. Retry** | `n8n-nodes-base.httpRequest` | Transform | n8n API: `POST /api/v1/workflows/{id}/run` (retry) |
| **4c. Dependency check** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && pip check 2>&1"` |
| **4d. AI-diagnose** | `@n8n/n8n-nodes-langchain.agent` | Transform | LLM: analyseer error + workflow context, stel fix voor |
| **5. Wait (retry)** | `n8n-nodes-base.wait` | Transform | 5 minuten wachten voor retry |
| **6. Issue** | `n8n-nodes-base.github` (v1.1) | Input | `resource: issue, operation: create, labels: [self-healing, {type}]` (PAT auth) |
| **7. Email** | `n8n-nodes-base.emailSend` | Output | Altijd: samenvatting + ernst + aanbevolen actie |

### Error Type Classificatie (Code node)

```javascript
const error = $input.first().json;
const errorMsg = (error.execution?.error?.message || '').toLowerCase();
const nodeName = error.execution?.error?.node?.name || 'unknown';

// Classificatie
let errorType = 'LOGIC'; // default

if (errorMsg.includes('401') || errorMsg.includes('403') ||
    errorMsg.includes('unauthorized') || errorMsg.includes('token') ||
    errorMsg.includes('credential') || errorMsg.includes('authentication')) {
  errorType = 'CREDENTIAL';
}
else if (errorMsg.includes('timeout') || errorMsg.includes('econnrefused') ||
         errorMsg.includes('econnreset') || errorMsg.includes('network') ||
         errorMsg.includes('dns')) {
  errorType = 'NETWORK';
}
else if (errorMsg.includes('module not found') || errorMsg.includes('import error') ||
         errorMsg.includes('no such file') || errorMsg.includes('command not found') ||
         errorMsg.includes('pip') || errorMsg.includes('npm')) {
  errorType = 'DEPENDENCY';
}

const context = {
  errorType,
  workflowName: error.workflow?.name || 'unknown',
  nodeName,
  errorMessage: errorMsg,
  timestamp: new Date().toISOString(),
  executionId: error.execution?.id
};

return [{ json: context }];
```

### Self-Healing Issue Template

```markdown
## 🔧 Self-Healing — {workflow_name} gefaald

**Error type:** {CREDENTIAL / NETWORK / DEPENDENCY / LOGIC}
**Workflow:** {workflow_name}
**Node:** {node_name}
**Timestamp:** {timestamp}
**Gegenereerd door:** n8n Self-Healing Workflow (automated)

### Error Details

```
{error_message}
```

### Diagnose

{Voor CREDENTIAL: "PAT of API-key is verlopen of ongeldig. Vernieuw via GitHub Settings → Developer Settings → PAT."}
{Voor NETWORK: "Connectie-probleem. Retry {X}x geprobeerd. Controleer of Docker netwerk en GitHub API bereikbaar zijn."}
{Voor DEPENDENCY: "Module/commando niet gevonden. pip check output: {output}"}
{Voor LOGIC: AI-diagnose output}

### Voorgestelde Fix

- [ ] {Concrete actie per error type}

### Retry Status

{Voor NETWORK: "Retry 1: {status} — Retry 2: {status}"}
{Voor overige: "Geen automatische retry — handmatige actie vereist"}

---
*Meta-bewaking — Art. 2 DEV_CONSTITUTION*
*Dit is een automatisch gegenereerd issue. De voorgestelde fix is een suggestie — Niels beslist (Art. 1).*
```

### Retry-logica

```javascript
// Alleen voor NETWORK errors: max 2 retries met 5 min interval
const MAX_RETRIES = 2;
const RETRY_INTERVAL_MS = 5 * 60 * 1000; // 5 minuten

// n8n API call om workflow opnieuw te starten
// Vereist: n8n API key in environment variables
const response = await fetch(`http://localhost:5678/api/v1/workflows/${workflowId}/run`, {
  method: 'POST',
  headers: {
    'X-N8N-API-KEY': process.env.N8N_API_KEY,
    'Content-Type': 'application/json'
  }
});
```

## Relatie bestaand

- **Alle n8n-workflows (IDEA 1-5)**: deze workflow bewaakt hun functioneren
- **Feedback Loop 4** (zelfverbeterend systeem): directe implementatie
- **devhub-health skill**: complementair — health checkt codebase, self-healing checkt n8n-infra
- **Cynefin mapping**: SPIKE (complex) — onvoorspelbare foutmodi vereisen experimentele aanpak

## BORIS-impact

**Nee** — bewaakt alleen DevHub's n8n-workflows. Niet BORIS-specifiek.

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Notificatie | GitHub Issue + email bij elke fout |
| Retry-strategie | Alleen NETWORK errors, max 2x, 5 min interval |
| AI-diagnose | LangChain agent voor LOGIC/ONBEKEND errors; Haiku model (snel, goedkoop) |
| Reparatie | Alleen voorstellen, nooit automatisch uitvoeren (Art. 1: menselijke regie) |

| Email SMTP | Gmail met App Password |
| AI-diagnose model | Haiku (snel, goedkoop) |

## Open punten (resterend — Claude Code scope)

1. **n8n API key**: Claude Code maakt aan in n8n Settings → API bij implementatie.
2. **Error Trigger koppeling**: Claude Code registreert Self-Healing als error handler in elke workflow.
3. **Oneindige loop**: self-healing registreert géén error handler voor zichzelf. Bij eigen falen → alleen n8n execution log.
4. **Kosten-limiet**: Claude Code implementeert een dagelijks budget-limiet voor Haiku API-calls (bijv. max 10 diagnoses/dag).
5. **Afhankelijkheid**: implementeer als laatste van Fase 2 (na minimaal IDEA 1 operationeel).
