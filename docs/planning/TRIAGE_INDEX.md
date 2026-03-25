# Triage Index — DevHub Planning Items

---
laatst_bijgewerkt: 2026-03-25
getriaged_door: "Claude Code — alsdan-devhub"
huidige_fase: 3 (Track A afgerond, Track B+C beschikbaar)
actieve_sprint: Planning Opschoning (CHORE, XS)
test_baseline: 395
---

## Fase-positie

`Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 2b ✅ → **Fase 3** 🔄`

Track A (uv workspace) is afgerond. Track B (storage) en Track C (vectorstore) zijn beschikbaar.

---

## Backlog (geshaped, klaar voor sprint)

_Leeg — alle items verplaatst naar sprints/ tijdens Planning Opschoning._

## Inbox (geshaped, wacht op promotie)

| # | Item | Bestand | Fase | Prio | Notitie |
|---|------|---------|------|------|---------|
| 1 | Storage Interface | `inbox/SPRINT_INTAKE_STORAGE_INTERFACE_2026-03-24.md` | 3 (Track B) | P2 | Geshaped. 3-4 sprints. READY, kan starten. |
| 2 | Vectorstore | `inbox/SPRINT_INTAKE_VECTORSTORE_2026-03-24.md` | 3 (Track C) | P2 | Geshaped. 2-3 sprints. Parallel met Track B. READY. |
| 3 | Mentor Supervisor Systeem | `inbox/SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM_2026-03-23.md` | 3 | P2 | Vereist KWP DEV operationeel. |
| 4 | Governance Automation | `inbox/SPRINT_INTAKE_GOVERNANCE_AUTOMATION_2026-03-25.md` | 3 | P3 | 7/16 governance + 4/10 security checks automatiseren. |
| 5 | Claude Optimalisatie Research | `inbox/RESEARCH_VOORSTEL_CLAUDE_OPTIMALISATIE_2026-03-23.md` | 2-3 | P3 | Achtergrond-research wanneer er ruimte is. |

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
Track A: UV Workspace ✅ (afgerond, 394 tests)
    ├── Operationele Validatie ✅ (alle 3 lagen bewezen, 395 tests)
    ├── Track B: Storage Interface (3-4 sprints, P2) ──┐
    ├── Track C: Vectorstore (2-3 sprints, P2) ────────┤── KWP DEV setup
    └── Code Check Architectuur (1 sprint, P3)          │
                                                        ├── Mentor Supervisor (2-3 sprints)
                                                        └── EVIDENCE-kopie
```

---

## Tellingen

| Categorie | Aantal |
|-----------|--------|
| Backlog | 0 |
| Inbox | 5 (+2 actief/afgerond) |
| Geparkeerd | 14 |
| Afgeronde sprints | 5 (+1 actief) |
| Gearchiveerde intakes | 10 |
| Test baseline | 395 |
