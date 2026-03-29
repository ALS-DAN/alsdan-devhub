"""Knowledge detail pagina — volledige artikelweergave met metadata."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.data.article_parser import ParsedArticle
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider

# Grade kleuren
_GRADE_COLORS = {
    "GOLD": "#FFD700",
    "SILVER": "#C0C0C0",
    "BRONZE": "#CD7F32",
    "SPECULATIVE": "#9E9E9E",
}


def knowledge_detail_page(
    article_id: str,
    provider: KnowledgeProvider,
) -> None:
    """Render de detail-pagina voor een kennisartikel."""
    article = provider.get_article(article_id)

    if not article:
        ui.label(f"Artikel '{article_id}' niet gevonden.").classes("text-red text-h5")
        ui.button(
            "Terug naar kennisbank",
            icon="arrow_back",
            on_click=lambda: ui.navigate.to("/knowledge"),
        )
        return

    # Breadcrumb
    with ui.row().classes("items-center gap-2 q-mb-md"):
        ui.link("Knowledge", "/knowledge").classes("text-grey-7")
        ui.icon("chevron_right").classes("text-grey-7")
        ui.label(article.title).classes("text-grey-5")

    # Layout: content + sidebar
    with ui.row().classes("w-full gap-8"):
        # Main content
        with ui.column().classes("flex-grow"):
            ui.label(article.title).classes("text-h4 q-mb-sm")

            # Tags
            with ui.row().classes("gap-2 q-mb-md flex-wrap"):
                ui.badge(
                    article.grade,
                    color=_GRADE_COLORS.get(article.grade, "grey"),
                ).classes("text-white")
                ui.badge(article.domain.replace("_", " ")).classes("text-white")
                ui.icon("circle", color=article.freshness_color).classes("text-sm")
                if article.freshness_days < 9999:
                    ui.label(f"{article.freshness_days} dagen oud").classes("text-sm text-grey-7")

            # Content — lees het volledige .md bestand
            _render_article_content(article, provider)

        # Sidebar
        with ui.column().classes("w-72"):
            _metadata_sidebar(article, provider)


def _render_article_content(article: ParsedArticle, provider: KnowledgeProvider) -> None:
    """Render de markdown content van een artikel."""
    knowledge_root = provider._knowledge_root
    # Zoek het .md bestand
    md_path = knowledge_root / f"{article.file_path}.md"
    if md_path.exists():
        try:
            content = md_path.read_text(encoding="utf-8")
            ui.markdown(content).classes("w-full")
        except OSError:
            ui.label("Kon artikel niet laden.").classes("text-grey-6 italic")
    else:
        ui.label("Artikelbestand niet gevonden.").classes("text-grey-6 italic")


def _metadata_sidebar(article: ParsedArticle, provider: KnowledgeProvider) -> None:
    """Render metadata sidebar."""
    with ui.card().classes("p-4 w-full"):
        ui.label("Metadata").classes("text-subtitle1 font-bold q-mb-sm")

        # Basisinfo
        _sidebar_row("Domein", article.domain.replace("_", " ").title())
        _sidebar_row("Ring", article.ring.title())
        _sidebar_row("Grade", article.grade)
        _sidebar_row("Auteur", article.author)
        if article.date:
            _sidebar_row("Datum", article.date)
        if article.sprint:
            _sidebar_row("Sprint", str(article.sprint))

        # Sources
        if article.sources:
            ui.separator().classes("q-my-sm")
            ui.label("Bronnen").classes("text-sm font-bold")
            for src in article.sources:
                ui.label(f"- {src}").classes("text-xs text-grey-7")

        # RQ-tags
        if article.rq_tags:
            ui.separator().classes("q-my-sm")
            ui.label("RQ Tags").classes("text-sm font-bold")
            for rq in article.rq_tags:
                ui.badge(rq, color="info").classes("text-white")

    # Gerelateerde artikelen
    related = provider.get_articles(domain=article.domain)
    related = [r for r in related if r.article_id != article.article_id][:5]

    if related:
        with ui.card().classes("p-4 w-full mt-4"):
            ui.label("Gerelateerd").classes("text-subtitle1 font-bold q-mb-sm")
            for r in related:
                with ui.row().classes(
                    "items-center gap-2 cursor-pointer hover:bg-grey-9 p-1 rounded"
                ):
                    ui.icon("article", color="primary")
                    ui.link(r.title, f"/knowledge/{r.article_id}").classes("text-sm")

    # Start Research knop bij verouderde artikelen
    if article.freshness_days >= 90:
        ui.button(
            "Start Research (verouderd)",
            icon="science",
            color="warning",
            on_click=lambda: ui.navigate.to(f"/research?topic={article.title}"),
        ).classes("w-full mt-4")


def _sidebar_row(label: str, value: str) -> None:
    """Helper: render een metadata rij."""
    with ui.row().classes("justify-between w-full"):
        ui.label(label).classes("text-xs text-grey-7")
        ui.label(value).classes("text-xs font-bold")
