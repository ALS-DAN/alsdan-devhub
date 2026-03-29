"""Tests voor GovernanceRouter — drie-stromen routing."""

from __future__ import annotations


import pytest

from devhub_core.agents.governance_router import GovernanceRouter, StreamDecision
from devhub_core.contracts.event_contracts import KnowledgeGapDetected
from devhub_core.contracts.pipeline_contracts import ProposalStatus
from devhub_core.contracts.research_contracts import (
    ResearchQueue,
    ResearchRequest,
    ResearchResponse,
)
from devhub_core.research.knowledge_config import DomainConfig, KnowledgeConfig, RingConfig
from devhub_core.research.proposal_queue import ResearchProposalQueue


# ---------------------------------------------------------------------------
# Fake ResearchQueue (in-memory)
# ---------------------------------------------------------------------------


class FakeResearchQueue(ResearchQueue):
    """In-memory ResearchQueue voor tests."""

    def __init__(self):
        self._items: list[ResearchRequest] = []

    def submit(self, request: ResearchRequest) -> str:
        self._items.append(request)
        return request.request_id

    def next(self) -> ResearchRequest | None:
        return self._items[0] if self._items else None

    def complete(self, request_id: str, response: ResearchResponse) -> None:
        pass

    def pending(self) -> list[ResearchRequest]:
        return list(self._items)

    def by_agent(self, agent_name: str) -> list[ResearchRequest]:
        return [r for r in self._items if r.requesting_agent == agent_name]

    def get_response(self, request_id: str) -> ResearchResponse | None:
        return None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def knowledge_config():
    """Minimale KnowledgeConfig met 2 Ring 1 domeinen en 1 Ring 2 domein."""
    return KnowledgeConfig(
        rings=(
            RingConfig(name="core", auto_bootstrap=True),
            RingConfig(name="agent"),
            RingConfig(name="project"),
        ),
        domains=(
            DomainConfig(name="ai_engineering", ring="core", bootstrap_priority=1),
            DomainConfig(name="python_architecture", ring="core", bootstrap_priority=2),
            DomainConfig(name="sprint_planning", ring="agent"),
            DomainConfig(name="healthcare_ict", ring="project"),
        ),
    )


@pytest.fixture
def research_queue():
    return FakeResearchQueue()


@pytest.fixture
def proposal_queue(tmp_path):
    return ResearchProposalQueue(tmp_path / "research_queue.yml")


@pytest.fixture
def router(knowledge_config, research_queue, proposal_queue):
    return GovernanceRouter(knowledge_config, research_queue, proposal_queue)


def _make_gap_event(domain: str, description: str = "Test gap") -> KnowledgeGapDetected:
    return KnowledgeGapDetected(
        source_agent="test_agent",
        domain=domain,
        gap_description=description,
        requesting_agent="coder",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGovernanceRouter:
    def test_stream_1_core_domain(self, router, research_queue):
        """Ring 1 domein → Stroom 1 (auto research)."""
        event = _make_gap_event("ai_engineering")
        decision = router.route_gap(event)

        assert decision.stream == 1
        assert decision.action == "auto_research"
        assert len(research_queue.pending()) == 1

    def test_stream_1_another_core_domain(self, router, research_queue):
        """Tweede Ring 1 domein → ook Stroom 1."""
        event = _make_gap_event("python_architecture")
        decision = router.route_gap(event)

        assert decision.stream == 1

    def test_stream_2_agent_domain(self, router, proposal_queue):
        """Ring 2 domein → Stroom 2 (goedkeuring)."""
        event = _make_gap_event("sprint_planning")
        decision = router.route_gap(event)

        assert decision.stream == 2
        assert decision.action == "queued_for_approval"
        assert len(proposal_queue.pending()) == 1

    def test_stream_2_project_domain(self, router, proposal_queue):
        """Ring 3 domein → ook Stroom 2."""
        event = _make_gap_event("healthcare_ict")
        decision = router.route_gap(event)

        assert decision.stream == 2

    def test_stream_2_unknown_domain(self, router, proposal_queue):
        """Onbekend domein → Stroom 2 (veilige default)."""
        event = _make_gap_event("unknown_domain")
        decision = router.route_gap(event)

        assert decision.stream == 2

    def test_stream_3_direct_request(self, router, research_queue):
        """Stroom 3: directe request van Niels."""
        decision = router.handle_direct_request(
            topic="Event-driven multi-agent architectuur",
            domain="ai_engineering",
        )

        assert decision.stream == 3
        assert decision.action == "direct_research"
        assert len(research_queue.pending()) == 1
        # Priority 1 voor directe requests
        assert research_queue.pending()[0].priority == 1

    def test_stream_3_custom_agent(self, router, research_queue):
        router.handle_direct_request(
            topic="Test topic",
            domain="ai_engineering",
            requesting_agent="custom_agent",
        )

        assert research_queue.pending()[0].requesting_agent == "custom_agent"

    def test_stream_decision_dataclass(self):
        d = StreamDecision(stream=1, action="auto_research", request_id="RQ-001")
        assert d.stream == 1
        assert d.request_id == "RQ-001"

    def test_proposal_has_correct_metadata(self, router, proposal_queue):
        """Stroom 2 proposals bevatten de juiste metadata."""
        event = _make_gap_event("sprint_planning", "Hoe werkt capacity planning?")
        router.route_gap(event)

        proposals = proposal_queue.pending()
        assert len(proposals) == 1
        p = proposals[0]
        assert p.topic == "Hoe werkt capacity planning?"
        assert p.domain == "sprint_planning"
        assert p.stream == 2
        assert p.status == ProposalStatus.PENDING

    def test_research_request_has_correct_metadata(self, router, research_queue):
        """Stroom 1 requests bevatten de juiste metadata."""
        event = _make_gap_event("ai_engineering", "Wat zijn de beste RAG patronen?")
        router.route_gap(event)

        requests = research_queue.pending()
        assert len(requests) == 1
        r = requests[0]
        assert r.question == "Wat zijn de beste RAG patronen?"
        assert r.domain == "ai_engineering"
        assert r.priority == 3

    def test_multiple_gaps_routed_correctly(self, router, research_queue, proposal_queue):
        """Mix van domeinen wordt correct gerouteerd."""
        router.route_gap(_make_gap_event("ai_engineering"))
        router.route_gap(_make_gap_event("sprint_planning"))
        router.route_gap(_make_gap_event("python_architecture"))

        assert len(research_queue.pending()) == 2  # 2x Ring 1
        assert len(proposal_queue.pending()) == 1  # 1x Ring 2
