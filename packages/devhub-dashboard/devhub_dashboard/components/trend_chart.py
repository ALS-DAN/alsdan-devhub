"""Trend Chart component — Plotly wrapper voor historische data."""

from __future__ import annotations

from nicegui import ui


def trend_chart(
    labels: list[str],
    values: list[float],
    *,
    title: str = "",
    y_label: str = "",
    color: str = "#1976D2",
    height: str = "300px",
) -> ui.plotly | ui.label:
    """Render een Plotly lijn-grafiek voor trend data.

    Args:
        labels: X-as labels (bijv. timestamps of sprint-nummers).
        values: Y-as waarden.
        title: Grafiek titel.
        y_label: Y-as label.
        color: Lijn kleur (hex).
        height: CSS hoogte.

    Returns:
        ui.plotly element of ui.label als geen data.
    """
    if not values:
        return ui.label("Geen historische data beschikbaar").classes("text-grey-6 italic")

    fig = {
        "data": [
            {
                "x": labels,
                "y": values,
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"color": color, "width": 2},
                "marker": {"size": 6},
            }
        ],
        "layout": {
            "title": {"text": title},
            "xaxis": {"title": ""},
            "yaxis": {"title": y_label},
            "height": int(height.replace("px", "")) if "px" in height else 300,
            "margin": {"l": 50, "r": 20, "t": 40, "b": 40},
            "template": "plotly_dark",
        },
    }
    return ui.plotly(fig).classes("w-full")
