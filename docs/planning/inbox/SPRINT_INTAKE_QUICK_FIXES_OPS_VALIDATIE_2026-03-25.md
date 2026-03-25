# Sprint Intake: Quick Fixes Operationele Validatie

---
gegenereerd_door: "Sprint Operationele Validatie"
status: INBOX
fase: 3
prioriteit: P2
sprint_type: CHORE
cynefin: obvious
impact_zone: GREEN (kleine fixes, geen architectuurwijzigingen)
bron: docs/planning/sprints/SPRINT_OPERATIONELE_VALIDATIE.md
---

## Doel

Repareer de 5 quick-fix gaps uit de Operationele Validatie sprint. Allemaal < 30 min, geen shaping nodig.

## Deliverables

### n8n fixes
- [ ] **QF-01** — WF-1 activeren via API: `PUT /api/v1/workflows/{id}/activate` (2 min)
- [ ] **QF-02** — 3 archived duplicate WF-1 workflows verwijderen via API (5 min)
- [ ] **QF-03** — `check_n8n_status()` in BorisAdapter: port configureerbaar maken via nodes.yml of env var (15 min)

### Python runtime fixes
- [ ] **QF-04** — `pip install pip-audit` in BORIS .venv (2 min)
- [ ] **QF-05** — Intake doc en skill docs updaten: `run_tests()` retourneert `TestResult` dataclass, geen tuple (10 min)

## Afhankelijkheden

- Geblokkeerd door: geen
- BORIS impact: QF-03 wijzigt BorisAdapter, QF-04 wijzigt BORIS venv
- n8n impact: QF-01/02 wijzigen n8n workflows

## Appetite

**Extra Small (XS)** — maximaal 1 uur totaal.
