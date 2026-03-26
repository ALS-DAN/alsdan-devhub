# Sprint: Governance S2 — SecurityScanner

---
track: G (Governance)
sprint: 2
golf: 2 (Uitbouw)
size: S
baseline_tests: 775
parallel_met: Track M S2 (Mentor Challenge Engine)
status: ✅ DONE
---

## Doelstelling

Bouw een geautomatiseerde SecurityScanner klasse (QAAgent-patroon) die OWASP ASI 2026 checks uitvoert: disallowedTools completeness (ASI02), supply chain (ASI04) en agent prompt tracking (ASI10). Report persistence in JSON.

## Deliverables

| # | Deliverable | Pad | Status |
|---|-------------|-----|--------|
| D1 | SecurityScanner klasse | `packages/devhub-core/devhub_core/agents/security_scanner.py` | ✅ |
| D2 | SA-01: disallowedTools check (ASI02) | Geïntegreerd in D1 | ✅ |
| D3 | SA-02: Supply chain check (ASI04) | Geïntegreerd in D1 | ✅ |
| D4 | SA-03: Submodule integrity (ASI04) | Geïntegreerd in D1 | ✅ |
| D5 | SA-04: Agent prompt tracking (ASI10) | Geïntegreerd in D1 | ✅ |
| D6 | Report persistence (JSON) | Geïntegreerd in D1 | ✅ |
| D7 | devhub-redteam SKILL.md v1.1 | `.claude/skills/devhub-redteam/SKILL.md` | ✅ |
| D8 | Tests SecurityScanner | `packages/devhub-core/tests/test_security_scanner.py` | ✅ |

## Technisch ontwerp

### SecurityScanner (QAAgent-patroon)
- `SECURITY_CHECKS` array: SA-01..SA-04 met ASI-koppeling
- Individual scan methods: `scan_disallowed_tools()`, `scan_supply_chain()`, `scan_submodule_integrity()`, `scan_agent_prompts()`
- `full_scan()` orchestrator → `SecurityAuditReport`
- JSON persistence: `save_report()`, `get_report()`, `list_reports()`

### Check details
- **SA-01 (ASI02)**: Parse agent .md files, check voor deny-list keywords
- **SA-02 (ASI04)**: `pip-audit --format=json` met graceful fallback bij ontbreken
- **SA-03 (ASI04)**: `git submodule status` voor pinning-verificatie
- **SA-04 (ASI10)**: `git ls-files` voor tracking-verificatie van agent/skill prompts

### ASI Coverage
- Geautomatiseerd: ASI02, ASI04, ASI10
- NOT_ASSESSED: ASI01, ASI03, ASI05-ASI09 (handmatige audit via redteam skill)

### Bestaande contracts hergebruikt
- `security_contracts.py`: SecurityFinding, SecurityAuditReport, ASI_IDS, MitigationStatus
- `qa_agent.py`: Check array patroon, reports_path, JSON persistence

## Testresultaten

- SecurityScanner tests: 34 passed
- Alle subprocess calls gemockt
- **Tests Δ: +34**

## DoR Checklist

- [x] Scope gedefinieerd in sprint-doc
- [x] Baseline tests slagen (775)
- [x] Afhankelijkheden afgerond (Governance S1 ✅)
- [x] Anti-patronen gedocumenteerd (read-only scanning, mocked subprocesses)
- [x] Acceptatiecriteria meetbaar (4 scan methods, report persistence roundtrip)
- [x] Risico's benoemd (pip-audit availability, git subprocess reliability)
- [x] n8n impact: geen n8n changes
