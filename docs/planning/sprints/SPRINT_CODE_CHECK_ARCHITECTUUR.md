# SPRINT_CODE_CHECK_ARCHITECTUUR — Vijf-lagen Code Check Architectuur

| Veld | Waarde |
|------|--------|
| Status | ACTIVE |
| Startdatum | 2026-03-25 |
| Baseline | 370 tests |
| Eindstand | 394 tests (+24) |
| Fase | 2 → 3 transitie |

## Doel

Formaliseer de vijf-lagen check-architectuur (ADR-002), vul ontbrekende lagen (pre-commit hooks, SAST tooling) en upgrade de reviewer agent tot orkestrator.

## Deliverables

- [x] D1 — Pre-commit hooks: `.pre-commit-config.yaml` (ruff, bandit, detect-secrets, conventional-commits)
- [x] D2 — Reviewer agent upgrade: `agents/reviewer.md` (Sonnet → Opus, 5-lagen bewustzijn, escalatie-protocol)
- [x] D3 — SAST integratie: bandit + detect-secrets via pre-commit, MCP SAST geparkeerd
- [x] D4 — ADR-002: `docs/adr/ADR-002-code-check-architectuur.md`
- [x] D5 — E2E tests: `packages/devhub-core/tests/test_review_chain.py` (24 tests)
- [x] D6 — Sprint-documentatie

## Architectuurbeslissing

Vijf check-lagen (ADR-002):

| Laag | Trigger | Verantwoordelijke |
|------|---------|-------------------|
| A Preventie | Sprint-start | dev-lead |
| B Realtime | Elke commit | coder + pre-commit hooks |
| C Review | Na implementatie | reviewer agent (orkestrator) |
| D Systeem | CI events / schedule | GitHub Actions + n8n |
| E Security | On-demand | red-team agent + bandit |

## Acceptatiecriteria

- [x] 394 tests groen (370 baseline + 24 nieuw)
- [x] `pre-commit run --all-files` slaagt (12 hooks)
- [x] Reviewer agent bevat 5-lagen referentie + escalatie-protocol
- [x] ADR-002 gedocumenteerd met overwogen alternatieven
- [x] E2E tests dekken PASS/NEEDS_WORK/BLOCK scenarios
- [x] Bandit + detect-secrets in pre-commit pipeline

## Lint-fixes (bijvangst)

6 E501 long-line errors in bestaande code gefixed:
- `boris_adapter.py` (3 regels)
- `test_boris_adapter_mentor.py` (1 regel)
- `test_mentor_contracts.py` (1 regel)
- `governance_check.py` (1 regel)

15 bestanden geformateerd door ruff-format bij eerste run.

## DEV_CONSTITUTION Impact

| Artikel | Implementatie |
|---------|-------------|
| Art. 2 (Verificatieplicht) | Reviewer verifieert claims in code tegen tests |
| Art. 3 (Codebase-integriteit) | Reviewer is read-only, wijzigt nooit code |
| Art. 4 (Transparantie) | Conventional commits afgedwongen via pre-commit |
| Art. 7 (Impact-zonering) | BLOCK → RED-zone escalatie in reviewer protocol |
| Art. 8 (Dataminimalisatie) | detect-secrets + bandit in pre-commit |
