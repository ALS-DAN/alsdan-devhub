# DevHub Sessiebriefing
_Levend document — bijgewerkt door Claude Code bij elke sprint-afsluiting._
_Bijgewerkt: 2026-03-24 | sprint: RED_TEAM_AGENT_

---

## Actieve sprint

| Sprint | Status | Tests |
|--------|--------|-------|
| RED_TEAM_AGENT | actief | 307 tests (startpunt) |

**Vorige sprint:** DEVHUB_FASE2_SKILLS_GOVERNANCE ✅ (2026-03-24) — +8 tests

**Fase-positie:**
`Fase 0 (fundament) ✅ → Fase 1 (kernagents + infra) ✅ → Fase 2 (skills + governance) ✅ → **Fase 2b (red team)** 🔄 → Fase 3 (knowledge + memory) 🔲`

---

## Agent-status

| Agent | Definitie | Memory | Status |
|-------|-----------|--------|--------|
| dev-lead | `agents/dev-lead.md` | `.claude/agent-memory/dev-lead/` | operationeel |
| coder | `agents/coder.md` | `.claude/agent-memory/coder/` | operationeel |
| reviewer | `agents/reviewer.md` | `.claude/agent-memory/reviewer/` | operationeel |
| researcher | `agents/researcher.md` | `.claude/agent-memory/researcher/` | operationeel |
| planner | `agents/planner.md` | `.claude/agent-memory/planner/` | operationeel |
| red-team | `agents/red-team.md` | — | operationeel |

---

## Plugin-status

| Component | Status |
|-----------|--------|
| plugin.json | ✅ v0.1.0 |
| DEV_CONSTITUTION | ✅ v1.0 (8 artikelen) |
| BorisAdapter | ✅ 38 methodes |
| NodeRegistry | ✅ boris-buurts geregistreerd |
| Python tests | ✅ 218 passed |
| Plugin-laag tests | ✅ 81 passed |

---

## Skills

| Skill | Pad | Gevalideerd |
|-------|-----|-------------|
| devhub-sprint | `.claude/skills/devhub-sprint/` | ✅ |
| devhub-health | `.claude/skills/devhub-health/` | ✅ |
| devhub-mentor | `.claude/skills/devhub-mentor/` | ✅ |
| devhub-review | `.claude/skills/devhub-review/` | ✅ |
| devhub-sprint-prep | `.claude/skills/devhub-sprint-prep/` | ✅ |
| devhub-research-loop | `.claude/skills/devhub-research-loop/` | ✅ Fase 2 |
| devhub-governance-check | `.claude/skills/devhub-governance-check/` | ✅ Fase 2 |
| devhub-redteam | `.claude/skills/devhub-redteam/` | ✅ Fase 2b |

---

## Golden Paths

| Template | Pad |
|----------|-----|
| GREEN Zone Feature | `docs/golden-paths/GREEN_ZONE_FEATURE.md` |
| YELLOW Zone Architectuur | `docs/golden-paths/YELLOW_ZONE_ARCHITECTURE.md` |
| Skill Development | `docs/golden-paths/SKILL_DEVELOPMENT.md` |
| Knowledge Article | `docs/golden-paths/KNOWLEDGE_ARTICLE.md` |
| Sprint Retrospective | `docs/golden-paths/SPRINT_RETROSPECTIVE.md` |

---

## Open beslissingen

_Geen open beslissingen._

---

## Planning Notes voor Cowork

- RED_TEAM_AGENT sprint actief: security contracts, red team agent, devhub-redteam skill
- OWASP ASI 2026 framework geïmplementeerd als Python contracts
- DeepTeam integratie uitgesteld naar volgende sprint

---

## Sinds vorige sessie

- Fase 2 volledig afgerond (7 skills, 307 tests, 5 Golden Paths)
- RED_TEAM_AGENT sprint: security_contracts.py, red-team agent, devhub-redteam skill
- 6 agents operationeel (dev-lead, coder, reviewer, researcher, planner, red-team)
- Tests: 307 → 339 (+32)

---

## Aanbevolen startpunt volgende sessie

DeepTeam integratie (externe red team tooling) of Fase 3: knowledge + memory
