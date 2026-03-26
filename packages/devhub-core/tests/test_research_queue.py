"""Tests voor InMemoryResearchQueue — Golf 1A kennispipeline."""

import pytest

from devhub_core.contracts.research_contracts import (
    ResearchRequest,
    ResearchResponse,
    ResearchStatus,
)
from devhub_core.research.in_memory_queue import InMemoryResearchQueue


def _make_request(
    request_id: str = "RES-001",
    agent: str = "docs_agent",
    priority: int = 5,
    **kwargs,
) -> ResearchRequest:
    return ResearchRequest(
        request_id=request_id,
        requesting_agent=agent,
        question=kwargs.get("question", "Test vraag"),
        domain=kwargs.get("domain", "dev"),
        priority=priority,
    )


class TestInMemoryResearchQueue:
    def test_submit_and_pending(self) -> None:
        queue = InMemoryResearchQueue()
        req = _make_request()
        rid = queue.submit(req)
        assert rid == "RES-001"
        assert len(queue.pending()) == 1
        assert queue.pending()[0].request_id == "RES-001"

    def test_next_returns_highest_priority(self) -> None:
        queue = InMemoryResearchQueue()
        queue.submit(_make_request("RES-LOW", priority=8))
        queue.submit(_make_request("RES-HIGH", priority=1))
        queue.submit(_make_request("RES-MID", priority=5))

        result = queue.next()
        assert result is not None
        assert result.request_id == "RES-HIGH"

    def test_next_returns_none_when_empty(self) -> None:
        queue = InMemoryResearchQueue()
        assert queue.next() is None

    def test_complete_stores_response(self) -> None:
        queue = InMemoryResearchQueue()
        queue.submit(_make_request("RES-001"))

        response = ResearchResponse(
            request_id="RES-001",
            status=ResearchStatus.COMPLETED,
            summary="Antwoord",
            grade="GOLD",
        )
        queue.complete("RES-001", response)

        stored = queue.get_response("RES-001")
        assert stored is not None
        assert stored.status == ResearchStatus.COMPLETED
        assert stored.grade == "GOLD"

    def test_complete_unknown_request_raises(self) -> None:
        queue = InMemoryResearchQueue()
        response = ResearchResponse(
            request_id="NONEXISTENT",
            status=ResearchStatus.COMPLETED,
        )
        with pytest.raises(ValueError, match="Unknown request_id"):
            queue.complete("NONEXISTENT", response)

    def test_by_agent_filters_correctly(self) -> None:
        queue = InMemoryResearchQueue()
        queue.submit(_make_request("RES-001", agent="docs_agent"))
        queue.submit(_make_request("RES-002", agent="orchestrator"))
        queue.submit(_make_request("RES-003", agent="docs_agent"))

        docs_requests = queue.by_agent("docs_agent")
        assert len(docs_requests) == 2
        assert all(r.requesting_agent == "docs_agent" for r in docs_requests)

        orch_requests = queue.by_agent("orchestrator")
        assert len(orch_requests) == 1

    def test_get_response_returns_none_for_pending(self) -> None:
        queue = InMemoryResearchQueue()
        queue.submit(_make_request("RES-001"))
        assert queue.get_response("RES-001") is None

    def test_get_response_returns_response_after_complete(self) -> None:
        queue = InMemoryResearchQueue()
        queue.submit(_make_request("RES-001"))

        response = ResearchResponse(
            request_id="RES-001",
            status=ResearchStatus.COMPLETED,
            summary="Klaar",
        )
        queue.complete("RES-001", response)
        assert queue.get_response("RES-001") is not None
        assert queue.get_response("RES-001").summary == "Klaar"

    def test_multiple_agents_multiple_requests(self) -> None:
        queue = InMemoryResearchQueue()
        agents = ["agent_a", "agent_b", "agent_c"]
        for i, agent in enumerate(agents):
            queue.submit(_make_request(f"RES-{i:03d}", agent=agent))
            queue.submit(_make_request(f"RES-{i+10:03d}", agent=agent))

        assert len(queue.pending()) == 6
        for agent in agents:
            assert len(queue.by_agent(agent)) == 2

    def test_next_skips_completed_requests(self) -> None:
        queue = InMemoryResearchQueue()
        queue.submit(_make_request("RES-HIGH", priority=1))
        queue.submit(_make_request("RES-MID", priority=5))

        # Complete the highest priority one
        response = ResearchResponse(
            request_id="RES-HIGH",
            status=ResearchStatus.COMPLETED,
        )
        queue.complete("RES-HIGH", response)

        # next() should skip the completed one
        result = queue.next()
        assert result is not None
        assert result.request_id == "RES-MID"

        # Pending should also exclude completed
        assert len(queue.pending()) == 1
