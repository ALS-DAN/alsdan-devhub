"""Research Card component — kaartje voor research requests met approve/reject."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from devhub_dashboard.data.research_queue import ResearchQueueItem


def research_card(
    item: ResearchQueueItem,
    *,
    on_approve: Callable[[str], None] | None = None,
    on_reject: Callable[[str], None] | None = None,
) -> ui.card:
    """Render een research request kaartje.

    Args:
        item: Het research queue item.
        on_approve: Callback bij goedkeuring (item_id).
        on_reject: Callback bij afwijzing (item_id).
    """
    # Kleur op basis van stream
    stream_colors = {"agent": "info", "user": "primary", "auto": "grey"}
    stream_color = stream_colors.get(item.stream, "grey")

    # Status kleuren
    status_colors = {
        "pending": "warning",
        "approved": "positive",
        "rejected": "negative",
        "in_progress": "info",
        "completed": "positive",
    }
    status_color = status_colors.get(item.status, "grey")

    with ui.card().classes("p-3 w-full") as card:
        # Header: stream badge + status
        with ui.row().classes("items-center justify-between w-full"):
            with ui.row().classes("items-center gap-2"):
                ui.badge(item.stream.upper(), color=stream_color).classes("text-white")
                ui.label(item.topic).classes("text-subtitle1 font-bold")
            ui.badge(item.status.upper(), color=status_color).classes("text-white")

        # Details
        with ui.row().classes("gap-4 mt-1"):
            ui.label(f"Domein: {item.domain}").classes("text-sm text-grey-7")
            if item.source_agent:
                ui.label(f"Bron: {item.source_agent}").classes("text-sm text-grey-7")
            if item.depth:
                ui.label(f"Diepte: {item.depth}").classes("text-sm text-grey-7")

        if item.description:
            ui.label(item.description).classes("text-sm text-grey-6 mt-1")

        # Acties (alleen voor pending items)
        if item.status == "pending" and (on_approve or on_reject):
            with ui.row().classes("gap-2 mt-2"):
                if on_approve:
                    ui.button(
                        "Goedkeuren",
                        icon="check",
                        color="positive",
                        on_click=lambda _, iid=item.item_id: on_approve(iid),
                    ).props("flat dense")
                if on_reject:
                    ui.button(
                        "Afwijzen",
                        icon="close",
                        color="negative",
                        on_click=lambda _, iid=item.item_id: on_reject(iid),
                    ).props("flat dense")

    return card
