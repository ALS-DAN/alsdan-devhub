"""Knowledge Card component — herbruikbare artikelkaart met metadata."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.data.article_parser import ParsedArticle

# Kleur-mappings
_RING_COLORS = {"core": "primary", "agent": "positive", "project": "warning"}
_GRADE_COLORS = {
    "GOLD": "#FFD700",
    "SILVER": "#C0C0C0",
    "BRONZE": "#CD7F32",
    "SPECULATIVE": "#9E9E9E",
}


def knowledge_card(
    article: ParsedArticle,
    *,
    show_summary: bool = True,
    clickable: bool = True,
) -> ui.card:
    """Render een kennisartikel-kaart.

    Args:
        article: Het geparseerde artikel.
        show_summary: Toon samenvatting (eerste 2-3 zinnen).
        clickable: Navigeer naar detail-pagina bij klik.
    """
    with ui.card().classes("p-3 w-full") as card:
        if clickable:
            card.classes("cursor-pointer")
            card.on("click", lambda: ui.navigate.to(f"/knowledge/{article.article_id}"))

        # Header: title + grade badge
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(article.title).classes("text-subtitle1 font-bold")
            ui.badge(
                article.grade,
                color=_GRADE_COLORS.get(article.grade, "grey"),
            ).classes("text-white")

        # Tags: domain, ring, freshness
        with ui.row().classes("gap-2 mt-1 flex-wrap"):
            ui.badge(
                article.domain.replace("_", " "),
                color=_RING_COLORS.get(article.ring, "grey"),
            ).classes("text-white")
            ring_num = {"core": "1", "agent": "2", "project": "3"}.get(article.ring, "?")
            ui.badge(f"Ring {ring_num}").classes("text-white")

            # Freshness indicator
            ui.icon("circle", color=article.freshness_color).classes("text-xs")
            if article.freshness_days < 9999:
                ui.label(f"{article.freshness_days}d").classes("text-xs text-grey-7")

        # Summary
        if show_summary and article.summary:
            ui.label(article.summary).classes("text-sm text-grey-6 mt-1").style(
                "display: -webkit-box; -webkit-line-clamp: 3; "
                "-webkit-box-orient: vertical; overflow: hidden;"
            )

        # Footer: date + author + sprint
        with ui.row().classes("gap-4 mt-2 text-xs text-grey-7"):
            if article.date:
                ui.label(f"{article.date}")
            if article.author != "unknown":
                ui.label(f"{article.author}")
            if article.sprint:
                ui.label(f"Sprint {article.sprint}")

    return card
