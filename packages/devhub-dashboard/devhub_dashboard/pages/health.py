"""Health paneel — 7 dimensies, severity findings, multi-metric trend chart."""

from __future__ import annotations

from devhub_core.contracts.node_interface import HealthStatus

from nicegui import ui

from devhub_dashboard.components.kpi_card import kpi_card
from devhub_dashboard.components.multi_trend_chart import multi_trend_chart
from devhub_dashboard.components.status_badge import StatusLevel, status_badge
from devhub_dashboard.data.history import HealthSnapshot, HistoryStore
from devhub_dashboard.data.providers import HealthProvider

_DIM_ICONS = {
    "tests": "🧪",
    "packages": "📦",
    "dependencies": "🔗",
    "architecture": "🏗️",
    "knowledge_health": "📚",
    "security": "🔒",
    "sprint_hygiene": "🏃",
}


def _status_to_level(status: HealthStatus) -> StatusLevel:
    mapping: dict[HealthStatus, StatusLevel] = {
        HealthStatus.HEALTHY: "healthy",
        HealthStatus.ATTENTION: "attention",
        HealthStatus.CRITICAL: "critical",
    }
    return mapping.get(status, "unknown")


def health_page(health_provider: HealthProvider, history_store: HistoryStore) -> None:
    """Render het Health paneel met 7 dimensies."""
    report = health_provider.get_health_report()

    # Sla snapshot op met uitgebreide metrics
    knowledge_items, knowledge_freshness = health_provider.get_knowledge_metrics()
    snapshot = HealthSnapshot.from_report(
        report,
        test_files=health_provider._count_test_files(),
        packages=health_provider._count_packages(),
    )
    history_store.save_snapshot(snapshot)

    # Header
    ui.label("System Health").classes("text-h4 q-mb-md")

    # KPI Strip
    with ui.row().classes("gap-4 q-mb-lg flex-wrap"):
        kpi_card(
            "Overall",
            report.overall.value.capitalize(),
            icon="monitor_heart",
            color="positive" if report.overall == HealthStatus.HEALTHY else "negative",
        )
        kpi_card(
            "Dimensies",
            len(report.checks),
            icon="checklist",
            color="primary",
            subtitle="gecontroleerd",
        )
        kpi_card(
            "P1 Alerts",
            len(report.p1_findings),
            icon="error",
            color="negative" if report.p1_findings else "positive",
        )
        kpi_card(
            "P2 Alerts",
            len(report.p2_findings),
            icon="warning",
            color="warning" if report.p2_findings else "positive",
        )

    # 7 Dimension Cards (2-koloms grid)
    ui.label("Dimensie Details").classes("text-h5 q-mb-sm")

    if report.checks:
        with ui.grid(columns=2).classes("gap-4 q-mb-lg"):
            for check in report.checks:
                icon = _DIM_ICONS.get(check.dimension, "📋")
                dim_label = f"{icon} {check.dimension.replace('_', ' ').title()}"

                with ui.card().classes("p-3"):
                    with ui.row().classes("items-center justify-between"):
                        ui.label(dim_label).classes("text-subtitle1 font-bold")
                        status_badge(_status_to_level(check.status))
                    ui.label(check.summary).classes("text-sm text-grey-7 mt-1")

                    if check.findings:
                        with ui.expansion("Findings", icon="search").classes("mt-2"):
                            for finding in check.findings:
                                with ui.row().classes("items-start gap-2"):
                                    ui.badge(
                                        finding.severity.value,
                                        color=(
                                            "negative"
                                            if "P1" in finding.severity.value
                                            else "warning"
                                        ),
                                    )
                                    with ui.column().classes("gap-0"):
                                        ui.label(finding.message).classes("text-sm")
                                        if finding.recommended_action:
                                            ui.label(
                                                f"Actie: {finding.recommended_action}"
                                            ).classes("text-xs text-grey-6")
    else:
        ui.label("Geen health checks beschikbaar.").classes("text-grey-6 italic")

    # Multi-metric Trend Chart
    ui.label("Trend — Multi-metric").classes("text-h5 q-mb-sm q-mt-lg")

    snapshots = history_store.load_snapshots()
    if snapshots:
        timestamps = [s.timestamp[:10] for s in snapshots]
        multi_trend_chart(
            timestamps,
            [
                ("Test bestanden", [float(s.test_files) for s in snapshots], "#4CAF50"),
                ("Packages", [float(s.packages) for s in snapshots], "#2196F3"),
                ("Knowledge items", [float(s.knowledge_items) for s in snapshots], "#9C27B0"),
            ],
            title="Metrics over tijd",
            y_label="Aantal",
        )
    else:
        ui.label("Geen historische data beschikbaar.").classes("text-grey-6 italic")

    # Health History tabel
    ui.label("Health Snapshots").classes("text-h5 q-mb-sm q-mt-lg")
    if snapshots:
        with ui.table(
            columns=[
                {
                    "name": "timestamp",
                    "label": "Datum",
                    "field": "timestamp",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "overall",
                    "label": "Status",
                    "field": "overall",
                    "align": "left",
                    "sortable": True,
                },
                {
                    "name": "dimensions",
                    "label": "Dimensies",
                    "field": "dimensions",
                    "align": "center",
                },
                {"name": "p1", "label": "P1", "field": "p1", "align": "center", "sortable": True},
                {"name": "p2", "label": "P2", "field": "p2", "align": "center", "sortable": True},
                {
                    "name": "tests",
                    "label": "Tests",
                    "field": "tests",
                    "align": "center",
                    "sortable": True,
                },
            ],
            rows=[
                {
                    "timestamp": s.timestamp[:10],
                    "overall": s.overall.capitalize(),
                    "dimensions": s.dimensions_checked,
                    "p1": s.p1_count,
                    "p2": s.p2_count,
                    "tests": s.test_files,
                }
                for s in reversed(snapshots[-10:])
            ],
        ).classes("w-full"):
            pass
    else:
        ui.label("Geen snapshots opgeslagen.").classes("text-grey-6 italic")
