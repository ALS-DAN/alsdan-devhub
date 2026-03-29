"""Status Flow component — horizontale status-pipeline visualisatie."""

from __future__ import annotations

from nicegui import ui


_STEPS = ["pending", "approved", "in_progress", "review", "completed"]
_STEP_LABELS = {
    "pending": "Pending",
    "approved": "Goedgekeurd",
    "in_progress": "Onderzoek",
    "review": "Review",
    "completed": "Afgerond",
}
_STEP_ICONS = {
    "pending": "hourglass_empty",
    "approved": "check_circle",
    "in_progress": "search",
    "review": "rate_review",
    "completed": "done_all",
}


def status_flow(
    current_status: str,
    history: list[dict] | None = None,
) -> None:
    """Render een horizontale status-pipeline.

    Args:
        current_status: Huidige status (RequestStatus value).
        history: Optionele status_history lijst met timestamps.
    """
    current_idx = _STEPS.index(current_status) if current_status in _STEPS else -1
    rejected = current_status == "rejected"

    with ui.row().classes("items-center gap-0 w-full justify-center flex-wrap"):
        for i, step in enumerate(_STEPS):
            # Determine display properties
            if rejected and step == "approved":
                color = "negative"
                icon = "cancel"
                label = "Afgewezen"
            elif i < current_idx:
                color = "positive"
                icon = _STEP_ICONS[step]
                label = _STEP_LABELS[step]
            elif i == current_idx:
                color = "info"
                icon = _STEP_ICONS[step]
                label = _STEP_LABELS[step]
            else:
                color = "grey-5"
                icon = _STEP_ICONS[step]
                label = _STEP_LABELS[step]

            # Step circle + label
            with ui.column().classes("items-center"):
                ui.icon(icon, color=color).classes("text-2xl")
                ui.label(label).classes(f"text-xs text-{color}")

                # Timestamp from history if available
                if history:
                    ts = next(
                        (h["timestamp"][:10] for h in history if h["status"] == step),
                        None,
                    )
                    if ts:
                        ui.label(ts).classes("text-xs text-grey-7")

            # Connector line (except after last)
            if i < len(_STEPS) - 1:
                line_color = "positive" if i < current_idx else "grey-8"
                ui.element("div").style(
                    f"height: 2px; width: 40px; background: var(--q-{line_color}); "
                    f"align-self: center; margin-top: -20px;"
                )
