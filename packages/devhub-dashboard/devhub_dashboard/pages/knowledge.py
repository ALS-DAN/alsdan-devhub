"""Knowledge paneel — catalogus, domein-dekking, versheid, artikelkaarten."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.components.kpi_card import kpi_card
from devhub_dashboard.components.knowledge_card import knowledge_card
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider


def knowledge_page(provider: KnowledgeProvider) -> None:
    """Render het Knowledge paneel met tabs."""
    ui.label("Knowledge & Kennisbank").classes("text-h4 q-mb-md")

    # KPI cards
    freshness = provider.get_freshness_summary()
    grading = provider.get_grading_distribution()

    with ui.row().classes("gap-4 q-mb-lg flex-wrap"):
        kpi_card(
            "Kennis-items",
            freshness.total_articles,
            icon="library_books",
            color="primary",
        )
        kpi_card(
            "Versheid",
            f"{freshness.freshness_score:.0%}",
            icon="schedule",
            color="positive" if freshness.freshness_score >= 0.7 else "warning",
            subtitle=f"{freshness.fresh_count} vers, {freshness.aging_count} verouderend",
        )
        kpi_card("GOLD", grading.get("GOLD", 0), icon="star", color="warning")
        kpi_card("SILVER", grading.get("SILVER", 0), icon="star_half", color="grey")

    # Tabs
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


def _catalog_panel(provider: KnowledgeProvider) -> None:
    """Catalogus: artikelkaarten met filters."""
    # Filter bar
    domains = provider.get_domains()
    domain_filter = ui.select(
        label="Domein",
        options=[""] + domains,
        value="",
    ).classes("w-48")
    grade_filter = ui.select(
        label="Grade",
        options=["", "GOLD", "SILVER", "BRONZE", "SPECULATIVE"],
        value="",
    ).classes("w-36")
    sort_select = ui.select(
        label="Sorteer",
        options={
            "date_desc": "Nieuwst eerst",
            "date_asc": "Oudst eerst",
            "grade_desc": "Hoogste grade",
            "freshness": "Verst eerst",
        },
        value="date_desc",
    ).classes("w-48")

    articles_container = ui.column().classes("w-full gap-2 mt-4")

    def render_articles() -> None:
        articles_container.clear()
        articles = provider.get_articles(
            domain=domain_filter.value or None,
            grade=grade_filter.value or None,
            sort_by=sort_select.value or "date_desc",
        )
        with articles_container:
            if not articles:
                ui.label("Geen artikelen gevonden.").classes("text-grey-6 italic")
                return
            for article in articles:
                knowledge_card(article)

    # Initial render
    render_articles()

    # Re-render on filter change
    domain_filter.on_value_change(lambda _: render_articles())
    grade_filter.on_value_change(lambda _: render_articles())
    sort_select.on_value_change(lambda _: render_articles())


def _coverage_matrix_panel(provider: KnowledgeProvider) -> None:
    """Domein-dekkingsmatrix: per domein artikelen, grades, freshness."""
    coverage = provider.get_domain_coverage()

    if not coverage:
        ui.label("Geen domein-data beschikbaar.").classes("text-grey-6 italic")
        return

    ui.label("Domein-dekking per Ring").classes("text-h6 q-mb-sm")

    # Groepeer per ring
    rings = {"core": [], "agent": [], "project": []}
    for c in coverage:
        rings.setdefault(c.ring, []).append(c)

    ring_labels = {"core": "Ring 1: Core", "agent": "Ring 2: Agent", "project": "Ring 3: Project"}

    for ring, items in rings.items():
        if not items:
            continue
        ui.label(ring_labels.get(ring, ring)).classes("text-subtitle1 font-bold mt-4")

        with ui.grid(columns=3).classes("gap-3 mt-2"):
            for c in sorted(items, key=lambda x: -x.coverage_score):
                _coverage_color = (
                    "positive"
                    if c.coverage_score >= 0.6
                    else "warning"
                    if c.coverage_score >= 0.3
                    else "negative"
                )
                with ui.card().classes("p-3 text-center"):
                    ui.label(c.domain.replace("_", " ").title()).classes("text-sm font-bold")
                    ui.label(str(c.article_count)).classes("text-2xl font-bold")
                    ui.label("artikelen").classes("text-xs text-grey-7")

                    # Grade verdeling als mini-bars
                    for grade, count in sorted(c.grade_distribution.items()):
                        if count > 0:
                            ui.label(f"{grade}: {count}").classes("text-xs text-grey-6")

                    # Freshness
                    ui.badge(
                        f"{c.avg_freshness_days:.0f}d",
                        color=_coverage_color,
                    ).classes("text-white mt-1")

                    # Coverage score
                    ui.linear_progress(
                        value=c.coverage_score,
                        color=_coverage_color,
                    ).classes("mt-1")


def _freshness_panel(provider: KnowledgeProvider) -> None:
    """Versheids-overzicht: heatmap per domein."""
    summary = provider.get_freshness_summary()
    coverage = provider.get_domain_coverage()

    # Totaal overzicht
    with ui.row().classes("gap-4 q-mb-lg flex-wrap"):
        kpi_card(
            "Vers (<30d)",
            summary.fresh_count,
            icon="check_circle",
            color="positive",
        )
        kpi_card(
            "Verouderend (30-90d)",
            summary.aging_count,
            icon="warning",
            color="warning",
        )
        kpi_card(
            "Verlopen (>90d)",
            summary.stale_count,
            icon="error",
            color="negative",
        )

    # Per-domein freshness
    if not coverage:
        return

    ui.label("Versheid per Domein").classes("text-h6 q-mb-sm")

    with ui.grid(columns=3).classes("gap-3"):
        for c in sorted(coverage, key=lambda x: x.avg_freshness_days):
            fresh_color = (
                "positive"
                if c.avg_freshness_days < 30
                else "warning"
                if c.avg_freshness_days < 90
                else "negative"
            )
            with ui.card().classes("p-3"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label(c.domain.replace("_", " ").title()).classes("text-sm font-bold")
                    ui.badge(
                        f"{c.avg_freshness_days:.0f}d",
                        color=fresh_color,
                    ).classes("text-white")
                ui.label(f"{c.article_count} artikelen").classes("text-xs text-grey-7")
