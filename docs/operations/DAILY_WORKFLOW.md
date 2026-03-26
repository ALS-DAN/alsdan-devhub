# DevHub Dagelijkse Workflow

## Overzicht

| Moment | Actie | Trigger |
|--------|-------|---------|
| Ochtend | `/devhub-sprint-prep` | Handmatig |
| Tijdens development | `/devhub-review` | Na code changes |
| 18:00 | WF-1: Health Check | Automatisch (n8n) |
| Wekelijks | `/devhub-health` | Handmatig |
| Bij PR | PR Quality Gate | Automatisch (GitHub Actions) |
| Bij push main | Governance Check | Automatisch (GitHub Actions) |

## Ochtend: Sprint Prep

```
/devhub-sprint-prep
```

Levert: health status, developer profile (O-B-B fase), overdracht, inbox items, actieve sprint docs. Gebruik dit als dagstart om context op te pakken.

## Tijdens Development: Review

```
/devhub-review
```

Na significante code changes. Levert: diff analyse, anti-pattern scan, QA findings.

## 18:00: Automatische Health Check

n8n WF-1 draait dagelijks om 18:00 (Europe/Amsterdam):
- Roept dev-os-api `/health/run` aan
- Bij YELLOW/RED: maakt automatisch GitHub Issue aan (labels: `health-alert`, `P1`/`P2`)
- Bij GREEN: geen actie (silent success)

Check: `http://localhost:5679` > Executions

## Wekelijks: Deep Health Check

```
/devhub-health
```

Volledige 6-dimensie check: code quality, dependencies, versions, architecture, vectorstore, n8n. Genereert rapport + HEALTH_STATUS.md.

## Automatisch: CI/CD

- **PR Quality Gate** (`.github/workflows/pr-quality-gate.yml`): pytest + ruff + pip-audit bij elke PR
- **Governance Check** (`.github/workflows/governance-check.yml`): compliance check bij push naar main

## Mentor Check (optioneel)

```
/devhub-mentor
```

O-B-B developer coaching: detecteert fase (Orienteren/Bouwen/Beheersen), geeft coaching signal (GREEN/AANDACHT/STAGNATIE).

## Voorwaarden

- Docker moet draaien: `docker compose -f docker/docker-compose.dev-os.yml up -d`
- BORIS submodule op `/Users/nielspostma/buurts-ecosysteem`
- n8n bereikbaar op `http://localhost:5679`
