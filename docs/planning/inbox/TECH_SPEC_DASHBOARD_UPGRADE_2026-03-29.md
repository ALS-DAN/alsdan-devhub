---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
type: TECHNICAL_SPECIFICATION
hoort_bij: SPRINT_INTAKE_DASHBOARD_KENNISBIBLIOTHEEK_RESEARCH_UPGRADE_2026-03-29.md
---

# Technische Specificatie: Dashboard Kennisbibliotheek & Research Management Upgrade

Bijlage bij de sprint intake. Beantwoordt alle open vragen en biedt concrete implementatie-specs die Claude Code direct kan oppakken.

---

## 1. NiceGUI Bevindingen — Opgeloste Aandachtspunten

### Path Parameters: ✅ Ondersteund

NiceGUI ≥2.0 ondersteunt FastAPI-style path parameters via `@ui.page`:

```python
@ui.page("/knowledge/{article_id}")
def knowledge_detail_page(article_id: str) -> None:
    """Artikel-detailpagina."""
    # article_id wordt automatisch geëxtraheerd uit de URL
    ...
```

Query parameters werken ook:

```python
@ui.page("/knowledge")
def knowledge_page(domain: str = "", grade: str = "") -> None:
    """Knowledge met optionele filters via query params."""
    ...
```

**Aanbeveling:** Gebruik path parameters voor detail-pagina's (`/knowledge/{id}`, `/research/{id}`) en query parameters voor filters (`/knowledge?domain=ai_engineering&grade=GOLD`).

### Autocomplete: ✅ Beschikbaar

```python
# Bestaande artikelen als suggesties
existing_topics = ["Agent Teams", "Event Bus", "Knowledge Curation"]
topic_input = ui.input(
    "Topic",
    autocomplete=existing_topics,
    placeholder="Wat wil je onderzocht hebben?"
)
```

Voor de zoekfunctie — `ui.input` met `on_value_change`:

```python
search_input = ui.input("Zoeken...", on_value_change=lambda e: _do_search(e.value))
```

Debounce moet handmatig via `asyncio` of een timer pattern. NiceGUI heeft geen ingebouwde debounce, maar het Quasar `q-input` component ondersteunt `debounce` als prop:

```python
search_input = ui.input("Zoeken...").props('debounce="300"')
```

### Dynamic Lists (RQ-velden): ✅ Haalbaar

NiceGUI's reactief model maakt dynamische formuliervelden mogelijk:

```python
rqs: list[str] = []
rq_container = ui.column()

def add_rq():
    rqs.append("")
    with rq_container:
        idx = len(rqs) - 1
        with ui.row().classes("items-center gap-2 w-full"):
            ui.label(f"RQ{idx + 1}").classes("font-bold w-12")
            ui.input(
                placeholder=f"Onderzoeksvraag {idx + 1}",
                on_change=lambda e, i=idx: rqs.__setitem__(i, e.value)
            ).classes("flex-grow")
            ui.button(icon="close", on_click=lambda _, i=idx: remove_rq(i)).props("flat dense")

ui.button("+ Onderzoeksvraag", icon="add", on_click=add_rq)
```

---

## 2. Frontmatter-parsing Strategie

### Probleem: Twee formaten in `knowledge/`

**Formaat A** — Research bestanden (3 stuks in root):
```yaml
# Research: <Titel>

---
sprint: 38
type: SPIKE
kennisgradering: SILVER
datum: 2026-03-28
bron: SPRINT_INTAKE_...
verdict: GEPARKEERD
---
```
Let op: `#`-header BOVEN de `---` frontmatter. Niet-standaard.

**Formaat B** — Retrospectives (7 stuks in `retrospectives/`):
```yaml
---
title: Retrospective — DevHub Dashboard NiceGUI (Sprint 43)
domain: retrospectives
grade: SILVER
date: 2026-03-28
author: devhub-sprint
sprint: DevHub Dashboard NiceGUI
---
```
Dit is standaard YAML frontmatter (Jekyll/Hugo-style).

### Aanbeveling: Fuzzy Parser met Normalisatie

Bouw een `KnowledgeArticleParser` die beide formaten ondersteunt:

```python
@dataclass
class ParsedArticle:
    """Genormaliseerd kennisartikel uit filesystem."""
    file_path: str
    title: str
    domain: str
    grade: str  # GOLD | SILVER | BRONZE | SPECULATIVE
    date: str   # ISO 8601
    author: str
    summary: str  # Eerste 2-3 zinnen na headers
    freshness_days: int  # Berekend uit date vs. vandaag
    sprint: str | None
    sources: list[str]
    rq_tags: list[str]
    raw_metadata: dict  # Alles uit frontmatter

class KnowledgeArticleParser:
    """Parse knowledge/*.md bestanden in beide frontmatter-formaten."""

    def parse(self, file_path: Path) -> ParsedArticle | None:
        content = file_path.read_text(encoding="utf-8")

        # Strategie 1: Standaard frontmatter (---\n...\n---)
        metadata = self._parse_standard_frontmatter(content)

        # Strategie 2: Header + frontmatter (# Title\n\n---\n...\n---)
        if not metadata:
            metadata = self._parse_header_frontmatter(content)

        if not metadata:
            return None  # Niet-parseerbaar bestand

        # Normaliseer veldnamen
        return self._normalize(file_path, metadata, content)

    def _normalize(self, path, meta, content) -> ParsedArticle:
        """Map variërende veldnamen naar uniform model."""
        title = (
            meta.get("title")
            or self._extract_h1(content)
            or path.stem.replace("_", " ")
        )
        grade = (
            meta.get("grade")
            or meta.get("kennisgradering")
            or "SPECULATIVE"
        ).upper()
        date = meta.get("date") or meta.get("datum") or ""
        domain = meta.get("domain") or self._infer_domain(path)
        author = meta.get("author") or "unknown"
        summary = self._extract_summary(content)
        ...
```

**Veldnaam-mapping** (beide formaten → uniform):

| Formaat A veld | Formaat B veld | Genormaliseerd |
|---------------|---------------|----------------|
| (H1 header) | `title:` | `title` |
| `kennisgradering:` | `grade:` | `grade` |
| `datum:` | `date:` | `date` |
| (niet aanwezig) | `author:` | `author` |
| (niet aanwezig) | `domain:` | `domain` (infer uit pad) |
| `sprint:` | `sprint:` | `sprint` |
| `bron:` | (niet aanwezig) | `sources` |
| `verdict:` | (niet aanwezig) | `verdict` (optioneel) |

**Domein-inferentie uit pad:**
- `knowledge/retrospectives/*.md` → domain = "retrospectives"
- `knowledge/skill_radar/*.md` → domain = "coaching_learning"
- `knowledge/*.md` (root) → domain inferred from content keywords of "unknown"

---

## 3. ResearchQueueItem v2 — Datamodel + Migratie

### Nieuwe velden

```python
@dataclass
class ResearchQueueItem:
    """Een item in de research queue — v2 met uitgebreide metadata."""

    # === v1 velden (bestaand, ongewijzigd) ===
    item_id: str
    stream: str            # "auto" | "agent" | "user"
    status: str            # RequestStatus value
    topic: str
    domain: str
    depth: str = "STANDARD"
    document_category: str = ""
    source_agent: str = ""
    priority: int = 5
    description: str = ""
    created_at: str = ""
    updated_at: str = ""

    # === v2 velden (nieuw, alle met defaults voor backwards-compat) ===
    background: str = ""           # Motivatie/achtergrond (waarom dit onderzoek?)
    research_questions: list[str] = field(default_factory=list)  # Expliciete RQs
    scope_in: str = ""             # Wat valt erin
    scope_out: str = ""            # Wat valt erbuiten
    expected_grade: str = ""       # Verwacht EVIDENCE-niveau
    related_articles: list[str] = field(default_factory=list)  # IDs gerelateerde kennis
    deadline: str = ""             # Optionele deadline (ISO 8601)
    rejection_reason: str = ""     # Reden bij REJECTED status
    completed_articles: list[str] = field(default_factory=list)  # IDs van output artikelen
    review_notes: str = ""         # Opmerkingen bij REVIEW status
    status_history: list[dict] = field(default_factory=list)  # [{status, timestamp, actor}]
```

**Let op:** `@dataclass` (niet frozen) want `ResearchQueueItem` is al mutable in v1.
De `list` defaults vereisen `field(default_factory=list)`.

### Migratie-strategie: Lazy upgrade bij read

```python
@classmethod
def from_dict(cls, data: dict) -> ResearchQueueItem:
    """Backwards-compatible deserialisatie. V1 items krijgen lege v2 velden."""
    valid_fields = {f for f in cls.__dataclass_fields__}
    # Filter onbekende keys (forward-compat)
    filtered = {k: v for k, v in data.items() if k in valid_fields}
    # list-velden moeten list zijn, niet None
    for list_field in ["research_questions", "related_articles",
                       "completed_articles", "status_history"]:
        if list_field in filtered and filtered[list_field] is None:
            filtered[list_field] = []
    return cls(**filtered)
```

Bestaande JSON-bestanden (zoals `4e3e2f16.json`) werken zonder aanpassing. Nieuwe velden worden als lege defaults ingelezen. **Geen migratie-script nodig.**

### Status uitbreiden

```python
class RequestStatus(Enum):
    """Status van een research request — v2."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"          # NIEUW: research afgerond, wacht op beoordeling
    COMPLETED = "completed"
```

### Status-history tracking

Bij elke statuswijziging een entry toevoegen:

```python
def update_status(self, item_id: str, new_status: RequestStatus, actor: str = "niels") -> bool:
    ...
    data["status_history"] = data.get("status_history", [])
    data["status_history"].append({
        "status": new_status.value,
        "timestamp": datetime.now(UTC).isoformat(),
        "actor": actor,
    })
    ...
```

---

## 4. KnowledgeProvider — Nieuwe Data-laag

### Architectuur

```
knowledge/**/*.md  →  KnowledgeArticleParser  →  KnowledgeProvider  →  Pages
                                                        ↓
                                              (cache: dict[str, ParsedArticle])
```

### Interface

```python
class KnowledgeProvider:
    """Data provider voor het Knowledge-paneel. Scant knowledge/ directory."""

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self._parser = KnowledgeArticleParser()
        self._cache: dict[str, ParsedArticle] | None = None
        self._cache_time: float = 0

    def get_articles(
        self,
        domain: str | None = None,
        ring: str | None = None,
        grade: str | None = None,
        max_freshness_days: int | None = None,
        sort_by: str = "date_desc",
    ) -> list[ParsedArticle]:
        """Gefilterde en gesorteerde artikellijst."""
        ...

    def get_article(self, article_id: str) -> ParsedArticle | None:
        """Eén artikel ophalen op basis van file-stem als ID."""
        ...

    def get_domain_coverage(self) -> list[DomainCoverage]:
        """Dekkingsmatrix: per domein artikelen, grades, freshness."""
        ...

    def get_freshness_summary(self) -> FreshnessSummary:
        """Totaal freshness overzicht voor KPI cards."""
        ...

    def get_grading_distribution(self) -> dict[str, int]:
        """Grading verdeling (vervangt huidige _scan_grading)."""
        ...

    def search(self, query: str) -> list[ParsedArticle]:
        """Keyword-based zoeken (Sprint 1). Sprint 2 voegt semantic toe."""
        ...
```

### Caching

```python
CACHE_TTL = 30  # seconden (match DashboardConfig.refresh_interval_seconds)

def _ensure_cache(self) -> dict[str, ParsedArticle]:
    now = time.time()
    if self._cache is None or (now - self._cache_time) > CACHE_TTL:
        self._cache = self._scan_all()
        self._cache_time = now
    return self._cache
```

### DomainCoverage dataclass

```python
@dataclass
class DomainCoverage:
    """Dekking van één kennisdomein."""
    domain: str
    ring: str  # "core" | "agent" | "project"
    article_count: int
    grade_distribution: dict[str, int]  # {"GOLD": 1, "SILVER": 3, ...}
    avg_freshness_days: float
    coverage_score: float  # 0.0-1.0 (berekend uit count + grade + freshness)
    has_gap: bool  # True als core-domein met 0 artikelen
```

### Article ID conventie

Gebruik de file stem (zonder extensie) als article_id:
- `RESEARCH_AGENT_TEAMS_SPIKE.md` → ID = `RESEARCH_AGENT_TEAMS_SPIKE`
- `retrospectives/RETRO_DEVHUB_DASHBOARD_NICEGUI.md` → ID = `retrospectives/RETRO_DEVHUB_DASHBOARD_NICEGUI`

Dit is stabiel (bestandsnaam wijzigt zelden), uniek, en menselijk leesbaar.

---

## 5. Pagina-structuur Refactoring

### Knowledge pagina → tabs

```python
@ui.page("/knowledge")
def knowledge_page_route() -> None:
    _nav_header()
    provider = _get_knowledge_provider()

    with ui.column().classes("p-8 w-full"):
        ui.label("Knowledge & Kennisbank").classes("text-h4 q-mb-md")

        # KPI cards (freshness, totaal, grades)
        _knowledge_kpis(provider)

        with ui.tabs().classes("w-full") as tabs:
            catalog_tab = ui.tab("Catalogus", icon="library_books")
            coverage_tab = ui.tab("Dekking", icon="grid_view")
            freshness_tab = ui.tab("Versheid", icon="schedule")

        with ui.tab_panels(tabs, value=catalog_tab).classes("w-full"):
            with ui.tab_panel(catalog_tab):
                _catalog_panel(provider)
            with ui.tab_panel(coverage_tab):
                _coverage_matrix_panel(provider)
            with ui.tab_panel(freshness_tab):
                _freshness_panel(provider)


@ui.page("/knowledge/{article_id}")
def knowledge_detail_route(article_id: str) -> None:
    _nav_header()
    provider = _get_knowledge_provider()
    article = provider.get_article(article_id)
    with ui.column().classes("p-8 w-full"):
        if article:
            _article_detail(article)
        else:
            ui.label(f"Artikel '{article_id}' niet gevonden.").classes("text-red")
```

### Research pagina → tabs

```python
@ui.page("/research")
def research_page_route() -> None:
    _nav_header()
    queue = _get_queue_manager()
    knowledge = _get_knowledge_provider()

    with ui.column().classes("p-8 w-full"):
        ui.label("Research & Kennisverzoeken").classes("text-h4 q-mb-md")

        with ui.tabs().classes("w-full") as tabs:
            new_tab = ui.tab("Nieuw Voorstel", icon="add_circle")
            my_tab = ui.tab("Mijn Verzoeken", icon="person")
            agent_tab = ui.tab("Agent-voorstellen", icon="smart_toy")
            auto_tab = ui.tab("Auto-kennis", icon="auto_fix_high")

        with ui.tab_panels(tabs, value=new_tab).classes("w-full"):
            with ui.tab_panel(new_tab):
                _extended_research_form(queue, knowledge)
            with ui.tab_panel(my_tab):
                _user_requests_panel(queue)
            with ui.tab_panel(agent_tab):
                _agent_proposals_panel(queue)
            with ui.tab_panel(auto_tab):
                _auto_knowledge_panel(queue)


@ui.page("/research/{item_id}")
def research_detail_route(item_id: str) -> None:
    _nav_header()
    queue = _get_queue_manager()
    item = queue.get_item(item_id)
    with ui.column().classes("p-8 w-full"):
        if item:
            _research_detail(item)
        else:
            ui.label(f"Research '{item_id}' niet gevonden.").classes("text-red")
```

---

## 6. Nieuwe Componenten Specificatie

### knowledge_card.py

```python
def knowledge_card(article: ParsedArticle, *, show_summary: bool = True) -> ui.card:
    """Herbruikbare kennisartikel-kaart."""
    # Ring kleuren
    ring_colors = {"core": "primary", "agent": "positive", "project": "warning"}
    # Grade kleuren
    grade_colors = {"GOLD": "#FFD700", "SILVER": "#C0C0C0", "BRONZE": "#CD7F32", "SPECULATIVE": "#9E9E9E"}
    # Freshness kleuren
    freshness_color = (
        "positive" if article.freshness_days < 30
        else "warning" if article.freshness_days < 90
        else "negative"
    )

    with ui.card().classes("p-3 w-full cursor-pointer") as card:
        card.on("click", lambda: ui.navigate.to(f"/knowledge/{article.file_path}"))

        # Header: title + grade badge
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(article.title).classes("text-subtitle1 font-bold")
            ui.badge(article.grade, color=grade_colors.get(article.grade, "grey"))

        # Tags: domain, ring, freshness
        with ui.row().classes("gap-2 mt-1"):
            ui.badge(article.domain, color=ring_colors.get(article.ring, "grey"))
            ui.badge(f"Ring {{'core':'1','agent':'2','project':'3'}[article.ring]}")
            ui.icon("circle", color=freshness_color).classes("text-xs")
            ui.label(f"{article.freshness_days}d").classes("text-xs text-grey-7")
            if article.rq_tags:
                for rq in article.rq_tags:
                    ui.badge(rq, color="info").classes("text-white")

        # Summary
        if show_summary and article.summary:
            ui.label(article.summary).classes("text-sm text-grey-6 mt-1 line-clamp-3")

        # Footer: date + author + verification
        with ui.row().classes("gap-4 mt-2 text-xs text-grey-7"):
            ui.label(f"📅 {article.date}")
            ui.label(f"✍️ {article.author}")

    return card
```

### status_flow.py

```python
def status_flow(current_status: str, history: list[dict] | None = None) -> None:
    """Horizontale status-pipeline visualisatie."""
    steps = ["pending", "approved", "in_progress", "review", "completed"]
    step_labels = {
        "pending": "Pending",
        "approved": "Goedgekeurd",
        "in_progress": "Onderzoek",
        "review": "Review",
        "completed": "Afgerond",
    }
    step_icons = {
        "pending": "hourglass_empty",
        "approved": "check_circle",
        "in_progress": "search",
        "review": "rate_review",
        "completed": "done_all",
    }

    current_idx = steps.index(current_status) if current_status in steps else -1
    rejected = current_status == "rejected"

    with ui.row().classes("items-center gap-0 w-full justify-center"):
        for i, step in enumerate(steps):
            # Determine color
            if rejected and step == "approved":
                color = "negative"
                icon = "cancel"
                label = "Afgewezen"
            elif i < current_idx:
                color = "positive"
                icon = step_icons[step]
                label = step_labels[step]
            elif i == current_idx:
                color = "info"
                icon = step_icons[step]
                label = step_labels[step]
            else:
                color = "grey-5"
                icon = step_icons[step]
                label = step_labels[step]

            # Step circle
            with ui.column().classes("items-center"):
                ui.icon(icon, color=color).classes("text-2xl")
                ui.label(label).classes(f"text-xs text-{color}")
                # Timestamp uit history als beschikbaar
                if history:
                    ts = next((h["timestamp"][:10] for h in history if h["status"] == step), None)
                    if ts:
                        ui.label(ts).classes("text-xs text-grey-7")

            # Connector line (behalve na laatste)
            if i < len(steps) - 1:
                line_color = "positive" if i < current_idx else "grey-8"
                ui.element("div").style(
                    f"height: 2px; width: 40px; background: var(--q-{line_color}); "
                    f"align-self: center; margin-top: -20px;"
                )
```

### search_bar.py

```python
def global_search_bar(knowledge_provider: KnowledgeProvider, queue_manager: ResearchQueueManager) -> None:
    """Globale zoekbalk in de header."""
    results_container = ui.column().classes("absolute bg-dark rounded shadow-lg p-2 w-96 z-50")
    results_container.visible = False

    async def on_search(e):
        query = e.value.strip()
        if len(query) < 2:
            results_container.visible = False
            return

        results_container.clear()
        results_container.visible = True

        # Zoek in kennis
        articles = knowledge_provider.search(query)[:5]
        if articles:
            with results_container:
                ui.label("Kennis").classes("text-xs text-grey-5 font-bold")
                for a in articles:
                    with ui.row().classes("items-center gap-2 cursor-pointer hover:bg-grey-9 p-1 rounded"):
                        ui.icon("article", color="primary")
                        ui.link(a.title, f"/knowledge/{a.file_path}").classes("text-sm")

        # Zoek in research queue
        all_items = queue_manager.list_items()
        matched = [i for i in all_items if query.lower() in i.topic.lower()][:5]
        if matched:
            with results_container:
                ui.label("Research").classes("text-xs text-grey-5 font-bold mt-2")
                for r in matched:
                    with ui.row().classes("items-center gap-2 cursor-pointer hover:bg-grey-9 p-1 rounded"):
                        ui.icon("science", color="info")
                        ui.link(r.topic, f"/research/{r.item_id}").classes("text-sm")

    with ui.row().classes("items-center"):
        ui.input(placeholder="Zoeken in kennis & research...").props(
            'debounce="300" dense outlined dark'
        ).classes("w-64").on("update:model-value", on_search)
```

---

## 7. Sprint 2 — Discovery Engine Specificatie

### ABC-Verbindingsdetector

Het Swanson ABC-paradigma vertaald naar DevHub:

```
Domein A ←→ Concept B ←→ Domein C
         (gedeeld)
```

Implementatie zonder vectorstore (Sprint 1 fallback):
- Parse alle artikelen op `entity_refs` en `rq_tags`
- Bouw een bipartite graph: {domein} → {concept}
- Vind A-C paren die B delen maar geen directe link hebben

Implementatie met vectorstore (Sprint 2):
- Per domein: gemiddelde embedding berekenen
- Cosine-similarity matrix tussen domeinen
- Hoge similarity + geen gedeelde artikelen = potentiële verbinding
- Confidence score = similarity × (1 - overlap_ratio)

```python
@dataclass
class DiscoveredConnection:
    """Een ontdekte potentiële verbinding tussen domeinen."""
    domain_a: str
    domain_c: str
    bridging_concepts: list[str]  # De B-concepten
    confidence: float  # 0.0-1.0
    explanation: str  # Menselijk leesbare uitleg
    suggested_rq: str  # Voorgestelde onderzoeksvraag
```

### Kennislacune-scanner

```python
@dataclass
class KnowledgeGap:
    """Een gedetecteerde kennislacune."""
    domain: str
    ring: str
    severity: str  # "critical" | "moderate" | "low"
    reason: str    # Waarom dit een lacune is
    article_count: int
    avg_grade: str | None
    suggested_topic: str
    suggested_rqs: list[str]

class GapScanner:
    """Detecteert kennislacunes op basis van dekkingsmatrix."""

    def scan(self, coverage: list[DomainCoverage]) -> list[KnowledgeGap]:
        gaps = []
        for dc in coverage:
            # Core-domein zonder artikelen = critical
            if dc.ring == "core" and dc.article_count == 0:
                gaps.append(KnowledgeGap(
                    domain=dc.domain, ring=dc.ring,
                    severity="critical",
                    reason=f"Core-domein {dc.domain} heeft 0 artikelen",
                    ...
                ))
            # Domein met alleen SPECULATIVE = moderate
            elif dc.grade_distribution.get("SPECULATIVE", 0) == dc.article_count:
                gaps.append(KnowledgeGap(
                    severity="moderate",
                    reason=f"Alle kennis in {dc.domain} is SPECULATIVE",
                    ...
                ))
            # Verouderde kennis = moderate
            elif dc.avg_freshness_days > 90:
                gaps.append(KnowledgeGap(
                    severity="moderate",
                    reason=f"Kennis in {dc.domain} is gemiddeld {dc.avg_freshness_days:.0f} dagen oud",
                    ...
                ))
        return sorted(gaps, key=lambda g: {"critical": 0, "moderate": 1, "low": 2}[g.severity])
```

---

## 8. Bestandsstructuur na implementatie

```
packages/devhub-dashboard/devhub_dashboard/
├── app.py                          # + /knowledge/{id}, /research/{id} routes
├── config.py                       # ongewijzigd
├── __init__.py
├── __main__.py
├── components/
│   ├── __init__.py
│   ├── kpi_card.py                 # bestaand
│   ├── status_badge.py             # bestaand
│   ├── trend_chart.py              # bestaand
│   ├── research_card.py            # bestaand (minor updates)
│   ├── knowledge_card.py           # NIEUW
│   ├── status_flow.py              # NIEUW
│   ├── search_bar.py               # NIEUW (Sprint 2)
│   └── discovery_card.py           # NIEUW (Sprint 2)
├── data/
│   ├── __init__.py
│   ├── providers.py                # bestaand (HealthProvider, PlanningProvider)
│   ├── research_queue.py           # UITGEBREID (v2 velden)
│   ├── history.py                  # bestaand
│   ├── event_listener.py           # bestaand
│   ├── knowledge_provider.py       # NIEUW
│   ├── article_parser.py           # NIEUW
│   └── discovery_service.py        # NIEUW (Sprint 2)
├── pages/
│   ├── __init__.py
│   ├── overview.py                 # UITGEBREID (freshness KPI, zoekbalk)
│   ├── health.py                   # bestaand
│   ├── planning.py                 # UITGEBREID (sprint-impact badges)
│   ├── knowledge.py                # HERSCHREVEN (tabs, catalogus, dekking, versheid)
│   ├── knowledge_detail.py         # NIEUW
│   ├── governance.py               # bestaand
│   ├── growth.py                   # bestaand
│   ├── research.py                 # HERSCHREVEN (tabs, uitgebreid formulier)
│   ├── research_detail.py          # NIEUW
│   ├── discovery.py                # NIEUW (Sprint 2)
│   └── activity.py                 # NIEUW (Sprint 2)
```

---

## 9. Test-strategie

### Unit tests (per component)

```python
# test_article_parser.py
def test_parse_standard_frontmatter():
    """Formaat B: ---\nyaml\n--- bovenaan."""
    ...

def test_parse_header_frontmatter():
    """Formaat A: # Title\n\n---\nyaml\n---."""
    ...

def test_normalize_field_names():
    """kennisgradering → grade, datum → date."""
    ...

def test_freshness_calculation():
    """Berekening dagen sinds publicatie."""
    ...
```

### Integration tests (per pagina)

```python
# test_knowledge_page.py — met NiceGUI test client
def test_knowledge_catalog_renders_articles():
    """Catalogus toont artikel-kaarten met juiste metadata."""
    ...

def test_knowledge_filter_by_domain():
    """Domein-filter beperkt getoonde artikelen."""
    ...

def test_knowledge_detail_shows_content():
    """Detail-pagina rendert markdown content."""
    ...
```

### Data provider tests

```python
# test_knowledge_provider.py
def test_get_articles_with_filters():
    ...

def test_domain_coverage_all_rings():
    ...

def test_cache_invalidation():
    ...
```

**Geschatte test-toename:** 40-60 nieuwe tests (Sprint 1), 30-40 (Sprint 2).

---

## 10. Samenvatting Open Vragen → Antwoorden

| # | Open Vraag | Antwoord |
|---|-----------|----------|
| 1 | Frontmatter-parsing | Fuzzy parser met normalisatie (§2). Beide formaten ondersteund. |
| 2 | NiceGUI path parameters | ✅ Ondersteund via FastAPI-syntax (§1). `/knowledge/{article_id}` werkt. |
| 3 | ResearchQueueItem v2 migratie | Lazy upgrade bij read — lege defaults, geen migratie-script (§3). |
| 4 | Embedding-queries abstractie | DiscoveryService als aparte laag in `data/` (§7). |
| 5 | Clustering-libraries | scikit-learn — al gangbaar in Python ecosystem, lightweight genoeg (§7). |
| 6 | Test-strategie | Unit tests per component + integration tests per pagina (§9). |
