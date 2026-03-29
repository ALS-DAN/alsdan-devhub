"""Multi Trend Chart component — Plotly multi-line chart voor meerdere metrics."""

from __future__ import annotations

from nicegui import ui


def multi_trend_chart(
    labels: list[str],
    series: list[tuple[str, list[float], str]],
    *,
    title: str = "",
    y_label: str = "",
    height: str = "300px",
) -> ui.plotly | ui.label:
    """Render een Plotly multi-line chart.

    Args:
        labels: X-as labels (shared across all series).
        series: List van (naam, waarden, kleur hex) tuples.
        title: Grafiek titel.
        y_label: Y-as label.
        height: CSS hoogte.
    """
    if not series or not any(vals for _, vals, _ in series):
        return ui.label("Geen historische data beschikbaar").classes("text-grey-6 italic")

    traces = []
    for name, values, color in series:
        traces.append(
            {
                "x": labels,
                "y": values,
                "type": "scatter",
                "mode": "lines+markers",
                "name": name,
                "line": {"color": color, "width": 2},
                "marker": {"size": 5},
            }
        )

    fig = {
        "data": traces,
        "layout": {
            "title": {"text": title},
            "xaxis": {"title": ""},
            "yaxis": {"title": y_label},
            "height": int(height.replace("px", "")) if "px" in height else 300,
            "margin": {"l": 50, "r": 20, "t": 40, "b": 40},
            "template": "plotly_dark",
            "legend": {"orientation": "h", "y": -0.15},
        },
    }
    return ui.plotly(fig).classes("w-full")
