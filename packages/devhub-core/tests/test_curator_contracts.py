"""Tests voor curator_contracts.py — 19 tests."""

from __future__ import annotations

import pytest

from devhub_core.contracts.curator_contracts import (
    CurationFinding,
    CurationReport,
    CurationVerdict,
    KnowledgeArticle,
    KnowledgeDomain,
    KnowledgeHealthReport,
    Observation,
    ObservationType,
)


# --- Enum tests ---


class TestKnowledgeDomainEnum:
    def test_knowledge_domain_enum_values(self) -> None:
        assert KnowledgeDomain.AI_ENGINEERING.value == "ai_engineering"
        assert KnowledgeDomain.CLAUDE_SPECIFIC.value == "claude_specific"
        assert KnowledgeDomain.PYTHON_ARCHITECTURE.value == "python_architecture"
        assert KnowledgeDomain.DEVELOPMENT_METHODOLOGY.value == "development_methodology"
        assert KnowledgeDomain.GOVERNANCE_COMPLIANCE.value == "governance_compliance"
        assert len(KnowledgeDomain) == 16

    def test_knowledge_domain_ring_core(self) -> None:
        core = KnowledgeDomain.core_domains()
        assert len(core) == 5
        assert KnowledgeDomain.AI_ENGINEERING in core
        assert KnowledgeDomain.CLAUDE_SPECIFIC in core
        assert KnowledgeDomain.GOVERNANCE_COMPLIANCE in core
        for d in core:
            assert d.ring == "core"

    def test_knowledge_domain_ring_agent(self) -> None:
        agent = KnowledgeDomain.agent_domains()
        assert len(agent) == 8
        assert KnowledgeDomain.SPRINT_PLANNING in agent
        assert KnowledgeDomain.CODE_REVIEW in agent
        assert KnowledgeDomain.SECURITY_APPSEC in agent
        assert KnowledgeDomain.TESTING_QA in agent
        assert KnowledgeDomain.KNOWLEDGE_METHODOLOGY in agent
        assert KnowledgeDomain.COACHING_LEARNING in agent
        assert KnowledgeDomain.DOCUMENTATION in agent
        assert KnowledgeDomain.PRODUCT_OWNERSHIP in agent
        for d in agent:
            assert d.ring == "agent"

    def test_knowledge_domain_ring_project(self) -> None:
        project = KnowledgeDomain.project_domains()
        assert len(project) == 3
        assert KnowledgeDomain.HEALTHCARE_ICT in project
        assert KnowledgeDomain.PRIVACY_AVG in project
        assert KnowledgeDomain.MULTI_TENANCY in project
        for d in project:
            assert d.ring == "project"

    def test_knowledge_domain_by_ring_covers_all(self) -> None:
        all_domains = (
            KnowledgeDomain.by_ring("core")
            + KnowledgeDomain.by_ring("agent")
            + KnowledgeDomain.by_ring("project")
        )
        assert len(all_domains) == len(KnowledgeDomain)
        assert set(all_domains) == set(KnowledgeDomain)

    def test_knowledge_domain_ring_property_all_members(self) -> None:
        for d in KnowledgeDomain:
            assert d.ring in ("core", "agent", "project")


class TestObservationTypeEnum:
    def test_observation_type_enum_values(self) -> None:
        assert ObservationType.GRADE_DEGRADATION.value == "grade_degradation"
        assert ObservationType.FRESHNESS_ALERT.value == "freshness_alert"
        assert ObservationType.SCOPE_VIOLATION.value == "scope_violation"
        assert ObservationType.INGEST_REJECTION.value == "ingest_rejection"
        assert ObservationType.HEALTH_DEGRADED.value == "health_degraded"
        assert ObservationType.DUPLICATE_DETECTED.value == "duplicate_detected"
        assert ObservationType.ANALYSIS_COMPLETED.value == "analysis_completed"
        assert ObservationType.ANALYSIS_FAILED.value == "analysis_failed"
        assert ObservationType.KNOWLEDGE_GAP_DETECTED.value == "knowledge_gap_detected"
        assert len(ObservationType) == 9


class TestCurationVerdictEnum:
    def test_curation_verdict_enum_values(self) -> None:
        assert CurationVerdict.APPROVED.value == "approved"
        assert CurationVerdict.NEEDS_REVISION.value == "needs_revision"
        assert CurationVerdict.REJECTED.value == "rejected"
        assert len(CurationVerdict) == 3


# --- KnowledgeArticle tests ---


def _make_article(**overrides) -> KnowledgeArticle:
    """Helper voor een valide KnowledgeArticle."""
    defaults = {
        "article_id": "ART-001",
        "title": "Test Article",
        "content": "Dit is een test artikel met voldoende content voor validatie checks.",
        "domain": KnowledgeDomain.AI_ENGINEERING,
        "grade": "SILVER",
        "sources": ("https://example.com",),
        "verification_pct": 60.0,
        "date": "2026-03-01",
    }
    defaults.update(overrides)
    return KnowledgeArticle(**defaults)


class TestKnowledgeArticle:
    def test_knowledge_article_creation(self) -> None:
        article = _make_article()
        assert article.article_id == "ART-001"
        assert article.title == "Test Article"
        assert article.domain == KnowledgeDomain.AI_ENGINEERING
        assert article.grade == "SILVER"
        assert article.verification_pct == 60.0
        assert article.author == "researcher-agent"
        assert article.embedding is None

    def test_knowledge_article_validation_empty_fields(self) -> None:
        with pytest.raises(ValueError, match="article_id is required"):
            _make_article(article_id="")
        with pytest.raises(ValueError, match="title is required"):
            _make_article(title="")
        with pytest.raises(ValueError, match="content is required"):
            _make_article(content="")

    def test_knowledge_article_verification_pct_range(self) -> None:
        with pytest.raises(ValueError, match="verification_pct must be between"):
            _make_article(verification_pct=-1.0)
        with pytest.raises(ValueError, match="verification_pct must be between"):
            _make_article(verification_pct=101.0)
        # Boundary values should work
        assert _make_article(verification_pct=0.0).verification_pct == 0.0
        assert _make_article(verification_pct=100.0).verification_pct == 100.0

    def test_knowledge_article_frozen(self) -> None:
        article = _make_article()
        with pytest.raises(AttributeError):
            article.title = "Modified"  # type: ignore[misc]

    def test_knowledge_article_defaults_new_fields(self) -> None:
        article = _make_article()
        assert article.rq_tags == ()
        assert article.entity_refs == ()
        assert article.domain_ring == "core"

    def test_knowledge_article_with_rq_tags(self) -> None:
        article = _make_article(
            rq_tags=("RQ1", "RQ4"),
            entity_refs=("ENT-001", "ENT-002"),
            domain_ring="agent",
        )
        assert article.rq_tags == ("RQ1", "RQ4")
        assert article.entity_refs == ("ENT-001", "ENT-002")
        assert article.domain_ring == "agent"

    def test_knowledge_article_to_dict(self) -> None:
        article = _make_article(rq_tags=("RQ1",), entity_refs=("ENT-001",), domain_ring="core")
        d = article.to_dict()
        assert d["article_id"] == "ART-001"
        assert d["domain"] == "ai_engineering"
        assert d["sources"] == ["https://example.com"]
        assert isinstance(d["sources"], list)
        assert d["rq_tags"] == ["RQ1"]
        assert d["entity_refs"] == ["ENT-001"]
        assert d["domain_ring"] == "core"
        # Embedding should not be in dict
        assert "embedding" not in d

    def test_knowledge_article_to_dict_empty_new_fields(self) -> None:
        article = _make_article()
        d = article.to_dict()
        assert d["rq_tags"] == []
        assert d["entity_refs"] == []
        assert d["domain_ring"] == "core"

    def test_knowledge_article_to_document_chunk(self) -> None:
        article = _make_article(
            embedding=(0.1, 0.2, 0.3),
            rq_tags=("RQ1", "RQ4"),
            domain_ring="core",
        )
        chunk = article.to_document_chunk()
        assert chunk.chunk_id == "ART-001"
        assert chunk.content == article.content
        assert chunk.source_id == "ART-001"
        assert chunk.embedding == (0.1, 0.2, 0.3)
        meta = chunk.metadata_dict
        assert meta["domain"] == "ai_engineering"
        assert meta["grade"] == "SILVER"
        assert meta["rq_tags"] == "RQ1|RQ4"
        assert meta["domain_ring"] == "core"

    def test_knowledge_article_to_document_chunk_empty_rq_tags(self) -> None:
        article = _make_article(embedding=(0.1,))
        chunk = article.to_document_chunk()
        meta = chunk.metadata_dict
        assert meta["rq_tags"] == ""
        assert meta["entity_refs"] == ""


# --- CurationFinding tests ---


class TestCurationFinding:
    def test_curation_finding_creation(self) -> None:
        finding = CurationFinding(
            severity="WARNING",
            category="sources",
            description="Geen bronvermelding",
            article_id="ART-001",
        )
        assert finding.severity == "WARNING"
        assert finding.category == "sources"
        assert finding.description == "Geen bronvermelding"
        assert finding.article_id == "ART-001"

    def test_curation_finding_description_required(self) -> None:
        with pytest.raises(ValueError, match="description is required"):
            CurationFinding(severity="INFO", category="content", description="")


# --- CurationReport tests ---


class TestCurationReport:
    def test_curation_report_auto_rejected_critical(self) -> None:
        critical = CurationFinding(
            severity="CRITICAL", category="grade", description="GOLD zonder bewijs"
        )
        report = CurationReport(
            article_id="ART-001",
            findings=(critical,),
            verdict=CurationVerdict.APPROVED,  # Should be overridden
        )
        assert report.verdict == CurationVerdict.REJECTED

    def test_curation_report_auto_needs_revision_error(self) -> None:
        error = CurationFinding(severity="ERROR", category="sources", description="Geen bronnen")
        report = CurationReport(
            article_id="ART-001",
            findings=(error,),
            verdict=CurationVerdict.APPROVED,  # Should be overridden
        )
        assert report.verdict == CurationVerdict.NEEDS_REVISION

    def test_curation_report_approved_no_findings(self) -> None:
        report = CurationReport(article_id="ART-001")
        assert report.verdict == CurationVerdict.APPROVED
        assert report.findings == ()

    def test_curation_report_is_approved_property(self) -> None:
        approved = CurationReport(article_id="ART-001")
        assert approved.is_approved is True

        error = CurationFinding(severity="ERROR", category="sources", description="test")
        not_approved = CurationReport(article_id="ART-002", findings=(error,))
        assert not_approved.is_approved is False


# --- KnowledgeHealthReport tests ---


class TestKnowledgeHealthReport:
    def test_knowledge_health_report_score_validation(self) -> None:
        with pytest.raises(ValueError, match="overall_score must be between"):
            KnowledgeHealthReport(overall_score=-1.0)
        with pytest.raises(ValueError, match="overall_score must be between"):
            KnowledgeHealthReport(overall_score=101.0)
        # Boundary values
        assert KnowledgeHealthReport(overall_score=0.0).overall_score == 0.0
        assert KnowledgeHealthReport(overall_score=100.0).overall_score == 100.0


# --- Observation tests ---


class TestObservation:
    def test_observation_creation(self) -> None:
        obs = Observation(
            observation_id="OBS-001",
            observation_type=ObservationType.FRESHNESS_ALERT,
            source_agent="knowledge-curator",
            severity="WARNING",
            payload="Artikel is 200 dagen oud",
            timestamp="2026-03-27T00:00:00+00:00",
        )
        assert obs.observation_id == "OBS-001"
        assert obs.observation_type == ObservationType.FRESHNESS_ALERT
        assert obs.source_agent == "knowledge-curator"
        assert obs.resolved is False

    def test_observation_validation(self) -> None:
        with pytest.raises(ValueError, match="observation_id is required"):
            Observation(
                observation_id="",
                observation_type=ObservationType.FRESHNESS_ALERT,
                source_agent="curator",
            )
        with pytest.raises(ValueError, match="source_agent is required"):
            Observation(
                observation_id="OBS-001",
                observation_type=ObservationType.FRESHNESS_ALERT,
                source_agent="",
            )

    def test_observation_to_dict(self) -> None:
        obs = Observation(
            observation_id="OBS-001",
            observation_type=ObservationType.GRADE_DEGRADATION,
            source_agent="knowledge-curator",
            severity="ERROR",
            payload="Grade degraded",
            timestamp="2026-03-27T00:00:00+00:00",
            resolved=True,
        )
        d = obs.to_dict()
        assert d["observation_id"] == "OBS-001"
        assert d["observation_type"] == "grade_degradation"
        assert d["source_agent"] == "knowledge-curator"
        assert d["severity"] == "ERROR"
        assert d["resolved"] is True
