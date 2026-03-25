# SPRINT_INTAKE: n8n Docker Fix

| Veld | Waarde |
|------|--------|
| Gegenereerd door | Cowork — alsdan-devhub |
| Status | INBOX |
| Fase | 0 (fundament) |
| Prioriteit | **Hoog** — n8n is momenteel volledig niet-functioneel |
| Sprint-type | PATCH (Cynefin: simpel — bekende oorzaken, bekende oplossingen) |
| Impact-zone | YELLOW — wijzigt Docker-configuratie, geen code-impact |

## Doel

Maak de n8n Docker-setup werkend door vijf geïdentificeerde configuratiefouten te herstellen.

## Probleemstelling

Claude Code heeft de n8n-setup voor DevHub aangemaakt als kopie van de BORIS-setup, maar met meerdere fouten. Het resultaat: n8n start in een onbruikbare toestand ("ghost UI", lege workflows, authenticatie-problemen). Niels kan de n8n-interface niet gebruiken.

### Root cause analyse (5 issues)

**Issue 1: Poortconflict — BORIS-poort overgenomen**
- `docker/docker-compose.dev-os.yml` mapt `5678:5678`
- ADR-001 specificeert dat DevHub op **5679** moet draaien (5678 = BORIS)
- `WEBHOOK_URL` verwijst ook naar `localhost:5678` i.p.v. `localhost:5679`
- Als BORIS ook draait → poortconflict → geen van beide bereikbaar

**Issue 2: Geen workflow JSON-bestanden**
- `N8N_SETUP.md` verwijst naar `n8n/workflows/wf1_devhub_health_check.json`
- Deze directory en dit bestand bestaan **niet**
- BORIS heeft wél werkende workflows (wf6, wf7, wf8 in `projects/buurts-ecosysteem/docker/n8n-local-files/`)
- DevHub heeft nul importeerbare workflows → lege UI

**Issue 3: Deprecated N8N_BASIC_AUTH variabelen**
- `N8N_BASIC_AUTH_ACTIVE`, `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD` zijn **deprecated sinds n8n v1.0**
- n8n 2.12.3 (huidige versie) negeert deze vars en gebruikt een owner-setup wizard bij eerste start
- De combinatie van deprecated vars + geen owner account = "ghost UI" (wizard in broken state)
- Bron: [n8n v2.0 breaking changes](https://docs.n8n.io/2-0-breaking-changes/)

**Issue 4: N8N_RUNNERS_ENABLED zonder sidecar**
- `N8N_RUNNERS_ENABLED=true` is gezet
- Sinds n8n 2.0 vereist dit ofwel een aparte `n8nio/runners` container (external mode) of correcte internal mode configuratie
- Zonder sidecar falen Code nodes of starten niet
- Aanbeveling: **verwijder de variabele** (n8n 2.x enablet runners standaard in internal mode)
- Bron: [n8n task runners docs](https://docs.n8n.io/hosting/configuration/task-runners/)

**Issue 5: Geen .env bestand**
- Alleen `.env.dev-os.example` bestaat — het echte `.env` is nooit aangemaakt (of wel aangemaakt maar niet functioneel door bovenstaande issues)

### Bewijs: BORIS-setup heeft identieke fouten
De BORIS docker-compose (`projects/buurts-ecosysteem/docker/docker-compose.dev-os.yml`) bevat exact dezelfde deprecated auth-vars en runners-configuratie. Als BORIS n8n ook niet werkt, is dat dezelfde oorzaak.

## Deliverables

- [ ] **D1**: Fix `docker/docker-compose.dev-os.yml` (alle 4 configuratie-issues)
- [ ] **D2**: Maak minimaal `wf1_devhub_health_check.json` workflow-bestand aan (valideer met n8n MCP validator)
- [ ] **D3**: Update `docker/.env.dev-os.example` (verwijder deprecated vars, documenteer owner-setup)
- [ ] **D4**: Update `docs/operations/N8N_SETUP.md` (correcte poort, nieuwe auth-flow, geen basic auth)
- [ ] **D5**: (Optioneel) Fix ook BORIS docker-compose met dezelfde correcties
- [ ] **D6**: Verificatie — `docker compose up -d` + n8n UI bereikbaar op `localhost:5679`

## Technische richting

> Claude Code mag afwijken — dit is een richtingaanwijzer.

### D1: docker-compose.dev-os.yml wijzigingen

```yaml
# WIJZIG: poort
ports:
  - "5679:5678"   # was: "5678:5678"

# VERWIJDER: deprecated auth (3 regels)
# - N8N_BASIC_AUTH_ACTIVE=true        ← DELETE
# - N8N_BASIC_AUTH_USER=${N8N_USER}   ← DELETE
# - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}  ← DELETE

# VERWIJDER: runners (n8n 2.x doet dit standaard in internal mode)
# - N8N_RUNNERS_ENABLED=true          ← DELETE

# WIJZIG: webhook URL
- WEBHOOK_URL=http://localhost:5679/  # was: localhost:5678

# BEHOUD: deze zijn correct
- N8N_BLOCK_ENV_ACCESS_IN_NODE=false
- GENERIC_TIMEZONE=Europe/Amsterdam
- N8N_DEFAULT_LOCALE=nl
```

### D2: Workflow JSON

Gebruik het BORIS `wf6_boris_heartbeat.json` als structuur-referentie. DevHub health check moet:
- Schedule trigger (dagelijks 18:00 of handmatig)
- HTTP Request naar `dev-os-api` health endpoint (`http://dev-os-api:8001/healthz`)
- Switch node op severity (GREEN/YELLOW/RED)
- Bij YELLOW/RED: GitHub Issue aanmaken (conform ADR-001)

Valideer met de n8n MCP `validate_workflow` tool vóór oplevering.

### D3: .env.dev-os.example

```bash
# n8n Database
N8N_POSTGRES_PASSWORD=changeme

# n8n API (voor MCP/automation)
N8N_API_KEY=changeme

# GitHub integratie
GITHUB_TOKEN=ghp_...

# NB: n8n 2.x gebruikt owner-setup via de UI bij eerste start.
# Er zijn GEEN basic auth variabelen meer nodig.
```

## Afhankelijkheden

| Veld | Waarde |
|------|--------|
| Geblokkeerd door | Geen |
| BORIS impact | Ja — BORIS docker-compose heeft dezelfde fouten (D5) |

## Fase-context

Past in **Fase 0 (fundament)**: n8n is onderdeel van de CI/CD foundation die in de huidige sprint is opgezet. Dit is een bugfix op die sprint, geen nieuwe scope.

## Open vragen voor Claude Code

1. Moeten de Docker volumes (`n8n_data`, `postgres_n8n_data`) eerst verwijderd worden (`docker compose down -v`) om de corrupte n8n state op te ruimen?
2. Wil je de BORIS docker-compose meteen meefixen (D5), of dat apart houden?
3. Is er een reden dat `N8N_RUNNERS_ENABLED` expliciet gezet was? (Zo ja: dan sidecar toevoegen i.p.v. verwijderen)

## DEV_CONSTITUTION impact

| Artikel | Geraakt | Toelichting |
|---------|---------|-------------|
| Art. 3 (Codebase integriteit) | Ja | Docker config wijziging — maar geen destructieve ops |
| Art. 4 (Transparantie) | Ja | Wijzigingen traceerbaar via commit |
| Art. 7 (Impact-zonering) | Ja | YELLOW: infra-wijziging, review gewenst |
| Art. 8 (Dataminimalisatie) | Ja | .env blijft gitignored, geen secrets in commits |
