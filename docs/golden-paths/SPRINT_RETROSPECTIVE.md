# Golden Path: Sprint Retrospective

_Template voor gestructureerde sprint-terugblik — basis voor het zelfverbeterend systeem (Loop 1)._

---

## Wanneer gebruiken

- Na elke sprint-afsluiting (stap 6 van devhub-sprint skill)
- Bij periodieke reflectie op development-patronen
- Impact-zone: GREEN (read-only analyse, schrijft alleen naar `knowledge/retrospectives/`)

---

## Retrospective Template

```markdown
---
title: Retrospective — SPRINT_<NAAM>
domain: retrospectives
grade: SILVER
date: <YYYY-MM-DD>
author: devhub-sprint
sprint: <SPRINT_NAAM>
---

# Retrospective — SPRINT_<NAAM>

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | <naam> |
| Duur | <start> → <eind> |
| Tests start | <N> |
| Tests eind | <N> |
| Tests delta | +<N> |
| Deliverables | <X/Y afgerond> |
| QA verdict | <PASS/NEEDS_WORK> |

## Git Analyse

| Metric | Waarde |
|--------|--------|
| Commits | <N> |
| Files changed | <N> |
| Insertions | +<N> |
| Deletions | -<N> |
| Netto groei | <N> regels |

## Wat ging goed

- <observatie 1>
- <observatie 2>
- <observatie 3>

## Wat kan beter

- <observatie 1 + concrete actie>
- <observatie 2 + concrete actie>

## Patronen

### Herhaalde patronen (positief)
- <patroon dat vaker terugkomt en werkt>

### Herhaalde patronen (aandacht)
- <patroon dat vaker terugkomt en frictie veroorzaakt>

## Agent-prestaties

| Agent | Ingezet | Observatie |
|-------|---------|------------|
| dev-lead | ja/nee | <hoe presteerde orchestratie?> |
| coder | ja/nee | <code-kwaliteit, test-coverage?> |
| reviewer | ja/nee | <review-diepte, false positives?> |
| researcher | ja/nee | <kenniskwaliteit, bronnen?> |
| planner | ja/nee | <planning-nauwkeurigheid?> |

## Lessen voor volgende sprint

1. <les 1 — concreet en actionable>
2. <les 2>
3. <les 3>

## Open items

- [ ] <item dat naar volgende sprint doorgeschoven wordt>
```

---

## Data-bronnen voor retrospective

| Bron | Hoe ophalen |
|------|-------------|
| Git statistieken | `git log --oneline --since=<start>`, `git diff --stat <start>..HEAD` |
| Test-delta | Sprint-doc startpunt vs `pytest` output |
| QA rapport | `QAAgent.produce_report()` output |
| Deliverables | Sprint-doc checklist |
| Agent-gebruik | Observatie tijdens sprint |

---

## Governance

- Retrospective is **ALTIJD eerlijk** — geen sugarcoating van problemen
- Lessen moeten **concreet en actionable** zijn, niet abstract
- Patronen worden pas benoemd als ze ≥2x voorkomen
- Developer beslist welke lessen in de volgende sprint worden toegepast (Art. 1)
- Retrospective wordt opgeslagen als SILVER-grade kennis (gevalideerd door 1 sprint)
