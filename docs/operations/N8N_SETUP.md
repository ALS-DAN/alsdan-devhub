# n8n Setup Guide — DevHub

## Prerequisites

- Docker Desktop geïnstalleerd en draaiend
- GitHub Personal Access Token (PAT) met `repo` scope
- Gmail App Password (voor RED-severity notificaties)

## Eerste keer opstarten

### 1. Environment variabelen

```bash
cp .env.example .env
# Vul echte waarden in:
# - N8N_POSTGRES_PASSWORD: sterk wachtwoord
# - N8N_USER / N8N_PASSWORD: n8n login
# - GITHUB_TOKEN: ghp_... met repo scope
# - GMAIL_USER / GMAIL_APP_PASSWORD: zie Google Account → App Passwords
```

### 2. Docker containers starten

```bash
docker compose up -d
```

n8n is bereikbaar op: **http://localhost:5679**

> Port 5679 (niet 5678) om conflict met BORIS n8n te voorkomen.

### 3. Workflow importeren

1. Open http://localhost:5679
2. Log in met N8N_USER / N8N_PASSWORD
3. Ga naar Workflows → Import from File
4. Importeer `n8n/workflows/wf1_devhub_health_check.json`

### 4. Credentials configureren

In n8n UI → Settings → Credentials:

**GitHub PAT:**
- Type: GitHub API
- Token: je GitHub PAT

**Gmail (optioneel, voor RED-severity email):**
- Type: Gmail OAuth2 of SMTP
- Configureer met App Password

### 5. Verificatie

1. Open de "WF-1: DevHub Health Check" workflow
2. Klik op "Execute Workflow" (handmatige trigger)
3. Verifieer dat alle nodes groen draaien
4. Check de output van "Parse & Format Results" voor correct JSON

## Dagelijks gebruik

De Health Check draait automatisch om 18:00 (Europe/Amsterdam).

- **GREEN**: Geen actie, stil
- **YELLOW**: GitHub Issue aangemaakt met label `health-alert` + `P2`
- **RED**: GitHub Issue + email notificatie

## Troubleshooting

### Container start niet
```bash
docker compose logs n8n
docker compose logs postgres-n8n
```

### Health check script faalt
```bash
docker compose exec n8n /scripts/run_health_check.sh /devhub
```

### n8n data resetten
```bash
docker compose down -v  # Verwijdert volumes!
docker compose up -d
```

## Architectuur

Zie `docs/adr/ADR-001-n8n-cicd-architecture.md` voor architectuurbeslissingen.
