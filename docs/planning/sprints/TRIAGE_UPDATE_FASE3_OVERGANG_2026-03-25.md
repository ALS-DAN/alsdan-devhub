# TRIAGE UPDATE — Fase 3 Overgang (v2, gecorrigeerd)

> Gegenereerd door: Cowork — alsdan-devhub
> Datum: 2026-03-25
> Status: INBOX — instructie voor CHORE-sprint
> Aanleiding: Administratie achtergebleven bij werkelijkheid. Schone Fase 3 start nodig.

---

## Zekerheidsgradering (Art. 2)

| Claim | Gradering | Bron |
|-------|-----------|------|
| Fase 0-2 compleet | Geverifieerd | `sprints/` + TRIAGE_INDEX update door Claude Code |
| Code Check Architectuur afgerond | Geverifieerd | TRIAGE_INDEX: ADR-002, pre-commit, reviewer upgrade, 24 tests |
| UV Workspace Transitie uitgevoerd | Geverifieerd | Claude Code melding + TRIAGE_INDEX update |
| N8N CI/CD + Docker Fix afgerond | Aangenomen | Niels-bevestiging + sprint-doc AFGEROND |
| Test baseline = 394 | Geverifieerd | TRIAGE_INDEX door Claude Code: 370→394 (+24 code check) |
| DEVHUB_BRIEF verouderd (307 tests, Fase 2b) | Geverifieerd | Claude Code rapportage |

---

## Afgeronde sprints (geverifieerd)

| Sprint | Fase | Tests | Datum |
|--------|------|-------|-------|
| SPRINT_FASE1_BOOTSTRAP | 1 | 218 → 299 (+81) | 2026-03-23 |
| SPRINT_FASE2_SKILLS_GOVERNANCE | 2 | 299 → 339 (+40) | 2026-03-23 |
| SPRINT_N8N_CICD_FOUNDATION | 2→3 | 339 → 370 (+31) | 2026-03-24/25 |
| SPRINT_CODE_CHECK_ARCHITECTUUR | 2 | 370 → 394 (+24) | 2026-03-25 |
| UV Workspace Transitie (Track A) | 3 | — (herstructurering) | 2026-03-25 |

**Huidige baseline: 394 tests | Fase: 3 (Track A afgerond)**

---

## Huidige positie

```
Fase 0 ✅ → Fase 1 ✅ → Fase 2 ✅ → Fase 2b ✅ → Fase 3 🔄
                                                    └─ Track A ✅ (UV Workspace)
                                                    ├─ Track B ⏳ (Storage Interface — NIET MEER GEBLOKKEERD)
                                                    └─ Track C ⏳ (Vectorstore — NIET MEER GEBLOKKEERD)
```

---

## CHORE-sprint: Planning Opschoning

Claude Code heeft een 6-fasen CHORE-sprint voorgesteld. Cowork onderschrijft dit:

**Type:** CHORE | **Impact:** GREEN | **Appetite:** S (klein)

### Fase 1: Bestandsverplaatsingen (9 moves)

**Inbox → sprints/** (afgerond werk):
1. `SPRINT_INTAKE_RED_TEAM_AGENT_2026-03-23.md`
2. `SPRINT_INTAKE_N8N_DOCKER_FIX_2026-03-25.md`

**Inbox → parked/** (referentie):
3. `IDEA_DEVHUB_ROADMAP_2026-03-23.md`

**Backlog → sprints/** (afgerond werk):
4. `SPRINT_INTAKE_N8N_HEALTH_CHECK_2026-03-24.md`
5. `SPRINT_INTAKE_N8N_GOVERNANCE_CHECK_2026-03-24.md`
6. `SPRINT_INTAKE_N8N_PR_QUALITY_GATE_2026-03-24.md`
7. `SPRINT_INTAKE_UV_WORKSPACE_TRANSITIE_2026-03-24.md`

**Backlog → parked/** (research compleet):
8. `RESEARCH_VOORSTEL_MONOREPO_BUILD_SYSTEM_ANALYSE_2026-03-24.md`

**Inbox → sprints/** (dit document zelf na verwerking):
9. `TRIAGE_UPDATE_FASE3_OVERGANG_2026-03-25.md`

### Fase 2-5: Skill/agent/docs updates

Zie Claude Code voorstel — sprint-prep skill, planner agent, TRIAGE_INDEX, DEVHUB_BRIEF, ROADMAP.

### Fase 6: Verificatie

394 tests groen + bestandstellingen matchen.

---

## Na opschoning — actieve items

### Backlog (2 items)

| # | Item | Fase | Prio | Status |
|---|------|------|------|--------|
| 1 | SPRINT_INTAKE_PLANNING_GOVERNANCE | 2 (restwerk) | P2 | 5/10 done, wordt afgerond in CHORE-sprint |
| 2 | (leeg na opschoning) | — | — | — |

### Inbox (4 items — allemaal Fase 3)

| # | Item | Fase | Prio | Geblokkeerd door |
|---|------|------|------|------------------|
| 1 | SPRINT_INTAKE_STORAGE_INTERFACE | 3 Track B | P2 | **Niets meer** (Track A afgerond) |
| 2 | SPRINT_INTAKE_VECTORSTORE | 3 Track C | P2 | **Niets meer** (Track A afgerond) |
| 3 | SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM | 3 | P3 | KWP DEV setup |
| 4 | RESEARCH_VOORSTEL_CLAUDE_OPTIMALISATIE | 2-3 | P3 | Niets |

### Parked (14 items na opschoning)

12 origineel + 2 nieuw (IDEA_DEVHUB_ROADMAP, MONOREPO_RESEARCH).

---

## Kritiek pad na opschoning

```
CHORE: Planning Opschoning (nu)
    │
    ├── Track B: Storage Interface (3-4 sprints, P2) ──┐
    ├── Track C: Vectorstore (2-3 sprints, P2) ────────┤── KWP DEV setup
    │                                                   │
    │                                                   ├── Mentor Supervisor
    │                                                   └── EVIDENCE-kopie
    └── Claude Optimalisatie (achtergrond, wanneer ruimte)
```

**Belangrijk:** Track B en C zijn niet meer geblokkeerd. Na de CHORE-sprint kan de eerste echte Fase 3 feature-sprint direct starten.

---

## Tellingen na opschoning

| Categorie | Aantal |
|-----------|--------|
| Afgeronde sprints | 5+ |
| Backlog | 1 (wordt opgeruimd in CHORE) |
| Inbox | 4 |
| Parked | 14 |
| Test baseline | 394 |
