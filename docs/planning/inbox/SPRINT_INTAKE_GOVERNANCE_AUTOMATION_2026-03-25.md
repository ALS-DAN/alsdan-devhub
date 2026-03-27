# Sprint Intake: Governance & Security Automation

---
gegenereerd_door: "Sprint Operationele Validatie"
status: DONE
fase: 3
prioriteit: P2 (verhoogd — 1/16 governance + 0/10 security automatisering is structureel onhoudbaar)
sprint_type: FEAT
cynefin: complicated (bekende patronen, vereist engineering)
impact_zone: YELLOW (wijzigt QA Agent en voegt SecurityScanner toe)
afgerond: 2026-03-26 (Golf 1 Governance: GA-01..GA-05 in qa_agent.py; Golf 2 Governance: SecurityScanner SA-01..SA-04; GA-06 in node_interface.py)
bron: docs/planning/sprints/SPRINT_OPERATIONELE_VALIDATIE.md
---

## Doel

Verhoog het percentage geautomatiseerde checks in governance en security skills. Huidige staat: governance 1/16, redteam 0/10. Doel: governance 7/16, redteam 4/10.

## Probleemstelling

De operationele validatie sprint bewees dat alle Python-methodes werken, maar ook dat de governance en security skills zwaar leunen op Claude's reasoning. Dit schaalt niet: elke check kost tokens en is niet reproduceerbaar. Triviale checks (PII regex, .env detectie, Co-Authored-By) horen in Python.

## Deliverables

### Sprint 1: Governance automation (QA Agent uitbreiden) — 🎯 DIRECT UITVOERBAAR

- [ ] **GA-01** — G-08: Co-Authored-By check in git log (triviale regex)
- [ ] **GA-02** — G-15: PII detectie — regex voor BSN, NL telefoon, email in staged files
- [ ] **GA-03** — G-16: .env detectie — check of .env files in staged changes zitten
- [ ] **GA-04** — G-01/G-05: Destructieve operatie scan — regex voor `--force`, `--hard`, `DROP TABLE`, `rm -rf` in diffs
- [ ] **GA-05** — G-11: Project governance wijziging detectie — check of CLAUDE.md, DEV_CONSTITUTION.md in diff
- [ ] **GA-06** — `get_review_context()` naar NodeInterface ABC (node-agnostiek) — ⚠️ architectureel significant, raakt alle adapters

**Modus:** Review-only (Laag C). Geen pre-commit hooks in Sprint 1 — pas toevoegen als checks bewezen stabiel zijn en geen false positives genereren.

### Sprint 2: Security automation (SecurityScanner klasse)

- [ ] **SA-01** — SecurityScanner klasse bouwen (equivalent van QAAgent)
- [ ] **SA-02** — ASI02: disallowedTools completeness check — verifieer dat agents juiste deny-lists hebben
- [ ] **SA-03** — ASI04: Supply chain — pip-audit integratie + submodule integrity check
- [ ] **SA-04** — ASI10: Agent prompt tracking — verifieer dat agent .md files in git staan
- [ ] **SA-05** — SecurityAuditReport persistentie — save/load naar scratchpad (zoals QAAgent)

## Afhankelijkheden

- Geblokkeerd door: geen (bouwt voort op bestaande QAAgent patronen)
- BORIS impact: nee (DevHub-interne wijzigingen)
- n8n impact: nee

## Grenzen

- Geen AI-afhankelijke checks automatiseren (die blijven bij Claude)
- Geen nieuwe governance artikelen toevoegen
- Geen wijzigingen aan bestaande agent-definities (alleen nieuwe Python checks)

## Appetite

**Sprint 1 (GA): Small (S)** — GA-items zijn elk < 1 uur. GA-06 is de grootste (raakt NodeInterface ABC). Totaal: ~1 sprint.
**Sprint 2 (SA): Small (S)** — SecurityScanner is een nieuwe klasse maar volgt QAAgent-patroon. Totaal: ~1 sprint.

## Sprint 1 scope (direct uitvoerbaar)

**Alleen GA-01 t/m GA-06** — governance checks in bestaande QA Agent.

**Acceptatiecriteria:**
- Governance automatiseringsgraad: 1/16 → 7/16
- Alle bestaande tests (394+) blijven groen
- Nieuwe checks draaien in review-modus (Laag C), niet als pre-commit hook
- GA-06: `get_review_context()` correct geïmplementeerd in NodeInterface ABC + BorisAdapter
- Geen false positives op bestaande codebase (valideer tegen huidige git history)

**Na Sprint 1:** Sprint 2 (SecurityScanner) wordt apart gepland na evaluatie van Sprint 1.

## Open vragen

1. Moet SecurityScanner een apart package worden of in devhub-core blijven?
2. Is PII-detectie voor Nederlandse patronen voldoende of ook internationaal?
3. GA-06: moet `get_review_context()` een verplichte of optionele methode in NodeInterface zijn? (verplicht = elke adapter moet implementeren)
