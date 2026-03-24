# Golden Path: YELLOW Zone Architectuur

_Template voor wijzigingen met architectuur-impact die review vereisen._

---

## Wanneer gebruiken

- Wijzigingen aan interfaces, contracts of adapters
- Nieuwe componenten die met bestaande interacteren
- Database schema wijzigingen
- Nieuwe afhankelijkheden toevoegen
- Cross-module refactoring
- **Impact-zone: YELLOW** (Art. 7 DEV_CONSTITUTION — review vereist)

---

## Stappen

### 1. Impact-analyse

- [ ] Welke componenten worden geraakt?
- [ ] Welke interfaces/contracts wijzigen?
- [ ] Zijn er downstream effecten op managed projecten? (Art. 6 — project-soevereiniteit)
- [ ] Is een ADR nodig? (bij architectuurkeuze: JA)

### 2. ADR schrijven (indien van toepassing)

Schrijf naar `docs/adr/ADR-NNN-beschrijving.md`:

```markdown
# ADR-NNN: <titel>

## Status
Voorstel

## Context
<waarom is deze beslissing nodig?>

## Beslissing
<wat is gekozen en waarom?>

## Gevolgen
<positief en negatief>

## Alternatieven overwogen
<wat is afgewezen en waarom?>
```

- [ ] ADR geschreven en genummerd
- [ ] Developer akkoord op ADR (Art. 1 — menselijke regie)

### 3. Plan mode

- [ ] Sprint-plan of plan-file aangemaakt
- [ ] Scope, deliverables en fasen gedefinieerd
- [ ] Developer akkoord op plan

### 4. Implementatie (fase voor fase)

Per fase:
- [ ] Implementatie
- [ ] Tests toegevoegd
- [ ] Lint clean
- [ ] Fase-resultaat gerapporteerd aan developer

### 5. Review

```bash
# Governance check
/devhub-governance-check

# Code review
/devhub-review
```

- [ ] Governance audit: PASS of NEEDS_REVIEW (niet BLOCK)
- [ ] Code review: PASS of NEEDS_WORK (niet BLOCK)
- [ ] Developer review en akkoord

### 6. Verificatie

- [ ] Alle tests groen, count ≥ startpunt
- [ ] Lint clean
- [ ] Geen secrets (Art. 8)
- [ ] ADR status bijgewerkt naar "Geaccepteerd"

### 7. Commit + documentatie

- [ ] Commit message bevat WAT + WAAROM + ADR-referentie
- [ ] CLAUDE.md bijgewerkt indien interface/module wijzigt
- [ ] OVERDRACHT.md bijgewerkt met beslissing

---

## Wanneer escaleren naar RED

Escaleer als:
- Destructieve operaties nodig zijn (force push, data migratie, schema drop)
- Wijzigingen onomkeerbaar zijn zonder backup
- Security-gevoelige code geraakt wordt (auth, secrets, permissions)

**RED-zone vereist expliciet developer-akkoord VOOR elke stap** (Art. 1 + Art. 7).
