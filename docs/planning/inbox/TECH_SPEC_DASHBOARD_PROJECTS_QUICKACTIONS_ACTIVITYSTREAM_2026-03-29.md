---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
type: TECHNICAL_SPECIFICATION
hoort_bij: SPRINT_INTAKE_DEVHUB_DASHBOARD_NICEGUI_2026-03-28.md
---

# Technische Specificatie: Project Pagina + Quick Actions + Activity Stream

Aanvulling op het dashboard-ecosysteem. Voegt drie cross-cutting features toe: een 8e top-level pagina (`/projects`), een dashboard-breed Quick Actions systeem, en een Activity Stream als visueel venster op het EventBus-systeem.

---

## 1. Project Pagina (`/projects`)

### 1.1 Positie in navigatie

8e top-level pagina, na Research. Route: `/projects`. NiceGUI: `@ui.page('/projects')`.

### 1.2 Twee-sectie layout

De pagina onderscheidt twee categorieën projecten die fundamenteel anders werken:

**Sectie A: Workspace Packages** — interne DevHub-bouwblokken uit `packages/`. Leven in de DevHub-repo, geen eigen adapter of node-registratie.

**Sectie B: Managed Projects** — externe projecten met eigen repo, geregistreerd in `config/nodes.yml`, aanwezig als git submodule in `projects/`.

### 1.3 Sectie A: Workspace Packages

#### Data-bronnen

```python
# Package discovery via pyproject.toml scanning
from pathlib import Path
import tomllib

def discover_workspace_packages(root: Path) -> list[PackageInfo]:
    """Scan packages/ directory voor workspace packages."""
    packages = []
    for pyproject in sorted(root.glob("packages/*/pyproject.toml")):
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        project = data.get("project", {})
        packages.append(PackageInfo(
            name=project.get("name", pyproject.parent.name),
            version=project.get("version", "0.0.0"),
            description=project.get("description", ""),
            path=pyproject.parent,
            dependencies=_extract_internal_deps(project.get("dependencies", [])),
        ))
    return packages
```

#### Dataclasses

```python
@dataclass(frozen=True)
class PackageInfo:
    """Workspace package metadata."""
    name: str
    version: str
    description: str
    path: Path
    dependencies: list[str]  # Interne devhub-* dependencies
    test_count: int = 0
    pass_rate: float = 1.0

@dataclass(frozen=True)
class PackageDependencyEdge:
    """Afhankelijkheid tussen workspace packages."""
    source: str  # Package dat importeert
    target: str  # Package dat geïmporteerd wordt
```

#### Visuele componenten

1. **Dependency Graph** — Plotly network graph of Mermaid diagram
   - Nodes = packages, edges = interne dependencies
   - Node-grootte = relatief aan test_count
   - Node-kleur = RAG op basis van pass_rate
   - Huidige packages: devhub-core → devhub-storage, devhub-core → devhub-vectorstore, devhub-core → devhub-documents

2. **Package Tabel** — sorteerbare kolommen
   | Kolom | Bron | Voorbeeld |
   |-------|------|-----------|
   | Naam | pyproject.toml `name` | devhub-core |
   | Versie | pyproject.toml `version` | v0.2.0 |
   | Status | RAG badge op test health | 🟢 |
   | Tests | pytest count per package | 847 |
   | Deps | Aantal interne dependencies | 0 |
   | Beschrijving | pyproject.toml `description` | Core contracts en agents |

### 1.4 Sectie B: Managed Projects

#### Data-bronnen

```python
from devhub_core.registry import NodeRegistry

class ProjectProvider:
    """Data provider voor de /projects pagina."""

    def __init__(self, root: Path):
        self.root = root
        self.registry = NodeRegistry(root / "config" / "nodes.yml")

    def get_managed_projects(self) -> list[ManagedProjectInfo]:
        projects = []
        for node_id in self.registry.list_nodes():
            config = self.registry.get_config(node_id)
            # Adapter reachability check
            adapter_ok, adapter_error = self._check_adapter(node_id)
            # NodeReport ophalen (als adapter bereikbaar)
            report = None
            if adapter_ok:
                try:
                    report = self.registry.get_report(node_id)
                except Exception as e:
                    adapter_error = str(e)
            # Plugin integratie check
            integration = self._check_integration(config)
            projects.append(ManagedProjectInfo(
                node_id=node_id,
                config=config,
                adapter_reachable=adapter_ok,
                adapter_error=adapter_error,
                report=report,
                integration=integration,
            ))
        return projects

    def _check_adapter(self, node_id: str) -> tuple[bool, str | None]:
        """Test of adapter importeerbaar en bereikbaar is."""
        try:
            self.registry.get_adapter(node_id)
            return True, None
        except Exception as e:
            return False, str(e)

    def _check_integration(self, config) -> IntegrationStatus:
        """Bepaal DevHub-integratieniveau per project."""
        project_path = Path(config.path) if hasattr(config, 'path') else None
        has_adapter = project_path and (project_path / "devhub_integration").exists()
        has_plugin_json = project_path and (project_path / "plugin.json").exists()
        has_project_agents = project_path and list((project_path / ".claude" / "agents").glob("*.md")) if project_path and (project_path / ".claude" / "agents").exists() else []
        devagents_enabled = getattr(config, 'devagents_enabled', False)

        # Niveau bepaling
        if not has_adapter:
            level = IntegrationLevel.NONE
        elif not devagents_enabled:
            level = IntegrationLevel.BASIS
        elif not has_plugin_json:
            level = IntegrationLevel.ACTIEF
        else:
            level = IntegrationLevel.VOLLEDIG

        return IntegrationStatus(
            level=level,
            has_adapter=has_adapter,
            has_plugin_json=has_plugin_json,
            devagents_enabled=devagents_enabled,
            project_agents=len(has_project_agents) if has_project_agents else 0,
            available_skills=self._count_available_skills(),
            available_agents=self._count_available_agents(),
        )

    def _count_available_skills(self) -> int:
        """Tel DevHub plugin skills."""
        return len(list(self.root.glob(".claude/skills/devhub-*")))

    def _count_available_agents(self) -> int:
        """Tel DevHub plugin agents."""
        return len(list(self.root.glob("agents/*.md")))
```

#### Dataclasses

```python
from enum import Enum

class IntegrationLevel(Enum):
    NONE = "none"          # 🔴 Geen adapter
    BASIS = "basis"        # 🟡 Adapter + registratie
    ACTIEF = "actief"      # 🟢 + devagents_enabled + sprint tracking
    VOLLEDIG = "volledig"  # 🔵 + eigen plugin.json + alle skills

@dataclass(frozen=True)
class IntegrationStatus:
    """DevHub plugin integratie-assessment per project."""
    level: IntegrationLevel
    has_adapter: bool
    has_plugin_json: bool
    devagents_enabled: bool
    project_agents: int       # Eigen .claude/agents/ count
    available_skills: int     # DevHub plugin skills beschikbaar
    available_agents: int     # DevHub plugin agents beschikbaar

@dataclass(frozen=True)
class ManagedProjectInfo:
    """Volledig profiel van een managed project."""
    node_id: str
    config: object            # NodeConfig
    adapter_reachable: bool
    adapter_error: str | None
    report: object | None     # NodeReport (als adapter bereikbaar)
    integration: IntegrationStatus
```

#### Visuele componenten per project

1. **Project Card** (PatternFly Aggregate Status patroon)
   - Header: naam + node_id + tags als badges
   - Adapter status: ✅/❌ met klasse-naam
   - Health strip: 4 mini-KPIs (status, tests, pass_rate, coverage)
   - Doc strip: total_pages, stale_pages
   - Integration level badge: 🔴/🟡/🟢/🔵 met label
   - "Details →" link naar detail-subpagina

2. **Project Detail Subpagina** (`/projects/{node_id}`)
   - Full NodeReport data
   - Sprint activiteit (gefilterd uit SPRINT_TRACKER op `node: boris-buurts`)
   - Observations lijst
   - DevHub Integration deep-dive (sectie 1.5)

### 1.5 DevHub Plugin Integratie Sectie

Per managed project op de detail-subpagina een dedicated blok:

#### Adapter Laag

| Check | Methode | BORIS status |
|-------|---------|-------------|
| `devhub_integration/` map aanwezig | Glob op project path | ✅ |
| Geregistreerd in `nodes.yml` | NodeRegistry.list_nodes() | ✅ boris-buurts |
| Adapter importeerbaar | try/except get_adapter() | ✅ BorisAdapter |
| `devagents_enabled` | NodeConfig attribuut | ✅ true |

#### Plugin Adoptie

| Categorie | Bron | Telling |
|-----------|------|---------|
| DevHub agents beschikbaar | `agents/*.md` | 7 (dev-lead, coder, reviewer, researcher, planner, red-team, knowledge-curator) |
| DevHub skills beschikbaar | `.claude/skills/devhub-*/` | 10 |
| Project-eigen agents | `projects/{id}/.claude/agents/` | 4 (BORIS) |
| Project plugin.json | `projects/{id}/plugin.json` | ❌ (BORIS heeft er geen) |

#### Integratie-diepte Meter

Visuele indicator met vier niveaus:

```
🔴 Geen ─── 🟡 Basis ─── 🟢 Actief ─── 🔵 Volledig
                                ▲
                          BORIS staat hier
```

Implementatie: CSS progress bar met 4 stappen, actieve stap gehighlight.

---

## 2. Quick Actions Systeem

### 2.1 SOTA-onderbouwing

| Patroon | Bron | Toepassing |
|---------|------|------------|
| **Command Palette** | Linear, VS Code, Raycast (2025) | Globale `Cmd+K` zoekbalk die overal beschikbaar is, filtert over alle acties |
| **Contextual Self-Service Actions** | Port.io, Backstage (CNCF 2025) | Acties die veranderen op basis van huidige pagina-context |
| **Runbook Automation** | Datadog, PagerDuty, Grafana Incident (2025) | Voorgedefinieerde procedures met één-klik uitvoering en traceerbare output |
| **Internal Developer Portal Actions** | Backstage Scaffolder (CNCF 2024) | Template-driven acties met formulier-input en real-time log streaming |
| **Dashboard-as-Command-Center** | Vercel Deploy Dashboard (2025) | Dashboard is niet alleen informatief maar ook actionable — elke metric heeft een bijbehorende actie |

**EVIDENCE-grading:** SILVER — gebaseerd op framework-documentatie (Backstage, Port.io), industriestandaarden (CNCF), en productie-implementaties (Vercel, Linear, Datadog).

### 2.2 Architectuur: drie lagen

```
┌─────────────────────────────────────────────┐
│  NiceGUI Dashboard                          │
│                                             │
│  ┌──────────┐  ┌──────────────────────────┐ │
│  │ Cmd+K    │  │ Pagina-content           │ │
│  │ Command  │  │                          │ │
│  │ Palette  │  │  [Contextual Actions]    │ │
│  └────┬─────┘  └──────────────────────────┘ │
│       │                                     │
│  ┌────▼────────────────────────────────────┐ │
│  │  Activity Stream (chat-formatted)       │ │
│  │  🔍 Health check gestart...             │ │
│  │  ✅ Tests: 1424 groen                   │ │
│  │  ⚠️ Dependencies: 2 outdated            │ │
│  └────┬────────────────────────────────────┘ │
└───────┼─────────────────────────────────────┘
        │
   ┌────▼─────┐
   │ EventBus │ ← publiceert typed events
   └────┬─────┘
        │
   ┌────▼──────────────┐
   │ Action Executors   │
   │ (Python backends)  │
   │ - HealthProvider   │
   │ - SprintTracker    │
   │ - NodeRegistry     │
   │ - GovernanceCheck  │
   └───────────────────┘
```

**Laag 1: Command Palette** — globaal, `Cmd+K` keyboard shortcut, zoekt over alle beschikbare acties.
**Laag 2: Contextual Actions** — per pagina, de 3-4 meest relevante acties prominent zichtbaar als knoppen.
**Laag 3: Activity Stream** — globaal paneel (onderaan of zijkant), toont EventBus events in chat-formaat.

### 2.3 Command Palette implementatie

```python
# NiceGUI Command Palette component
from nicegui import ui

class CommandPalette:
    """Globale Cmd+K command palette voor het dashboard."""

    def __init__(self):
        self.actions: list[QuickAction] = []
        self.visible = False

    def register(self, action: QuickAction):
        self.actions.append(action)

    def render(self):
        """Render als overlay dialog met zoekbalk."""
        with ui.dialog() as self.dialog:
            with ui.card().classes('w-96'):
                self.search = ui.input(
                    placeholder='Zoek actie...',
                    on_change=self._filter,
                ).classes('w-full')
                self.results = ui.column().classes('w-full max-h-64 overflow-y-auto')

        # Keyboard shortcut: Cmd+K / Ctrl+K
        ui.keyboard(on_key=self._handle_key)

    def _filter(self, e):
        query = e.value.lower()
        self.results.clear()
        with self.results:
            for action in self.actions:
                if query in action.label.lower() or query in action.page.lower():
                    self._render_action_row(action)

    def _render_action_row(self, action: QuickAction):
        with ui.row().classes('items-center gap-2 p-2 hover:bg-gray-700 cursor-pointer rounded'):
            ui.label(action.icon).classes('text-lg')
            with ui.column().classes('gap-0'):
                ui.label(action.label).classes('text-sm font-medium')
                ui.label(action.page).classes('text-xs text-gray-500')
            ui.button(icon='play_arrow', on_click=lambda: self._execute(action)).props('flat dense')


@dataclass
class QuickAction:
    """Eén uitvoerbare actie in het dashboard."""
    id: str
    label: str
    icon: str
    page: str               # Welke pagina (voor filtering + contextueel tonen)
    category: str            # health | planning | governance | growth | knowledge | research | projects
    executor: Callable       # Python functie die de actie uitvoert
    requires_input: bool = False  # Heeft het actie een formulier nodig?
    description: str = ""
```

### 2.4 Contextual Actions per pagina

#### Overview

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Full System Pulse | 🔍 | `HealthProvider.run_all_checks()` | HealthDegraded (als nodig) |
| Generate Status Report | 📋 | `StatusReportGenerator.generate()` | ObservationEmitted |
| Decay Scan | ⏳ | `KnowledgeProvider.check_freshness()` | KnowledgeGapDetected |

#### Health

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Run Dimension Check | 🩺 | `HealthProvider.check_dimension(dim)` | HealthDegraded |
| Dependency Audit | 📦 | `HealthProvider.check_dependencies()` | ObservationEmitted |
| Test Regression Check | 🧪 | `HealthProvider.check_tests()` | ObservationEmitted |

#### Planning

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Start Sprint Prep | 🚀 | `PlanningProvider.start_sprint_prep()` | SprintStarted |
| Close Sprint | ✅ | `PlanningProvider.close_sprint()` | SprintClosed |
| New Intake | 📝 | Opent formulier → schrijft naar inbox/ | — (file write) |
| Recalculate Velocity | 📊 | `SprintTrackerParser.recalculate()` | ObservationEmitted |

#### Knowledge

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Freshness Scan | 🔄 | `KnowledgeProvider.scan_freshness()` | KnowledgeGapDetected |
| Ingest Document | 📥 | Opent upload formulier → ingest pipeline | ObservationEmitted |
| Coverage Check | 🗺️ | `KnowledgeProvider.check_coverage()` | KnowledgeGapDetected |

#### Governance

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Compliance Audit | 🛡️ | `GovernanceProvider.full_audit()` | ObservationEmitted |
| Security Scan | 🔒 | `SecurityProvider.run_asi_audit()` | ObservationEmitted |
| Impact Check | ⚖️ | Opent formulier → zonering result | — (instant) |

#### Growth

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Update Skill Radar | 📡 | `GrowthProvider.reload_radar()` | ObservationEmitted |
| Next Challenge | 🎯 | `GrowthProvider.next_challenge()` | — (instant) |
| Learning Scan | 📚 | `GrowthProvider.scan_resources()` | KnowledgeGapDetected |

#### Research

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Submit Research Question | ❓ | Opent formulier → RESEARCH_VOORSTEL in inbox/ | — (file write) |
| Run Research Loop | 🔬 | `ResearchProvider.execute_loop(rq_id)` | ObservationEmitted |
| Grade Evidence | ⭐ | Opent formulier → GOLD/SILVER/BRONZE/SPECULATIVE | — (instant) |

#### Projects

| Actie | Icoon | Executor | Events |
|-------|-------|----------|--------|
| Check Adapter | 🔌 | `ProjectProvider.check_adapter(node_id)` | ObservationEmitted |
| Sync Submodule | 🔄 | `git submodule update --remote` | — (git operation) |
| Project Health | 🏥 | `registry.get_report(node_id)` | HealthDegraded |
| Integration Scan | 🧩 | `ProjectProvider.check_integration(node_id)` | ObservationEmitted |

### 2.5 Contextual Actions component

```python
class ContextualActions:
    """Toon 3-4 meest relevante acties per pagina."""

    def __init__(self, palette: CommandPalette):
        self.palette = palette

    def render_for_page(self, page_name: str):
        """Render action bar voor een specifieke pagina."""
        actions = [a for a in self.palette.actions if a.page == page_name][:4]
        with ui.row().classes('gap-2 mb-4'):
            for action in actions:
                ui.button(
                    f'{action.icon} {action.label}',
                    on_click=lambda a=action: self._execute(a),
                ).props('outline').classes('text-sm')
```

---

## 3. Activity Stream

### 3.1 SOTA-onderbouwing

| Patroon | Bron | Toepassing |
|---------|------|------------|
| **Live Deploy Logs** | Vercel (2025) | Real-time chat-formatted log van build/deploy stappen |
| **Live Workflow Output** | GitHub Actions (2025) | Stap-voor-stap feedback tijdens workflow execution |
| **Scaffolder Live Feed** | Backstage (CNCF 2024) | Template-actie toont progressie als berichten-stroom |
| **ChatOps Event Feed** | Mattermost, Slack Workflows (2025) | Systeem-events weergegeven in chat-formaat met icoon + beschrijving + timestamp |

**EVIDENCE-grading:** SILVER — industriestandaard patroon bij developer tooling.

### 3.2 Geen AI — puur EventBus visualisatie

De Activity Stream is **geen AI-chatvenster**. Het is een visueel venster op het EventBus-systeem. Elke event wordt geformateerd als een chat-achtig bericht met:

- Icoon (per event type)
- Beschrijving (menselijk leesbaar)
- Timestamp
- Optioneel: status badge (success/warning/error)

### 3.3 Event-to-Message mapping

```python
EVENT_TEMPLATES = {
    "SprintStarted": ("🚀", "Sprint {sprint_id} gestart: {naam}"),
    "SprintClosed": ("✅", "Sprint {sprint_id} afgerond — {tests_delta:+d} tests"),
    "TaskCompleted": ("📋", "Taak afgerond: {task_name}"),
    "TaskFailed": ("❌", "Taak gefaald: {task_name} — {reason}"),
    "QACompleted": ("🧪", "QA check compleet: {pass_count}/{total_count} passed"),
    "HealthDegraded": ("⚠️", "Health degraded: {component} → {status}"),
    "KnowledgeGapDetected": ("🔍", "Kennislacune: {domain} — {description}"),
    "ObservationEmitted": ("💡", "{observation}"),
    "DocGenRequested": ("📄", "Document generatie aangevraagd: {doc_type}"),
    "SecurityFinding": ("🔒", "Security finding: {asi_id} — {severity}"),
}
```

### 3.4 NiceGUI implementatie

```python
class ActivityStream:
    """Chat-formatted event stream als dashboard component."""

    def __init__(self, event_bus, max_messages: int = 50):
        self.event_bus = event_bus
        self.max_messages = max_messages
        self.messages: list[StreamMessage] = []

    def render(self, position: str = "bottom"):
        """Render als collapsible paneel onderaan of zijkant."""
        with ui.expansion('Activity Stream', icon='timeline').classes('w-full'):
            self.container = ui.column().classes('w-full max-h-64 overflow-y-auto gap-1 p-2')
            self._render_messages()

    def add_message(self, icon: str, text: str, level: str = "info"):
        """Voeg bericht toe en update UI."""
        msg = StreamMessage(
            icon=icon,
            text=text,
            timestamp=datetime.now(),
            level=level,
        )
        self.messages.insert(0, msg)
        if len(self.messages) > self.max_messages:
            self.messages.pop()
        self._render_messages()

    def _render_messages(self):
        self.container.clear()
        with self.container:
            for msg in self.messages:
                with ui.row().classes('items-center gap-2 text-sm'):
                    ui.label(msg.icon)
                    ui.label(msg.text).classes('flex-1')
                    ui.label(msg.timestamp.strftime('%H:%M')).classes('text-gray-500 text-xs')


@dataclass
class StreamMessage:
    icon: str
    text: str
    timestamp: datetime
    level: str = "info"  # info | success | warning | error
```

### 3.5 Quick Action ↔ Activity Stream koppeling

Wanneer een Quick Action wordt uitgevoerd:

1. Stream toont: `🔍 {actie.label} gestart...`
2. Executor draait (async waar mogelijk)
3. Executor publiceert events naar EventBus
4. EventBus events verschijnen in Stream als geformatteerde berichten
5. Stream toont: `✅ {actie.label} afgerond` of `❌ {actie.label} gefaald: {error}`

```python
async def execute_action(action: QuickAction, stream: ActivityStream):
    """Voer actie uit met Activity Stream feedback."""
    stream.add_message(action.icon, f"{action.label} gestart...", "info")
    try:
        result = await action.executor()
        stream.add_message("✅", f"{action.label} afgerond", "success")
        return result
    except Exception as e:
        stream.add_message("❌", f"{action.label} gefaald: {e}", "error")
        raise
```

---

## 4. Bestandsstructuur na implementatie

### Nieuwe bestanden

```
packages/devhub-dashboard/devhub_dashboard/
├── pages/
│   └── projects.py              # NIEUW — /projects pagina
├── components/
│   ├── command_palette.py       # NIEUW — Cmd+K command palette
│   ├── contextual_actions.py    # NIEUW — per-pagina actie-knoppen
│   ├── activity_stream.py       # NIEUW — chat-formatted event stream
│   ├── integration_meter.py     # NIEUW — 4-staps integratie indicator
│   └── dependency_graph.py      # NIEUW — workspace package graph
├── data/
│   └── providers.py             # UITBREIDEN met ProjectProvider
└── actions/
    ├── __init__.py              # NIEUW
    ├── registry.py              # NIEUW — QuickAction registratie
    ├── health_actions.py        # NIEUW — Health executors
    ├── planning_actions.py      # NIEUW — Planning executors
    ├── governance_actions.py    # NIEUW — Governance executors
    ├── growth_actions.py        # NIEUW — Growth executors
    ├── knowledge_actions.py     # NIEUW — Knowledge executors
    ├── research_actions.py      # NIEUW — Research executors
    └── project_actions.py       # NIEUW — Project executors
```

### Uitgebreide bestanden

| Bestand | Wijziging |
|---------|-----------|
| `app.py` | Nieuwe route `/projects`, `/projects/{node_id}`. Command palette + Activity Stream initialisatie in layout. Keyboard handler voor Cmd+K. |
| `providers.py` | `ProjectProvider` class toevoegen |
| Elke `pages/*.py` | `ContextualActions.render_for_page()` call toevoegen bovenaan |

### Totaal: 13 nieuwe bestanden, 9+ uitgebreide bestanden

---

## 5. Test strategie

### Nieuwe tests (~30-40)

| Test | Type | Dekt |
|------|------|------|
| `test_project_provider.py` | Unit | PackageInfo discovery, ManagedProjectInfo opbouw, IntegrationLevel bepaling |
| `test_command_palette.py` | Unit | Actie-registratie, filtering, uitvoering |
| `test_activity_stream.py` | Unit | Message toevoegen, max_messages cap, event-to-message mapping |
| `test_contextual_actions.py` | Unit | Juiste acties per pagina, filtering |
| `test_integration_meter.py` | Unit | 4 niveaus correct berekend voor diverse configs |
| `test_quick_actions_*.py` | Integration | Elke actie draait succesvol tegen test fixtures |
| `test_projects_page.py` | Integration | NiceGUI page rendering met mock data |

### Bestaande tests

Geen impact — dit zijn nieuwe bestanden en uitbreidingen. Bestaande 1424+ tests blijven ongewijzigd.

---

## 6. Open vragen voor Claude Code

1. **Command Palette keyboard binding**: NiceGUI's `ui.keyboard()` ondersteunt key events. Is `Cmd+K` / `Ctrl+K` betrouwbaar cross-platform? Alternatief: dedicated knop in header.

2. **Activity Stream persistentie**: In-memory verliest historie bij restart. Optie A: EventBus history (al beschikbaar). Optie B: file-based log. Optie C: in-memory is voldoende voor v1.

3. **Async executors**: Sommige acties (git submodule sync, security scan) kunnen lang duren. NiceGUI's `ui.timer()` of `asyncio` voor non-blocking execution? Aanbeveling: `run.io_bound()` wrapper.

4. **Project detail subpagina**: NiceGUI ondersteunt `@ui.page('/projects/{node_id}')` met path parameters. Is FastAPI-style routing stabiel genoeg voor dynamische pagina's?

5. **Package test counts**: Per-package test count vereist `pytest --collect-only -q packages/devhub-core/` parsing. Acceptabel qua performance? Alternatief: cache bij elke test run.

6. **Dependency graph renderer**: Plotly network graph (via `go.Scatter` met edges) of Mermaid diagram (via `ui.mermaid()`)? Mermaid is simpeler, Plotly is interactiever.

---

## 7. DEV_CONSTITUTION impact

| Artikel | Impact |
|---------|--------|
| Art. 3 (Codebase integriteit) | Geen destructieve wijzigingen, alleen toevoegingen |
| Art. 4 (Transparantie) | Quick Actions en Activity Stream maken systeemgedrag transparanter |
| Art. 6 (Soevereiniteit) | Project pagina respecteert node-configuratie en adapter-grenzen |
| Art. 7 (Impact-zonering) | GREEN — nieuwe bestanden, geen wijzigingen aan bestaande code |

---

## 8. Relatie met andere intakes

| Intake | Relatie |
|--------|---------|
| Dashboard Bestaande Panelen Upgrade | Complementair — die doet 5 pagina-upgrades, deze voegt de 8e pagina + cross-cutting features toe |
| Dashboard Kennisbibliotheek & Research | Complementair — Knowledge en Research pagina's krijgen ook Quick Actions |
| Kennisketen End-to-End | Activity Stream wordt rijker na kennisketen sprint (meer events) |
| Event Bus Lifecycle Hooks (Sprint 42) | ✅ DONE — Activity Stream leest direct uit EventBus |

---

## 9. Info Tooltips — Dashboard-breed contextuitleg

### 9.1 Patroon

Elk meetbaar item, KPI, dimensie-titel, of sectie-header in het dashboard krijgt een info-icoon (ⓘ) met hover-tooltip die uitlegt:

1. **Wat** het item meet of toont
2. **Waar** de data vandaan komt (welke bron/provider)
3. **Waarom** het relevant is (context voor beslissingen)

### 9.2 Twee niveaus

**Niveau 1: Quasar `.tooltip()`** — voor korte hints (< 1 zin)
Toepassing: badges, status-dots, kleine indicatoren.

```python
# NiceGUI voorbeeld
ui.label('UP').tooltip('Adapter is bereikbaar en retourneert valid data')
ui.badge('GOLD').tooltip('Peer-reviewed bron met hoge betrouwbaarheid')
```

**Niveau 2: Info-icoon met uitgebreide tooltip** — voor items die context nodig hebben
Toepassing: KPI-cards, dimensie-titels, sectie-headers, meter-stappen, tabel-kolommen.

```python
# NiceGUI component
class InfoTooltip:
    """Herbruikbaar ⓘ icoon met hover-uitleg."""

    def __init__(self, text: str, width: str = '280px'):
        with ui.element('span').classes('info-icon-wrapper'):
            icon = ui.icon('info', size='14px').classes('info-icon')
            with ui.element('div').classes('info-popup').style(f'width:{width}'):
                ui.label(text).classes('text-xs')

# Gebruik in KPI card:
with ui.row().classes('items-center gap-1'):
    ui.label('Tests').classes('kpi-label')
    InfoTooltip('Totaal aantal testbestanden in de DevHub monorepo. Bron: pytest discovery over alle packages. Trend toont groei per sprint.')

# Gebruik in sectie-header:
with ui.row().classes('items-center gap-2'):
    ui.label('7 Health Dimensies').classes('section-title')
    InfoTooltip('Elke dimensie checkt een ander aspect van systeemgezondheid. Groen = OK, Geel = aandacht, Rood = actie vereist. Data wordt gecached met 30s TTL.')
```

### 9.3 Tooltip-teksten per pagina

#### Overview

| Item | Tooltip |
|------|---------|
| KPI: Tests | Totaal testbestanden in de monorepo. Bron: pytest discovery. Sparkline toont groei over laatste 10 sprints. |
| KPI: Sprint | Huidige actieve sprint. Bron: SPRINT_TRACKER.md. Badge toont estimation accuracy. |
| KPI: Packages | Actieve uv workspace packages. Bron: packages/*/pyproject.toml scanning. |
| KPI: Knowledge | Kennisartikelen in de kennisbank. Freshness breakdown: hoe recent de inhoud is bijgewerkt. |
| KPI: Research | Openstaande research requests. Combineert agent-voorstellen (stroom 2) en eigen verzoeken (stroom 3). |
| KPI: Health | Overall systeemgezondheid. Samengesteld uit 7 dimensies — groen als alle dimensies OK. |
| KPI: Fase | Huidige roadmap-fase (0-5). Elke fase heeft een afgerond criterium. Bron: SPRINT_TRACKER.md. |
| System Pulse | Laatste systeem-events in chronologische volgorde. Bron: EventBus history. |
| Domein-kaarten | Samenvatting per domein met key metrics. Klik "→ Details" voor de volledige pagina. |

#### Health

| Item | Tooltip |
|------|---------|
| Tests dimensie | Controleert: testbestanden gevonden, pass rate 100%, geen regressie t.o.v. baseline. Bron: pytest. |
| Packages dimensie | Controleert: alle workspace packages hebben pyproject.toml, versie ≥ 0.1.0. Bron: packages/ scan. |
| Dependencies dimensie | Controleert: geen outdated of kwetsbare dependencies. Bron: pyproject.toml analyse. |
| Architecture dimensie | Controleert: NodeInterface contract intact, adapter pattern correct, geen circulaire imports. |
| Knowledge Health | Controleert: freshness score, grading verdeling, stale artikelen. Bron: kennisbank metadata. |
| Security dimensie | Controleert: laatste OWASP ASI audit resultaat. Bron: SecurityAuditReport als beschikbaar. |
| Sprint Hygiene | Controleert: velocity accuracy, stale inbox items, actieve sprint aanwezig. Bron: SPRINT_TRACKER. |
| Trend Chart | Multi-metric trend over tijd. Drie lijnen: tests (groen), packages (blauw), knowledge (paars). |

#### Planning

| Item | Tooltip |
|------|---------|
| Fase Pipeline | Visuele voortgang door roadmap-fases 0-5. ✅ = afgerond, 🔄 = actief, ○ = toekomstig. |
| Kanban kolommen | Planning pipeline: INBOX (nieuw) → KLAAR (shaped) → ACTIEF (huidige sprint) → DONE (afgerond). |
| Velocity Chart | Test-delta per sprint. Positief = tests toegevoegd, negatief = refactoring. Bron: SPRINT_TRACKER. |
| Cycle Time | Doorlooptijd van intake tot afronding. Korter = efficiënter. Bron: SPRINT_TRACKER timestamps. |
| Estimation Accuracy | Verhouding tussen geplande en werkelijke sprint-grootte. 100% = perfect ingeschat. |

#### Knowledge

| Item | Tooltip |
|------|---------|
| Catalogus | Alle kennisartikelen met EVIDENCE-grading. GOLD = peer-reviewed, SILVER = gevalideerd, BRONZE = ervaring. |
| Dekking matrix | Drie-ringen model: Ring 1 (kern) moet 100% gedekt zijn, Ring 2/3 naar behoefte. |
| Versheid tabel | Leeftijd per artikel. Fresh (&lt;30d), Aging (30-90d), Stale (&gt;90d). Stale = review nodig. |

#### Governance

| Item | Tooltip |
|------|---------|
| Compliance Score | Percentage artikelen met actieve verificatie. 100% = alle 9 artikelen gecontroleerd en compliant. |
| Per-artikel status | ✅ Actief: verificatie slaagt. ⚠️ Aandacht: deels compliant. ❌ Overtreding: actie vereist. |
| OWASP ASI bars | 10 AI Security Initiative checkpoints. Mitigated = afgedekt, Partial = deels, Open = nog te doen. |
| Impact Zonering | GREEN = veilig (tests draaien), YELLOW = review vereist, RED = menselijke goedkeuring nodig. |
| Audit Trail | Chronologisch logboek van governance-relevante wijzigingen. Wie, wanneer, wat, welk artikel. |

#### Growth

| Item | Tooltip |
|------|---------|
| Skill Radar | Dreyfus levels (1-5) per kennisdomein. Solid lijn = huidig, dashed = doel (6 maanden). |
| T-Shape Profiel | Horizontaal = brede kennis (level 2+), verticaal = specialisatie. Doel: breed fundament + diepte. |
| Domain Cards | Per domein: huidig level, evidence, groeisnelheid (↗/→/↘), en ZPD-taken (zone of proximal development). |
| Challenges | Ontwikkeluitdagingen per domein. Type: PRACTICE/STRETCH/CONSOLIDATION. Scaffolding: begeleiding-niveau. |
| Learning Recs | Aanbevolen bronnen afgestemd op huidige kennislacunes. Prioriteit: ZPD-alignment × domein-urgentie. |

#### Research

| Item | Tooltip |
|------|---------|
| Nieuw Voorstel | Dien een research question in. Wordt een RESEARCH_VOORSTEL in docs/planning/inbox/. |
| Mijn Verzoeken | Stroom 3: door jou ingediende research requests met status-tracking. |
| Agent-voorstellen | Stroom 2: door agents gegenereerde kennislacunes via KnowledgeGapDetected events. Vereist goedkeuring. |
| Auto-kennis | Stroom 1: automatisch bijgewerkte basiskennis (Ring 1). Read-only overzicht. |

#### Projects

| Item | Tooltip |
|------|---------|
| Dependency Graph | Visualiseert hoe workspace packages van elkaar afhangen. Grotere node = meer tests. |
| Package Tabel | Metadata per package uit pyproject.toml. Status badge op basis van test health. |
| Integration Meter | 4 niveaus: Geen → Basis (adapter) → Actief (devagents) → Volledig (eigen plugin.json). |
| Adapter status | Controleert of de NodeInterface adapter importeerbaar en bereikbaar is. |
| Plugin Adoptie | Hoeveel DevHub agents/skills beschikbaar zijn voor dit project en of het eigen agents heeft. |

#### Quick Actions

| Item | Tooltip |
|------|---------|
| ⌘K knop | Open het Command Palette om snel een actie te vinden. Werkt ook met Ctrl+K. |
| Elke actie-knop | Voert de actie uit en toont voortgang in de Activity Stream onderaan. |

#### Activity Stream

| Item | Tooltip |
|------|---------|
| LIVE badge | Stream toont events in real-time vanuit het EventBus-systeem. |
| ▼/▲ toggle | Klap de stream in of uit. Stream blijft actief op de achtergrond. |

### 9.4 CSS specificatie

```css
/* Info icon + tooltip */
.info-icon-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    cursor: help;
}
.info-icon {
    width: 16px; height: 16px;
    color: #555;
    transition: color 0.2s;
}
.info-icon-wrapper:hover .info-icon {
    color: #4ecca3;
}
.info-popup {
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: #0e1628;
    border: 1px solid #4ecca3;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #ccd6f6;
    line-height: 1.5;
    z-index: 50;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    pointer-events: none;
    white-space: normal;
}
.info-popup::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #4ecca3;
}
.info-icon-wrapper:hover .info-popup {
    display: block;
}
```

### 9.5 Implementatie-richtlijn

- Elk KPI-card krijgt een `InfoTooltip` naast het label
- Elke sectie-header krijgt een `InfoTooltip` naast de titel
- Elke tabel-kolom header kan een `InfoTooltip` krijgen (optioneel, alleen bij niet-voor-de-hand-liggende kolommen)
- De integration meter stappen krijgen elk een tooltip
- Quick Action knoppen krijgen een korte `.tooltip()` (Quasar niveau 1)
- Tooltip-teksten worden centraal beheerd in een `TOOLTIPS` dict in `config.py` zodat ze makkelijk aan te passen zijn

```python
# config.py
TOOLTIPS = {
    'kpi_tests': 'Totaal testbestanden in de monorepo. Bron: pytest discovery. Sparkline toont groei over laatste 10 sprints.',
    'kpi_sprint': 'Huidige actieve sprint. Bron: SPRINT_TRACKER.md. Badge toont estimation accuracy.',
    # ... etc
}
```
