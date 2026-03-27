# Golden Path: Growth Report

_Template voor periodieke developer groei-rapportage — basis voor het Mentor Supervisor Systeem._

---

## Wanneer gebruiken

- Na sprint-afsluiting (optioneel, gekoppeld aan retrospective)
- Wekelijks bij actieve coaching
- Bij periodieke skill assessment (maandelijks)
- Impact-zone: GREEN (read-only analyse, schrijft alleen naar `knowledge/skill_radar/`)

---

## Growth Report Template

```markdown
---
title: Growth Report — <PERIOD>
domain: growth
grade: SILVER
date: <YYYY-MM-DD>
author: devhub-mentor
period: <sprint-X of week-YYYY-WW>
---

# Growth Report — <PERIOD>

## Skill Radar

| Domein | Niveau | Δ | ZPD-taken |
|--------|--------|---|-----------|
| AI-Engineering | <1-5>/5 | <+0.X> | <taken> |
| Python | <1-5>/5 | <+0.X> | <taken> |
| Governance | <1-5>/5 | <+0.X> | <taken> |
| Testing | <1-5>/5 | <+0.X> | <taken> |
| Security | <1-5>/5 | <+0.X> | <taken> |
| Architecture | <1-5>/5 | <+0.X> | <taken> |
| DevOps/Tooling | <1-5>/5 | <+0.X> | <taken> |
| Methodiek | <1-5>/5 | <+0.X> | <taken> |

## T-Shape

**Deep (>=4):** <domeinen>
**Broad (>=2):** <domeinen>
**Primary gap:** <domein>

## Deliberate Practice

| Challenge | Type | Domein | Status |
|-----------|------|--------|--------|
| <beschrijving> | <stretch/explain_it/reverse_engineer/teach_back/cross_domain/adversarial> | <domein> | <done/in_progress/new/skipped> |

## Scaffolding-afbouw

| Domein | Vorig | Huidig | Observatie |
|--------|-------|--------|------------|
| <domein> | <HIGH/MEDIUM/LOW/NONE> | <level> | <waarom afgebouwd> |

## Leeslijst (geprioriteerd op ZPD)

| Prioriteit | Titel | Type | Geschatte tijd | ZPD-alignment |
|------------|-------|------|----------------|---------------|
| URGENT | <titel> | <paper/docs/tutorial/video/book_chapter> | <min> min | <exact/stretch/review> |
| IMPORTANT | <titel> | <type> | <min> min | <alignment> |
| NICE_TO_HAVE | <titel> | <type> | <min> min | <alignment> |

## Strategisch Inzicht

<1-3 observaties over groeirichting, career trajectory, of cross-domain verbanden>

## Metrics

| Metric | Waarde |
|--------|--------|
| Challenges completed | <N> |
| Challenges proposed | <N> |
| Challenges skipped | <N> |
| Growth velocity overall | <X%> |
| Deliberate practice minutes | <N> min |
| Scaffolding reductions | <N> domeinen |
```

---

## Data-bronnen voor Growth Report

| Bron | Hoe ophalen |
|------|-------------|
| Skill Radar | `knowledge/skill_radar/SKILL_RADAR_PROFILE_*.yaml` |
| Sprint data | `docs/planning/SPRINT_TRACKER.md` velocity tabel |
| Challenge log | (Sprint 2: challenge engine output) |
| Git statistieken | `git log --shortstat` per domein |

---

## Governance

- Growth Report is **eerlijk en constructief** — geen feel-good metrics
- Primary gap wordt altijd benoemd, ook als het oncomfortabel is
- Scaffolding-afbouw is een positief signaal, geen straf
- Developer beslist of en wanneer challenges worden geaccepteerd (Art. 1)
- Growth Reports worden opgeslagen als SILVER-grade kennis (gevalideerd door 1 sprint)
