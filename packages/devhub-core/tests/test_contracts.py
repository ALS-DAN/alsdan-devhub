"""Tests voor NodeInterface en Dev Contracts."""

import pytest

from devhub_core.contracts.node_interface import (
    NodeDocStatus,
    NodeHealth,
    NodeReport,
    TestResult,
)
from devhub_core.contracts.dev_contracts import (
    DevTaskRequest,
    DevTaskResult,
    DocGenRequest,
    QAFinding,
    QAReport,
)


# ---------------------------------------------------------------------------
# NodeHealth
# ---------------------------------------------------------------------------


class TestNodeHealth:
    def test_valid_health(self):
        h = NodeHealth(
            status="UP",
            components={"weaviate": "UP", "ollama": "UP"},
            test_count=2229,
            test_pass_rate=1.0,
            coverage_pct=75.0,
        )
        assert h.status == "UP"
        assert h.test_count == 2229

    def test_frozen(self):
        h = NodeHealth(
            status="UP", components={}, test_count=0, test_pass_rate=0.0, coverage_pct=0.0
        )
        with pytest.raises(AttributeError):
            h.status = "DOWN"  # type: ignore[misc]

    def test_invalid_pass_rate(self):
        with pytest.raises(ValueError, match="test_pass_rate"):
            NodeHealth(
                status="UP", components={}, test_count=0, test_pass_rate=1.5, coverage_pct=0.0
            )

    def test_invalid_coverage(self):
        with pytest.raises(ValueError, match="coverage_pct"):
            NodeHealth(
                status="UP", components={}, test_count=0, test_pass_rate=0.5, coverage_pct=101.0
            )


# ---------------------------------------------------------------------------
# NodeDocStatus
# ---------------------------------------------------------------------------


class TestNodeDocStatus:
    def test_valid(self):
        d = NodeDocStatus(total_pages=100, stale_pages=5, diataxis_coverage={"tutorial": 10})
        assert d.total_pages == 100

    def test_stale_exceeds_total(self):
        with pytest.raises(ValueError, match="stale_pages"):
            NodeDocStatus(total_pages=5, stale_pages=10, diataxis_coverage={})


# ---------------------------------------------------------------------------
# TestResult
# ---------------------------------------------------------------------------


class TestTestResult:
    def test_pass_rate(self):
        r = TestResult(total=100, passed=95, failed=5, errors=0, duration_seconds=10.0)
        assert r.pass_rate == 0.95
        assert not r.success

    def test_success(self):
        r = TestResult(total=100, passed=100, failed=0, errors=0, duration_seconds=5.0)
        assert r.success

    def test_zero_total(self):
        r = TestResult(total=0, passed=0, failed=0, errors=0, duration_seconds=0.0)
        assert r.pass_rate == 0.0


# ---------------------------------------------------------------------------
# NodeReport
# ---------------------------------------------------------------------------


class TestNodeReport:
    def test_valid_report(self):
        health = NodeHealth(
            status="UP", components={}, test_count=100, test_pass_rate=1.0, coverage_pct=70.0
        )
        doc = NodeDocStatus(total_pages=50, stale_pages=2, diataxis_coverage={})
        report = NodeReport(
            node_id="boris-buurts",
            timestamp="2026-03-23T12:00:00Z",
            health=health,
            doc_status=doc,
        )
        assert report.node_id == "boris-buurts"

    def test_empty_node_id(self):
        health = NodeHealth(
            status="UP", components={}, test_count=0, test_pass_rate=0.0, coverage_pct=0.0
        )
        doc = NodeDocStatus(total_pages=0, stale_pages=0, diataxis_coverage={})
        with pytest.raises(ValueError, match="node_id"):
            NodeReport(node_id="", timestamp="2026-03-23T12:00:00Z", health=health, doc_status=doc)


# ---------------------------------------------------------------------------
# DevTaskRequest
# ---------------------------------------------------------------------------


class TestDevTaskRequest:
    def test_valid(self):
        req = DevTaskRequest(
            task_id="TASK-001",
            description="Add LUMEN export",
            node_id="boris-buurts",
            scope_files=["agents/lumen_agent.py"],
        )
        assert req.task_id == "TASK-001"

    def test_empty_task_id(self):
        with pytest.raises(ValueError, match="task_id"):
            DevTaskRequest(task_id="", description="test", node_id="boris")

    def test_empty_description(self):
        with pytest.raises(ValueError, match="description"):
            DevTaskRequest(task_id="T1", description="", node_id="boris")

    def test_frozen(self):
        req = DevTaskRequest(task_id="T1", description="test", node_id="boris")
        with pytest.raises(AttributeError):
            req.task_id = "T2"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DevTaskResult
# ---------------------------------------------------------------------------


class TestDevTaskResult:
    def test_valid(self):
        res = DevTaskResult(task_id="T1", files_changed=["a.py"], tests_added=5, lint_clean=True)
        assert res.tests_added == 5

    def test_empty_task_id(self):
        with pytest.raises(ValueError, match="task_id"):
            DevTaskResult(task_id="")


# ---------------------------------------------------------------------------
# DocGenRequest
# ---------------------------------------------------------------------------


class TestDocGenRequest:
    def test_valid(self):
        req = DocGenRequest(
            task_id="T1",
            target_files=["docs/tutorial.md"],
            diataxis_category="tutorial",
            audience="developer",
        )
        assert req.diataxis_category == "tutorial"

    def test_invalid_category(self):
        with pytest.raises(ValueError, match="diataxis_category"):
            DocGenRequest(
                task_id="T1",
                target_files=["docs/x.md"],
                diataxis_category="invalid",  # type: ignore[arg-type]
                audience="dev",
            )

    def test_empty_target_files(self):
        with pytest.raises(ValueError, match="target_files"):
            DocGenRequest(task_id="T1", target_files=[], diataxis_category="howto", audience="dev")


# ---------------------------------------------------------------------------
# QAReport
# ---------------------------------------------------------------------------


class TestQAReport:
    def test_clean_report(self):
        report = QAReport(task_id="T1")
        assert report.is_clean
        assert report.verdict == "PASS"
        assert report.total_findings == 0

    def test_with_findings(self):
        finding = QAFinding(severity="WARNING", category="code", description="Missing docstring")
        report = QAReport(task_id="T1", code_findings=[finding], verdict="NEEDS_WORK")
        assert report.total_findings == 1
        assert not report.is_clean

    def test_critical_auto_blocks(self):
        critical = QAFinding(severity="CRITICAL", category="code", description="Security vuln")
        report = QAReport(task_id="T1", code_findings=[critical], verdict="PASS")
        # __post_init__ should auto-correct to BLOCK
        assert report.verdict == "BLOCK"

    def test_frozen(self):
        report = QAReport(task_id="T1")
        with pytest.raises(AttributeError):
            report.task_id = "T2"  # type: ignore[misc]
