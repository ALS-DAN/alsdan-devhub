---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
node: devhub
sprint_type: FEAT
fase: 4
---

# Sprint Intake: Dashboard migratie NiceGUI → FastAPI + Jinja2 + HTMX

## Doel

NiceGUI vervangen door FastAPI + Jinja2 + HTMX als dashboard-framework, zodat het dashboard de volledige visuele kwaliteit en interactiviteit levert die de HTML/CSS/JS mockup demonstreert.

## Probleemstelling

NiceGUI's Quasar/Vue.js-laag blokkeert pixel-precieze styling. NiceGUI v3 heeft CSS layers geïntroduceerd waardoor Quasar-stijlen prioriteit krijgen boven custom CSS ([Discussion #5240](https://github.com/zauberzeug/nicegui/discussions/5240)). De Plotly-integratie heeft bekende issues met resizing en positie na updates. Het resultaat: disproportionele effort voor een visueel niveau dat een pure HTML/CSS mockup wél moeiteloos levert.

De bestaande mockup (`MOCKUP_DASHBOARD_BESTAANDE_PANELEN_V2_2026-03-29.html`) demonstreert het gewenste niveau: dark theme, 8 pagina's, Plotly charts, info-tooltips, interactieve elementen. Die mockup is pure HTML/CSS/JS — geen framework nodig voor de visuele laag.

**Waarom nu:** het dashboard is een Fase 4-deliverable. De huidige NiceGUI-implementatie (6.840 regels) kan niet groeien naar de gewenste kwaliteit zonder constant tegen het framework te vechten. Hoe langer we doorbouwen op NiceGUI, hoe meer code we later moeten weggooien.

## Oplossing op hoofdlijnen

### Architectuur

```
Browser ←→ FastAPI (uvicorn) ←→ Bestaande data-laag (providers)
  ↑                ↑
  HTMX          Jinja2 templates
  (interactie)  (gebaseerd op mockup)
```

### Stack

| Component | Technologie | Waarom |
|-----------|-------------|--------|
| Server | **FastAPI** | Async, modern, al bekend in DevHub-ecosysteem |
| Templates | **Jinja2** | Standaard bij FastAPI, mockup-HTML wordt direct template |
| Interactiviteit | **HTMX** | Partial page updates, formulier submits, Quick Actions — zonder JavaScript te schrijven. CDN script-tag, geen Python dependency |
| Charts | **Plotly** (blijft) | `fig.to_html(full_html=False)` rendert charts server-side als HTML-fragmenten |
| Styling | **Eigen CSS** (uit mockup) | 100% controle, geen framework-overrides |

### Wat HTMX doet

HTMX vervangt de noodzaak voor custom JavaScript bij interactieve elementen:

- **Quick Actions** (refresh health, update radar, etc.): `hx-post="/api/actions/refresh-health"` op de knop → FastAPI endpoint roept provider aan → stuurt HTML-fragment terug → HTMX vervangt het target-element
- **Reflectie formulier**: `hx-post="/api/reflections"` → server verwerkt, stuurt bevestiging terug
- **Pagina-navigatie**: gewone links (`<a href="/health">`) — geen HTMX nodig
- **Live data refresh**: `hx-get="/partials/health-kpis" hx-trigger="every 30s"` voor automatische updates

## Deliverables

- [ ] FastAPI app met routing voor alle pagina's (Overview, Health, Planning, Knowledge, Governance, Profile, Research, Projects)
- [ ] Jinja2 templates gebaseerd op de bestaande mockup (`MOCKUP_DASHBOARD_BESTAANDE_PANELEN_V2_2026-03-29.html`)
- [ ] Jinja2 base template met navigatie, dark theme CSS, Plotly CDN, HTMX CDN
- [ ] `static/` map met CSS en eventuele JS (minimal)
- [ ] HTMX-interactie voor: Quick Actions, formulieren, partial page updates
- [ ] Plotly charts server-side gerenderd via providers → `fig.to_html()`
- [ ] NiceGUI volledig verwijderd uit package
- [ ] Bestaande data-laag ongewijzigd aangesloten
- [ ] Tests: FastAPI endpoint tests (vervangen NiceGUI UI tests)
- [ ] `pyproject.toml` bijgewerkt: `nicegui` → `fastapi`, `jinja2`, `uvicorn[standard]`

## Wat blijft ongewijzigd

De volledige data-laag (1.917 regels, 0 NiceGUI imports):

| Bestand | Regels | Functie |
|---------|--------|---------|
| `data/providers.py` | 754 | Health, Planning, Governance, Growth providers |
| `data/sprint_tracker_parser.py` | 336 | SPRINT_TRACKER.md parser |
| `data/knowledge_provider.py` | 228 | Knowledge artikelen provider |
| `data/research_queue.py` | 206 | Research queue management |
| `data/article_parser.py` | 245 | Artikel content parser |
| `data/history.py` | 93 | Historische data opslag |
| `data/event_listener.py` | 54 | Event bus listener |
| `config.py` | 35 | DashboardConfig dataclass |

Tests voor de data-laag (test_providers.py, test_sprint_tracker_parser.py, test_knowledge_provider.py, test_article_parser.py, test_research.py, test_new_providers.py, test_history.py, test_events.py) blijven ongewijzigd.

## Wat wordt verwijderd

| Map | Regels | Reden |
|-----|--------|-------|
| `pages/` (9 bestanden) | 1.931 | NiceGUI `ui.*` calls → vervangen door Jinja2 templates |
| `components/` (8 bestanden) | 476 | NiceGUI widgets → vervangen door HTML in templates |
| `app.py` (NiceGUI routing) | 201 | Vervangen door FastAPI app |
| NiceGUI-specifieke tests | ~300 | test_pages.py, test_components.py, test_governance_growth.py, test_knowledge_pages.py (deels) |

## Wat nieuw wordt aangemaakt

```
packages/devhub-dashboard/
├── devhub_dashboard/
│   ├── app.py                    # HERSCHREVEN — FastAPI app + routing
│   ├── config.py                 # ONGEWIJZIGD
│   ├── data/                     # ONGEWIJZIGD (hele map)
│   ├── templates/
│   │   ├── base.html             # NIEUW — layout, nav, CSS, CDN imports
│   │   ├── overview.html         # NIEUW — gebaseerd op mockup
│   │   ├── health.html           # NIEUW
│   │   ├── planning.html         # NIEUW
│   │   ├── knowledge.html        # NIEUW
│   │   ├── knowledge_detail.html # NIEUW
│   │   ├── governance.html       # NIEUW
│   │   ├── profile.html          # NIEUW (vervangt growth)
│   │   ├── research.html         # NIEUW
│   │   ├── research_detail.html  # NIEUW
│   │   ├── projects.html         # NIEUW
│   │   └── partials/             # NIEUW — HTMX fragmenten
│   │       ├── health_kpis.html
│   │       ├── activity_stream.html
│   │       ├── quick_action_result.html
│   │       └── reflection_form.html
│   └── static/
│       ├── css/
│       │   └── dashboard.css     # NIEUW — uit mockup geëxtraheerd
│       └── js/
│           └── charts.js         # NIEUW — Plotly init functies (minimaal)
├── tests/
│   ├── test_app.py               # HERSCHREVEN — FastAPI TestClient
│   ├── test_endpoints.py         # NIEUW — API endpoint tests
│   ├── test_templates.py         # NIEUW — template rendering tests
│   ├── test_providers.py         # ONGEWIJZIGD
│   ├── test_sprint_tracker_parser.py  # ONGEWIJZIGD
│   ├── test_knowledge_provider.py     # ONGEWIJZIGD
│   ├── test_article_parser.py         # ONGEWIJZIGD
│   ├── test_research.py               # ONGEWIJZIGD
│   ├── test_new_providers.py          # ONGEWIJZIGD
│   ├── test_history.py                # ONGEWIJZIGD
│   └── test_events.py                 # ONGEWIJZIGD
└── pyproject.toml                # BIJGEWERKT — dependencies
```

## Migratiestrategie

Drie stappen, geen big bang:

### Stap 1: FastAPI naast NiceGUI (proof of concept)
- FastAPI app opzetten met base template + Overview pagina
- Eén complexe interactie testen (Quick Action via HTMX)
- Beide apps kunnen tijdelijk naast elkaar bestaan (verschillende poorten)
- **Gate:** als HTMX-interactie niet werkt zoals verwacht → stoppen en herbeoordelen

### Stap 2: Alle pagina's migreren
- Per pagina: mockup-HTML → Jinja2 template + FastAPI route + HTMX attributen
- Volgorde: Health → Planning → Knowledge → Governance → Profile → Research → Projects
- Per pagina test schrijven

### Stap 3: NiceGUI verwijderen
- `pages/` en `components/` mappen verwijderen
- `nicegui` uit `pyproject.toml`
- NiceGUI-specifieke tests verwijderen
- app.py is nu puur FastAPI
- Alle tests groen

## Afhankelijkheden

| Afhankelijkheid | Status |
|----------------|--------|
| Geblokkeerd door | Geen |
| BORIS impact | Nee — intern DevHub dashboard |
| Mockup als basis | `MOCKUP_DASHBOARD_BESTAANDE_PANELEN_V2_2026-03-29.html` (bestaat) |
| Profile pagina data | Vereist nieuwe providers (EvidenceCollector etc.) — **aparte sprint** |

## Fase-context

Fase 4 (Verbindingen). Het dashboard is een kerndeliverable van Fase 4. Deze migratie versterkt de basis waarop verdere uitbreidingen (Profile pagina, nieuwe panelen) gebouwd worden. Door nu te migreren voorkom je dat elke toekomstige feature tweemaal gebouwd moet worden (NiceGUI + gewenst resultaat).

## Risico's

| Risico | Ernst | Mitigatie |
|--------|-------|-----------|
| HTMX onvoldoende voor complexe interactie | Middel | Stap 1 test de complexste interactie eerst (PoC gate) |
| Template-onderhoud naast Python | Laag | Templates zijn stabiel na initiële opzet; data-laag verandert vaker |
| Plotly server-side rendering performance | Laag | `to_html()` is bewezen patroon; caching indien nodig |

## Open vragen voor Claude Code

1. **HTMX versie:** HTMX 1.x of 2.x? 2.x heeft breaking changes maar betere WebSocket support.
2. **Template engine:** pure Jinja2 of Jinja2 via `fastapi.templating.Jinja2Templates`? (Standaard FastAPI aanpak is de tweede.)
3. **Static files:** FastAPI `StaticFiles` mount of apart serveren? (StaticFiles is standaard en simpelst.)
4. **Test approach:** `httpx.AsyncClient` met FastAPI TestClient voor endpoint tests. Bestaande data-tests ongewijzigd.
5. **CSS extractie:** de mockup heeft inline `<style>` — extraheren naar `static/css/dashboard.css` of inline laten in base template? (Extern bestand is beter voor caching.)

## DEV_CONSTITUTION impact

| Artikel | Impact |
|---------|--------|
| Art. 3 (Codebase integriteit) | Destructieve operatie: NiceGUI pages/components verwijderen. Expliciet beschreven in migratiestrategie. |
| Art. 4 (Transparantie) | Migratie traceerbaar via commits per stap. |
| Art. 7 (Impact-zonering) | **YELLOW** — framework-wissel raakt het hele dashboard-package. Data-laag ongeraakt. Mitigatie: stapsgewijze migratie met PoC gate. |

## Prioriteit

**Hoog** — blokkeert verdere dashboard-uitbreiding (Profile pagina, nieuwe panelen). Hoe langer NiceGUI blijft, hoe meer code dubbel werk wordt.
