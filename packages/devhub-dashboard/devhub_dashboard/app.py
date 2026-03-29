"""DevHub Dashboard — NiceGUI app entry point met multi-page routing."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.history import HistoryStore
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider
from devhub_dashboard.data.providers import (
    GovernanceProvider,
    GrowthProvider,
    HealthProvider,
    PlanningProvider,
)
from devhub_dashboard.data.research_queue import ResearchQueueManager

# Providers worden lazy geïnitialiseerd bij eerste page load
_config: DashboardConfig | None = None
_health_provider: HealthProvider | None = None
_planning_provider: PlanningProvider | None = None
_history_store: HistoryStore | None = None
_queue_manager: ResearchQueueManager | None = None
_governance_provider: GovernanceProvider | None = None
_growth_provider: GrowthProvider | None = None
_knowledge_provider: KnowledgeProvider | None = None


def _get_config() -> DashboardConfig:
    global _config
    if _config is None:
        _config = DashboardConfig()
    return _config


def _get_health_provider() -> HealthProvider:
    global _health_provider
    if _health_provider is None:
        _health_provider = HealthProvider(_get_config())
    return _health_provider


def _get_planning_provider() -> PlanningProvider:
    global _planning_provider
    if _planning_provider is None:
        _planning_provider = PlanningProvider(_get_config())
    return _planning_provider


def _get_history_store() -> HistoryStore:
    global _history_store
    if _history_store is None:
        _history_store = HistoryStore(_get_config())
    return _history_store


def _get_queue_manager() -> ResearchQueueManager:
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = ResearchQueueManager(_get_config())
    return _queue_manager


def _get_governance_provider() -> GovernanceProvider:
    global _governance_provider
    if _governance_provider is None:
        _governance_provider = GovernanceProvider(_get_config())
    return _governance_provider


def _get_growth_provider() -> GrowthProvider:
    global _growth_provider
    if _growth_provider is None:
        _growth_provider = GrowthProvider(_get_config())
    return _growth_provider


def _get_knowledge_provider() -> KnowledgeProvider:
    global _knowledge_provider
    if _knowledge_provider is None:
        _knowledge_provider = KnowledgeProvider(_get_config())
    return _knowledge_provider


def _nav_header() -> None:
    """Gedeelde navigatie-header voor alle pagina's."""
    with ui.header().classes("items-center justify-between"):
        ui.label("DevHub Dashboard").classes("text-h6 text-white")
        with ui.row().classes("gap-2"):
            ui.link("Overview", "/").classes("text-white")
            ui.link("Health", "/health").classes("text-white")
            ui.link("Planning", "/planning").classes("text-white")
            ui.link("Knowledge", "/knowledge").classes("text-white")
            ui.link("Governance", "/governance").classes("text-white")
            ui.link("Growth", "/growth").classes("text-white")
            ui.link("Research", "/research").classes("text-white")


@ui.page("/")
def index_page() -> None:
    """Executive Summary — landing page."""
    from devhub_dashboard.pages.overview import overview_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        overview_page(
            _get_health_provider(),
            _get_planning_provider(),
            _get_governance_provider(),
            _get_growth_provider(),
            knowledge_provider=_get_knowledge_provider(),
        )


@ui.page("/health")
def health_page_route() -> None:
    from devhub_dashboard.pages.health import health_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        health_page(_get_health_provider(), _get_history_store())


@ui.page("/planning")
def planning_page_route() -> None:
    from devhub_dashboard.pages.planning import planning_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        planning_page(_get_planning_provider())


@ui.page("/knowledge")
def knowledge_page_route() -> None:
    from devhub_dashboard.pages.knowledge import knowledge_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        knowledge_page(_get_knowledge_provider())


@ui.page("/knowledge/{article_id:path}")
def knowledge_detail_route(article_id: str) -> None:
    from devhub_dashboard.pages.knowledge_detail import knowledge_detail_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        knowledge_detail_page(article_id, _get_knowledge_provider())


@ui.page("/governance")
def governance_page_route() -> None:
    from devhub_dashboard.pages.governance import governance_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        governance_page(_get_governance_provider())


@ui.page("/growth")
def growth_page_route() -> None:
    from devhub_dashboard.pages.growth import growth_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        growth_page(_get_growth_provider())


@ui.page("/research")
def research_page_route() -> None:
    from devhub_dashboard.pages.research import research_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        research_page(_get_queue_manager(), _get_knowledge_provider())


@ui.page("/research/{item_id}")
def research_detail_route(item_id: str) -> None:
    from devhub_dashboard.pages.research_detail import research_detail_page

    _nav_header()
    with ui.column().classes("p-8 w-full"):
        research_detail_page(item_id, _get_queue_manager())


def main() -> None:
    """Start het dashboard."""
    config = _get_config()
    ui.run(
        title=config.title,
        port=config.port,
        host=config.host,
        dark=config.dark_mode,
        reload=False,
    )


if __name__ == "__main__":
    main()
