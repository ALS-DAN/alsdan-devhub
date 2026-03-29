"""KPI Card component — herbruikbare metric-weergave met kleurindicator."""

from __future__ import annotations

from nicegui import ui


def kpi_card(
    label: str,
    value: str | int | float,
    *,
    icon: str = "info",
    color: str = "primary",
    subtitle: str = "",
) -> ui.card:
    """Render een KPI card met waarde, label en optioneel subtitle.

    Args:
        label: Korte beschrijving van de metric.
        value: De weer te geven waarde.
        icon: Quasar icon naam (bijv. "check_circle", "warning").
        color: Quasar kleur (bijv. "positive", "negative", "warning", "primary").
        subtitle: Optionele toelichting onder de waarde.
    """
    with ui.card().classes("w-48 p-4 text-center") as card:
        ui.icon(icon, color=color).classes("text-3xl")
        ui.label(str(value)).classes("text-2xl font-bold mt-1")
        ui.label(label).classes("text-sm text-grey-7")
        if subtitle:
            ui.label(subtitle).classes("text-xs text-grey-5 mt-1")
    return card
