"""Event Bus wiring helpers — standaard koppelingen tussen events en handlers.

Biedt convenience-functies om veelvoorkomende event→handler koppelingen
te registreren op een EventBusInterface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import logging

from devhub_core.contracts.event_contracts import (
    EventBusInterface,
    KnowledgeGapDetected,
    KnowledgeIngested,
    ResearchCompleted,
    SprintClosed,
)
from devhub_core.contracts.research_contracts import (
    ResearchQueue,
    ResearchRequest,
)

logger = logging.getLogger(__name__)


def wire_knowledge_pipeline(
    bus: EventBusInterface,
    research_queue: ResearchQueue,
) -> str:
    """Koppel KnowledgeGapDetected events aan de ResearchQueue.

    Wanneer een kennislacune wordt gedetecteerd, wordt automatisch
    een ResearchRequest aangemaakt en in de queue geplaatst.

    Returns:
        subscription_id voor eventuele unsubscribe.
    """

    def _handle_gap(event: Any) -> None:
        if not isinstance(event, KnowledgeGapDetected):
            return
        request = ResearchRequest(
            request_id=f"RQ-auto-{event.event_id[:8]}",
            requesting_agent=event.requesting_agent or event.source_agent,
            question=event.gap_description,
            domain=event.domain,
            priority=3,
        )
        research_queue.submit(request)

    return bus.subscribe(KnowledgeGapDetected, _handle_gap)


def wire_sprint_lifecycle(
    bus: EventBusInterface,
    on_sprint_closed: Any | None = None,
) -> str:
    """Koppel SprintClosed events aan een callback.

    Args:
        bus: De event bus.
        on_sprint_closed: Optionele callback die wordt aangeroepen met het
            SprintClosed event. Gebruik dit om bijv. kennisextractie te triggeren.

    Returns:
        subscription_id voor eventuele unsubscribe.
    """

    def _handle_close(event: Any) -> None:
        if not isinstance(event, SprintClosed):
            return
        if on_sprint_closed is not None:
            on_sprint_closed(event)

    return bus.subscribe(SprintClosed, _handle_close)


def wire_ingestion_pipeline(
    bus: EventBusInterface,
    ingestor: Any,  # KnowledgeIngestor — Any om circulaire import te voorkomen
) -> str:
    """Koppel ResearchCompleted events aan KnowledgeIngestor.

    Wanneer research afgerond is, wordt het resulterende artikel
    automatisch geïngest in de vectorstore.

    Args:
        bus: De event bus.
        ingestor: KnowledgeIngestor instantie met ingest_file() methode.

    Returns:
        subscription_id voor eventuele unsubscribe.
    """

    def _handle_research_completed(event: Any) -> None:
        if not isinstance(event, ResearchCompleted):
            return
        article_path = Path(event.article_path)
        if article_path.exists():
            ingestor.ingest_file(article_path)

    return bus.subscribe(ResearchCompleted, _handle_research_completed)


def wire_governance_router(
    bus: EventBusInterface,
    router: Any,  # GovernanceRouter — Any om circulaire import te voorkomen
) -> str:
    """Koppel KnowledgeGapDetected events aan de GovernanceRouter.

    Routeert elke kennislacune naar de juiste stroom (1/2/3)
    op basis van domein-ring classificatie.

    Args:
        bus: De event bus.
        router: GovernanceRouter instantie met route_gap() methode.

    Returns:
        subscription_id voor eventuele unsubscribe.
    """

    def _handle_gap(event: Any) -> None:
        if not isinstance(event, KnowledgeGapDetected):
            return
        router.route_gap(event)

    return bus.subscribe(KnowledgeGapDetected, _handle_gap)


def produce_from_knowledge(
    document_service: Any,  # DocumentService — Any om circulaire import te voorkomen
    domain: str,
    category: str,
    node_id: str = "devhub",
) -> Any:  # DocumentProductionResult
    """Produceer een document vanuit de vectorstore kennis over een domein.

    Convenience helper die een DocumentProductionRequest opbouwt en
    DocumentService.produce() aanroept.

    Args:
        document_service: DocumentService instantie.
        domain: Kennisdomein (bijv. "ai_engineering").
        category: Documentcategorie (bijv. "sota_review").
        node_id: Target node ID.

    Returns:
        DocumentProductionResult van DocumentService.produce().
    """
    from devhub_core.contracts.pipeline_contracts import DocumentProductionRequest
    from devhub_documents.contracts import DocumentCategory

    request = DocumentProductionRequest(
        topic=f"{domain} — kennisoverzicht",
        category=DocumentCategory(category),
        target_node=node_id,
        knowledge_query=domain,
    )
    return document_service.produce(request)


def wire_knowledge_to_docs(
    bus: EventBusInterface,
    document_service: Any,  # DocumentService — Any om circulaire import te voorkomen
    auto_produce_categories: tuple[str, ...] = ("sota_review",),
) -> str:
    """Koppel KnowledgeIngested events aan automatische document-productie.

    Wanneer kennis geïngest wordt, produceert dit automatisch een document
    via DocumentService. Bedoeld voor stroom 1 (auto) kennis.

    Args:
        bus: De event bus.
        document_service: DocumentService instantie met produce() methode.
        auto_produce_categories: Documentcategorieën om te produceren.

    Returns:
        subscription_id voor eventuele unsubscribe.
    """

    def _handle_ingested(event: Any) -> None:
        if not isinstance(event, KnowledgeIngested):
            return
        for category in auto_produce_categories:
            try:
                produce_from_knowledge(
                    document_service,
                    domain=event.domain,
                    category=category,
                    node_id="devhub",
                )
            except Exception:
                logger.warning(
                    "Auto document production failed for domain=%s category=%s",
                    event.domain,
                    category,
                    exc_info=True,
                )

    return bus.subscribe(KnowledgeIngested, _handle_ingested)
