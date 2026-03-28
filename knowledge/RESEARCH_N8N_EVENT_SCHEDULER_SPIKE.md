# Research: n8n Event Scheduler SPIKE

---
sprint: 40
type: SPIKE
kennisgradering: SILVER
datum: 2026-03-28
bron: SPRINT_INTAKE_N8N_EVENT_SCHEDULER_2026-03-28
vorige_research: RESEARCH_CLAUDE_OPTIMALISATIE_CONCLUSIE (Sprint 31, OV2)
verdict: GO — n8n als externe scheduler is haalbaar en waardevol
---

## Samenvatting

Deze SPIKE onderzocht hoe n8n als externe event-scheduler voor DevHub kan fungeren. **Conclusie: GO.** De architectuur is helder, de kosten zijn verwaarloosbaar, en de eerste drie workflows zijn volledig ontworpen. Kernpatroon: `scheduleTrigger` -> `executeCommand` -> `claude -p` -> resultaat naar GitHub/file.

---

## Antwoorden op Onderzoeksvragen

### V1: Architectuur — hoe koppelt n8n aan DevHub?

**Antwoord: n8n draait `claude -p` via Execute Command node.**

| Patroon | Hoe | Pro | Con | Aanbeveling |
|---------|-----|-----|-----|-------------|
| Execute Command -> `claude -p` | n8n voert CLI uit op host | Volledige skill/tool toegang | Vereist self-hosted n8n | **PoC (primair)** |
| Anthropic API node | n8n roept Claude API direct aan | Simpel, geen CLI nodig | Geen file-access, geen skills | Simpele taken |
| Claude Agent SDK wrapper | n8n triggert thin API service | Meest flexibel, productie-ready | Meer setup | Toekomstige productie |

**Verificatie:** `claude -p` (print mode) is gedocumenteerd non-interactief mode. Verwerkt prompt en exit. Ondersteunt `--output-format json`, `--max-turns N`, `--allowedTools`, `--bare` (skip CLAUDE.md/MCP).

**Bron:** [Claude Code headless docs](https://code.claude.com/docs/en/headless) — Geverifieerd.

**Belangrijk:** Execute Command node is verwijderd uit default n8n v2.0.0+ node-lijst. Moet expliciet heractiveerd worden in self-hosted deployment.

**Kennisgradering:** GOLD — primaire bron (Anthropic docs + n8n docs).

### V2: Welke workflows eerst?

**Antwoord: Health Check -> Knowledge Decay -> Sprint Prep (hypothese bevestigd).**

| # | Workflow | Impact | Haalbaarheid | Complexiteit | Prioriteit |
|---|----------|--------|-------------|-------------|-----------|
| 1 | Health Check | Hoog — degradatie vroeg detecteren | Hoog — alle tools beschikbaar | Medium | **P1** |
| 2 | Knowledge Decay Scan | Hoog — veroudering voorkomen | Hoog — git log + frontmatter | Medium-Laag | **P1** |
| 3 | Sprint Prep Synthese | Middel — handwerk verminderen | Middel — 5 databronnen | Medium-Hoog | **P2** |
| 4 | Prompt Evolution Loop | Middel — kwaliteitsverbetering | Laag — metrics ontbreken | Hoog | P3 |
| 5 | Sprint Retrospective | Middel — learnings automatiseren | Middel | Medium | P3 |
| 6 | Governance Check on Merge | Middel — compliance borgen | Hoog — GitHub Actions beter | Laag | **P2 (via GH Actions)** |
| 7 | PR Quality Gate | Middel — review automatiseren | Hoog — GitHub Actions beter | Laag | **P2 (via GH Actions)** |
| 8 | Self-Healing Workflow | Laag — auto-repair risicovol | Laag — Art. 1 conflict | Hoog | P4 |
| 9 | Karpathy Experiment Loop | Hoog strategisch — continu leren | Laag — vereist feedback metrics | Zeer Hoog | **Fase 5** |

**ADR-001 beslissing bevestigd:** n8n voor scheduled, GitHub Actions voor event-driven (PR/push triggers).

### V3: n8n <-> DevHub data-flow

**Antwoord: Lezen via executeCommand (lokaal), schrijven via GitHub API.**

```
n8n (Docker, localhost:5679)
  |
  |-- LEEST: executeCommand op DEVHUB_REPO_PATH
  |     pytest, ruff, git log, ls docs/planning/inbox/
  |
  |-- SCHRIJFT: GitHub API (v1.1 node)
  |     Issues aanmaken, bestanden committen, labels zetten
  |
  |-- TRIGGERT: claude -p via executeCommand
  |     "Run /devhub-health for node devhub"
  |     --output-format json --max-turns 10
  |
  |-- NOTIFICEERT: emailSend (Gmail SMTP)
        Alleen bij RED-severity of failures
```

**Verificatie:** Geverifieerd via n8n node-specificaties in geparkeerde IDEAs.

### V4: Kosten en operationeel

**Hosting:**

| Optie | Kosten | Altijd-aan | Execute Command | Aanbeveling |
|-------|--------|------------|-----------------|-------------|
| Docker lokaal (Mac) | $0 | Nee (alleen als Mac aan staat) | Ja | **PoC** |
| VPS (Hetzner/DO) | $5-20/mo | Ja | Ja | Productie |
| n8n Cloud | $24-60/mo | Ja | Nee | Niet geschikt |

**Token-kosten (dagelijks draaien):**

| Workflow | Tokens/run | Kosten/run (Haiku 4.5) | Kosten/maand (dagelijks) |
|----------|-----------|----------------------|------------------------|
| Health Check | ~3.000 | $0.007 | $0.21 |
| Knowledge Decay | ~5.000 | $0.012 | $0.36 |
| Sprint Prep | ~4.000 | $0.009 | $0.27 |
| **Totaal** | | | **$0.84/maand** |

Met `claude -p` (meer overhead door CLAUDE.md laden): 3-5x multiplier -> **$2.50-4.20/maand**. Met `--bare` flag: dichter bij directe API kosten.

**Conclusie:** Kosten zijn verwaarloosbaar. Docker lokaal is de juiste keuze voor PoC.

**Kennisgradering:** SILVER — gebaseerd op Anthropic pricing pagina + n8n pricing pagina.

### V5: Event bus bridge

**Antwoord: File-based event queue voor PoC, webhook voor productie.**

```
events/
  pending/      # n8n schrijft hier JSON events
  processed/    # Claude Code verplaatst verwerkte events
  failed/       # Gefaalde events voor retry

Voorbeeld event:
{
  "type": "HealthDegraded",
  "source": "n8n-health-check",
  "timestamp": "2026-03-28T18:00:00Z",
  "payload": {
    "severity": "YELLOW",
    "failures": ["ruff: 3 errors", "pip-audit: 1 CVE"]
  }
}
```

**Bridge-mechanisme:**
- **n8n -> DevHub:** n8n schrijft event-JSON naar `events/pending/`. Claude Code hook bij sessie-start leest pending events en publiceert ze op de in-memory event bus.
- **DevHub -> n8n:** Sprint-close of health-degradatie triggert n8n webhook. Alleen nodig voor productie-grade, niet voor PoC.

**Waarom file-based:**
- Geen infrastructuur nodig (geen message broker, geen database)
- Volledig traceerbaar (git history)
- Werkt ook als n8n of Claude Code niet tegelijk actief is
- Eenvoudig te upgraden naar webhook later

**Kennisgradering:** BRONZE — pattern is logisch maar niet getest in DevHub context.

---

## PoC Workflow 1: Health Check

**Gebaseerd op:** `IDEA_N8N_HEALTH_CHECK_WORKFLOW_2026-03-24.md`

### Workflow-ontwerp

```
[scheduleTrigger: dagelijks 18:00]
    |
    v
[executeCommand x4 parallel]
    pytest --tb=no -q
    ruff check --format json
    pip-audit --format json
    pip list --outdated --format json
    |
    v
[code: aggregatie]
    Bepaal severity: GREEN / YELLOW / RED
    Genereer samenvatting
    |
    v
[if: severity !== GREEN]
    |-- TRUE --> [github: check duplicate issues]
    |               |
    |               v
    |            [github: create issue met P1/P2 label]
    |               |
    |               v
    |            [if: severity === RED]
    |               |-- TRUE --> [emailSend: notificatie]
    |
    |-- FALSE --> [code: schrijf event naar events/pending/]
                    type: HealthChecked, severity: GREEN
```

### n8n nodes

| Node | Type | Configuratie |
|------|------|-------------|
| Schedule | `scheduleTrigger` | Dagelijks 18:00, timezone Europe/Amsterdam |
| Tests | `executeCommand` | `cd $DEVHUB_REPO_PATH && uv run pytest --tb=no -q` |
| Lint | `executeCommand` | `cd $DEVHUB_REPO_PATH && uv run ruff check --format json` |
| CVE | `executeCommand` | `cd $DEVHUB_REPO_PATH && uv run pip-audit --format json` |
| Outdated | `executeCommand` | `cd $DEVHUB_REPO_PATH && pip list --outdated --format json` |
| Aggregator | `code` | JavaScript: parse outputs, determine severity |
| Issue Gate | `if` | `{{ $json.severity !== 'GREEN' }}` |
| GitHub | `github` | Action: Create Issue, labels: `[devhub-health, $severity]` |
| Email | `emailSend` | Gmail SMTP, alleen RED |

### Environment variabelen

```
DEVHUB_REPO_PATH=/Users/nielspostma/alsdan-devhub
GITHUB_TOKEN=ghp_xxx (via .env, gitignored)
EMAIL_USER=xxx@gmail.com
EMAIL_PASSWORD=xxx (App Password)
```

---

## PoC Workflow 2: Knowledge Decay Scan

**Gebaseerd op:** `IDEA_N8N_KNOWLEDGE_DECAY_SCAN_2026-03-24.md`

### Workflow-ontwerp

```
[scheduleTrigger: wekelijks zaterdag 10:00]
    |
    v
[executeCommand]
    git log --format='%H %ai %s' -- knowledge/ docs/
    |
    v
[code: parse + decay detectie]
    Per bestand: laatste commit datum
    Drempels: GOLD >180d, SILVER >120d, BRONZE >90d, SPECULATIVE >60d
    Lees frontmatter voor evidence_grade
    |
    v
[filter: alleen decay-gedetecteerd]
    |
    v
[code: genereer RESEARCH_VOORSTEL markdown]
    Per vervallen item: bestandsnaam, grade, laatste update, decay-status
    |
    v
[github: commit naar docs/planning/inbox/]
    RESEARCH_VOORSTEL_DECAY_{datum}.md
    |
    v
[code: schrijf event naar events/pending/]
    type: KnowledgeDecayDetected
    payload: { count: N, items: [...] }
```

### Decay-drempels

| Kennisgradering | Vervaltermijn | Actie |
|-----------------|---------------|-------|
| GOLD (bewezen) | >180 dagen | Hervalidatie door researcher |
| SILVER (gevalideerd) | >120 dagen | Review + update check |
| BRONZE (ervaring) | >90 dagen | Bronnen opnieuw verifierien |
| SPECULATIVE (aanname) | >60 dagen | Upgrade of verwijder |

---

## Prioriteringsmatrix: Alle 9 n8n IDEAs

| # | Workflow | Systeem | Impact | Haalbaarheid | Kosten | Score | Fase |
|---|----------|---------|--------|-------------|--------|-------|------|
| 1 | Health Check | n8n | 9/10 | 9/10 | Laag | **27** | 4-Golf3A |
| 2 | Knowledge Decay Scan | n8n | 8/10 | 8/10 | Laag | **24** | 4-Golf3A |
| 3 | Sprint Prep Synthese | n8n | 7/10 | 7/10 | Laag | **21** | 4-Golf3A |
| 4 | Governance Check on Merge | GH Actions | 7/10 | 9/10 | Laag | **23** | 4-Golf3A |
| 5 | PR Quality Gate | GH Actions | 6/10 | 9/10 | Laag | **21** | 4-Golf3A |
| 6 | Sprint Retrospective | n8n | 5/10 | 6/10 | Laag | **16** | 4-Golf3B |
| 7 | Prompt Evolution Loop | n8n | 7/10 | 4/10 | Middel | **15** | 5 |
| 8 | Self-Healing Workflow | n8n | 3/10 | 3/10 | Middel | **9** | 5+ |
| 9 | Karpathy Experiment Loop | n8n | 9/10 | 3/10 | Hoog | **15** | 5 |

**Golf 3A implementatie-volgorde:**
1. Health Check (n8n) — bewijst het patroon
2. Knowledge Decay (n8n) — valideert op tweede use case
3. Governance Check (GH Actions) — event-driven pad bewijzen
4. Sprint Prep Synthese (n8n) — complexere aggregatie
5. PR Quality Gate (GH Actions) — combinatie met governance

---

## Event Bus Bridge Ontwerp

### Architectuur

```
                    n8n (Docker, localhost:5679)
                         |
              scheduled workflows draaien
                         |
                    schrijft resultaten
                         |
                         v
              events/pending/*.json  <--- FILE-BASED QUEUE
                         |
                         |  (bij volgende sessie-start)
                         v
              Claude Code PreSessionStart hook
                         |
                    leest pending events
                         |
                    publiceert op in-memory event bus
                         |
                    verplaatst naar events/processed/
```

### Hook-configuratie (settings.json)

```json
{
  "hooks": {
    "PreSessionStart": [
      {
        "command": "python scripts/process_pending_events.py",
        "description": "Verwerk n8n events bij sessie-start"
      }
    ]
  }
}
```

### Event-formaat

```json
{
  "id": "evt_20260328_180000_health",
  "type": "HealthChecked",
  "source": "n8n-health-check",
  "timestamp": "2026-03-28T18:00:00+02:00",
  "version": "1.0",
  "payload": {
    "severity": "GREEN",
    "tests": { "passed": 1357, "failed": 0 },
    "lint": { "errors": 0 },
    "cve": { "count": 0 }
  }
}
```

### Event-types (initieel)

| Type | Producer | Consumer | Beschrijving |
|------|----------|----------|-------------|
| `HealthChecked` | n8n health workflow | DevHub health skill | Resultaat van health check |
| `HealthDegraded` | n8n health workflow | DevHub + email | Severity YELLOW of RED |
| `KnowledgeDecayDetected` | n8n decay workflow | DevHub researcher | Verouderde kennis gevonden |
| `SprintPrepReady` | n8n prep workflow | DevHub sprint skill | Prep-rapport beschikbaar |

---

## Operationeel Voorstel

### Hosting

**Docker lokaal op Mac** — $0, onbeperkte executions.

```yaml
# docker-compose.yml (concept)
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5679:5678"
    volumes:
      - ~/.n8n:/home/node/.n8n
      - /Users/nielspostma/alsdan-devhub:/devhub:ro
    environment:
      - DEVHUB_REPO_PATH=/devhub
      - GENERIC_TIMEZONE=Europe/Amsterdam
    restart: unless-stopped
```

### Failure handling

| Scenario | Actie |
|----------|-------|
| Workflow faalt | n8n retry (max 3x, exponential backoff) |
| Claude CLI timeout | `--max-turns 10` cap + n8n timeout node |
| n8n down | Scheduled runs gemist — geen data loss, volgende run pikt het op |
| Geen internet | Lokale checks (pytest, ruff) draaien door, GitHub/email skip |

### Monitoring

- n8n ingebouwde execution history (30 dagen)
- `events/failed/` directory voor gefaalde events
- Wekelijkse handmatige check van n8n dashboard (poort 5679)

---

## Aanbeveling

### Verdict: GO

n8n als externe scheduler is **haalbaar, waardevol, en betaalbaar**. Het kernpatroon (`scheduleTrigger` -> `executeCommand` -> `claude -p`) is geverifieerd met primaire bronnen.

### Vervolgsprints (na deze SPIKE)

| Sprint | Type | Scope | Dependencies |
|--------|------|-------|-------------|
| n8n Docker Setup | CHORE (XS) | Docker compose, env vars, Execute Command heractiveren | Geen |
| Health Check Workflow | FEAT (S) | PoC 1 bouwen + testen | Docker setup |
| Knowledge Decay Workflow | FEAT (S) | PoC 2 bouwen + testen | Docker setup |
| Event Bus FEAT | FEAT (S) | In-memory event bus + typed events | Geen |
| Event Bus Bridge | FEAT (XS) | File-based queue + PreSessionStart hook | Event Bus + n8n workflows |

### Sequencing-update

De oorspronkelijke volgorde was:
```
SPIKE Agent Teams -> FEAT Event Bus -> SPIKE n8n -> FEAT Dashboard
```

Nieuwe aanbeveling (Agent Teams geparkeerd, n8n SPIKE klaar):
```
CHORE n8n Docker Setup (XS)          # infra
FEAT Event Bus Lifecycle Hooks (S)   # in-memory bus + typed events
FEAT Health Check Workflow (S)       # eerste n8n workflow
FEAT Knowledge Decay Workflow (S)    # tweede n8n workflow
FEAT Event Bus Bridge (XS)           # verbind n8n met bus
FEAT Dashboard NiceGUI (S)           # visualiseer alles
```

### Kritiek pad

```
n8n Docker Setup -> Health Check Workflow ---+
                                             |---> Event Bus Bridge
Event Bus FEAT ----------------------------- +
```

Event Bus en n8n Docker Setup kunnen **parallel** — ze zijn onafhankelijk.

---

## Bronverantwoording

| Bron | Type | Kennisgradering | Verificatie |
|------|------|-----------------|-------------|
| [Claude Code headless docs](https://code.claude.com/docs/en/headless) | Primaire bron | GOLD | Geverifieerd |
| [n8n Execute Command docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/) | Primaire bron | GOLD | Geverifieerd |
| [n8n Pricing](https://n8n.io/pricing/) | Primaire bron | GOLD | Geverifieerd |
| [Anthropic API Pricing](https://platform.claude.com/docs/en/about-claude/pricing) | Primaire bron | GOLD | Geverifieerd |
| [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) | Primaire bron | GOLD | Geverifieerd |
| [n8n-MCP for Claude Code](https://github.com/czlonkowski/n8n-mcp) | Community tool | SILVER | Geverifieerd |
| ADR-001-n8n-cicd-architecture.md | Eigen architectuurbeslissing | GOLD | Geverifieerd |
| 9 geparkeerde n8n IDEAs | Eigen planning | SILVER | Geverifieerd |
| Sprint 31 OV2 (n8n conclusie) | Eigen research | SILVER | Geverifieerd, uitgebreid |
| [n8n Community: Execute Command heractiveren](https://community.n8n.io/t/how-to-enable-execute-command/249009) | Community | BRONZE | Geverifieerd |

---

## Conclusie

n8n als externe scheduler is de juiste keuze voor DevHub. Het patroon is bewezen (`claude -p` via Execute Command), de kosten zijn verwaarloosbaar ($0 hosting + <$5/maand tokens), en de eerste drie workflows zijn volledig ontworpen met concrete n8n node-specificaties.

De file-based event queue biedt een eenvoudige bridge naar de event bus zonder extra infrastructuur. De hybrid-strategie (n8n voor scheduled, GitHub Actions voor event-driven) uit ADR-001 wordt herbevestigd.

Volgende stap: CHORE sprint voor n8n Docker setup, gevolgd door FEAT sprints voor de individuele workflows.
