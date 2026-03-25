# SPRINT_FASE2_SKILLS_GOVERNANCE — DevHub Fase 2 Skills + Governance

| Veld | Waarde |
|------|--------|
| Status | AFGEROND |
| Startdatum | 2026-03-23 |
| Einddatum | 2026-03-23 |
| Baseline | 299 tests |
| Eindstand | 339 tests (+40) |
| Fase | 2 (Skills + Governance) |

---

## Doel

Fase 2 completeren: DevHub leert consistent en betrouwbaar werken. Skills voor research, governance en security. Golden Path templates voor gestandaardiseerde patronen.

## Deliverables

### D1 — Research-loop skill
- [x] `.claude/skills/devhub-research-loop/SKILL.md` — gestructureerde kennisverrijking
- [x] Integreert met researcher-agent memory
- [x] EVIDENCE-gradering in output

### D2 — Governance-check skill
- [x] `.claude/skills/devhub-governance-check/SKILL.md` — DEV_CONSTITUTION compliance audit
- [x] Toetst tegen alle 8 artikelen
- [x] Output: per artikel PASS/WARN/FAIL

### D3 — Golden Path templates (5x)
- [x] `docs/golden-paths/GREEN_ZONE_FEATURE.md`
- [x] `docs/golden-paths/YELLOW_ZONE_ARCHITECTURE.md`
- [x] `docs/golden-paths/SPRINT_RETROSPECTIVE.md`
- [x] `docs/golden-paths/SKILL_DEVELOPMENT.md`
- [x] `docs/golden-paths/KNOWLEDGE_ARTICLE.md`

### D4 — Red Team Agent + Security Skill
- [x] `agents/red-team.md` — OWASP ASI 2026 security audit agent
- [x] `.claude/skills/devhub-redteam/SKILL.md` — security audit skill
- [x] `devhub/contracts/security_contracts.py` — SecurityFinding, SecurityAuditReport (frozen dataclasses)
- [x] 295 tests voor security contracts

### D5 — Inbox vulling
- [x] 3 sprint intakes (code-check architectuur, red-team agent, mentor-supervisor)
- [x] 2 research voorstellen (zelfverbeterend systeem, Claude optimalisatie)

## Git Analyse

| Metric | Waarde |
|--------|--------|
| Commits | 2 |
| Files changed | 24 |
| Insertions | +3.229 |
| Deletions | -14 |
| Netto groei | +3.215 regels |

## Acceptatiecriteria

- [x] Research-loop skill operationeel
- [x] Governance-check skill operationeel
- [x] 5 Golden Path templates gedefinieerd en gevalideerd
- [x] Red-team agent + skill + security contracts operationeel
- [x] Tests geschreven en groen (339 totaal)
- [x] Bestaande 299 tests blijven groen

## Anti-patronen

- Geen wijzigingen in buurts-ecosysteem (BORIS impact: nee)
- Geen nieuwe architectuur — hergebruik bestaande structuren
- Inbox items als brug naar Fase 3
