"""Tests voor ResearchProposalQueue — YAML-backed governance queue."""

from __future__ import annotations


import pytest

from devhub_core.contracts.pipeline_contracts import ProposalStatus, ResearchProposal
from devhub_core.research.proposal_queue import ResearchProposalQueue


@pytest.fixture
def queue_path(tmp_path):
    return tmp_path / "research_queue.yml"


@pytest.fixture
def queue(queue_path):
    return ResearchProposalQueue(queue_path)


def _make_proposal(**overrides) -> ResearchProposal:
    defaults = {
        "topic": "Event-driven architectuur",
        "domain": "ai_engineering",
        "requesting_agent": "coder",
        "stream": 2,
    }
    defaults.update(overrides)
    return ResearchProposal(**defaults)


class TestResearchProposalQueue:
    def test_submit_and_get(self, queue):
        proposal = _make_proposal()
        pid = queue.submit(proposal)

        found = queue.get(pid)
        assert found is not None
        assert found.topic == "Event-driven architectuur"
        assert found.status == ProposalStatus.PENDING

    def test_pending_filter(self, queue):
        queue.submit(_make_proposal(topic="A"))
        queue.submit(_make_proposal(topic="B"))

        pending = queue.pending()
        assert len(pending) == 2

    def test_approve(self, queue):
        proposal = _make_proposal()
        pid = queue.submit(proposal)

        result = queue.approve(pid)
        assert result is True

        found = queue.get(pid)
        assert found.status == ProposalStatus.APPROVED
        assert found.approved_at != ""

    def test_reject(self, queue):
        proposal = _make_proposal()
        pid = queue.submit(proposal)

        result = queue.reject(pid)
        assert result is True

        found = queue.get(pid)
        assert found.status == ProposalStatus.REJECTED

    def test_start_and_complete(self, queue):
        proposal = _make_proposal()
        pid = queue.submit(proposal)
        queue.approve(pid)

        queue.start(pid)
        found = queue.get(pid)
        assert found.status == ProposalStatus.IN_PROGRESS

        queue.complete(pid)
        found = queue.get(pid)
        assert found.status == ProposalStatus.COMPLETED
        assert found.completed_at != ""

    def test_approve_nonexistent(self, queue):
        result = queue.approve("nonexistent-id")
        assert result is False

    def test_all(self, queue):
        queue.submit(_make_proposal(topic="A"))
        queue.submit(_make_proposal(topic="B"))

        all_items = queue.all()
        assert len(all_items) == 2

    def test_persistence_roundtrip(self, queue_path):
        queue1 = ResearchProposalQueue(queue_path)
        proposal = _make_proposal()
        pid = queue1.submit(proposal)
        queue1.approve(pid)

        # Nieuwe instantie leest zelfde bestand
        queue2 = ResearchProposalQueue(queue_path)
        found = queue2.get(pid)
        assert found is not None
        assert found.status == ProposalStatus.APPROVED

    def test_approved_filter(self, queue):
        p1 = _make_proposal(topic="A")
        p2 = _make_proposal(topic="B")
        pid1 = queue.submit(p1)
        queue.submit(p2)
        queue.approve(pid1)

        approved = queue.approved()
        assert len(approved) == 1
        assert approved[0].topic == "A"

    def test_empty_queue(self, queue):
        assert queue.pending() == []
        assert queue.all() == []

    def test_yaml_file_created(self, queue_path):
        ResearchProposalQueue(queue_path)
        assert queue_path.exists()
