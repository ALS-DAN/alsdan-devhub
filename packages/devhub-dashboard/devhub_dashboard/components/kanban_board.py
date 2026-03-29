"""Kanban Board component — kolom-layout voor planning pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui


@dataclass(frozen=True)
class KanbanItem:
    """Eén item in een kanban kolom."""

    title: str
    subtitle: str = ""
    badge_text: str = ""
    badge_color: str = "primary"
    border_color: str = "primary"


@dataclass(frozen=True)
class KanbanColumn:
    """Eén kolom in het kanban board."""

    title: str
    items: list[KanbanItem]
    dot_color: str = "grey"
    extra_count: int = 0  # "+N meer..." indicator


def kanban_board(columns: list[KanbanColumn]) -> None:
    """Render een kanban board met meerdere kolommen.

    Args:
        columns: Lijst van KanbanColumn objecten.
    """
    with ui.row().classes("gap-4 w-full overflow-x-auto"):
        for col in columns:
            with ui.card().classes("p-4 min-w-60 flex-1"):
                # Column header
                with ui.row().classes("items-center gap-2 mb-3"):
                    ui.icon("circle", color=col.dot_color).classes("text-xs")
                    ui.label(col.title).classes("text-subtitle2 font-bold uppercase")
                    ui.badge(
                        str(len(col.items) + col.extra_count),
                        color=col.dot_color,
                    ).classes("text-white")

                # Items
                if col.items:
                    for item in col.items:
                        with (
                            ui.card()
                            .classes("p-2 mb-2 border-l-4")
                            .style(f"border-left-color: var(--q-{item.border_color})")
                        ):
                            ui.label(item.title).classes("text-sm font-medium")
                            if item.subtitle:
                                with ui.row().classes("gap-2 items-center"):
                                    if item.badge_text:
                                        ui.badge(
                                            item.badge_text,
                                            color=item.badge_color,
                                        ).classes("text-white text-xs")
                                    ui.label(item.subtitle).classes("text-xs text-grey-6")
                else:
                    ui.label("Geen items").classes("text-xs text-grey-6 italic text-center py-4")

                # Extra count
                if col.extra_count > 0:
                    ui.label(f"+{col.extra_count} meer...").classes(
                        "text-xs text-grey-6 text-center mt-1"
                    )
