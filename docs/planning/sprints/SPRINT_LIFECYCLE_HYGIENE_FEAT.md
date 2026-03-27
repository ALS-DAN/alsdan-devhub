# Sprint 27: FEAT Lifecycle Hygiene — Afronding & Verificatie

---
sprint: 27
type: FEAT
node: devhub
status: DONE
datum: 2026-03-27
test_baseline_voor: 1156
test_baseline_na: 1156
test_delta: 0
---

## Doel

Afronding en verificatie van de Sprint Lifecycle Hygiene implementatie (Sprint 25 SPIKE + Sprint 26 FEAT). Alle resterende FASE3_TRACKER referenties verwijderen, SPRINT_TRACKER inconsistenties fixen, en nieuw inbox-item registreren.

## Context

Sprint 25 (SPIKE) analyseerde 4 structurele lifecycle-problemen en stelde 6 migratiestappen voor. Sprint 26 (FEAT) implementeerde deze in commit 9c49022. Bij verificatie bleken 6 residuele FASE3_TRACKER referenties over het hoofd gezien in actieve skills/agents, en de SPRINT_TRACKER had een header-inconsistentie.

## Uitgevoerd

### 1. FASE3_TRACKER → SPRINT_TRACKER referenties (6 fixes)

| Bestand | Regel | Fix |
|---------|-------|-----|
| `.claude/skills/devhub-sprint/SKILL.md` | 69 | 0F stap-naam |
| `.claude/skills/devhub-sprint/SKILL.md` | 200 | 6E stap-naam |
| `.claude/skills/devhub-sprint-prep/SKILL.md` | 5 | Changelog |
| `.claude/skills/devhub-sprint-prep/SKILL.md` | 163 | Sectie-header |
| `agents/planner.md` | 181 | Scan-lijst |
| `docs/golden-paths/GROWTH_REPORT.md` | 92 | Bronverwijzing |

### 2. SPRINT_TRACKER inconsistenties

- Header "sprint 26 actief" → "sprint 27 actief" (Sprint 26 was reeds DONE in golf-tabel)
- Cycle time entry Sprint 26 FEAT toegevoegd
- Sprint 27 als Golf 4 actieve sprint toegevoegd

### 3. TRIAGE_INDEX

- Nieuw inbox-item geregistreerd: IDEA_PROVIDER_PATTERN_ADAPTER_SCHEIDING (P2, Fase 3)

### 4. Verificatie

- **Tests:** 1156 passed, 2 skipped — geen regressie
- **Grep FASE3_TRACKER:** 0 hits in `.claude/skills/` en `agents/` — volledig opgeruimd
- Historische bestanden (SPIKE, archief) bewust ongemoeid gelaten

## Impact

- **Alle actieve skills en agents** refereren nu consistent naar `SPRINT_TRACKER.md`
- **Fase-overgangen** vereisen voortaan geen file-renames meer in skills/agents
- **Sprint-close flow v2** is operationeel: intake-archivering, conditionele HERALD, SPRINT_TRACKER als SSoT
- **Inbox** is actueel: 4 items met `status: INBOX`, alle afgehandelde intakes gearchiveerd

## Bestanden gewijzigd

- `.claude/skills/devhub-sprint/SKILL.md`
- `.claude/skills/devhub-sprint-prep/SKILL.md`
- `agents/planner.md`
- `docs/golden-paths/GROWTH_REPORT.md`
- `docs/planning/SPRINT_TRACKER.md`
- `docs/planning/TRIAGE_INDEX.md`
