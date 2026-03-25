# Sprint Intake: Governance & Security Automation

---
gegenereerd_door: "Sprint Operationele Validatie"
status: INBOX
fase: 3
prioriteit: P3
sprint_type: FEAT
cynefin: complicated (bekende patronen, vereist engineering)
impact_zone: YELLOW (wijzigt QA Agent en voegt SecurityScanner toe)
bron: docs/planning/sprints/SPRINT_OPERATIONELE_VALIDATIE.md
---

## Doel

Verhoog het percentage geautomatiseerde checks in governance en security skills. Huidige staat: governance 1/16, redteam 0/10. Doel: governance 7/16, redteam 4/10.

## Probleemstelling

De operationele validatie sprint bewees dat alle Python-methodes werken, maar ook dat de governance en security skills zwaar leunen op Claude's reasoning. Dit schaalt niet: elke check kost tokens en is niet reproduceerbaar. Triviale checks (PII regex, .env detectie, Co-Authored-By) horen in Python.

## Deliverables

### Governance automation (QA Agent uitbreiden)
- [ ] **GA-01** — G-08: Co-Authored-By check in git log (triviale regex)
- [ ] **GA-02** — G-15: PII detectie — regex voor BSN, NL telefoon, email in staged files
- [ ] **GA-03** — G-16: .env detectie — check of .env files in staged changes zitten
- [ ] **GA-04** — G-01/G-05: Destructieve operatie scan — regex voor `--force`, `--hard`, `DROP TABLE`, `rm -rf` in diffs
- [ ] **GA-05** — G-11: Project governance wijziging detectie — check of CLAUDE.md, DEV_CONSTITUTION.md in diff
- [ ] **GA-06** — `get_review_context()` naar NodeInterface ABC (node-agnostiek)

### Security automation (SecurityScanner klasse)
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

**Medium (M)** — 1-2 sprints. GA-items zijn klein (elk < 1 uur). SA-items vereisen nieuwe klasse.

## Open vragen

1. Moet SecurityScanner een apart package worden of in devhub-core blijven?
2. Moeten de nieuwe governance checks als pre-commit hook draaien (Laag B) of alleen in review (Laag C)?
3. Is PII-detectie voor Nederlandse patronen voldoende of ook internationaal?
