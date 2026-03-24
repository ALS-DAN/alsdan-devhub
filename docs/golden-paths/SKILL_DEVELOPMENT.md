# Golden Path: Skill Development

_Template voor het bouwen van een nieuwe DevHub skill._

---

## Wanneer gebruiken

- Een nieuwe `/devhub-*` skill toevoegen aan het plugin-systeem
- Impact-zone: GREEN (skill is read-only, gebruikt bestaande adapters)

---

## Stappen

### 1. Skill-ontwerp

- [ ] **Naam:** `devhub-<naam>` (kebab-case)
- [ ] **Trigger-woorden:** minimaal 3 activatietermen
- [ ] **Doel:** 1-2 zinnen die de kernwaarde beschrijven
- [ ] **Governance-artikelen:** welke DEV_CONSTITUTION artikelen zijn relevant?

### 2. Bestandsstructuur

```
.claude/skills/devhub-<naam>/
  SKILL.md          # Skill-definitie (verplicht)
```

### 3. SKILL.md schrijven

Volg het vaste format:

```markdown
# devhub-<naam> — Node-Agnostische <Beschrijving> Skill

## Trigger
Activeer bij: "<term1>", "<term2>", "<term3>".

## Doel
<1-2 zinnen kernwaarde>
De kracht: (1) ..., (2) ..., (3) ...

---

## Setup
[Python setup met NodeRegistry + adapter]

---

## Workflow

### Stap 1: <actie>
[Details + Python code]

### Stap 2: <actie>
[Details]

...

### Stap N: Rapportage
[Output format]

---

## Regels
- [Governance constraints]
- Developer beslist. DevHub voert uit.

## Contract Referentie
| Component | Doel |
|-----------|------|
| `adapter.<methode>()` | ... |
```

### 4. Verplichte secties

Elke skill MOET bevatten:
- [ ] **Trigger** — activatiewoorden
- [ ] **Doel** — met "De kracht: (1), (2), (3)"
- [ ] **Setup** — Python NodeRegistry integratie
- [ ] **Workflow** — genummerde stappen
- [ ] **Regels** — governance-verwijzingen (Art. referenties)
- [ ] **Contract Referentie** — adapter/agent methodes

### 5. Tests uitbreiden

In `tests/test_plugin_skills.py`:
- [ ] Skill toevoegen aan `REQUIRED_SKILLS` lijst
- [ ] Bestaande parametrized tests dekken automatisch de nieuwe skill

### 6. Verificatie

```bash
PYTHONPATH=/Users/nielspostma/alsdan-devhub python -m pytest tests/test_plugin_skills.py -v
```

- [ ] Skill directory bestaat
- [ ] SKILL.md is niet leeg (>100 chars)
- [ ] Vereiste secties aanwezig
- [ ] Governance-verwijzing aanwezig
- [ ] Python-integratie aanwezig

### 7. Registratie

- [ ] CLAUDE.md bijwerken: skill toevoegen aan "Beschikbare skills" tabel
- [ ] DEVHUB_BRIEF.md bijwerken: skill toevoegen aan skills-tabel
