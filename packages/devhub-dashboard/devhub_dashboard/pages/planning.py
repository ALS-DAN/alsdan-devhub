"""Sprint & Planning paneel — analytics tabs, Kanban, velocity, cycle time."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.components.kanban_board import KanbanColumn, KanbanItem, kanban_board
from devhub_dashboard.components.kpi_card import kpi_card
from devhub_dashboard.data.providers import PlanningProvider


def planning_page(planning_provider: PlanningProvider) -> None:
    """Render het Sprint & Planning paneel."""
    sprint = planning_provider.get_sprint_info()
    inbox_items = planning_provider.get_inbox_items()
    fase_progress = planning_provider.get_fase_progress()

    # Header
    ui.label("Sprint & Planning").classes("text-h4 q-mb-md")

    # KPI Strip
    metrics = planning_provider.get_derived_metrics()
    with ui.row().classes("gap-4 q-mb-lg flex-wrap"):
        kpi_card(
            "Sprints",
            metrics.get("sprints_afgerond", sprint.nummer),
            icon="check_circle",
            color="positive",
            subtitle="afgerond",
        )
        kpi_card(
            "Accuracy",
            str(metrics.get("estimation_accuracy", "—")),
            icon="trending_up",
            color="positive",
            subtitle="schattingen",
        )
        kpi_card(
            "Avg Test Δ",
            f"+{metrics.get('avg_test_delta', 0)}",
            icon="science",
            color="primary",
            subtitle="per sprint",
        )
        kpi_card(
            "Inbox",
            len(inbox_items),
            icon="inbox",
            color="warning" if inbox_items else "positive",
            subtitle="items",
        )
        kpi_card(
            "Fase",
            sprint.fase or "?",
            icon="flag",
            color="info",
            subtitle="actief",
        )

    # Fase Pipeline (connected circles)
    _render_fase_pipeline(fase_progress)

    # Sprint Analytics Tabs
    ui.label("Sprint Analytics").classes("text-h5 q-mb-sm q-mt-lg")
    with ui.tabs().classes("w-full") as tabs:
        velocity_tab = ui.tab("Velocity & Cycle Time")
        history_tab = ui.tab("Sprint Historie")

    with ui.tab_panels(tabs, value=velocity_tab).classes("w-full"):
        with ui.tab_panel(velocity_tab):
            _render_velocity_tab(planning_provider)
        with ui.tab_panel(history_tab):
            _render_history_tab(planning_provider)

    # Planning Kanban
    ui.label("Planning Pipeline").classes("text-h5 q-mb-sm q-mt-lg")
    _render_kanban(planning_provider)


def _render_fase_pipeline(fase_progress: list[tuple[str, bool]]) -> None:
    """Render fase pipeline als connected circles."""
    if not fase_progress:
        return

    ui.label("Fase Pipeline").classes("text-h5 q-mb-sm")

    fase_names = {
        0: "Fundament",
        1: "Kernagents",
        2: "Skills",
        3: "Knowledge",
        4: "Verbindingen",
        5: "Uitbreiding",
    }

    with ui.row().classes("gap-0 items-center justify-center q-mb-lg flex-wrap"):
        for i, (fase_name, done) in enumerate(fase_progress):
            # Circle
            nummer = i
            is_active = not done and i > 0 and fase_progress[i - 1][1]
            # Check if this is the active fase (first non-done after a done)
            if not done:
                prev_done = all(fase_progress[j][1] for j in range(i))
                is_active = prev_done

            color = "positive" if done else ("primary" if is_active else "grey-5")
            icon_name = "check" if done else str(nummer)

            with ui.column().classes("items-center gap-1"):
                with ui.element("div").classes(
                    f"w-12 h-12 rounded-full flex items-center justify-center "
                    f"bg-{color} text-white font-bold text-lg"
                ):
                    ui.label(icon_name if not done else "✓")
                ui.label(fase_name).classes(f"text-xs text-{color} font-bold")
                ui.label(fase_names.get(nummer, "")).classes("text-xs text-grey-6")

            # Connector line (except after last)
            if i < len(fase_progress) - 1:
                line_color = "positive" if done else "grey-5"
                ui.element("div").classes(f"w-8 h-1 bg-{line_color} mt-n6")


def _render_velocity_tab(provider: PlanningProvider) -> None:
    """Render velocity bar chart + cycle time chart."""
    labels, deltas = provider.get_velocity_data()

    if labels:
        # Velocity bar chart
        fig = {
            "data": [
                {
                    "x": labels,
                    "y": deltas,
                    "type": "bar",
                    "marker": {
                        "color": ["#4CAF50" if d > 0 else "#9E9E9E" for d in deltas],
                    },
                    "name": "Test Delta",
                }
            ],
            "layout": {
                "title": {"text": "Test Delta per Sprint"},
                "xaxis": {"title": "Sprint"},
                "yaxis": {"title": "Tests Δ"},
                "height": 300,
                "margin": {"l": 50, "r": 20, "t": 40, "b": 60},
                "template": "plotly_dark",
            },
        }
        ui.plotly(fig).classes("w-full q-mb-md")

    # Cycle time chart
    ct_labels, ct_days = provider.get_cycle_time_data()
    if ct_labels:
        fig = {
            "data": [
                {
                    "x": ct_labels,
                    "y": ct_days,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "line": {"color": "#2196F3", "width": 2},
                    "marker": {"size": 6},
                    "name": "Cycle Time",
                }
            ],
            "layout": {
                "title": {"text": "Cycle Time Trend (dagen)"},
                "xaxis": {"title": ""},
                "yaxis": {"title": "Dagen"},
                "height": 250,
                "margin": {"l": 50, "r": 20, "t": 40, "b": 80},
                "template": "plotly_dark",
            },
        }
        ui.plotly(fig).classes("w-full")

    if not labels and not ct_labels:
        ui.label("Geen velocity data beschikbaar.").classes("text-grey-6 italic")


def _render_history_tab(provider: PlanningProvider) -> None:
    """Render sorteerbare sprint historie tabel."""
    history = provider.get_sprint_history()

    if not history:
        ui.label("Geen sprint historie beschikbaar.").classes("text-grey-6 italic")
        return

    with ui.table(
        columns=[
            {"name": "nr", "label": "#", "field": "nr", "align": "center", "sortable": True},
            {"name": "naam", "label": "Sprint", "field": "naam", "align": "left", "sortable": True},
            {"name": "type", "label": "Type", "field": "type", "align": "center", "sortable": True},
            {"name": "size", "label": "Size", "field": "size", "align": "center", "sortable": True},
            {
                "name": "delta",
                "label": "Tests Δ",
                "field": "delta",
                "align": "center",
                "sortable": True,
            },
            {"name": "status", "label": "Status", "field": "status", "align": "center"},
        ],
        rows=[
            {
                "nr": h.nummer,
                "naam": h.naam,
                "type": h.sprint_type,
                "size": h.size,
                "delta": f"+{h.tests_delta}" if h.tests_delta > 0 else str(h.tests_delta),
                "status": "✅ DONE",
            }
            for h in history
        ],
        pagination={"rowsPerPage": 15},
    ).classes("w-full"):
        pass


def _render_kanban(provider: PlanningProvider) -> None:
    """Render planning pipeline kanban board."""
    inbox_items = provider.get_inbox_items()
    sprint = provider.get_sprint_info()
    history = provider.get_sprint_history()

    # INBOX kolom
    inbox_kanban = [
        KanbanItem(
            title=item.filename.replace(
                "SPRINT_INTAKE_",
                "",
            )
            .replace(".md", "")
            .replace("_", " ")[:40],
            badge_text=item.sprint_type,
            badge_color="primary" if item.sprint_type == "FEAT" else "purple",
            subtitle=item.node,
            border_color="warning",
        )
        for item in inbox_items[:5]
    ]

    # ACTIEF kolom
    actief_items = []
    if sprint.naam:
        actief_items.append(
            KanbanItem(
                title=f"#{sprint.nummer} {sprint.naam}",
                badge_text="ACTIEF",
                badge_color="primary",
                border_color="primary",
            )
        )

    # DONE kolom (laatste 3)
    done_items = [
        KanbanItem(
            title=f"#{h.nummer} {h.naam[:30]}",
            badge_text=h.sprint_type,
            badge_color="positive",
            subtitle=f"+{h.tests_delta} tests" if h.tests_delta > 0 else "",
            border_color="positive",
        )
        for h in reversed(history[-3:])
    ]

    kanban_board(
        [
            KanbanColumn(
                title="INBOX",
                items=inbox_kanban,
                dot_color="warning",
                extra_count=max(0, len(inbox_items) - 5),
            ),
            KanbanColumn(
                title="ACTIEF",
                items=actief_items,
                dot_color="primary",
            ),
            KanbanColumn(
                title="DONE",
                items=done_items,
                dot_color="positive",
                extra_count=max(0, len(history) - 3),
            ),
        ]
    )
