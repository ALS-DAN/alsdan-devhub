# SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR_2026-03-23

---
gegenereerd_door: Cowork — alsdan-devhub
status: INBOX
fase: 1
---

## Doel

Bouw een gelaagde code-check architectuur die de bestaande QA Agent, devhub-review skill, GitHub MCP, n8n-nodes en engineering skills combineert tot een geïntegreerd quality assurance systeem, geörkestreerd door een nieuwe reviewer agent.

## Probleemstelling

DevHub heeft sterke individuele check-componenten (QA Agent met 18 checks, devhub-review skill, devhub-health met 6 dimensies, GitHub MCP) maar mist:
1. Een **reviewer agent** die deze componenten orkestreert
2. **Security-specifieke tooling** (SAST, SCA, secrets detection op industrieniveau)
3. **Geautomatiseerde periodieke checks** via n8n scheduled workflows
4. Een **gelaagd model** dat duidelijk maakt welke check wanneer draait

Dit is urgent omdat de industrie in 2026 een 40% kwaliteitsdeficit verwacht: AI-gegenereerde code groeit sneller dan review-capaciteit. De reviewer agent is het antwoord.

### Fase-context
Fase 1 deliverable: reviewer agent is één van de drie ontbrekende plugin-agents. Dit intake-voorstel geeft de reviewer agent een concrete architectuur die maximaal gebruik maakt van bestaande tooling.

## Deliverables

- [ ] **reviewer agent** (`agents/reviewer.md`) — Opus-model, orkestreert alle check-lagen
- [ ] **Gelaagde check-architectuur** gedocumenteerd in reviewer agent prompt
- [ ] **n8n workflow-specificatie** voor periodieke health checks (Claude Code bouwt de workflow)
- [ ] **MCP-integratie configuratie** voor Datadog Code Security of SAST MCP Tool
- [ ] **E2E test** die de reviewer agent → QA Agent → rapport keten valideert

## Architectuur: Vijf Check-Lagen

### Laag A — Preventie (vóór code geschreven wordt)

| Component | Beschikbaar? | Bron |
|-----------|-------------|------|
| devhub-sprint-prep skill (DoR checklist) | JA | `.claude/skills/devhub-sprint-prep/` |
| Impact-zonering (GREEN/YELLOW/RED) | JA | DEV_CONSTITUTION Art. 7 |
| `engineering:testing-strategy` skill | JA | Cowork plugin |

**Verantwoordelijke:** dev-lead agent (bestaand)

### Laag B — Realtime (tijdens het schrijven)

| Component | Beschikbaar? | Bron |
|-----------|-------------|------|
| Coder agent volgt CLAUDE.md constraints | JA | `agents/coder.md` |
| Pre-commit hooks (detect-secrets, ruff) | JA | DEV_CONSTITUTION Art. 8 |
| Claude Code Security (ingebouwd) | JA | Anthropic (feb 2026) |

**Verantwoordelijke:** coder agent (bestaand)

### Laag C — Review (na implementatie) — NIEUW: reviewer agent

| Component | Beschikbaar? | Bron |
|-----------|-------------|------|
| QA Agent (12 code + 6 doc checks) | JA | `devhub/agents/qa_agent.py` |
| devhub-review skill (diff + anti-patronen) | JA | `.claude/skills/devhub-review/` |
| `engineering:code-review` skill | JA | Cowork plugin |
| Anti-patroon scan (node-specifiek) | JA | BorisAdapter |

**Verantwoordelijke:** reviewer agent (TE BOUWEN)

**Reviewer agent workflow:**
1. Ontvang review-verzoek van dev-lead
2. Haal git diff + gewijzigde bestanden via BorisAdapter
3. Draai QA Agent review_code() → QAFindings
4. Draai QA Agent review_docs() → QAFindings (indien docs gewijzigd)
5. Scan anti-patronen via adapter.scan_anti_patterns()
6. Voer diepte-analyse uit op security, performance, edge cases (engineering:code-review kennis)
7. Produceer QAReport met verdict (PASS/NEEDS_WORK/BLOCK)
8. Bij BLOCK → escaleer naar Niels (Art. 7, RED-zone)
9. Bij NEEDS_WORK → rapporteer aan dev-lead met concrete fixes
10. Bij PASS → rapporteer met positieve observaties (min. 5 bevindingen)

### Laag D — Systeem-niveau (periodiek)

| Component | Beschikbaar? | Bron |
|-----------|-------------|------|
| devhub-health skill (6 dimensies) | JA | `.claude/skills/devhub-health/` |
| pip-audit (CVE/dependency scan) | JA | BorisAdapter.run_pip_audit() |
| `engineering:tech-debt` skill | JA | Cowork plugin |
| GitHub Issues alert routing | JA | GitHub MCP |

**Verantwoordelijke:** n8n scheduled workflow (TE BOUWEN)

**n8n workflow specificatie:**
```
Trigger: scheduleTrigger (dagelijks 06:00 of wekelijks maandag)
→ GitHub API: check laatste commit timestamp
→ Run: tests + lint + pip-audit (via webhook naar Claude Code)
→ Evalueer: resultaten tegen drempelwaarden
→ Bij afwijking: create GitHub Issue (P1/P2 labels)
→ Altijd: update HEALTH_STATUS.md
```

**Relevante n8n-nodes (geverifieerd beschikbaar):**
- `n8n-nodes-base.scheduleTrigger`
- `n8n-nodes-base.github` / `n8n-nodes-base.githubTrigger`
- `n8n-nodes-base.webhook`
- `@n8n/n8n-nodes-langchain.agent`

### Laag E — Security-specifiek (toe te voegen)

| Component | Beschikbaar? | Bron |
|-----------|-------------|------|
| Datadog Code Security MCP | NEE — toe te voegen | MCP Server |
| SAST MCP Tool (Semgrep/Bandit/TruffleHog) | NEE — toe te voegen | mcpmarket.com |
| StackHawk (DAST) | NEE — optioneel | Externe service |

**Aanbeveling:** Begin met SAST MCP Tool (gratis, open-source bridge naar 15+ tools) of Datadog Code Security MCP (uitgebreider maar vereist Datadog account).

**Vier scantypen die Laag E toevoegt:**
1. **SAST** — Static Application Security Testing (code-patronen)
2. **Secrets detection** — op industrieniveau (TruffleHog, beyond regex)
3. **SCA** — Software Composition Analysis (dependency vulnerabilities)
4. **IaC scanning** — Infrastructure-as-Code checks

## Afhankelijkheden

- **Geblokkeerd door:** geen — kan direct starten als eerste Fase 1 sprint
- **BORIS impact:** NEE — reviewer agent werkt via BorisAdapter (read-only), geen wijzigingen in BORIS

## Fase Context

- **Huidige fase:** 0 afgerond → Fase 1
- **Fit:** reviewer agent is een expliciete Fase 1 deliverable
- **Relatie tot andere Fase 1 werk:** researcher en planner agents kunnen parallel gebouwd worden

## Open Vragen voor Claude Code

1. Moet de reviewer agent Opus of Sonnet zijn? Opus geeft diepere analyse maar is trager/duurder. Aanbeveling: Opus (review vereist redenering, niet snelheid).
2. Hoe integreren we de SAST MCP Tool in `.mcp.json`? Welke configuratie is nodig?
3. Kan de reviewer agent de `engineering:code-review` Cowork skill aanroepen, of moet die kennis in de agent prompt zelf?
4. Welk format gebruiken we voor de n8n health check workflow? Direct JSON of via n8n-MCP template?
5. Hoe voorkomen we dat reviewer + QA Agent dubbel werk doen? De reviewer zou de QA Agent moeten aanroepen, niet dupliceren.

## DEV_CONSTITUTION Impact

| Artikel | Geraakt? | Toelichting |
|---------|----------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Reviewer rapporteert, beslist niet over merge |
| Art. 2 (Verificatieplicht) | Ja | Reviewer verifieert claims in code tegen tests |
| Art. 3 (Codebase-integriteit) | Ja | Reviewer is read-only, wijzigt nooit code |
| Art. 7 (Impact-zonering) | Ja | BLOCK → RED-zone escalatie naar Niels |
| Art. 8 (Dataminimalisatie) | Ja | Secret detection is kernfunctie van reviewer |

## Prioriteit

- **Prioriteit:** Hoog
- **Motivatie:** De reviewer agent is de ontbrekende schakel die alle bestaande check-componenten operationeel maakt. Zonder orkestrator worden QA Agent, anti-patronen scan, en engineering skills niet systematisch ingezet. Het 40% review-deficit (industrie 2026) maakt dit urgent.

## Technische Richting (Claude Code mag afwijken)

```yaml
reviewer_agent:
  model: opus
  file: agents/reviewer.md
  delegatie: geen (leaf agent, rapporteert aan dev-lead)
  tools:
    - QAAgent.review_code()
    - QAAgent.review_docs()
    - QAAgent.produce_report()
    - adapter.get_review_context()
    - adapter.scan_anti_patterns()
    - adapter.run_lint()
    - adapter.run_tests()
  output: QAReport (JSON in scratchpad)
  escalatie:
    BLOCK: → Niels (RED-zone)
    NEEDS_WORK: → dev-lead
    PASS: → dev-lead (met min. 5 observaties)
```

## Bestaande Tooling Inventaris (geverifieerd 2026-03-23)

### In DevHub repo

| Tool | Pad | Checks |
|------|-----|--------|
| QA Agent | `devhub/agents/qa_agent.py` | CR-01..12 (code), DR-01..06 (docs) |
| devhub-review skill | `.claude/skills/devhub-review/` | git diff, anti-patronen, lint, tests |
| devhub-health skill | `.claude/skills/devhub-health/` | 6 dimensies, P1-P4 severity |
| BorisAdapter | `devhub/adapters/boris_adapter.py` | 38 methodes, review context, anti-patronen |

### Via MCP (beschikbaar)

| Tool | Type | Functie |
|------|------|--------|
| GitHub MCP | MCP Server | PR reviews, code search, issue creation |
| n8n MCP | MCP Server | Workflow building, node search, validation |

### Via Cowork Skills (beschikbaar)

| Skill | Functie |
|-------|--------|
| `engineering:code-review` | Security, performance, correctness review |
| `engineering:testing-strategy` | Teststrategie ontwerp |
| `engineering:tech-debt` | Tech debt identificatie |
| `engineering:architecture` | ADR evaluatie |

### Toe te voegen (Laag E)

| Tool | Type | Functie |
|------|------|--------|
| Datadog Code Security MCP | MCP Server | SAST + SCA + secrets + IaC |
| SAST MCP Tool | MCP Server | Bridge naar 15+ SAST tools |
| StackHawk | Externe service | DAST (dynamisch) |

## Bronnen

| Bron | Relevantie |
|------|------------|
| [Datadog Code Security MCP](https://docs.datadoghq.com/security/code_security/dev_tool_int/mcp_server/) | SAST/SCA integratie |
| [SAST MCP Tool](https://mcpmarket.com/server/sast) | Semgrep/Bandit/TruffleHog bridge |
| [Claude Code Security](https://www.penligent.ai/hackinglabs/claude-code-security-breaks-the-old-model-of-code-scanning/) | Ingebouwde vulnerability scanner |
| [StackHawk + Claude Code](https://www.stackhawk.com/blog/developers-guide-to-writing-secure-code-with-claude-code/) | DAST integratie |
| [40% Review Deficit 2026](https://www.qodo.ai/blog/best-automated-code-review-tools-2026/) | Urgentie-onderbouwing |
| [50+ MCP Servers voor Claude Code](https://claudefa.st/blog/tools/mcp-extensions/best-addons) | MCP ecosysteem overzicht |
| [Bounded Autonomy Framework](https://www.ewsolutions.com/agentic-ai-governance/) | Governance paradigma |
