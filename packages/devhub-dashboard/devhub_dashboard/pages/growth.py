"""Growth/Mentor paneel — dynamic Skill Radar, challenges, recommendations, T-shape."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.components.kpi_card import kpi_card
from devhub_dashboard.data.providers import GrowthProvider

_DREYFUS_LABELS = {1: "Novice", 2: "Beginner", 3: "Competent", 4: "Proficient", 5: "Expert"}


def growth_page(provider: GrowthProvider) -> None:
    """Render het Growth/Mentor paneel."""
    ui.label("Developer Growth").classes("text-h4 q-mb-md")

    radar_data = provider.get_skill_radar_data()
    broad, deep = provider.get_t_shape()
    challenges = provider.get_challenges()
    recommendations = provider.get_recommendations()
    sprint_count = provider.get_completed_sprint_count()

    # KPIs
    avg_level = sum(lv for _, lv in radar_data) / len(radar_data) if radar_data else 0
    with ui.row().classes("gap-4 q-mb-lg flex-wrap"):
        kpi_card("Fase", "BOUWEN", icon="construction", color="primary", subtitle="O-B-B model")
        kpi_card(
            "Sprints",
            sprint_count,
            icon="check_circle",
            color="positive",
            subtitle="afgerond",
        )
        kpi_card(
            "Avg Level",
            f"{avg_level:.1f}",
            icon="trending_up",
            color="primary",
            subtitle=_DREYFUS_LABELS.get(round(avg_level), ""),
        )
        kpi_card(
            "Domeinen",
            len(radar_data),
            icon="radar",
            color="info",
            subtitle=f"{len(broad)} broad, {len(deep)} deep",
        )

    # Skill Radar
    ui.label("Skill Radar — Dreyfus Model").classes("text-h5 q-mb-sm")
    _render_skill_radar(radar_data)

    # Domain Detail Cards
    ui.label("Domein Details").classes("text-h5 q-mb-sm q-mt-lg")
    _render_domain_cards(radar_data)

    # T-Shape Profiel
    ui.label("T-Shape Profiel").classes("text-h5 q-mb-sm q-mt-lg")
    _render_t_shape(broad, deep)

    # Challenge Engine
    ui.label("Challenge Engine").classes("text-h5 q-mb-sm q-mt-lg")
    _render_challenges(challenges)

    # Learning Recommendations
    ui.label("Learning Recommendations").classes("text-h5 q-mb-sm q-mt-lg")
    _render_recommendations(recommendations)


def _render_skill_radar(radar_data: list[tuple[str, int]]) -> None:
    """Render Plotly radar chart met Dreyfus levels."""
    if not radar_data:
        ui.label("Geen skill data beschikbaar.").classes("text-grey-6 italic")
        return

    domains = [d[0] for d in radar_data]
    levels = [d[1] for d in radar_data]

    # Close the radar
    domains_closed = domains + [domains[0]]
    levels_closed = levels + [levels[0]]

    # Target: current + 1 (capped at 5)
    target_levels = [min(lv + 1, 5) for lv in levels] + [min(levels[0] + 1, 5)]

    fig = {
        "data": [
            {
                "type": "scatterpolar",
                "r": levels_closed,
                "theta": domains_closed,
                "fill": "toself",
                "fillcolor": "rgba(25, 118, 210, 0.2)",
                "line": {"color": "#1976D2", "width": 2},
                "name": "Huidig",
            },
            {
                "type": "scatterpolar",
                "r": target_levels,
                "theta": domains_closed,
                "fill": "none",
                "line": {"color": "#4CAF50", "width": 1, "dash": "dash"},
                "name": "Target (+1)",
            },
        ],
        "layout": {
            "polar": {
                "radialaxis": {
                    "visible": True,
                    "range": [0, 5],
                    "tickvals": [1, 2, 3, 4, 5],
                    "ticktext": list(_DREYFUS_LABELS.values()),
                },
            },
            "showlegend": True,
            "legend": {"orientation": "h", "y": -0.1},
            "height": 400,
            "template": "plotly_dark",
            "margin": {"l": 80, "r": 80, "t": 20, "b": 40},
        },
    }
    ui.plotly(fig).classes("w-full")


def _render_domain_cards(radar_data: list[tuple[str, int]]) -> None:
    """Render uitklapbare domain detail cards."""
    if not radar_data:
        return

    with ui.grid(columns=2).classes("gap-3"):
        for name, level in radar_data:
            label = _DREYFUS_LABELS.get(level, "?")
            progress = level / 5.0
            next_level = min(level + 1, 5)
            next_label = _DREYFUS_LABELS.get(next_level, "?")

            level_color = {
                1: "grey",
                2: "primary",
                3: "positive",
                4: "warning",
                5: "positive",
            }.get(level, "grey")

            with ui.card().classes("p-3"):
                with ui.row().classes("items-center justify-between"):
                    ui.label(name).classes("text-subtitle1 font-bold")
                    ui.badge(f"{level} {label}", color=level_color).classes("text-white")

                # Progress bar to next level
                with ui.linear_progress(value=progress).classes("mt-2"):
                    pass
                ui.label(f"Volgende: {next_label} (level {next_level})").classes(
                    "text-xs text-grey-6 mt-1"
                )


def _render_t_shape(broad: list[str], deep: list[str]) -> None:
    """Render T-shape developer profiel."""
    with ui.card().classes("p-4 w-full"):
        # Breed (horizontale balk)
        ui.label("Breedte (level 2+)").classes("text-subtitle2 font-bold")
        with ui.row().classes("gap-2 flex-wrap q-mb-md"):
            if broad:
                for domain in broad:
                    ui.badge(domain, color="primary").classes("text-white")
            else:
                ui.label("Nog geen brede domeinen").classes("text-grey-6 italic text-xs")

        # Diep (verticale balk)
        ui.label("Diepte (level 3+ specialisatie)").classes("text-subtitle2 font-bold")
        with ui.row().classes("gap-2 flex-wrap"):
            if deep:
                for domain in deep:
                    ui.badge(domain, color="info").classes("text-white")
            else:
                ui.label("Nog geen specialisatie — focus op level 3 bereiken").classes(
                    "text-grey-6 italic text-xs"
                )


def _render_challenges(challenges: list[dict]) -> None:
    """Render challenge engine paneel."""
    if not challenges:
        ui.label(
            "Geen challenges beschikbaar. "
            "Draai /devhub-mentor voor gepersonaliseerde uitdagingen."
        ).classes("text-grey-6 italic")
        return

    # Group by status
    active = [c for c in challenges if c.get("status") == "ACCEPTED"]
    proposed = [c for c in challenges if c.get("status") == "PROPOSED"]
    completed = [c for c in challenges if c.get("status") == "COMPLETED"]

    if active:
        ui.label("Actieve Challenges").classes("text-subtitle2 font-bold q-mb-sm")
        for c in active:
            _challenge_card(c, "primary")

    if proposed:
        ui.label("Voorgesteld").classes("text-subtitle2 font-bold q-mb-sm q-mt-md")
        for c in proposed:
            _challenge_card(c, "info")

    if completed:
        ui.label("Afgerond").classes("text-subtitle2 font-bold q-mb-sm q-mt-md")
        for c in completed[:3]:
            _challenge_card(c, "positive")


def _challenge_card(challenge: dict, color: str) -> None:
    with ui.card().classes("p-3 mb-2"):
        with ui.row().classes("items-center gap-2"):
            ui.badge(
                challenge.get("challenge_type", "challenge"),
                color=color,
            ).classes("text-white text-xs")
            ui.badge(
                challenge.get("domain", ""),
                color="grey",
            ).classes("text-white text-xs")
        ui.label(challenge.get("description", "")).classes("text-sm mt-1")
        if challenge.get("scaffolding_level"):
            ui.label(f"Scaffolding: {challenge['scaffolding_level']}").classes(
                "text-xs text-grey-6 mt-1"
            )


def _render_recommendations(recommendations: list[dict]) -> None:
    """Render learning recommendation cards."""
    if not recommendations:
        ui.label(
            "Geen aanbevelingen beschikbaar. " "Draai /devhub-mentor voor learning recommendations."
        ).classes("text-grey-6 italic")
        return

    with ui.grid(columns=2).classes("gap-3"):
        for rec in recommendations[:6]:
            type_colors = {
                "paper": "purple",
                "docs": "primary",
                "tutorial": "positive",
                "video": "info",
                "book_chapter": "warning",
            }
            with ui.card().classes("p-3"):
                with ui.row().classes("items-center gap-2"):
                    ui.badge(
                        rec.get("resource_type", "resource"),
                        color=type_colors.get(rec.get("resource_type", ""), "grey"),
                    ).classes("text-white text-xs")
                    ui.badge(
                        rec.get("domain", ""),
                        color="grey",
                    ).classes("text-white text-xs")
                ui.label(rec.get("title", "")).classes("text-sm font-bold mt-1")
                if rec.get("rationale"):
                    ui.label(rec["rationale"]).classes("text-xs text-grey-7 mt-1")
                with ui.row().classes("gap-2 mt-1"):
                    if rec.get("estimated_minutes"):
                        ui.label(f"~{rec['estimated_minutes']} min").classes("text-xs text-grey-6")
                    if rec.get("priority"):
                        ui.badge(
                            rec["priority"],
                            color="warning" if rec["priority"] == "URGENT" else "grey",
                        ).classes("text-white text-xs")
