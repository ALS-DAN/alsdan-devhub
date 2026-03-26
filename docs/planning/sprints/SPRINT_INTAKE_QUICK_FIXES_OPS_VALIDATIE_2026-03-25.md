# Sprint Intake: Quick Fixes Operationele Validatie

---
gegenereerd_door: "Sprint Operationele Validatie"
status: DONE
fase: 3
prioriteit: P2
sprint_type: CHORE
cynefin: obvious
impact_zone: GREEN (kleine fixes, geen architectuurwijzigingen)
bron: docs/planning/sprints/SPRINT_OPERATIONELE_VALIDATIE.md
---

## Doel

Repareer de 6 quick-fix gaps uit de Operationele Validatie sprint. Allemaal < 30 min, geen shaping nodig.

## Deliverables

### n8n fixes
- [x] **QF-01** — WF-1 activeren via API — was al actief (id: 5wFpIb8g8xDAcdMD)
- [x] **QF-02** — 3 archived duplicate WF-1 workflows verwijderd via DELETE API
- [x] **QF-03** — `check_n8n_status()` port configureerbaar via `N8N_PORT` env var (default 5678)

### Python runtime fixes
- [x] **QF-04** — `pip install pip-audit` in BORIS .venv (v2.10.0)
- [x] **QF-05** — Docs gemarkeerd: `run_tests()` retourneert `TestResult` dataclass (skills/ADR waren al correct)

### Python runtime fix (aanvullend)
- [x] **QF-06** — `_build_report_from_externals()` roept nu `run_tests()` aan als fallback voor test_count

## Afhankelijkheden

- Geblokkeerd door: geen
- BORIS impact: QF-03 wijzigt BorisAdapter, QF-04 wijzigt BORIS venv, QF-06 raakt BorisAdapter get_report()
- n8n impact: QF-01/02 wijzigen n8n workflows

## Open vragen Claude Code

- QF-06: Is het LUMEN report-pad correct geconfigureerd? Moet de fallback-logica een alternatieve bron raadplegen of is het pad-probleem de root cause?

## Appetite

**Extra Small (XS)** — maximaal 1,5 uur totaal (was 1 uur; QF-06 voegt ~20 min toe).
