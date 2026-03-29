"""Event Bus wiring helpers — standaard koppelingen tussen events en handlers.

Biedt convenience-functies om veelvoorkomende event→handler koppelingen
te registreren op een EventBusInterface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devhub_core.contracts.event_contracts import (
    EventBusInterface,
    KnowledgeGapDetected,
    ResearchCompleted,
    SprintClosed,
)
from devhub_core.contracts.research_contracts import (
    ResearchQueue,
    ResearchRequest,
)


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
