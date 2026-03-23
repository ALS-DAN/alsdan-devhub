# RESEARCH_VOORSTEL_CLAUDE_OPTIMALISATIE_2026-03-23

---
gegenereerd_door: Cowork — alsdan-devhub
status: INBOX
fase: 1-2
---

## Kennislacune

- **Domein:** AI-engineering / development-methodiek
- **Gat:** DevHub benut nog niet het volledige spectrum aan Claude Code mogelijkheden (Agent Teams, plugin-ecosysteem, MCP-integraties, n8n-bridge). De huidige setup is solide maar operationeel beperkt tot 2 agents en 5 skills — terwijl het platform significant meer biedt.
- **Huidige grading:** BRONZE (bestaande setup werkt, maar niet gevalideerd tegen state-of-the-art)

## Onderzoeksvraag

**Hoe kan DevHub optimaal gebruik maken van Claude Code's plugin-ecosysteem, Agent Teams, MCP-servers en n8n-integratie om als development-systeem state-of-the-art te opereren?**

## Bevindingen (Cowork deep-dive, 2026-03-23)

### 1. Multi-Agent Architectuur

**Huidige staat:** Opus dev-lead → Sonnet coder delegatie. Dit is het bewezen orchestrator-worker pattern.

**Wat de industrie laat zien:**
- 90.2% betere resultaten op complexe taken versus single-agent systemen (bron: multi-agent benchmarks 2025-2026)
- "Bounded autonomy" is het leidende governance-paradigma van 2026: agents opereren zelfstandig binnen gedefinieerde grenzen, met verplichte escalatie voor high-stakes beslissingen
- 40% kwaliteitsdeficit verwacht in 2026: code-productie groeit exponentieel door AI, maar review-capaciteit blijft lineair

**Aanbeveling voor DevHub:**
- Fase 1: Bouw reviewer, researcher, planner agents → completeert het team
- De reviewer is het meest urgent vanwege het review-deficit probleem

**Kennisgradering:** SILVER — breed gevalideerd in enterprise, DevHub's DEV_CONSTITUTION past bounded autonomy al toe

### 2. Agent Teams (experimenteel)

**Wat het is:** Meerdere Claude Code instanties die parallel werken met eigen context windows, gecoördineerd via TeammateTool. Beschikbaar via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` setting.

**Relevantie voor DevHub:**
- Reviewer + Coder als onafhankelijke teammates (gescheiden contexten → betere resultaten)
- Parallelle research: meerdere researchers die verschillende aspecten tegelijk onderzoeken
- Cross-layer coördinatie: frontend/backend/tests door aparte agents
- Sweet spot: 5-6 taken per teammate met duidelijk file-ownership

**Kennisgradering:** SPECULATIVE — experimentele feature, geen productie-bewijs in vergelijkbare setups

### 3. n8n-integratie

**Beschikbare MCP-tools (geverifieerd):**
- `mcp__n8n__search_nodes` — 1.239 workflow-nodes doorzoekbaar
- `mcp__n8n__search_templates` — 1.240+ templates beschikbaar
- `mcp__n8n__validate_workflow` — workflow-validatie
- `mcp__n8n__validate_node` — node-configuratie validatie
- `mcp__n8n__get_template` — template ophalen

**Relevante n8n-nodes (geverifieerd):**
- `scheduleTrigger` / `cron` — periodieke triggers
- `githubTrigger` — start bij push/PR events
- `GitHub` node + `GitHub Tool` (AI Agent variant) — repo-interactie
- `GitHub Document Loader` — repository-inhoud laden

**Concrete toepassingen:**
- Geautomatiseerde health checks via scheduled workflows → rapportage
- Sprint lifecycle automation: notificaties, statusupdates, dependency checks
- CI/CD integratie: test-resultaten, deployment status, security scans
- Monitoring & alerting: code quality metrics, test coverage trends

**Kennisgradering:** BRONZE — volwassen extern ecosysteem, niet getest in onze context

### 4. Persistent Memory

**Drie strategieën die samen het beste resultaat geven:**

| Strategie | Tool | Toepassing |
|-----------|------|------------|
| Project-geheugen | CLAUDE.md + .claude/rules/ | Architectuur, conventies, routing |
| Auto-memory | Ingebouwd | Correcties, voorkeuren, feedback |
| Structured knowledge | Basic Memory / Claude-Mem plugin | KWP DEV, EVIDENCE-opslag |

**Best practice:** CLAUDE.md onder 200 regels houden, verwijzen naar aparte bestanden. Huidige CLAUDE.md is goed ingericht.

**Kennisgradering:** SILVER — Anthropic-gedocumenteerd, breed geadopteerd

### 5. Beschikbare Cowork Skills (geverifieerd)

DevHub kan deze skills direct benutten vanuit Cowork:

| Skill | Toepassing in DevHub |
|-------|---------------------|
| `engineering:code-review` | Diepte-review op security, performance, correctness |
| `engineering:testing-strategy` | Teststrategie per sprint/feature |
| `engineering:tech-debt` | Tech debt audit en prioritering |
| `engineering:architecture` | ADR evaluatie en creatie |
| `engineering:system-design` | Systeemontwerp voor nieuwe componenten |
| `engineering:debug` | Gestructureerde debugging |
| `engineering:documentation` | Technische documentatie |
| `product-management:sprint-planning` | Sprint planning ondersteuning |
| `product-management:write-spec` | Feature specs / PRDs |

## Bronnen

| Bron | Type | Relevantie |
|------|------|------------|
| [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams) | Anthropic docs | Agent Teams setup |
| [Claude Code Memory System](https://code.claude.com/docs/en/memory) | Anthropic docs | Persistent memory |
| [90% Performance Gain with Subagents](https://www.codewithseb.com/blog/claude-code-sub-agents-multi-agent-systems-guide) | Blog | Multi-agent benchmarks |
| [Swarm Orchestration Skill](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea) | GitHub Gist | TeammateTool referentie |
| [n8n-MCP for Claude Code](https://github.com/czlonkowski/n8n-mcp) | GitHub | n8n integratie |
| [Claude Code Monitoring Guide](https://github.com/anthropics/claude-code-monitoring-guide) | Anthropic | Monitoring best practices |
| [Bounded Autonomy Framework](https://www.ewsolutions.com/agentic-ai-governance/) | Industry | Governance paradigma |
| [40% Code Review Deficit](https://www.qodo.ai/blog/best-automated-code-review-tools-2026/) | Industry | Review-capaciteit probleem |
| [WEF: AI Agent Governance](https://www.weforum.org/stories/2026/03/ai-agent-autonomy-governance/) | WEF | Enterprise governance |

## Evidence Doel

- **Grade:** SILVER (gevalideerd in tenminste 1 sprint)
- **Vereist:** Implementatie van Fase 1 agents + meting van effectiviteit over 1 sprint

## Prioriteit

- **Fase:** 1-2
- **Kritiek pad:** JA — de Fase 1 agents (reviewer, researcher, planner) zijn direct afhankelijk van deze inzichten
- **Motivatie:** Zonder deze optimalisatie bouwt DevHub agents die het platform suboptimaal benutten

## Open Vragen voor Claude Code

1. Hoe integreren we Agent Teams met de bestaande dev-lead → coder delegatie? Vervangt het de subagent-flow of werken ze naast elkaar?
2. Welke n8n-workflows moeten eerst gebouwd worden om de health check skill te automatiseren?
3. Hoe structureren we persistent memory voor de researcher agent zodat kennis accumuleert over sprints?
4. Is er een manier om de engineering:code-review skill te wrappen in de reviewer agent zodat hij als skill EN als agent beschikbaar is?
