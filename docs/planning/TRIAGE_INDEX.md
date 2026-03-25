# Triage Index — DevHub Planning Items

---
laatst_bijgewerkt: 2026-03-25
getriaged_door: "Claude Code — alsdan-devhub"
huidige_fase: 2 (afgerond) → Fase 3 start
actieve_sprint: CODE_CHECK_ARCHITECTUUR (afronding)
test_baseline: 394
---

## Backlog (geshaped, klaar voor sprint)

| # | Item | Fase | Prio | Afhankelijk van | Sprint-type | Notitie |
|---|------|------|------|-----------------|-------------|---------|
| 1 | SPRINT_INTAKE_N8N_HEALTH_CHECK | 2 | **P1** | Geen | FEAT | Basis voor alle n8n automatisering. Hoogste ROI. |
| 2 | SPRINT_INTAKE_N8N_GOVERNANCE_CHECK | 2 | P2 | #1 (Health Check) | FEAT | Post-merge DEV_CONSTITUTION validatie. |
| 3 | SPRINT_INTAKE_N8N_PR_QUALITY_GATE | 2 | P2 | #1 (Health Check) | FEAT | Pre-merge checks. Combineren met #2 in één sprint. |
| ~~4~~ | ~~SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR~~ | ~~2~~ | ~~P3~~ | — | ~~FEAT~~ | **AFGEROND** — ADR-002, pre-commit, reviewer upgrade, 24 tests |
| 5 | RESEARCH_VOORSTEL_MONOREPO_BUILD_SYSTEM_ANALYSE | 2-3 | P3 | Geen | RESEARCH | uv workspaces analyse — beslissing genomen. Intake is #21. |
| 21 | SPRINT_INTAKE_UV_WORKSPACE_TRANSITIE | 3 | **P1** | Geen | FEAT | Track A fundament. Blokkeert Track B + C. Eerste Fase 3 sprint. |

## Inbox (nog te shapen)

| # | Item | Fase | Notitie |
|---|------|------|---------|
| 6 | SPRINT_INTAKE_STORAGE_INTERFACE | 3 (Track B) | Geshaped. Geblokkeerd door Track A. |
| 7 | SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM | 2-3 | Goed geshaped maar vereist KWP DEV (Fase 3). |
| 8 | RESEARCH_VOORSTEL_CLAUDE_OPTIMALISATIE | 2-3 | Waardevol maar niet blokkerend. Kan parallel. |
| 20 | SPRINT_INTAKE_VECTORSTORE | 3 (Track C) | Geshaped. Geblokkeerd door Track A. Parallel met Track B. |

## Geparkeerd (buiten huidige fase)

| # | Item | Fase | Reden parkering |
|---|------|------|-----------------|
| 9 | IDEA_N8N_EXPERIMENT_LOOP_KARPATHY | 5 | Vereist Fase 1-4 stabiel. Verst weg. |
| 10 | IDEA_N8N_PROMPT_EVOLUTION_LOOP | 3-4 | Vereist KWP DEV + n8n foundation. |
| 11 | IDEA_N8N_SELF_HEALING_WORKFLOW | 3+ | Vereist bewezen n8n foundation. |
| 12 | IDEA_N8N_KNOWLEDGE_DECAY_SCAN | 3+ | Vereist KWP DEV operationeel. |
| 13 | IDEA_N8N_SPRINT_RETROSPECTIVE_LOOP | 3 | Vereist KWP DEV operationeel. |
| 14 | IDEA_N8N_SPRINT_PREP_SYNTHESE | 3 | Nice-to-have, geen kritiek pad. |
| 15 | RESEARCH_VOORSTEL_DEVHUB_MULTI_PROJECT_DATA_LAAG | 3-4 | Vereist monorepo-transitie + vectorstore. |
| 16 | RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM | 3-5 | Meta-systeem. Pas na Fase 3 stabiel. |
| 19 | IDEA_DEVHUB_MONOREPO_PANTS_STORAGE | 2-3 | Vervangen door #5 (monorepo) + #6 (storage). Origineel IDEA geparkeerd. |

## Afgerond / Verwerkt

| # | Item | Status | Notitie |
|---|------|--------|---------|
| 4 | SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR | AFGEROND | ADR-002, pre-commit hooks, reviewer upgrade, 24 E2E tests. 370→394 tests. |
| 17 | SPRINT_INTAKE_RED_TEAM_AGENT | AFGEROND | Sprint voltooid. 40 tests, red-team agent + skill operationeel. |
| 18 | IDEA_DEVHUB_ROADMAP | REFERENTIE | Blijft als strategisch ankerdocument. Niet verplaatsen. |
| — | SPRINT_N8N_CICD_FOUNDATION | AFGEROND | Hybride n8n + GH Actions CI/CD. 31 tests. 339→370 tests. |

## Duplicaten / Overlap (opgelost)

| Items | Overlap | Actie | Status |
|-------|---------|-------|--------|
| IDEA_N8N_HEALTH_CHECK_WORKFLOW + SPRINT_INTAKE_N8N_HEALTH_CHECK | Zelfde onderwerp | IDEA → parked/, intake is leidend | ✅ |
| IDEA_N8N_GOVERNANCE_CHECK_ON_MERGE + SPRINT_INTAKE_N8N_GOVERNANCE_CHECK | Zelfde onderwerp | IDEA → parked/, intake is leidend | ✅ |
| IDEA_N8N_PR_QUALITY_GATE + SPRINT_INTAKE_N8N_PR_QUALITY_GATE | Zelfde onderwerp | IDEA → parked/, intake is leidend | ✅ |
| IDEA_DEVHUB_MONOREPO_PANTS_STORAGE + RESEARCH_VOORSTEL_MONOREPO_BUILD_SYSTEM_ANALYSE | Monorepo + storage gecombineerd | IDEA opgesplitst: monorepo → research (#5), storage → intake (#6). IDEA → parked/. | ✅ |

## Samenvatting

- **Backlog:** 5 items (klaar voor sprint)
- **Inbox:** 4 items (nog te shapen of te promoveren)
- **Geparkeerd:** 12 items (buiten huidige fase of vervangen)
- **Afgerond:** 4 items
- **Duplicaten opgelost:** 4 paren
- **Totaal actief:** 11 items (was 21)
