# n8n Setup Guide — DevHub

## Prerequisites

- Docker Desktop geïnstalleerd en draaiend
- GitHub Personal Access Token (PAT) met `repo` scope

## Eerste keer opstarten

### 1. Environment variabelen

```bash
cp docker/.env.dev-os.example docker/.env
# Vul echte waarden in:
# - N8N_POSTGRES_PASSWORD: sterk wachtwoord
# - N8N_API_KEY: genereer via n8n UI (Settings → API)
# - GITHUB_TOKEN: ghp_... met repo scope
```

### 2. Docker containers starten

```bash
# Bij eerste keer of na configuratiewijziging: wis oude volumes
docker compose -f docker/docker-compose.dev-os.yml down -v

# Start alle services
docker compose -f docker/docker-compose.dev-os.yml --env-file docker/.env up -d
```

n8n is bereikbaar op: **http://localhost:5679**

> Port 5679 (niet 5678) om conflict met BORIS n8n te voorkomen.

### 3. Owner account aanmaken

Bij eerste start toont n8n een **owner setup wizard**:

1. Open http://localhost:5679
2. Vul je naam, email en wachtwoord in
3. Klik op "Next" om het account aan te maken

> n8n 2.x gebruikt geen basic auth meer. De owner setup wizard vervangt dit.

### 4. Workflow importeren

1. Open http://localhost:5679
2. Ga naar Workflows → Import from File
3. Importeer `docker/n8n-local-files/workflows/wf1_devhub_health_check.json`

### 5. Credentials configureren

In n8n UI → Settings → Credentials:

**GitHub PAT:**
- Type: GitHub API
- Token: je GitHub PAT

### 6. Verificatie

1. Open de "WF-1: DevHub Health Check" workflow
2. Klik op "Execute Workflow" (handmatige trigger)
3. Verifieer dat alle nodes groen draaien
4. Check de output van "Run Health Check" voor correct JSON van dev-os-api

## Dagelijks gebruik

De Health Check draait automatisch om 18:00 (Europe/Amsterdam).

- **GREEN**: Geen actie, stil
- **YELLOW**: GitHub Issue aangemaakt met label `health-alert` + `P2`
- **RED**: GitHub Issue met label `health-alert` + `P1`

## Troubleshooting

### Container start niet
```bash
docker compose -f docker/docker-compose.dev-os.yml logs n8n
docker compose -f docker/docker-compose.dev-os.yml logs postgres-n8n
docker compose -f docker/docker-compose.dev-os.yml logs dev-os-api
```

### Health check handmatig testen
```bash
curl http://localhost:8001/health/run
```

### n8n data resetten
```bash
docker compose -f docker/docker-compose.dev-os.yml down -v  # Verwijdert volumes!
docker compose -f docker/docker-compose.dev-os.yml --env-file docker/.env up -d
```

## Architectuur

Zie `docs/adr/ADR-001-n8n-cicd-architecture.md` voor architectuurbeslissingen.

### Services

| Service | Poort | Functie |
|---------|-------|---------|
| n8n | 5679 (extern) → 5678 (intern) | Workflow automation |
| dev-os-api | 8001 | Health checks, logging, performance tracking |
| postgres-n8n | - (intern) | n8n database |
