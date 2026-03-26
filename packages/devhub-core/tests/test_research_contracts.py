"""Tests voor research_contracts.py — Golf 1A kennispipeline."""

import pytest

from devhub_core.contracts.research_contracts import (
    ResearchDepth,
    ResearchRequest,
    ResearchResponse,
    ResearchStatus,
)


class TestResearchDepthEnum:
    def test_research_depth_enum_values(self) -> None:
        assert ResearchDepth.QUICK.value == "quick"
        assert ResearchDepth.STANDARD.value == "standard"
        assert ResearchDepth.DEEP.value == "deep"
        assert len(ResearchDepth) == 3


class TestResearchStatusEnum:
    def test_research_status_enum_values(self) -> None:
        assert ResearchStatus.PENDING.value == "pending"
        assert ResearchStatus.IN_PROGRESS.value == "in_progress"
        assert ResearchStatus.COMPLETED.value == "completed"
        assert ResearchStatus.FAILED.value == "failed"
        assert len(ResearchStatus) == 4


class TestResearchRequest:
    def test_research_request_creation(self) -> None:
        req = ResearchRequest(
            request_id="RES-001",
            requesting_agent="docs_agent",
            question="Wat is de beste aanpak voor vectorstore indexing?",
            domain="dev",
        )
        assert req.request_id == "RES-001"
        assert req.requesting_agent == "docs_agent"
        assert req.depth == ResearchDepth.STANDARD
        assert req.priority == 5
        assert req.context == ""
        assert req.deadline == ""
        assert req.related_knowledge == ()
        assert req.output_format == "knowledge_note"
        assert req.verification_required is True
        assert req.created_at == ""

    def test_research_request_validation_empty_request_id(self) -> None:
        with pytest.raises(ValueError, match="request_id is required"):
            ResearchRequest(
                request_id="",
                requesting_agent="agent",
                question="vraag",
                domain="dev",
            )

    def test_research_request_validation_empty_requesting_agent(self) -> None:
        with pytest.raises(ValueError, match="requesting_agent is required"):
            ResearchRequest(
                request_id="RES-001",
                requesting_agent="",
                question="vraag",
                domain="dev",
            )

    def test_research_request_validation_empty_question(self) -> None:
        with pytest.raises(ValueError, match="question is required"):
            ResearchRequest(
                request_id="RES-001",
                requesting_agent="agent",
                question="",
                domain="dev",
            )

    def test_research_request_validation_empty_domain(self) -> None:
        with pytest.raises(ValueError, match="domain is required"):
            ResearchRequest(
                request_id="RES-001",
                requesting_agent="agent",
                question="vraag",
                domain="",
            )

    def test_research_request_priority_validation_too_low(self) -> None:
        with pytest.raises(ValueError, match="priority must be between 1 and 10"):
            ResearchRequest(
                request_id="RES-001",
                requesting_agent="agent",
                question="vraag",
                domain="dev",
                priority=0,
            )

    def test_research_request_priority_validation_too_high(self) -> None:
        with pytest.raises(ValueError, match="priority must be between 1 and 10"):
            ResearchRequest(
                request_id="RES-001",
                requesting_agent="agent",
                question="vraag",
                domain="dev",
                priority=11,
            )

    def test_research_request_to_dict(self) -> None:
        req = ResearchRequest(
            request_id="RES-002",
            requesting_agent="orchestrator",
            question="Hoe werkt BORIS caching?",
            domain="autisme",
            depth=ResearchDepth.DEEP,
            priority=2,
            related_knowledge=("KN-001", "KN-002"),
        )
        d = req.to_dict()
        assert d["request_id"] == "RES-002"
        assert d["depth"] == "deep"
        assert d["priority"] == 2
        assert d["related_knowledge"] == ["KN-001", "KN-002"]
        assert isinstance(d["related_knowledge"], list)

    def test_research_request_frozen(self) -> None:
        req = ResearchRequest(
            request_id="RES-003",
            requesting_agent="agent",
            question="vraag",
            domain="dev",
        )
        with pytest.raises(AttributeError):
            req.request_id = "CHANGED"  # type: ignore[misc]


class TestResearchResponse:
    def test_research_response_creation(self) -> None:
        resp = ResearchResponse(request_id="RES-001")
        assert resp.request_id == "RES-001"
        assert resp.status == ResearchStatus.PENDING
        assert resp.summary == ""
        assert resp.knowledge_refs == ()
        assert resp.grade == "SPECULATIVE"
        assert resp.verification_pct == 0.0
        assert resp.sources == ()
        assert resp.completed_at == ""

    def test_research_response_validation_empty_request_id(self) -> None:
        with pytest.raises(ValueError, match="request_id is required"):
            ResearchResponse(request_id="")

    def test_research_response_verification_pct_validation_too_low(self) -> None:
        with pytest.raises(ValueError, match="verification_pct must be between"):
            ResearchResponse(request_id="RES-001", verification_pct=-1.0)

    def test_research_response_verification_pct_validation_too_high(self) -> None:
        with pytest.raises(ValueError, match="verification_pct must be between"):
            ResearchResponse(request_id="RES-001", verification_pct=101.0)

    def test_research_response_is_complete(self) -> None:
        pending = ResearchResponse(request_id="RES-001")
        assert pending.is_complete is False

        completed = ResearchResponse(
            request_id="RES-001",
            status=ResearchStatus.COMPLETED,
            summary="Antwoord gevonden.",
            grade="GOLD",
            verification_pct=95.0,
        )
        assert completed.is_complete is True

        failed = ResearchResponse(
            request_id="RES-001",
            status=ResearchStatus.FAILED,
        )
        assert failed.is_complete is False

    def test_research_response_to_dict(self) -> None:
        resp = ResearchResponse(
            request_id="RES-005",
            status=ResearchStatus.COMPLETED,
            summary="Resultaat",
            knowledge_refs=("knowledge/note1.md",),
            grade="SILVER",
            verification_pct=80.0,
            sources=("https://example.com",),
            completed_at="2026-03-26T12:00:00Z",
        )
        d = resp.to_dict()
        assert d["request_id"] == "RES-005"
        assert d["status"] == "completed"
        assert d["grade"] == "SILVER"
        assert d["knowledge_refs"] == ["knowledge/note1.md"]
        assert isinstance(d["sources"], list)
        assert d["verification_pct"] == 80.0
