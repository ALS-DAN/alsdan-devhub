"""Tests voor Scanner Contracts — DomainScanStatus, KnowledgeScanResult, BootstrapAuditReport."""

from __future__ import annotations

import pytest

from devhub_core.contracts.scanner_contracts import (
    BootstrapAuditReport,
    BootstrapDomainReport,
    DomainScanStatus,
    KnowledgeScanResult,
    grade_gte,
)


class TestGradeGte:
    """Tests voor grade_gte helper."""

    @pytest.mark.parametrize(
        ("actual", "required", "expected"),
        [
            ("GOLD", "GOLD", True),
            ("GOLD", "SILVER", True),
            ("GOLD", "BRONZE", True),
            ("GOLD", "SPECULATIVE", True),
            ("SILVER", "GOLD", False),
            ("SILVER", "SILVER", True),
            ("SILVER", "BRONZE", True),
            ("BRONZE", "SILVER", False),
            ("BRONZE", "BRONZE", True),
            ("SPECULATIVE", "BRONZE", False),
            ("SPECULATIVE", "SPECULATIVE", True),
        ],
    )
    def test_grade_comparisons(self, actual: str, required: str, expected: bool):
        assert grade_gte(actual, required) is expected

    def test_unknown_grade_defaults_to_zero(self):
        assert grade_gte("UNKNOWN", "SPECULATIVE") is True  # 0 >= 0
        assert grade_gte("UNKNOWN", "BRONZE") is False


class TestDomainScanStatus:
    """Tests voor DomainScanStatus dataclass."""

    def test_creation(self):
        status = DomainScanStatus(
            domain="ai_engineering",
            required_grade="SILVER",
            actual_articles=5,
            actual_best_grade="SILVER",
            rq_coverage=(("RQ1", True), ("RQ4", True), ("RQ5", False)),
            sufficient=True,
        )
        assert status.domain == "ai_engineering"
        assert status.actual_articles == 5
        assert status.sufficient is True

    def test_frozen(self):
        status = DomainScanStatus(
            domain="ai_engineering", required_grade="SILVER", actual_articles=3
        )
        with pytest.raises(AttributeError):
            status.domain = "other"  # type: ignore[misc]

    def test_domain_required(self):
        with pytest.raises(ValueError, match="domain is required"):
            DomainScanStatus(domain="", required_grade="SILVER", actual_articles=0)

    def test_required_grade_required(self):
        with pytest.raises(ValueError, match="required_grade is required"):
            DomainScanStatus(domain="ai_engineering", required_grade="", actual_articles=0)

    def test_negative_articles(self):
        with pytest.raises(ValueError, match="actual_articles must be >= 0"):
            DomainScanStatus(domain="ai_engineering", required_grade="SILVER", actual_articles=-1)

    def test_covered_rqs(self):
        status = DomainScanStatus(
            domain="test",
            required_grade="BRONZE",
            actual_articles=2,
            rq_coverage=(("RQ1", True), ("RQ4", False), ("RQ5", True)),
        )
        assert status.covered_rqs == ["RQ1", "RQ5"]

    def test_missing_rqs(self):
        status = DomainScanStatus(
            domain="test",
            required_grade="BRONZE",
            actual_articles=2,
            rq_coverage=(("RQ1", True), ("RQ4", False), ("RQ5", False)),
        )
        assert status.missing_rqs == ["RQ4", "RQ5"]

    def test_rq_coverage_pct(self):
        status = DomainScanStatus(
            domain="test",
            required_grade="BRONZE",
            actual_articles=2,
            rq_coverage=(("RQ1", True), ("RQ4", False), ("RQ5", True)),
        )
        assert abs(status.rq_coverage_pct - 66.67) < 0.1

    def test_rq_coverage_pct_empty(self):
        status = DomainScanStatus(domain="test", required_grade="BRONZE", actual_articles=0)
        assert status.rq_coverage_pct == 100.0


class TestKnowledgeScanResult:
    """Tests voor KnowledgeScanResult dataclass."""

    def test_creation(self):
        result = KnowledgeScanResult(agent_name="dev-lead")
        assert result.agent_name == "dev-lead"
        assert result.overall_sufficient is True
        assert result.gap_domains == []

    def test_frozen(self):
        result = KnowledgeScanResult(agent_name="dev-lead")
        with pytest.raises(AttributeError):
            result.agent_name = "other"  # type: ignore[misc]

    def test_agent_name_required(self):
        with pytest.raises(ValueError, match="agent_name is required"):
            KnowledgeScanResult(agent_name="")

    def test_gap_domains(self):
        statuses = (
            DomainScanStatus(
                domain="ai_engineering",
                required_grade="SILVER",
                actual_articles=5,
                sufficient=True,
            ),
            DomainScanStatus(
                domain="claude_specific",
                required_grade="SILVER",
                actual_articles=0,
                sufficient=False,
            ),
        )
        result = KnowledgeScanResult(
            agent_name="dev-lead",
            domain_statuses=statuses,
            overall_sufficient=False,
        )
        assert result.gap_domains == ["claude_specific"]

    def test_gap_summary_no_gaps(self):
        result = KnowledgeScanResult(agent_name="coder")
        assert "alle domeinen voldoende" in result.gap_summary

    def test_gap_summary_with_gaps(self):
        statuses = (
            DomainScanStatus(
                domain="ai_engineering",
                required_grade="SILVER",
                actual_articles=0,
                sufficient=False,
                rq_coverage=(("RQ1", False),),
            ),
        )
        result = KnowledgeScanResult(
            agent_name="dev-lead",
            domain_statuses=statuses,
            overall_sufficient=False,
        )
        assert "ai_engineering" in result.gap_summary
        assert "RQ1" in result.gap_summary


class TestBootstrapDomainReport:
    """Tests voor BootstrapDomainReport dataclass."""

    def test_creation(self):
        report = BootstrapDomainReport(
            domain="ai_engineering",
            articles_created=6,
            coverage_pct=100.0,
        )
        assert report.domain == "ai_engineering"
        assert report.articles_created == 6

    def test_frozen(self):
        report = BootstrapDomainReport(domain="test")
        with pytest.raises(AttributeError):
            report.domain = "other"  # type: ignore[misc]

    def test_domain_required(self):
        with pytest.raises(ValueError, match="domain is required"):
            BootstrapDomainReport(domain="")

    def test_negative_articles(self):
        with pytest.raises(ValueError, match="articles_created must be >= 0"):
            BootstrapDomainReport(domain="test", articles_created=-1)

    def test_invalid_coverage_pct(self):
        with pytest.raises(ValueError, match="coverage_pct must be between 0 and 100"):
            BootstrapDomainReport(domain="test", coverage_pct=101.0)


class TestBootstrapAuditReport:
    """Tests voor BootstrapAuditReport dataclass."""

    def test_creation(self):
        report = BootstrapAuditReport(
            total_articles=30,
            total_domains=5,
            overall_coverage_pct=95.0,
        )
        assert report.total_articles == 30
        assert report.total_domains == 5

    def test_frozen(self):
        report = BootstrapAuditReport()
        with pytest.raises(AttributeError):
            report.total_articles = 10  # type: ignore[misc]

    def test_negative_articles(self):
        with pytest.raises(ValueError, match="total_articles must be >= 0"):
            BootstrapAuditReport(total_articles=-1)

    def test_invalid_coverage(self):
        with pytest.raises(ValueError, match="overall_coverage_pct must be between 0 and 100"):
            BootstrapAuditReport(overall_coverage_pct=200.0)

    def test_with_domain_reports(self):
        dr = BootstrapDomainReport(domain="test", articles_created=3, coverage_pct=50.0)
        report = BootstrapAuditReport(
            domain_reports=(dr,),
            total_articles=3,
            total_domains=1,
            overall_coverage_pct=50.0,
        )
        assert len(report.domain_reports) == 1
        assert report.domain_reports[0].domain == "test"
