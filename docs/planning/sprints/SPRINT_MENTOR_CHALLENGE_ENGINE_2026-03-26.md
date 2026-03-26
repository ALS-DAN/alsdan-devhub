# Sprint: Mentor S2 — Challenge Engine + Scaffolding

---
track: M (Mentor)
sprint: 2
golf: 2 (Uitbouw)
size: S
baseline_tests: 775
parallel_met: Track G S2 (Governance SecurityScanner)
status: ✅ DONE
---

## Doelstelling

Bouw een deterministische Challenge Engine die op basis van het SkillRadarProfile deliberate practice challenges genereert, gekoppeld aan Dreyfus-level scaffolding. Anti-Zone-of-No-Development mechanisme voorkomt dat scaffolding te lang op hetzelfde niveau blijft.

## Deliverables

| # | Deliverable | Pad | Status |
|---|-------------|-----|--------|
| D1 | ChallengeEngine klasse | `packages/devhub-core/devhub_core/agents/challenge_engine.py` | ✅ |
| D2 | ScaffoldingManager klasse | `packages/devhub-core/devhub_core/agents/scaffolding_manager.py` | ✅ |
| D3 | Challenge templates YAML | `config/challenge_templates.yml` | ✅ |
| D4 | devhub-mentor SKILL.md v2.0 | `.claude/skills/devhub-mentor/SKILL.md` | ✅ |
| D5 | Tests ChallengeEngine | `packages/devhub-core/tests/test_challenge_engine.py` | ✅ |
| D6 | Tests ScaffoldingManager | `packages/devhub-core/tests/test_scaffolding_manager.py` | ✅ |

## Technisch ontwerp

### ChallengeEngine
- Input: `SkillRadarProfile` → Output: `list[DevelopmentChallenge]`
- Dreyfus→ChallengeType mapping: 1=explain_it/teach_back, 2=stretch/reverse_engineer, 3+=cross_domain/adversarial
- Prioriteert primary_gap domein, daarna laagste growth_velocity
- Template-driven via YAML met hardcoded fallback

### ScaffoldingManager
- Dreyfus→ScaffoldingLevel mapping: 1=HIGH, 2=MEDIUM, 3=LOW, 4-5=NONE
- Anti-ZoND: stagnatie-detectie bij >2 sprints zonder level-up
- `apply_scaffolding()` retourneert nieuw frozen instance
- `reduce_scaffolding()` verlaagt met één stap

### Bestaande contracts hergebruikt
- `growth_contracts.py`: DevelopmentChallenge, SkillRadarProfile, SkillDomain, DreyfusLevel, ChallengeType, ScaffoldingLevel

## Testresultaten

- ChallengeEngine tests: 25 passed
- ScaffoldingManager tests: 18 passed
- **Tests Δ: +43**

## DoR Checklist

- [x] Scope gedefinieerd in sprint-doc
- [x] Baseline tests slagen (775)
- [x] Afhankelijkheden afgerond (Mentor S1 ✅)
- [x] Anti-patronen gedocumenteerd (frozen dataclasses, deterministic engine)
- [x] Acceptatiecriteria meetbaar (challenge generatie, scaffolding mapping)
- [x] Risico's benoemd (template loading, Dreyfus edge cases)
- [x] n8n impact: geen n8n changes
