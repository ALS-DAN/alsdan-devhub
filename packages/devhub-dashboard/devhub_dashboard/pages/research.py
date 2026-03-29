"""Research & Kennisverzoeken paneel — drie-stromen tabs + uitgebreid formulier."""

from __future__ import annotations

from nicegui import ui

from devhub_dashboard.components.research_card import research_card
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider
from devhub_dashboard.data.research_queue import (
    RequestStatus,
    RequestStream,
    ResearchQueueManager,
)


def research_page(
    queue_manager: ResearchQueueManager,
    knowledge_provider: KnowledgeProvider | None = None,
) -> None:
    """Render het Research & Kennisverzoeken paneel met tabs."""
    ui.label("Research & Kennisverzoeken").classes("text-h4 q-mb-md")

    with ui.tabs().classes("w-full") as tabs:
        new_tab = ui.tab("Nieuw Voorstel", icon="add_circle")
        agent_tab = ui.tab("Agent-voorstellen", icon="smart_toy")
        user_tab = ui.tab("Mijn verzoeken", icon="person")
        auto_tab = ui.tab("Auto-kennis log", icon="auto_fix_high")

    with ui.tab_panels(tabs, value=new_tab).classes("w-full"):
        with ui.tab_panel(new_tab):
            _extended_research_form(queue_manager, knowledge_provider)

        with ui.tab_panel(agent_tab):
            _agent_proposals_panel(queue_manager)

        with ui.tab_panel(user_tab):
            _user_requests_panel(queue_manager)

        with ui.tab_panel(auto_tab):
            _auto_knowledge_panel(queue_manager)


def _extended_research_form(
    queue_manager: ResearchQueueManager,
    knowledge_provider: KnowledgeProvider | None = None,
) -> None:
    """Uitgebreid research-indienformulier (v2)."""
    ui.label("Nieuw onderzoeksvoorstel indienen").classes("text-grey-7 q-mb-md")

    with ui.card().classes("p-4 w-full"):
        # Topic met autocomplete suggesties
        existing_topics: list[str] = []
        if knowledge_provider:
            existing_topics = [a.title for a in knowledge_provider.get_articles()]

        topic_input = ui.input(
            "Topic",
            placeholder="Wat wil je onderzocht hebben?",
            autocomplete=existing_topics[:20] if existing_topics else None,
        ).classes("w-full")

        # Achtergrond / motivatie
        background_input = ui.textarea(
            "Achtergrond & Motivatie",
            placeholder="Waarom is dit onderzoek nodig? Wat is de aanleiding?",
        ).classes("w-full")

        # Onderzoeksvragen (dynamisch)
        ui.label("Onderzoeksvragen").classes("text-sm font-bold mt-4")
        rqs: list[str] = []
        rq_container = ui.column().classes("w-full gap-2")

        def add_rq() -> None:
            rqs.append("")
            idx = len(rqs) - 1
            with rq_container:
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label(f"RQ{idx + 1}").classes("font-bold w-12")
                    ui.input(
                        placeholder=f"Onderzoeksvraag {idx + 1}",
                        on_change=lambda e, i=idx: rqs.__setitem__(i, e.value),
                    ).classes("flex-grow")

        ui.button("+ Onderzoeksvraag", icon="add", on_click=add_rq).props("flat dense")

        # Scope
        with ui.row().classes("gap-4 w-full mt-4"):
            scope_in = ui.textarea(
                "Scope IN",
                placeholder="Wat valt er wel onder?",
            ).classes("flex-grow")
            scope_out = ui.textarea(
                "Scope OUT",
                placeholder="Wat valt er niet onder?",
            ).classes("flex-grow")

        # Domein + verwachte grade + diepte
        with ui.row().classes("gap-4 w-full mt-2"):
            domain_input = ui.select(
                label="Domein",
                options=[
                    "ai_engineering",
                    "claude_specific",
                    "python_architecture",
                    "development_methodology",
                    "governance_compliance",
                    "security_appsec",
                    "testing_qa",
                    "documentation",
                ],
            ).classes("flex-grow")

            expected_grade = (
                ui.select(
                    label="Verwachte Grade",
                    options=["", "GOLD", "SILVER", "BRONZE"],
                    value="",
                )
                .classes("w-36")
                .tooltip("GOLD = peer-reviewed nodig, SILVER = docs, BRONZE = ervaring")
            )

            depth_input = (
                ui.select(
                    label="Diepte",
                    options=["QUICK", "STANDARD", "DEEP"],
                    value="STANDARD",
                )
                .classes("w-36")
                .tooltip("QUICK = snelle scan, STANDARD = normaal, DEEP = grondig")
            )

        # Gerelateerde kennis + document type
        with ui.row().classes("gap-4 w-full mt-2"):
            # Gerelateerde artikelen
            related_options: list[str] = []
            if knowledge_provider:
                related_options = [a.article_id for a in knowledge_provider.get_articles()]

            related_input = (
                ui.select(
                    label="Gerelateerde kennis",
                    options=related_options,
                    multiple=True,
                    value=[],
                ).classes("flex-grow")
                if related_options
                else None
            )

            category_input = ui.select(
                label="Document type",
                options=[
                    "",
                    "TUTORIAL",
                    "HOWTO",
                    "REFERENCE",
                    "EXPLANATION",
                    "METHODOLOGY",
                    "BEST_PRACTICE",
                    "SOTA_REVIEW",
                ],
                value="",
            ).classes("w-48")

        # Prioriteit + deadline
        with ui.row().classes("gap-4 w-full mt-2 items-end"):
            priority_slider = ui.slider(min=1, max=10, value=5).classes("flex-grow")
            ui.label().bind_text_from(
                priority_slider, "value", backward=lambda v: f"Prioriteit: {v}"
            )

            deadline_input = ui.input(
                "Deadline (optioneel)",
                placeholder="YYYY-MM-DD",
            ).classes("w-48")

        # Submit
        def submit() -> None:
            if not topic_input.value or not domain_input.value:
                ui.notify("Vul minimaal topic en domein in.", type="negative")
                return

            item = queue_manager.create_user_request(
                topic=topic_input.value,
                domain=domain_input.value,
                depth=depth_input.value or "STANDARD",
                document_category=category_input.value or "",
            )

            # Update v2 velden via direct file update
            import json

            item_path = queue_manager._dir / f"{item.item_id}.json"
            if item_path.exists():
                data = json.loads(item_path.read_text(encoding="utf-8"))
                data["background"] = background_input.value or ""
                data["research_questions"] = [rq for rq in rqs if rq.strip()]
                data["scope_in"] = scope_in.value or ""
                data["scope_out"] = scope_out.value or ""
                data["expected_grade"] = expected_grade.value or ""
                data["related_articles"] = (
                    list(related_input.value) if related_input and related_input.value else []
                )
                data["deadline"] = deadline_input.value or ""
                data["priority"] = int(priority_slider.value)
                item_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

            ui.notify("Onderzoeksvoorstel ingediend!", type="positive")
            topic_input.value = ""
            background_input.value = ""

        ui.button(
            "Voorstel Indienen",
            icon="send",
            color="primary",
            on_click=submit,
        ).classes("mt-4")


def _agent_proposals_panel(queue_manager: ResearchQueueManager) -> None:
    """Stroom 2: Agent-voorstellen uit KnowledgeGapDetected events."""
    ui.label("Research requests gegenereerd door agents via KnowledgeGapDetected events.").classes(
        "text-grey-7 q-mb-md"
    )

    items = queue_manager.list_items(stream=RequestStream.AGENT.value)

    if not items:
        ui.label(
            "Geen agent-voorstellen — nog geen KnowledgeGapDetected events ontvangen."
        ).classes("text-grey-6 italic")
        return

    def approve(item_id: str) -> None:
        queue_manager.update_status(item_id, RequestStatus.APPROVED)
        ui.notify(f"Goedgekeurd: {item_id}", type="positive")

    def reject(item_id: str) -> None:
        queue_manager.update_status(item_id, RequestStatus.REJECTED)
        ui.notify(f"Afgewezen: {item_id}", type="warning")

    for item in items:
        research_card(item, on_approve=approve, on_reject=reject)


def _user_requests_panel(queue_manager: ResearchQueueManager) -> None:
    """Stroom 3: Overzicht van ingediende verzoeken."""
    ui.label("Eerder ingediende onderzoeksverzoeken.").classes("text-grey-7 q-mb-md")

    items = queue_manager.list_items(stream=RequestStream.USER.value)
    if items:
        for item in items:
            research_card(item)
    else:
        ui.label("Nog geen verzoeken ingediend.").classes("text-grey-6 italic")


def _auto_knowledge_panel(queue_manager: ResearchQueueManager) -> None:
    """Stroom 1: Read-only overzicht van automatisch bijgewerkte kennis."""
    ui.label(
        "Automatisch bijgewerkte basiskennis door KWP DEV. "
        "Read-only: wat is bijgekomen, wat is afgewezen door KnowledgeCurator."
    ).classes("text-grey-7 q-mb-md")

    items = queue_manager.list_items(stream=RequestStream.AUTO.value)
    if items:
        for item in items:
            research_card(item)
    else:
        ui.label(
            "Geen auto-kennis activiteit gelogd. "
            "Dit vult zich automatisch wanneer de kennispipeline draait."
        ).classes("text-grey-6 italic")
