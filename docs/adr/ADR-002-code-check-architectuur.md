# ADR-002: Vijf-lagen Code Check Architectuur

| Veld | Waarde |
|------|--------|
| Status | Accepted |
| Datum | 2026-03-25 |
| Context | Sprint: Code Check Architectuur |
| Impact-zone | YELLOW (nieuwe tooling + agent upgrade) |

## Context

DevHub heeft sterke individuele check-componenten (QA Agent met 18 checks, devhub-review skill, CI/CD workflows via ADR-001, red-team agent met OWASP ASI) maar mist een geformaliseerd model dat duidelijk maakt welke check wanneer draait en wie verantwoordelijk is. Dit leidt tot ad-hoc inzet van tooling.

De industrie verwacht in 2026 een 40% kwaliteitsdeficit: AI-gegenereerde code groeit sneller dan review-capaciteit. Een gelaagd model maakt systematische kwaliteitsborging mogelijk.

## Beslissing

Vijf check-lagen, elk met een duidelijke trigger, verantwoordelijke en toolset.

### Laag A — Preventie (vóór code geschreven wordt)

| Component | Bron | Status |
|-----------|------|--------|
| DoR checklist (8 punten) | devhub-sprint-prep skill | Operationeel |
| Impact-zonering (GREEN/YELLOW/RED) | DEV_CONSTITUTION Art. 7 | Operationeel |
| Testing strategy | engineering:testing-strategy skill | Beschikbaar |

**Trigger:** Sprint-start, taak-decompositie
**Verantwoordelijke:** dev-lead agent

### Laag B — Realtime (tijdens het schrijven)

| Component | Bron | Status |
|-----------|------|--------|
| Coder agent CLAUDE.md constraints | agents/coder.md | Operationeel |
| Pre-commit hooks (ruff, detect-secrets) | .pre-commit-config.yaml | Nieuw (devhub root) |
| Claude Code Security (ingebouwd) | Anthropic | Beschikbaar |
| Conventional commits | pre-commit hook | Nieuw |

**Trigger:** Elke commit
**Verantwoordelijke:** coder agent + git hooks

### Laag C — Review (na implementatie)

| Component | Bron | Status |
|-----------|------|--------|
| QA Agent (CR-01..12, DR-01..06) | devhub_core/agents/qa_agent.py | Operationeel |
| devhub-review skill | .claude/skills/devhub-review/ | Operationeel |
| Anti-patroon scan (node-specifiek) | BorisAdapter | Operationeel |

**Trigger:** Review-verzoek van dev-lead
**Verantwoordelijke:** reviewer agent (orkestrator)

### Laag D — Systeem (periodiek / CI)

| Component | Bron | Status |
|-----------|------|--------|
| PR Quality Gate | .github/workflows/pr-quality-gate.yml | Operationeel |
| Governance Check | .github/workflows/governance-check.yml | Operationeel |
| devhub-health skill (6 dimensies) | .claude/skills/devhub-health/ | Operationeel |
| pip-audit (CVE scan) | CI workflow | Operationeel |
| n8n Health Check | n8n/workflows/ | Gepland |

**Trigger:** PR open/sync, push naar main, dagelijks schedule
**Verantwoordelijke:** GitHub Actions + n8n

### Laag E — Security (on-demand)

| Component | Bron | Status |
|-----------|------|--------|
| OWASP ASI 2026 audit (10 risico's) | red-team agent | Operationeel |
| Kill chain analyse (7 stappen) | red-team agent | Operationeel |
| Bandit (SAST) | pre-commit hook | Nieuw |
| detect-secrets (industrieniveau) | pre-commit hook | Nieuw |

**Trigger:** Sprint-closure, security concern, fase-transitie
**Verantwoordelijke:** red-team agent

## Orchestratie

```
dev-lead → reviewer agent (Laag C)
                ↓ roept aan
           QA Agent (18 checks)
           devhub-review skill
           anti-patroon scan
                ↓ produceert
           QAReport (PASS/NEEDS_WORK/BLOCK)
                ↓ escaleert bij BLOCK
           Niels (RED-zone, Art. 7)
```

De reviewer agent is de centrale orkestrator voor Laag C. Lagen A, B, D en E opereren onafhankelijk met eigen triggers.

## Overwogen alternatieven

### Alternatief A: Één mega-agent die alles orkestreert
- **Con:** Te complex, single point of failure, moeilijk te testen
- **Con:** Conflicteert met bestaande trigger-modellen (CI events, cron, handmatig)

### Alternatief B: Geen formeel model, ad-hoc tooling
- **Con:** Huidige situatie — tooling wordt niet systematisch ingezet
- **Con:** Geen duidelijke verantwoordelijkheden

### Alternatief C: Vijf-lagen model (gekozen)
- **Pro:** Elke laag heeft eigen trigger, verantwoordelijke en scope
- **Pro:** Bestaande tooling past 1:1 in het model
- **Pro:** Onafhankelijke lagen — uitval in één laag blokkeert anderen niet

## Consequenties

- Pre-commit hooks worden toegevoegd aan devhub root (.pre-commit-config.yaml)
- Reviewer agent wordt geüpgraded naar Opus met 5-lagen bewustzijn
- Bandit wordt toegevoegd voor SAST in pre-commit
- SAST MCP integratie wordt geparkeerd tot er een betrouwbare gratis optie is
- Elke sprint-closure activeert minimaal Laag C (reviewer) + Laag E (red-team)
