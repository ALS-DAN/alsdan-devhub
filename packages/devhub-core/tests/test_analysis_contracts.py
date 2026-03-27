"""Tests voor Analysis Contracts — Golf 3 kerntypen."""

import pytest

from devhub_core.contracts.analysis_contracts import (
    AnalysisRequest,
    AnalysisResult,
    AnalysisStepResult,
    AnalysisStepStatus,
    AnalysisType,
    KnowledgeGap,
)
from devhub_core.contracts.research_contracts import ResearchDepth


# ---------------------------------------------------------------------------
# AnalysisType enum
# ---------------------------------------------------------------------------


def test_analysis_type_enum_values():
    assert AnalysisType.SOTA.value == "sota"
    assert AnalysisType.COMPARATIVE.value == "comparative"
    assert AnalysisType.APPLICATION.value == "application"
    assert AnalysisType.FREE.value == "free"


# ---------------------------------------------------------------------------
# AnalysisRequest
# ---------------------------------------------------------------------------


def _make_request(**overrides) -> AnalysisRequest:
    defaults = dict(
        request_id="REQ-001",
        title="Test Analyse",
        question="Wat is de stand van zaken?",
        analysis_type=AnalysisType.FREE,
        domains=("ai_engineering",),
    )
    defaults.update(overrides)
    return AnalysisRequest(**defaults)


def test_analysis_request_valid():
    req = _make_request()
    assert req.request_id == "REQ-001"
    assert req.analysis_type == AnalysisType.FREE
    assert req.depth == ResearchDepth.STANDARD
    assert req.skip_research is False
    assert req.output_format == "markdown"


def test_analysis_request_missing_request_id():
    with pytest.raises(ValueError, match="request_id"):
        _make_request(request_id="")


def test_analysis_request_missing_question():
    with pytest.raises(ValueError, match="question"):
        _make_request(question="")


def test_analysis_request_missing_domains():
    with pytest.raises(ValueError, match="domains"):
        _make_request(domains=())


def test_analysis_request_invalid_output_format():
    with pytest.raises(ValueError, match="output_format"):
        _make_request(output_format="pdf")


# ---------------------------------------------------------------------------
# KnowledgeGap
# ---------------------------------------------------------------------------


def test_knowledge_gap_valid():
    gap = KnowledgeGap(
        gap_id="GAP-001",
        description="Onvoldoende kennis over embeddings",
        domain="ai_engineering",
        suggested_question="Hoe werken embeddings in Weaviate?",
    )
    assert gap.priority == 5
    assert gap.gap_id == "GAP-001"


def test_knowledge_gap_priority_out_of_range():
    with pytest.raises(ValueError, match="priority"):
        KnowledgeGap(
            gap_id="GAP-001",
            description="Test",
            domain="ai_engineering",
            suggested_question="Test?",
            priority=11,
        )


# ---------------------------------------------------------------------------
# AnalysisStepResult
# ---------------------------------------------------------------------------


def test_analysis_step_result_skipped():
    result = AnalysisStepResult(
        step_name="research",
        status=AnalysisStepStatus.SKIPPED,
        message="skip_research=True",
    )
    assert result.status == AnalysisStepStatus.SKIPPED
    assert result.items_processed == 0


# ---------------------------------------------------------------------------
# AnalysisResult
# ---------------------------------------------------------------------------


def test_analysis_result_document_generated_property():
    result = AnalysisResult(
        request_id="REQ-001",
        analysis_type=AnalysisType.FREE,
        title="Test",
        synthesis="tekst",
        document_path="docs/analyses/test.md",
    )
    assert result.document_generated is True


def test_analysis_result_no_document():
    result = AnalysisResult(
        request_id="REQ-001",
        analysis_type=AnalysisType.FREE,
        title="Test",
        synthesis="tekst",
    )
    assert result.document_generated is False


def test_analysis_result_stored_remotely_property():
    result = AnalysisResult(
        request_id="REQ-001",
        analysis_type=AnalysisType.FREE,
        title="Test",
        synthesis="tekst",
        storage_paths=("docs/analyses/test.md", "remote:docs/analyses/test.md"),
    )
    assert result.stored_remotely is True


def test_analysis_result_only_local_not_remotely():
    result = AnalysisResult(
        request_id="REQ-001",
        analysis_type=AnalysisType.FREE,
        title="Test",
        synthesis="tekst",
        storage_paths=("docs/analyses/test.md",),
    )
    assert result.stored_remotely is False
