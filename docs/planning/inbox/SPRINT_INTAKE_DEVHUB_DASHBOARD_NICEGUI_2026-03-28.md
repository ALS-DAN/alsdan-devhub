---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 4
---

# Sprint Intake: DevHub Dashboard — Overkoepelend NiceGUI Web-dashboard

## Doel

Bouw een overkoepelend web-dashboard met NiceGUI dat alle DevHub-domeinen (health, sprint/planning, knowledge, governance, growth) samenbrengt in één lokaal draaiend interface.

## Probleemstelling

DevHub heeft inmiddels een volledige stack — 1082+ tests, 4 packages, 6 agents, 8 skills, governance, kennispipeline — maar er is geen plek waar je in één oogopslag ziet hoe het systeem ervoor staat. De `/devhub-health` skill geeft tekst-output per aanvraag, maar er is:

- **Geen persistent overzicht** — elke health-check is een momentopname die verdwijnt
- **Geen cross-domein inzicht** — health, kennis, governance en groei leven in gescheiden silo's
- **Geen historische trends** — je kunt niet zien of het systeem verbetert of verslechtert over tijd
- **Geen visuele samenvatting** — alles is tekst in de terminal

**Waarom nu:** Fase 3 (Knowledge & Memory) is grotendeels afgerond. De packages (core, storage, vectorstore, documents) zijn operationeel. Het dashboard kan deze packages direct aanspreken als data-bronnen. Dit is ook de eerste Fase 4-sprint (Verbindingen) die direct zichtbaar maakt wat DevHub kan.

**Fase-context:** Fase 4 — Verbindingen. Het dashboard verbindt alle bestaande subsystemen in één interface. Past bij het Event Bus en Agent Teams thema: het dashboard wordt een consumer van events en status-informatie uit de hele stack.

## Framework-keuze: NiceGUI

**Gekozen na SOTA-vergelijking** van NiceGUI, Dash (Plotly), Streamlit, Reflex en Panel.

NiceGUI wint op 5 van 8 dimensies voor DevHub's context:

| Dimensie | NiceGUI | Beste alternatief (Dash) |
|---|---|---|
| Stack-fit | ✅ FastAPI/ASGI native | ❌ Flask/WSGI |
| State management | ✅ direct Python binding | ⚠️ callback-systeem |
| Multi-page/tabs | ✅ native routing + tabs | ⚠️ add-on |
| Testing | ✅ pytest native | ⚠️ Selenium |
| Dependency-profiel | ✅ licht, ASGI-aligned | ⚠️ Flask-mix |
| Visualisatie | ✅ Plotly + ECharts | ✅✅ Plotly native |
| Community | ⚠️ kleiner (~10k stars) | ✅ groot (~24.5k stars) |

**Kernargumenten:**
- NiceGUI draait op FastAPI — dezelfde stack als DevHub. Geen Flask/ASGI conflict.
- State is gewoon Python objecten — geen callback-spaghetti, geen rerun-model.
- Plotly-integratie is native beschikbaar — geen verlies aan chart-kwaliteit.
- `nicegui.testing` integreert met pytest — past bij DevHub's 1082+ test-suite.
- Textual Web (TUI-alternatief) overwogen maar verworpen: minder flexibel voor dashboards met meerdere panelen en charts.

**EVIDENCE-grading:** SILVER — gebaseerd op framework-documentatie, community-vergelijkingen, en productie-ervaring bij Zauberzeug (robotica).

## Deliverables

- [ ] **Nieuw package `packages/devhub-dashboard/`** in uv workspace
  - NiceGUI als dependency
  - Eigen pyproject.toml, standaard DevHub package-structuur
- [ ] **Executive Summary pagina** (landing page)
  - 5-6 KPI-cards bovenaan: tests groen, packages actief, kennis-items, open governance issues, actieve sprint, overall health score
  - Status-indicatoren (groen/geel/rood) per domein
- [ ] **Health paneel** (`/health`)
  - 6-dimensie health check (bestaande health-skill data hergebruiken)
  - Historische trend-grafiek (Plotly)
- [ ] **Sprint & Planning paneel** (`/planning`)
  - Actieve sprint status (uit SPRINT_TRACKER.md)
  - Inbox items overzicht
  - Fase-voortgang visualisatie (0-5)
- [ ] **Knowledge paneel** (`/knowledge`)
  - Kennisbank dekking per domein
  - EVIDENCE-grading verdeling (GOLD/SILVER/BRONZE/SPECULATIVE)
  - Recente research-activiteit
- [ ] **Governance paneel** (`/governance`)
  - DEV_CONSTITUTION compliance overzicht per artikel
  - Security findings (als security scanner data beschikbaar is)
  - Impact-zonering status (GREEN/YELLOW/RED items)
- [ ] **Growth/Mentor paneel** (`/growth`)
  - Skill Radar visualisatie
  - Challenge Engine status
  - T-shape progressie
- [ ] **Research & Kennisverzoeken paneel** (`/research`)
  - **Agent-voorstellen (stroom 2):** kaartjes met research requests die agents hebben gegenereerd via `KnowledgeGapDetected` events. Per kaartje: domein, gap-beschrijving, bron-agent, prioriteit. Acties: Goedkeuren / Afwijzen / Aanpassen.
  - **Niels-verzoeken (stroom 3):** formulier "Onderzoek aanvragen" — topic, domein, diepte (QUICK/STANDARD/DEEP), verwachte output (kennis-artikel, document, of beide). Submitted requests verschijnen in dezelfde queue.
  - **Lopende onderzoeken:** status-tracker per research request — Wachtend / Goedgekeurd / In Uitvoering / Afgerond / Afgewezen. Progressie-indicator.
  - **Auto-kennis log (stroom 1):** read-only overzicht van automatisch bijgewerkte basiskennis (KWP DEV). Wat is er bijgekomen, wat is afgewezen door KnowledgeCurator, freshness-status.
  - **Research-resultaten:** link naar gegenereerde documenten in Google Drive per afgerond onderzoek.
- [ ] **Tests** — pytest suite voor dashboard-componenten, integratietests met devhub-core

## Technische richting

> *Claude Code mag afwijken — dit is een suggestie, geen voorschrift.*

```
packages/devhub-dashboard/
├── pyproject.toml
├── devhub_dashboard/
│   ├── __init__.py
│   ├── app.py              # NiceGUI app entry point
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── overview.py     # Executive summary
│   │   ├── health.py
│   │   ├── planning.py
│   │   ├── knowledge.py
│   │   ├── governance.py
│   │   ├── growth.py
│   │   └── research.py     # Research & Kennisverzoeken
│   ├── components/
│   │   ├── __init__.py
│   │   ├── kpi_card.py     # Herbruikbare KPI card component
│   │   ├── status_badge.py # Groen/geel/rood indicator
│   │   ├── trend_chart.py  # Plotly trend wrapper
│   │   └── research_card.py # Research request kaartje met approve/reject
│   ├── data/
│   │   ├── __init__.py
│   │   └── providers.py    # Data ophalen uit devhub-core, storage, vectorstore
│   └── config.py           # Dashboard configuratie
└── tests/
    ├── __init__.py
    ├── test_app.py
    ├── test_pages.py
    └── test_providers.py
```

**Data-integratie:** De `providers.py` module importeert direct uit de bestaande packages:
- `devhub_core` → health checks, agent status, sprint tracking
- `devhub_storage` → historische data, trends
- `devhub_vectorstore` → kennisbank statistics
- `devhub_documents` → document pipeline status

**Opstarten:** `uv run python -m devhub_dashboard.app` → opent browser op `localhost:8080`

## Afhankelijkheden

- **Geblokkeerd door:** geen — alle benodigde packages (core, storage, vectorstore, documents) zijn operationeel
- **BORIS-impact:** nee — dit is een DevHub-intern dashboard. Kan later uitgebreid worden met node-specifieke views (via BorisAdapter) maar dat is buiten scope.
- **Event Bus relatie:** het dashboard is een Event Bus consumer. Het Research-paneel luistert naar `KnowledgeGapDetected` events om agent-voorstellen te tonen. Event Bus (Sprint 42) is afgerond en operationeel — directe integratie mogelijk.
- **Kennisketen relatie:** het Research-paneel is de menselijke interface voor stroom 2 (agent-geïnitieerde research met Niels-goedkeuring) en stroom 3 (Niels-geïnitieerde research). Geblokkeerd door: Pipeline-sprint (Knowledge Ingestion + Document Production) voor volledige end-to-end flow. Dashboard kan Research Queue tonen zonder werkende pipeline, maar resultaten verschijnen pas na pipeline-sprint.

## Fase-context

**Fase 4 — Verbindingen.** Dit is de eerste sprint die alle Fase 0-3 deliverables visueel verbindt. Past bij het Fase 4 thema naast Agent Teams en Event Bus.

Niels heeft Fase 4 goedkeuring gegeven (zie beslissingen 2026-03-28).

## Open vragen voor Claude Code

1. **NiceGUI versie:** v3.7.1 is actueel — compatibiliteitscheck met uv workspace en bestaande dependencies nodig.
2. **Data refresh:** polling interval of handmatige refresh? NiceGUI's `ui.timer()` maakt auto-refresh triviaal.
3. **Historische data:** waar opslaan? Optie A: devhub-storage (LocalAdapter). Optie B: SQLite naast de app. Optie C: in-memory voor nu, persistent later.
4. **Theming:** Quasar (NiceGUI's default) biedt dark mode out-of-the-box. DevHub-specifiek kleurenschema wenselijk?
5. **Health-skill integratie:** bestaande health-check logica hergebruiken of dupliceren? Liefst hergebruiken via devhub-core imports.
6. **Research Queue persistentie:** waar slaat het dashboard goedgekeurde/afgewezen requests op? Opties: (A) YAML-bestand `config/research_queue.yml`, (B) devhub-storage via LocalAdapter, (C) in-memory + Event Bus history. YAML is simpelst en past bij bestaande config-patronen.
7. **Research-formulier scope:** het Niels-verzoeken formulier (stroom 3) moet minimaal topic + domein + diepte bevatten. Moet het ook een DocumentCategory kiezen (welk type output)? Of bepaalt de pipeline dat automatisch?
8. **Drie-stromen visuele scheiding:** hoe onderscheidt het Research-paneel de drie stromen visueel? Suggestie: tabs ("Agent-voorstellen" / "Mijn verzoeken" / "Auto-kennis log") of kleurcodering.

## DEV_CONSTITUTION impact

- **Art. 3 (Codebase integriteit):** nieuw package — geen destructieve impact op bestaande code
- **Art. 4 (Transparantie):** dashboard maakt systeemstatus juist transparanter
- **Art. 5 (Kennisintegriteit):** dashboard toont EVIDENCE-grading — versterkt Art. 5
- **Art. 7 (Impact-zonering):** GREEN — nieuw package, geen wijzigingen aan bestaande code

## Prioriteit

**Hoog** — Dit dashboard wordt het primaire interface voor DevHub-monitoring en maakt de waarde van alle Fase 0-3 werk zichtbaar. Voor een solo-developer is "in 10 seconden weten hoe het ervoor staat" essentieel.
