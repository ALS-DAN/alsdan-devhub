"""
GovernanceRouter — Drie-stromen routing voor kennislacunes.

Routeert KnowledgeGapDetected events naar de juiste stroom:
- Stroom 1 (auto): Ring 1 domeinen → direct ResearchRequest
- Stroom 2 (goedkeuring): buiten Ring 1 → ResearchProposal in queue
- Stroom 3 (Niels): directe requests → priority 1, meteen IN_PROGRESS
"""

from __future__ import annotations

from dataclasses import dataclass

from devhub_core.contracts.event_contracts import KnowledgeGapDetected
from devhub_core.contracts.pipeline_contracts import ResearchProposal
from devhub_core.contracts.research_contracts import ResearchQueue, ResearchRequest
from devhub_core.research.knowledge_config import KnowledgeConfig
from devhub_core.research.proposal_queue import ResearchProposalQueue


@dataclass(frozen=True)
class StreamDecision:
    """Resultaat van de governance routing."""

    stream: int  # 1, 2, of 3
    action: str  # "auto_research", "queued_for_approval", "direct_research"
    request_id: str = ""


class GovernanceRouter:
    """Routeert kennislacunes naar de juiste governance-stroom.

    Args:
        knowledge_config: Configuratie met domein-ring mappings.
        research_queue: Queue voor automatische research requests (stroom 1+3).
        proposal_queue: Queue voor voorstellen die goedkeuring vereisen (stroom 2).
    """

    def __init__(
        self,
        knowledge_config: KnowledgeConfig,
        research_queue: ResearchQueue,
        proposal_queue: ResearchProposalQueue,
    ) -> None:
        self._config = knowledge_config
        self._research_queue = research_queue
        self._proposal_queue = proposal_queue
        # Cache Ring 1 domeinnamen voor snelle lookup
        self._core_domains = {d.name for d in self._config.domains_by_ring("core")}

    def route_gap(self, event: KnowledgeGapDetected) -> StreamDecision:
        """Routeer een KnowledgeGapDetected event naar de juiste stroom.

        Ring 1 domein → Stroom 1 (auto research)
        Overig → Stroom 2 (wacht op goedkeuring)
        """
        if event.domain in self._core_domains:
            return self._route_stream_1(event)
        return self._route_stream_2(event)

    def handle_direct_request(
        self,
        topic: str,
        domain: str,
        requesting_agent: str = "niels",
    ) -> StreamDecision:
        """Stroom 3: directe research request van Niels.

        Geen goedkeuring nodig — gaat direct naar IN_PROGRESS.
        """
        request = ResearchRequest(
            request_id=f"RQ-direct-{topic[:20].replace(' ', '_')}",
            requesting_agent=requesting_agent,
            question=topic,
            domain=domain,
            priority=1,  # Hoogste prioriteit voor directe requests
        )
        req_id = self._research_queue.submit(request)
        return StreamDecision(
            stream=3,
            action="direct_research",
            request_id=req_id,
        )

    def _route_stream_1(self, event: KnowledgeGapDetected) -> StreamDecision:
        """Stroom 1: auto-research voor Ring 1 domeinen."""
        request = ResearchRequest(
            request_id=f"RQ-auto-{event.event_id[:8]}",
            requesting_agent=event.requesting_agent or event.source_agent,
            question=event.gap_description,
            domain=event.domain,
            priority=3,
        )
        req_id = self._research_queue.submit(request)
        return StreamDecision(
            stream=1,
            action="auto_research",
            request_id=req_id,
        )

    def _route_stream_2(self, event: KnowledgeGapDetected) -> StreamDecision:
        """Stroom 2: voorstel voor goedkeuring buiten Ring 1."""
        proposal = ResearchProposal(
            topic=event.gap_description,
            domain=event.domain,
            requesting_agent=event.requesting_agent or event.source_agent,
            rationale=f"Kennislacune gedetecteerd door {event.source_agent}",
            stream=2,
        )
        pid = self._proposal_queue.submit(proposal)
        return StreamDecision(
            stream=2,
            action="queued_for_approval",
            request_id=pid,
        )
