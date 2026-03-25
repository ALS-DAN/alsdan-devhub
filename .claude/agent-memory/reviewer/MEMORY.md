# Reviewer Memory

## Projecten
- boris-buurts: buurts-ecosysteem — 2364+ tests, 59 ADRs, strict governance

## Governance
- DEV_CONSTITUTION Art. 2: verifieer claims tegen primaire bronnen (bestanden, git log)
- DEV_CONSTITUTION Art. 6: project-regels gaan voor
- DEV_CONSTITUTION Art. 7: classificeer bevindingen als GREEN / YELLOW / RED

## QA Agent
- Python QA: `devhub/agents/qa_agent.py` — 12 code checks + 6 doc checks
- Aanroep: `PYTHONPATH=/Users/nielspostma/alsdan-devhub python3 -c "from devhub.agents.qa_agent import QAAgent; ..."`

## Werkwijze
- Read-only: rapporteer, fix nooit zelf
- Adversarial: zoek actief naar problemen en edge cases
- disallowedTools: Edit, Write, Agent
