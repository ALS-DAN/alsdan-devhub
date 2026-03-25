# SPRINT_INTAKE: n8n Dagelijkse Health Check Workflow

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |
| **Bron** | IDEA_N8N_HEALTH_CHECK_WORKFLOW_2026-03-24.md |

---

## Doel

Implementeer een n8n-workflow die dagelijks om 18:00 de DevHub-codebase controleert op test-failures, lint-fouten, CVE's en verouderde dependencies, en bij problemen automatisch een GitHub Issue aanmaakt met prioriteitslabels (P1/P2) plus email-notificatie bij RED-severity.

## Probleemstelling

**Waarom nu**: De `devhub-health` skill bestaat en werkt (6-dimensie check), maar draait alleen reactief — als iemand hem handmatig aanroept. Niels werkt solo in avonduren/weekenden; zonder proactieve bewaking worden regressies, CVE's en dependency-drift pas ontdekt wanneer ze al sprints blokkeren.

**Fase-context**: Dit is de eerste n8n-workflow en het fundament voor alle andere workflows (PR Quality Gate, Governance Check, Self-Healing, etc.). Zonder een werkende Health Check is er geen basis om op te bouwen. Dit past in Fase 2 (Skills + Governance) omdat het de bestaande `devhub-health` skill verlengt met een geautomatiseerde trigger.

**Probleem**: Stille regressie — de codebase kan dagen kapot zijn zonder dat iemand het merkt.
**Oplossing**: Dagelijkse geautomatiseerde health check met issue-creatie en notificatie.
**Grenzen**: Alleen DevHub-repo, geen BORIS. Alleen read-only checks, geen destructieve operaties.
**Appetite**: Klein-Middel — één sprint, voornamelijk n8n-configuratie + Docker setup.

## Deliverables

- [ ] n8n Docker container operationeel op Niels' Mac met volume mount naar DevHub-repo
- [ ] n8n-workflow "DevHub Health Check" met 7 nodes:
  - `scheduleTrigger` (dagelijks 18:00)
  - 4× `executeCommand` (pytest, ruff, pip-audit, pip list --outdated)
  - `code` (aggregatie + severity-bepaling)
  - `if` (severity !== GREEN)
  - `github` (duplicaat-check + issue create, PAT auth)
  - `emailSend` (bij RED-severity, Gmail + App Password)
- [ ] Environment variables geconfigureerd: `$DEVHUB_REPO_PATH`, GitHub PAT via n8n credentials
- [ ] Issue template met severity-mapping: tests/CVE → RED (P1), lint/outdated → YELLOW (P2)
- [ ] Issue lifecycle: stale na 14 dagen, auto-close na 28 dagen
- [ ] Handmatige test-run: trigger workflow, verifieer issue-creatie bij geforceerde failure
- [ ] Documentatie: korte setup-guide in `docs/operations/n8n-health-check.md`

## Afhankelijkheden

| Type | Detail |
|------|--------|
| **Geblokkeerd door** | Geen — dit is de eerste workflow |
| **BORIS-impact** | Nee — draait puur op DevHub |
| **Tooling vereist** | Docker Desktop, n8n Docker image, GitHub PAT, Gmail App Password |
| **Bestaande code** | `devhub-health` skill (referentie voor check-logica) |

## Fase-context

**Huidige fase**: Fase 2 (Skills + Governance).
**Fit**: Direct — automatiseert een bestaande skill, implementeert Art. 2 (verificatieplicht), Art. 3 (codebase-integriteit) en Art. 7 (impact-zonering). Geen scope creep; is letterlijk "maak de health check autonoom."

## Open vragen voor Claude Code

1. **Docker volume mount**: repo-pad moet als volume gemount worden in de n8n Docker container. Wat is de optimale mount-configuratie (`-v` flag) zodat `executeCommand` toegang heeft tot de Python venv en pytest/ruff/pip-audit kan draaien?
2. **Python environment in Docker**: draait pytest binnen de n8n container of via host-mounted venv? Aanbeveling: host-mounted venv via volume, zodat dezelfde dependencies worden gebruikt als bij lokale development.
3. **n8n persistence**: n8n data (workflows, credentials) opslaan in een Docker volume zodat workflows niet verloren gaan bij container restart.
4. **Eerste test-run**: na implementatie een geforceerde failure induceren (bijv. kapotte test) om de hele keten te verifiëren (issue + email).

## Prioriteit

**Hoog** — dit is het fundament voor alle 8 andere n8n-workflows. Zonder werkende n8n Docker + Health Check kan niets anders worden gebouwd. Eerste workflow = proof of concept voor het hele n8n-ecosysteem.

## Technische richting

*(Claude Code mag afwijken)*

- **n8n Docker**: `docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n -v /Users/nielspostma/alsdan-devhub:/repo n8nio/n8n`
- **Severity-mapping**: zie IDEA document voor Code node logica
- **Issue template**: zie IDEA document voor markdown template
- **Issue lifecycle**: GitHub Actions of n8n sub-workflow voor stale/auto-close

## DEV_CONSTITUTION impact

| Artikel | Impact | Toelichting |
|---------|--------|-------------|
| Art. 2 (Verificatieplicht) | Directe implementatie | Automatische verificatie van codebase-gezondheid |
| Art. 3 (Codebase-integriteit) | Bewaking | Read-only checks, geen destructieve operaties |
| Art. 7 (Impact-zonering) | Directe implementatie | GREEN/YELLOW/RED mapping op issue-prioriteit |
| Art. 8 (Dataminimalisatie) | Geen risico | Workflow bevat geen secrets in code; PAT via n8n credentials |

## Cynefin-classificatie

**Simpel** → Sprint-type: **CHORE**. De logica is helder (run commands, check output, create issue), de n8n nodes zijn geverifieerd, het enige onbekende is de Docker mount-configuratie.

## Shape Up samenvatting

| Dimensie | Waarde |
|----------|--------|
| Probleem | Stille regressie door gebrek aan proactieve codebase-bewaking |
| Oplossing | Dagelijkse n8n-workflow met issue-creatie en email-notificatie |
| Grenzen | Alleen DevHub, alleen read-only, geen BORIS |
| Appetite | Klein-Middel (1 sprint) |
| Risico | GREEN — geen destructieve operaties |
