"""Status Badge component — groen/geel/rood indicator voor domein-status."""

from __future__ import annotations

from typing import Literal

from nicegui import ui

StatusLevel = Literal["healthy", "attention", "critical", "unknown"]

_STATUS_CONFIG: dict[StatusLevel, tuple[str, str, str]] = {
    # (kleur, icon, label)
    "healthy": ("positive", "check_circle", "Gezond"),
    "attention": ("warning", "warning", "Aandacht"),
    "critical": ("negative", "error", "Kritiek"),
    "unknown": ("grey", "help", "Onbekend"),
}


def status_badge(level: StatusLevel, text: str = "") -> ui.row:
    """Render een status badge met kleur-indicator.

    Args:
        level: Status niveau (healthy/attention/critical/unknown).
        text: Optionele tekst naast de badge.
    """
    color, icon, default_text = _STATUS_CONFIG.get(level, _STATUS_CONFIG["unknown"])
    display_text = text or default_text

    with ui.row(wrap=False).classes("items-center gap-2") as row:
        ui.icon(icon, color=color).classes("text-lg")
        ui.label(display_text).classes("text-sm")
    return row
