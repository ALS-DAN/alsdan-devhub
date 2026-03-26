# Triage Index — DevHub Planning Items

---
laatst_bijgewerkt: 2026-03-26
getriaged_door: "Claude Code — alsdan-devhub"
huidige_fase: 3 (Track A+B S1+C S1 afgerond, Golf 1 actief)
actieve_sprint: — (geen actieve sprint)
test_baseline: 575
---

## Fase-positie

`Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 2b ✅ → **Fase 3** 🔄`

Track A (uv workspace), Track B S1 (storage) en Track C S1 (vectorstore) zijn afgerond. Golf 1 actief.

---

## Backlog (geshaped, klaar voor sprint)

_Leeg — alle items verplaatst naar sprints/ tijdens Planning Opschoning._

## Inbox (geshaped, wacht op promotie)

| # | Item | Bestand | Fase | Prio | Notitie |
|---|------|---------|------|------|---------|
| 1 | Mentor Supervisor Systeem | `inbox/SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM_2026-03-23.md` | 3 | P2 | Geshaped. Skill Radar + Growth Contracts. READY. |
| 2 | Governance Automation | `inbox/SPRINT_INTAKE_GOVERNANCE_AUTOMATION_2026-03-25.md` | 3 | P2 | 7/16 governance + 4/10 security checks automatiseren. READY. |
| 3 | Claude Optimalisatie Research | `inbox/RESEARCH_VOORSTEL_CLAUDE_OPTIMALISATIE_2026-03-23.md` | 2-3 | P3 | Achtergrond-research wanneer er ruimte is. |

## Geparkeerd (buiten huidige fase)

| # | Item | Bestand | Reden |
|---|------|---------|-------|
| 7 | IDEA_N8N_EXPERIMENT_LOOP_KARPATHY | `parked/` | Fase 5, verst weg |
| 8 | IDEA_N8N_PROMPT_EVOLUTION_LOOP | `parked/` | Vereist KWP DEV + n8n |
| 9 | IDEA_N8N_SELF_HEALING_WORKFLOW | `parked/` | Vereist bewezen n8n foundation |
| 10 | IDEA_N8N_KNOWLEDGE_DECAY_SCAN | `parked/` | Vereist KWP DEV |
| 11 | IDEA_N8N_SPRINT_RETROSPECTIVE_LOOP | `parked/` | Vereist KWP DEV |
| 12 | IDEA_N8N_SPRINT_PREP_SYNTHESE | `parked/` | Nice-to-have |
| 13 | RESEARCH_DEVHUB_MULTI_PROJECT_DATA_LAAG | `parked/` | Vereist monorepo + vectorstore |
| 14 | RESEARCH_ZELFVERBETEREND_SYSTEEM | `parked/` | Meta-systeem, pas na Fase 3 |
| 15 | IDEA_DEVHUB_MONOREPO_PANTS_STORAGE | `parked/` | Vervangen door uv workspace + storage intake |
| 16 | IDEA_N8N_HEALTH_CHECK_WORKFLOW | `parked/` | Duplicaat, intake afgerond |
| 17 | IDEA_N8N_GOVERNANCE_CHECK_ON_MERGE | `parked/` | Duplicaat, intake afgerond |
| 18 | IDEA_N8N_PR_QUALITY_GATE | `parked/` | Duplicaat, intake afgerond |
| 19 | IDEA_DEVHUB_ROADMAP | `parked/` | Referentiedocument |
| 20 | RESEARCH_MONOREPO_BUILD_SYSTEM_ANALYSE | `parked/` | Beslissing genomen: uv workspaces |

## Afgeronde sprints

| Sprint | Fase | Tests | Datum |
|--------|------|-------|-------|
| SPRINT_FASE1_BOOTSTRAP | 1 | 218 → 299 (+81) | 2026-03-23 |
| SPRINT_FASE2_SKILLS_GOVERNANCE | 2 | 299 → 339 (+40) | 2026-03-23 |
| SPRINT_N8N_CICD_FOUNDATION | 2→3 | 339 → 370 (+31) | 2026-03-24/25 |
| SPRINT_CODE_CHECK_ARCHITECTUUR | 2→3 | 370 → 394 (+24) | 2026-03-25 |
| SPRINT_OPERATIONELE_VALIDATIE | 3 | 394 → 395 (+1) | 2026-03-25 |
| Quick Fixes Ops Validatie | 3 | 395 → 397 (+2) | 2026-03-26 |
| Planning Opschoning | 3 | 397 → 397 (+0) | 2026-03-26 |
| Storage Interface + LocalAdapter | 3 (B) | 397 → 497 (+100) | 2026-03-26 |
| Vectorstore Interface + ChromaDB | 3 (C) | 497 → 575 (+78) | 2026-03-26 |
| Planning & Tracking Systeem | 3 | 575 → 575 (+0) | 2026-03-26 |
| Mentor: Skill Radar + Contracts | 3 (M) | 575 → 611 (+36) | 2026-03-26 |
| Governance: QA Checks | 3 (G) | 611 → 662 (+51) | 2026-03-26 |

Gearchiveerde intakes in `sprints/`:
- SPRINT_INTAKE_RED_TEAM_AGENT (operationeel: agent + skill + 40 tests)
- SPRINT_INTAKE_N8N_DOCKER_FIX (Niels bevestigd afgerond)
- SPRINT_INTAKE_N8N_HEALTH_CHECK (geleverd in N8N CICD sprint)
- SPRINT_INTAKE_N8N_GOVERNANCE_CHECK (geleverd in N8N CICD sprint)
- SPRINT_INTAKE_N8N_PR_QUALITY_GATE (geleverd in N8N CICD sprint)
- SPRINT_INTAKE_UV_WORKSPACE_TRANSITIE (Track A afgerond, 394 tests)
- SPRINT_INTAKE_CODE_CHECK_ARCHITECTUUR (5-laags code check afgerond)
- SPRINT_INTAKE_PLANNING_GOVERNANCE (10/10 deliverables afgerond)
- SPRINT_INTAKE_OPERATIONELE_VALIDATIE (alle 3 lagen bewezen, 395 tests)
- TRIAGE_UPDATE_FASE3_OVERGANG (transitiedocument)

---

## Kritiek pad Fase 3

```
Track A: UV Workspace ✅ (394 tests)
    ├── Operationele Validatie ✅ (395 tests)
    ├── Track B S1: Storage Interface ✅ (497 tests) ── Track B S2: Google Drive ──┐
    ├── Track C S1: Vectorstore ✅ (575 tests) ──────── Track C S2: Weaviate ──────┤── KWP DEV setup
    ├── Planning & Tracking ✅ (575 tests)                                          │
    └── Code Check Architectuur ✅                                                 ├── Mentor Supervisor
                                                                                   └── EVIDENCE-kopie
```

---

## Tellingen

| Categorie | Aantal |
|-----------|--------|
| Backlog | 0 |
| Inbox | 3 |
| Geparkeerd | 14 |
| Afgeronde sprints | 13 |
| Gearchiveerde intakes | 10 |
| Test baseline | 662 |
