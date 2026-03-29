"""Research detail pagina — status-flow, RQ tracking, review paneel."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.components.status_flow import status_flow
from devhub_dashboard.data.research_queue import (
    ResearchQueueItem,
    ResearchQueueManager,
)


def research_detail_page(
    item_id: str,
    queue_manager: ResearchQueueManager,
) -> None:
    """Render de detail-pagina voor een research request."""
    item = queue_manager.get_item(item_id)

    if not item:
        ui.label(f"Research '{item_id}' niet gevonden.").classes("text-red text-h5")
        ui.button(
            "Terug naar research",
            icon="arrow_back",
            on_click=lambda: ui.navigate.to("/research"),
        )
        return

    # Breadcrumb
    with ui.row().classes("items-center gap-2 q-mb-md"):
        ui.link("Research", "/research").classes("text-grey-7")
        ui.icon("chevron_right").classes("text-grey-7")
        ui.label(item.topic).classes("text-grey-5")

    # Title
    ui.label(item.topic).classes("text-h4 q-mb-md")

    # Status flow
    ui.label("Status").classes("text-h6 q-mb-sm")
    status_flow(item.status, item.status_history)

    # Layout: details + sidebar
    with ui.row().classes("w-full gap-8 mt-6"):
        # Main content
        with ui.column().classes("flex-grow"):
            _detail_content(item)

        # Sidebar
        with ui.column().classes("w-72"):
            _detail_sidebar(item, queue_manager)


def _detail_content(item: ResearchQueueItem) -> None:
    """Render de hoofdcontent van een research detail."""
    # Achtergrond
    if item.background:
        ui.label("Achtergrond & Motivatie").classes("text-h6 q-mb-sm")
        ui.label(item.background).classes("text-grey-7 q-mb-md")

    # Onderzoeksvragen
    if item.research_questions:
        ui.label("Onderzoeksvragen").classes("text-h6 q-mb-sm")
        for i, rq in enumerate(item.research_questions, 1):
            with ui.row().classes("items-start gap-2 q-mb-sm"):
                ui.badge(f"RQ{i}", color="info").classes("text-white mt-1")
                ui.label(rq).classes("text-grey-7")

    # Scope
    if item.scope_in or item.scope_out:
        ui.label("Scope").classes("text-h6 q-mb-sm mt-4")
        with ui.row().classes("gap-4 w-full"):
            if item.scope_in:
                with ui.card().classes("p-3 flex-grow"):
                    ui.label("IN scope").classes("text-sm font-bold text-positive")
                    ui.label(item.scope_in).classes("text-sm text-grey-7")
            if item.scope_out:
                with ui.card().classes("p-3 flex-grow"):
                    ui.label("OUT scope").classes("text-sm font-bold text-negative")
                    ui.label(item.scope_out).classes("text-sm text-grey-7")

    # Beschrijving (v1 field)
    if item.description:
        ui.label("Beschrijving").classes("text-h6 q-mb-sm mt-4")
        ui.label(item.description).classes("text-grey-7")

    # Review notes
    if item.review_notes:
        ui.label("Review Opmerkingen").classes("text-h6 q-mb-sm mt-4")
        with ui.card().classes("p-3 w-full bg-yellow-900"):
            ui.label(item.review_notes).classes("text-grey-7")

    # Rejection reason
    if item.rejection_reason:
        ui.label("Reden Afwijzing").classes("text-h6 q-mb-sm mt-4")
        with ui.card().classes("p-3 w-full bg-red-900"):
            ui.label(item.rejection_reason).classes("text-grey-7")

    # Completed articles
    if item.completed_articles:
        ui.label("Opgeleverde Artikelen").classes("text-h6 q-mb-sm mt-4")
        for art_id in item.completed_articles:
            with ui.row().classes("items-center gap-2"):
                ui.icon("article", color="positive")
                ui.link(art_id, f"/knowledge/{art_id}").classes("text-sm")


def _detail_sidebar(item: ResearchQueueItem, queue_manager: ResearchQueueManager) -> None:
    """Render de metadata sidebar."""
    with ui.card().classes("p-4 w-full"):
        ui.label("Details").classes("text-subtitle1 font-bold q-mb-sm")

        _sidebar_row("ID", item.item_id)
        _sidebar_row("Stream", item.stream.upper())
        _sidebar_row("Status", item.status.upper())
        _sidebar_row("Domein", item.domain.replace("_", " ").title())
        _sidebar_row("Diepte", item.depth)
        _sidebar_row("Prioriteit", str(item.priority))

        if item.expected_grade:
            _sidebar_row("Verwachte Grade", item.expected_grade)
        if item.document_category:
            _sidebar_row("Document Type", item.document_category)
        if item.source_agent:
            _sidebar_row("Bron Agent", item.source_agent)
        if item.deadline:
            _sidebar_row("Deadline", item.deadline)
        if item.created_at:
            _sidebar_row("Aangemaakt", item.created_at[:10])
        if item.updated_at:
            _sidebar_row("Bijgewerkt", item.updated_at[:10])

    # Gerelateerde artikelen
    if item.related_articles:
        with ui.card().classes("p-4 w-full mt-4"):
            ui.label("Gerelateerde Kennis").classes("text-subtitle1 font-bold q-mb-sm")
            for art_id in item.related_articles:
                with ui.row().classes("items-center gap-2"):
                    ui.icon("article", color="primary")
                    ui.link(art_id, f"/knowledge/{art_id}").classes("text-sm")

    # Status history
    if item.status_history:
        with ui.card().classes("p-4 w-full mt-4"):
            ui.label("Geschiedenis").classes("text-subtitle1 font-bold q-mb-sm")
            for h in reversed(item.status_history):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("history", color="grey").classes("text-sm")
                    ui.label(h.get("status", "").upper()).classes("text-xs font-bold")
                    ts = h.get("timestamp", "")[:16]
                    ui.label(ts).classes("text-xs text-grey-7")
                    actor = h.get("actor", "")
                    if actor:
                        ui.label(f"({actor})").classes("text-xs text-grey-7")


def _sidebar_row(label: str, value: str) -> None:
    """Helper: render een metadata rij."""
    with ui.row().classes("justify-between w-full"):
        ui.label(label).classes("text-xs text-grey-7")
        ui.label(value).classes("text-xs font-bold")
