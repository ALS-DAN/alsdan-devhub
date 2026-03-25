# SPRINT_INTAKE: n8n PR Quality Gate Workflow

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |
| **Bron** | IDEA_N8N_PR_QUALITY_GATE_2026-03-24.md |

---

## Doel

Implementeer een n8n-workflow die bij elke Pull Request automatisch tests, lint en CVE-scan draait, het resultaat als PR comment post, de juiste labels toevoegt (quality-gate-passed / needs-attention / blocked), en bij RED-severity Niels mailt.

## Probleemstelling

**Waarom nu**: Niels werkt solo, vaak laat op de avond. Er is geen CI/CD pipeline en geen tweede reviewer. Code-problemen worden pas ontdekt na merge — als de Health Check ze oppikt. Een quality gate vóór merge verschuift de detectie naar het juiste moment: voordat slechte code in main belandt.

**Fase-context**: Fase 2 (Skills + Governance). Bouwt voort op dezelfde n8n-infra als de Health Check (IDEA 1) — hergebruikt Docker setup, PAT credentials, en executeCommand-patroon. Implementeert Laag C (Review) van de 5-laags check-architectuur.

**Probleem**: Geen automatisch vangnet bij PR's — code kan naar main mergen met test-failures, CVE's of lint-fouten.
**Oplossing**: Event-driven n8n-workflow die bij `pull_request` events automatisch checks draait en rapporteert als PR comment.
**Grenzen**: Alleen DevHub-repo. Alleen read-only checks + non-destructieve GitHub schrijfacties (comments, labels). Geen blocking required check (recommended).
**Appetite**: Klein-Middel — één sprint, hergebruikt n8n-infra van Health Check.

## Deliverables

- [ ] n8n-workflow "PR Quality Gate" met nodes:
  - `githubTrigger` (pull_request: opened + synchronize)
  - `github` (PR info: changed files, diff)
  - `executeCommand` (git worktree add voor PR-branch isolatie)
  - 3× `executeCommand` (pytest, ruff, pip-audit op PR-branch)
  - `code` (resultaat-analyse + severity-bepaling)
  - `switch` (route op GREEN/YELLOW/RED)
  - `github` (PR comment: create of edit bestaand)
  - `github` (labels: quality-gate-passed / needs-attention / blocked)
  - `executeCommand` (git worktree remove — cleanup)
  - `emailSend` (bij RED-severity)
- [ ] Comment-edit logica: bij re-trigger (`synchronize`) bestaand comment updaten i.p.v. nieuw comment (voorkom spam)
- [ ] Label-management: oude quality-gate labels verwijderen vóór nieuw label toevoegen
- [ ] Git worktree-gebaseerde isolatie (geen checkout op main working tree)
- [ ] PR comment template met severity-badge, resultaat-tabel en aanbevelingen
- [ ] Handmatige test-run: maak test-PR, verifieer comment + label + email-keten
- [ ] Documentatie: setup-guide in `docs/operations/n8n-pr-quality-gate.md`

## Afhankelijkheden

| Type | Detail |
|------|--------|
| **Geblokkeerd door** | SPRINT_INTAKE_N8N_HEALTH_CHECK — vereist werkende n8n Docker + credentials |
| **BORIS-impact** | Nee — draait puur op DevHub |
| **Tooling vereist** | n8n Docker (al opgezet door Health Check), GitHub PAT, Gmail App Password |
| **Bestaande code** | `devhub-review` skill (referentie voor check-logica), QA Agent (toekomstige integratie) |

## Fase-context

**Huidige fase**: Fase 2 (Skills + Governance).
**Fit**: Direct — automatiseert de review-stap vóór merge, implementeert Art. 2 (verificatieplicht), Art. 3 (codebase-integriteit) en Art. 7 (impact-zonering). Sluit aan bij de 5-laags check-architectuur als Laag C (Review).

## Open vragen voor Claude Code

1. **Git worktree in Docker**: de n8n container moet `git worktree add` kunnen uitvoeren. Is git beschikbaar in het n8n Docker image, of moet het worden geïnstalleerd? Aanbeveling: custom Dockerfile met `git` + Python venv.
2. **Race condition**: als twee PR's tegelijk open staan, moeten twee worktrees naast elkaar kunnen bestaan. Gebruik unieke worktree-namen: `/tmp/pr-{PR_NUMBER}`.
3. **Comment edit vs. create**: GitHub API biedt `PATCH /repos/{owner}/{repo}/issues/comments/{comment_id}`. Claude Code implementeert: zoek bestaand comment met marker `<!-- n8n-quality-gate -->`, edit als gevonden, create als niet gevonden.
4. **QA Agent integratie**: nu basis-checks (test/lint/CVE). Volledige QA Agent (12+6 checks) als vervolgstap — niet in deze sprint.

## Prioriteit

**Hoog** — tweede workflow in de implementatievolgorde. Samen met Health Check (scheduled) en Governance Check (post-merge) vormt dit de drie-punts bewaking: vóór merge, na merge, en dagelijks.

## Technische richting

*(Claude Code mag afwijken)*

- **Trigger**: `githubTrigger` met `pull_request` events (opened + synchronize)
- **Isolatie**: `git worktree add /tmp/pr-{number} origin/pr-branch` — geen checkout op main
- **Severity-mapping**: tests/CVE failed → RED, lint errors → YELLOW, warnings >3 → YELLOW, rest → GREEN
- **Label-management**: verwijder oude labels `[quality-gate-passed, needs-attention, blocked]` vóór nieuw label
- **Comment-marker**: `<!-- n8n-quality-gate -->` als hidden marker voor edit-detectie

## DEV_CONSTITUTION impact

| Artikel | Impact | Toelichting |
|---------|--------|-------------|
| Art. 2 (Verificatieplicht) | Directe implementatie | Automatische verificatie bij elke PR |
| Art. 3 (Codebase-integriteit) | Bewaking vóór merge | Vangt problemen voordat ze in main belanden |
| Art. 7 (Impact-zonering) | Directe implementatie | GREEN/YELLOW/RED mapping op PR-labels |
| Art. 8 (Dataminimalisatie) | Geen risico | PAT via n8n credentials, geen secrets in workflow |

## Cynefin-classificatie

**Gecompliceerd** → Sprint-type: **FEAT**. De individuele checks zijn simpel, maar de integratie (worktree-isolatie, comment edit-logica, label-management, re-trigger handling) vereist engineering-expertise.

## Shape Up samenvatting

| Dimensie | Waarde |
|----------|--------|
| Probleem | Geen automatisch vangnet bij PR's — code kan ongecontroleerd naar main mergen |
| Oplossing | Event-driven n8n-workflow met PR comment, labels en email-notificatie |
| Grenzen | Alleen DevHub, non-destructieve acties, recommended (niet required) check |
| Appetite | Klein-Middel (1 sprint, hergebruikt n8n-infra) |
| Risico | YELLOW — schrijft PR comments en labels (zichtbaar, niet-destructief) |
