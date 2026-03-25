# SPRINT_N8N_CICD_FOUNDATION — n8n CI/CD Foundation

| Veld | Waarde |
|------|--------|
| Status | AFGEROND |
| Startdatum | 2026-03-24 |
| Einddatum | 2026-03-25 |
| Baseline | 339 tests |
| Eindstand | 370 tests (+31) |
| Fase | 2 → 3 transitie |

## Doel

Drie-punts bewakingssysteem voor DevHub: dagelijks (health check via n8n), pre-merge (PR quality gate via GitHub Actions), post-merge (governance check via GitHub Actions).

## Deliverables

- [x] D1 — Docker foundation: `n8n/Dockerfile`, `docker-compose.yml`, `.env.example`
- [x] D2 — Health check script: `n8n/scripts/run_health_check.sh`
- [x] D3 — n8n Health Check workflow: `n8n/workflows/wf1_devhub_health_check.json`
- [x] D4 — PR Quality Gate: `.github/workflows/pr-quality-gate.yml`
- [x] D5 — Governance Check: `.github/workflows/governance-check.yml` + `scripts/governance_check.py`
- [x] D6 — ADR: `docs/adr/ADR-001-n8n-cicd-architecture.md`
- [x] D7 — Operations docs: `docs/operations/N8N_SETUP.md`, `docs/operations/CI_CD_RUNBOOK.md`
- [x] D8 — Tests: `tests/test_governance_check.py` (31 tests)
- [x] D9 — `.gitignore` update: `.env` + `.secrets.baseline`

## Architectuurbeslissing

Hybride n8n + GitHub Actions:
- **n8n** (lokaal, port 5679): dagelijkse Health Check (schedule trigger, geen webhook nodig)
- **GitHub Actions**: PR Quality Gate (op PR open/sync) + Governance Check (op push naar main)

Zie ADR-001 voor volledige onderbouwing.

## Acceptatiecriteria

- [x] 370 tests groen (339 baseline + 31 nieuw)
- [x] governance_check.py implementeert G-01, G-05, G-07, G-11, G-14, G-15, G-16
- [x] PR Quality Gate: comment + labels (quality:green/yellow/red)
- [x] Governance Check: stil bij PASS, Issue bij NEEDS_REVIEW/BLOCK
- [x] Health Check: JSON output met severity mapping
- [x] Geen secrets in code (Art. 8): `.env` in `.gitignore`
- [x] ADR gedocumenteerd

## Anti-patronen

- Geen ngrok/smee tunnel — fragiel voor solo-dev setup
- Geen destructieve CI/CD acties — alles is read-only + reporting
- Geen blocking required checks — recommended only (solo dev)

## DEV_CONSTITUTION Impact

| Artikel | Implementatie |
|---------|-------------|
| Art. 2 (Verificatieplicht) | Automatische verificatie via alle 3 workflows |
| Art. 3 (Codebase-integriteit) | Read-only checks, geen destructieve operaties |
| Art. 4 (Transparantie) | G-07 commit message check, ADR-001 |
| Art. 5 (Kennisintegriteit) | Frontmatter check in governance (toekomstig) |
| Art. 6 (Project-soevereiniteit) | G-11 detecteert project-governance wijzigingen |
| Art. 7 (Impact-zonering) | GREEN/YELLOW/RED mapping in alle workflows |
| Art. 8 (Dataminimalisatie) | G-14 secrets, G-15 PII, G-16 .env detectie |

## Retrospective

### Wat ging goed
- Hybride n8n + GitHub Actions architectuur voorkomt over-engineering
- 31 tests in één sprint toegevoegd (339 → 370)
- ADR-001 vastgelegd vóór implementatie (architecture-first)
- Governance check script dekt 7 constitutionele regels

### Wat kan beter
- n8n Docker configuratie heeft 5 operationele issues (port conflict, deprecated auth, missing .env) — zie SPRINT_INTAKE_N8N_DOCKER_FIX
- Health check workflow niet end-to-end getest in draaiende n8n container

### Actiepunten
- Docker fix als aparte patch plannen (P1)
- Pre-commit hooks toevoegen aan devhub root (ontbreekt, alleen BORIS heeft ze)
