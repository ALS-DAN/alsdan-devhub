# CI/CD Runbook — DevHub

## Overzicht

DevHub gebruikt een hybride CI/CD architectuur:

| Systeem | Trigger | Workflows |
|---------|---------|-----------|
| n8n (lokaal) | Schedule (18:00 dagelijks) | WF-1: Health Check |
| GitHub Actions | PR open/sync | PR Quality Gate |
| GitHub Actions | Push naar main | Governance Check |

## PR Quality Gate

**Trigger:** Pull Request geopend of ge-updated

**Wat het doet:**
1. Draait pytest, ruff, pip-audit op de PR branch
2. Post een comment met resultaten (create of update)
3. Voegt label toe: `quality:green`, `quality:yellow`, of `quality:red`

**Bij YELLOW/RED:**
- Check de PR comment voor specifieke failures
- Fix de issues en push een nieuwe commit
- De workflow draait opnieuw en update de comment

**Handmatig re-triggeren:** Push een lege commit of close/reopen de PR.

## Governance Check

**Trigger:** Push naar main branch

**Wat het doet:**
1. Draait `scripts/governance_check.py` op de laatste commit
2. Bij schendingen: maakt GitHub Issue aan met label `governance-violation`
3. Bij PASS: stil (geen actie)

**Checks:**
- G-01: Destructieve patronen (`--force`, `rm -rf`, etc.)
- G-05: Destructieve git operaties
- G-07: Commit message kwaliteit (min 10 chars)
- G-11: Wijzigingen aan project-governance bestanden
- G-14: Secrets detectie (via detect-secrets)
- G-15: PII-patronen (email, BSN, telefoonnummer)
- G-16: .env bestanden in commits

**Bij BLOCK verdict:**
1. Fix de schending onmiddellijk
2. Als secret gedetecteerd: roteer de secret, verwijder uit git history
3. Sluit het governance issue als opgelost

**Bij NEEDS_REVIEW verdict:**
- Beoordeel de findings
- Sluit het issue als de findings acceptabel zijn

## n8n Health Check

**Trigger:** Dagelijks 18:00 (Europe/Amsterdam)

**Wat het doet:**
1. Draait pytest, ruff, pip-audit, pip list --outdated
2. Bij YELLOW: maakt GitHub Issue met label `health-alert`
3. Bij RED: GitHub Issue + email

**Health Check Issues beheren:**
- Issues met label `health-alert` zijn automatisch gegenereerd
- Fix de onderliggende problemen
- Sluit het issue handmatig na fix
- Bij herhaalde issues: onderzoek root cause

## Troubleshooting

### GitHub Actions faalt
1. Ga naar Actions tab in GitHub
2. Klik op de gefaalde run
3. Check de logs per stap

### n8n draait niet
```bash
docker compose ps          # Check status
docker compose logs n8n    # Check logs
docker compose restart n8n # Herstart
```

### False positives in governance check
- PII-patronen: voeg false positives toe aan de filter in `scripts/governance_check.py`
- detect-secrets: update `.secrets.baseline` met `detect-secrets scan > .secrets.baseline`
