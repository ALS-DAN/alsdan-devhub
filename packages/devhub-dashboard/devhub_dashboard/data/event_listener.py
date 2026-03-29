"""Event Listener — subscribe op EventBusInterface, push naar dashboard.

Luistert naar KnowledgeGapDetected events en voegt ze toe als
agent-voorstellen in de research queue.
"""

from __future__ import annotations

from devhub_core.contracts.event_contracts import (
    Event,
    EventBusInterface,
    KnowledgeGapDetected,
)

from devhub_dashboard.data.research_queue import ResearchQueueManager


class DashboardEventListener:
    """Koppelt EventBus events aan dashboard data."""

    def __init__(
        self,
        event_bus: EventBusInterface,
        queue_manager: ResearchQueueManager,
    ) -> None:
        self._bus = event_bus
        self._queue = queue_manager
        self._subscription_ids: list[str] = []

    def start(self) -> None:
        """Registreer alle event handlers."""
        sub_id = self._bus.subscribe(
            KnowledgeGapDetected,
            self._on_knowledge_gap,
        )
        self._subscription_ids.append(sub_id)

    def stop(self) -> None:
        """Verwijder alle event handlers."""
        for sub_id in self._subscription_ids:
            self._bus.unsubscribe(sub_id)
        self._subscription_ids.clear()

    def _on_knowledge_gap(self, event: Event) -> None:
        """Verwerk een KnowledgeGapDetected event → agent-voorstel."""
        if not isinstance(event, KnowledgeGapDetected):
            return

        self._queue.create_agent_proposal(
            topic=event.gap_description,
            domain=event.domain,
            source_agent=event.requesting_agent or event.source_agent,
            description=f"Gedetecteerd door {event.source_agent}",
        )
