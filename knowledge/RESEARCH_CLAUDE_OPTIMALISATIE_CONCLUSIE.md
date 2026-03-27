# Research Conclusie: Claude Code Optimalisatie

---
sprint: 31
type: RESEARCH
kennisgradering: SILVER
datum: 2026-03-27
bron: RESEARCH_VOORSTEL_CLAUDE_OPTIMALISATIE_2026-03-23
---

## Samenvatting

Dit document actualiseert het oorspronkelijke research-voorstel (2026-03-23) tegen de huidige staat van DevHub (Sprint 30, post-Fase 3). Van de 5 onderzoeksgebieden zijn 3 volledig geadresseerd door implementatie. De resterende 2 (Agent Teams, n8n automation) zijn gevalideerd als toekomstige actiepunten.

---

## Actualisatie: Gebouwd vs. Open

| Onderzoeksgebied | Status voorstel (23 mrt) | Status nu (27 mrt) | Conclusie |
|------------------|--------------------------|---------------------|-----------|
| Multi-Agent Architectuur | "Bouw reviewer, researcher, planner" | 7 plugin + 3 interne agents operationeel | **AFGEROND** |
| Agent Teams | "Experimenteel, relevant" | Niet geconfigureerd, nog steeds experimenteel | **GEPARKEERD** |
| n8n Integratie | "MCP tools beschikbaar, geen workflows" | Idem — tools beschikbaar, geen workflows | **OPEN** |
| Persistent Memory | "Drie strategieen combineren" | Auto-memory actief, CLAUDE.md gestructureerd | **AFGEROND** |
| Cowork Skills | "Direct benutten" | 10 eigen skills gebouwd, Cowork skills beschikbaar | **AFGEROND** |

---

## Antwoorden op Open Vragen

### OV1: Hoe integreren we Agent Teams met dev-lead/coder delegatie?

**Antwoord: Niet doen (nu).**

Agent Teams is experimenteel (vereist `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Het biedt peer-to-peer communicatie tussen Claude Code instanties, maar:

- DevHub's sequentiele pattern (orchestrator -> coder -> reviewer) is beter geschikt voor governance-workflows waar elke stap geaudit moet worden
- Agent Teams heeft geen session-resumption — na `/resume` zijn teammates verdwenen
- Token-overhead is significant (elk teammate heeft een eigen context window)
- DevHub's subagent-model (Explore, Plan agents) werkt al goed voor parallelle verkenning

**Aanbeveling:** Heroverweeg wanneer Agent Teams uit experimentele status komt. Sweet spot zou zijn: parallelle code review (security + performance + correctness reviewers tegelijk).

**Kennisgradering:** SILVER — gevalideerd tegen Anthropic docs en DevHub's architectuur.

### OV2: Welke n8n workflows moeten eerst gebouwd worden?

**Antwoord: Health check automation als eerste.**

Prioriteit-volgorde:

1. **Scheduled Health Check** — `scheduleTrigger` (dagelijks) -> DevHub health API -> rapportage
2. **GitHub Push Trigger** — `githubTrigger` bij push naar main -> governance-check -> alert bij BLOCK
3. **Sprint Status Dashboard** — periodieke SPRINT_TRACKER parse -> metrics rapportage

Concrete n8n MCP optimalisaties:
- Project-scoped `.mcp.json` met n8n stdio server configureren
- `MCP_TIMEOUT=10000` instellen voor langere health checks
- n8n webhooks als MCP channels overwegen (push naar Claude Code i.p.v. polling)

**Kennisgradering:** BRONZE — concrete plan, maar niet getest in DevHub context.

### OV3: Hoe structureren we persistent memory voor de researcher agent?

**Antwoord: Al opgelost door bestaande architectuur.**

De researcher agent schrijft naar `knowledge/{domain}/` als Markdown. De Knowledge Curator valideert voor vectorstore-ingestie. Auto-memory vangt terugkerende patronen op.

Optimalisatie-mogelijkheid:
- `.claude/rules/` gebruiken voor path-scoped instructies (nieuw feature)
- Rules laden alleen wanneer Claude bestanden in het matchende pad leest
- Voorbeeld: `governance.md` (DEV_CONSTITUTION regels) alleen laden bij compliance-werk

**Kennisgradering:** SILVER — werkende implementatie, gevalideerd over 30 sprints.

### OV4: engineering:code-review wrappen in reviewer agent?

**Antwoord: Al geimplementeerd.**

De `reviewer` agent (agents/reviewer.md) integreert:
- QA Agent Python checks (CR-01..12, DR-01..06)
- Anti-patroon scan
- Security checks
- Vijf-laags review model

De Cowork `engineering:code-review` skill is beschikbaar als aanvulling maar niet nodig als wrapper — de reviewer agent IS de geintegreerde review-capability.

**Kennisgradering:** SILVER — operationeel, gevalideerd in meerdere sprints.

---

## Nieuwe Inzichten (niet in oorspronkelijk voorstel)

### Path-scoped Rules
`.claude/rules/` ondersteunt frontmatter met `paths:` filter. Dit optimaliseert context-laden:
```yaml
---
paths:
  - "packages/devhub-core/**/*.py"
---
# Alleen laden bij devhub-core werk
```
**Actie:** Overweeg CLAUDE.md opsplitsen in modulaire rules.

### Hooks voor Quality Gates
`PostToolUse` hooks kunnen security-contracts automatisch triggeren na code-wijzigingen. `PreToolUse` hooks kunnen n8n workflow-deployments valideren.
**Actie:** Concrete hook-configuratie ontwerpen in toekomstige sprint.

### Scheduled Tasks
`/loop 5m <prompt>` voor periodieke health checks binnen sessies. Session-scoped (3 dagen max). Geen vervanging voor n8n maar nuttig voor ad-hoc monitoring.

---

## Actiepunten voor Toekomstige Sprints

| # | Actie | Prio | Fase | Size | Afhankelijkheid |
|---|-------|------|------|------|-----------------|
| A1 | n8n Health Check workflow bouwen | P2 | 4/5 | S | n8n Docker operationeel |
| A2 | Path-scoped rules opsplitsing | P3 | 4 | XS | Geen |
| A3 | PostToolUse hooks voor security gates | P3 | 4 | XS | Geen |
| A4 | Agent Teams heroverweging | P4 | 5+ | — | Feature uit experimenteel |

---

## Bronverantwoording

| Bron | Type | Kennisgradering |
|------|------|-----------------|
| Anthropic Claude Code Docs (Agent Teams, MCP, Memory) | Primaire bron | GOLD |
| DevHub codebase inventarisatie (Sprint 30) | Eigen systeem | GOLD |
| Oorspronkelijk research-voorstel (2026-03-23) | Cowork deep-dive | SILVER |
| Industry benchmarks multi-agent (2025-2026) | Externe bronnen | SILVER |

---

## Conclusie

DevHub benut Claude Code's mogelijkheden al op een hoog niveau. De oorspronkelijke kennislacune (BRONZE) is opgehoogd naar **SILVER**: 3 van 5 gebieden zijn volledig geimplementeerd, de overige 2 zijn bewust geparkeerd met concrete criteria voor heropening. De belangrijkste optimalisatie-mogelijkheden liggen in n8n workflow-automation en hooks — beide geschikt als Fase 4/5 sprints.
