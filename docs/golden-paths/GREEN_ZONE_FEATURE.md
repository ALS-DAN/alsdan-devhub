# Golden Path: GREEN Zone Feature

_Template voor low-risk, reversibele wijzigingen (tests, docs, refactoring, kleine features)._

---

## Wanneer gebruiken

- Wijzigingen die volledig gedekt worden door bestaande tests
- Geen architectuur-impact
- Geen externe afhankelijkheden
- Geen destructieve operaties
- **Impact-zone: GREEN** (Art. 7 DEV_CONSTITUTION)

---

## Stappen

### 1. Scope definiëren

- [ ] Wat wordt gewijzigd? (bestanden, functies, tests)
- [ ] Waarom? (bug, feature, refactor, docs)
- [ ] Welke tests dekken de wijziging?

### 2. Pre-check

```bash
# Tests moeten groen zijn VOOR je begint
PYTHONPATH=/Users/nielspostma/alsdan-devhub python -m pytest tests/ -v
```

- [ ] Alle tests groen
- [ ] Geen openstaande lint errors (`ruff check`)

### 3. Implementatie

- [ ] Wijzigingen doorgevoerd
- [ ] Tests toegevoegd/aangepast (geen code zonder tests — CR-01)
- [ ] Geen hardcoded secrets (Art. 8)
- [ ] Type hints op publieke functies (CR-08)

### 4. Verificatie

```bash
# Tests na wijziging
PYTHONPATH=/Users/nielspostma/alsdan-devhub python -m pytest tests/ -v

# Lint
ruff check .
```

- [ ] Tests groen, count ≥ startpunt (geen regressie)
- [ ] Lint clean

### 5. Commit

- [ ] Commit message bevat WAT + WAAROM (Art. 4)
- [ ] Co-Authored-By trailer aanwezig
- [ ] Geen `.env` of credentials in staged files (Art. 8)

---

## Wanneer escaleren naar YELLOW

Escaleer als je tijdens implementatie ontdekt dat:
- Meerdere modules/componenten geraakt worden
- Een interface of contract wijzigt
- Een ADR nodig is
- Review door een ander vereist is

Gebruik dan: `docs/golden-paths/YELLOW_ZONE_ARCHITECTURE.md`
