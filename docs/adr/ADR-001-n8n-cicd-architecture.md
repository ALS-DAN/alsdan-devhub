# ADR-001: Hybride n8n + GitHub Actions CI/CD Architectuur

| Veld | Waarde |
|------|--------|
| Status | Accepted |
| Datum | 2026-03-24 |
| Context | Sprint: n8n CI/CD Foundation |
| Impact-zone | RED (nieuwe CI/CD infrastructuur) |

## Context

DevHub had geen CI/CD. De `devhub-health` skill draaide alleen reactief. Er was geen automatische bewaking voor regressies, CVE's of governance-schendingen. DevHub heeft drie bewakingsbehoeften:

1. **Dagelijkse health check** (scheduled)
2. **PR quality gate** (event-driven, op PR open/sync)
3. **Governance check** (event-driven, op push naar main)

## Beslissing

**Hybride architectuur:** n8n voor scheduled workflows, GitHub Actions voor event-driven workflows.

| Workflow | Systeem | Reden |
|----------|---------|-------|
| Health Check | n8n (lokaal) | Schedule trigger, geen webhook nodig, n8n UI voor monitoring |
| PR Quality Gate | GitHub Actions | PR events vereisen webhook; GH Actions is native, zero-config |
| Governance Check | GitHub Actions | Push events vereisen webhook; native integratie met Issues/Labels |

## Overwogen alternatieven

### Alternatief A: Alles in n8n
- **Pro:** Eén systeem, n8n UI voor alle workflows
- **Con:** PR/push triggers vereisen webhook naar localhost → ngrok/smee tunnel nodig → fragiel, extra dependency, veiligheidsrisico

### Alternatief B: Alles in GitHub Actions
- **Pro:** Zero-config, geen Docker dependency
- **Con:** Verliest n8n's visuele workflow editor, moeilijker te debuggen voor scheduled checks, geen lokale orchestratie

### Alternatief C: Hybride (gekozen)
- **Pro:** Elk systeem doet waar het goed in is; geen tunnel nodig; check-logica herbruikbaar
- **Con:** Twee systemen om te onderhouden

## Consequenties

- n8n Docker container draait lokaal op port 5679 (5678 is BORIS)
- Custom Dockerfile met git + Python (n8n base image mist deze)
- `.env` bevat secrets, is gitignored (Art. 8)
- `scripts/governance_check.py` is standalone (geen DevHub imports) voor CI-eenvoud
- Health check script (`n8n/scripts/run_health_check.sh`) is herbruikbaar
