"""Governance paneel — compliance gauge, interactive articles, OWASP ASI, audit trail."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.data.providers import GovernanceProvider


def governance_page(provider: GovernanceProvider) -> None:
    """Render het Governance paneel."""
    ui.label("Governance & Compliance").classes("text-h4 q-mb-md")

    score = provider.get_compliance_score()
    articles = provider.get_article_statuses()
    security = provider.get_security_summary()
    asi_coverage = provider.get_asi_coverage()

    # KPI + Compliance Gauge row
    with ui.row().classes("gap-6 q-mb-lg items-start flex-wrap"):
        # Compliance Score card met CSS gauge
        with ui.card().classes("p-4"):
            ui.label("Compliance Score").classes("text-subtitle1 font-bold q-mb-sm")
            with ui.row().classes("items-center gap-6"):
                _render_compliance_gauge(score)
                with ui.column().classes("gap-2"):
                    _gauge_legend("positive", f"{score.active} Actief")
                    _gauge_legend("warning", f"{score.attention} Aandacht")
                    _gauge_legend("negative", f"{score.violation} Overtreding")

        # Security Summary
        with ui.card().classes("p-4 flex-1 min-w-64"):
            ui.label("Security Status").classes("text-subtitle1 font-bold q-mb-sm")
            if security.get("available"):
                with ui.row().classes("gap-6"):
                    _security_metric("LOW", "Overall Risk", "positive")
                    _security_metric(
                        str(security.get("report_count", 0)),
                        "Audit rapporten",
                        "primary",
                    )
            else:
                ui.label("Geen audit data — draai /devhub-redteam").classes("text-grey-6 italic")

    # DEV_CONSTITUTION Interactive View
    ui.label("DEV_CONSTITUTION — 9 Artikelen").classes("text-h5 q-mb-sm")

    for article in articles:
        status_color = {
            "active": "positive",
            "attention": "warning",
            "violation": "negative",
        }.get(article.status, "grey")

        badge_text = {
            "active": "Actief",
            "attention": "Aandacht",
            "violation": "Overtreding",
        }.get(article.status, "Onbekend")

        with ui.card().classes("p-3 mb-2 w-full"):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-3"):
                    ui.badge(article.article_id, color="primary").classes("text-white")
                    ui.label(article.title).classes("text-subtitle1 font-bold")
                with ui.row().classes("items-center gap-2"):
                    ui.label(article.verification).classes("text-xs text-grey-6")
                    ui.badge(badge_text, color=status_color).classes("text-white")
            ui.label(article.description).classes("text-xs text-grey-7 mt-1")

    # OWASP ASI Coverage
    ui.label("OWASP ASI 2026 Coverage").classes("text-h5 q-mb-sm q-mt-lg")
    _render_asi_bars(asi_coverage)

    # Impact Zone Distribution
    ui.label("Impact-zonering").classes("text-h5 q-mb-sm q-mt-lg")
    with ui.row().classes("gap-4"):
        for zone, color, desc in [
            ("GREEN", "positive", "Veilig — tests draaien, geen review nodig"),
            ("YELLOW", "warning", "Review vereist — significante wijzigingen"),
            ("RED", "negative", "Menselijke goedkeuring — architectuur/breaking changes"),
        ]:
            with ui.card().classes("p-3 flex-1"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("circle", color=color)
                    ui.label(zone).classes("font-bold")
                ui.label(desc).classes("text-xs text-grey-7 mt-1")


def _render_compliance_gauge(score) -> None:
    """Render compliance gauge als circulaire indicator."""
    pct = score.percentage
    # CSS conic-gradient gauge
    angle = int(pct * 3.6)  # 360 degrees
    with ui.element("div").classes("flex items-center justify-center"):
        bg = (
            f"conic-gradient(#4CAF50 0deg {angle}deg, " f"rgba(255,255,255,0.08) {angle}deg 360deg)"
        )
        with ui.element("div").style(
            f"width: 120px; height: 120px; border-radius: 50%; "
            f"background: {bg}; "
            f"display: flex; align-items: center; justify-content: center;"
        ):
            with ui.element("div").style(
                "width: 85px; height: 85px; border-radius: 50%; "
                "background: var(--q-dark); display: flex; flex-direction: column; "
                "align-items: center; justify-content: center;"
            ):
                ui.label(f"{pct:.0f}%").classes("text-2xl font-bold text-positive")
                ui.label("compliance").classes("text-xs text-grey-6")


def _gauge_legend(color: str, text: str) -> None:
    with ui.row().classes("items-center gap-2"):
        ui.icon("circle", color=color).classes("text-xs")
        ui.label(text).classes("text-sm")


def _security_metric(value: str, label: str, color: str) -> None:
    with ui.column().classes("items-center"):
        ui.label(value).classes(f"text-2xl font-bold text-{color}")
        ui.label(label).classes("text-xs text-grey-7")


def _render_asi_bars(coverage: dict[str, str]) -> None:
    """Render OWASP ASI horizontal bars."""
    color_map = {
        "MITIGATED": ("positive", 100),
        "PARTIAL": ("warning", 50),
        "VULNERABLE": ("negative", 25),
        "NOT_ASSESSED": ("grey-5", 0),
    }

    with ui.card().classes("p-4 w-full"):
        for asi_id, status in sorted(coverage.items()):
            color, width = color_map.get(status, ("grey-5", 0))
            badge_color = {
                "MITIGATED": "positive",
                "PARTIAL": "warning",
                "VULNERABLE": "negative",
                "NOT_ASSESSED": "grey",
            }.get(status, "grey")

            with ui.row().classes("items-center gap-3 mb-2 w-full"):
                ui.label(asi_id).classes("text-xs font-mono w-12 text-grey-6")
                with (
                    ui.element("div")
                    .classes("flex-1 h-5 rounded")
                    .style("background: rgba(255,255,255,0.05)")
                ):
                    if width > 0:
                        ui.element("div").classes(f"h-5 rounded bg-{color}").style(
                            f"width: {width}%"
                        )
                ui.badge(status, color=badge_color).classes("text-white text-xs w-24")
