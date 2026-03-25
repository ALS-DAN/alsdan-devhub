"""Tests voor F4 health contracts: Severity, HealthFinding, HealthCheckResult, FullHealthReport."""

import pytest

from devhub_core.contracts.node_interface import (
    FullHealthReport,
    HealthCheckResult,
    HealthFinding,
    HealthStatus,
    Severity,
)


class TestSeverity:
    def test_severity_values(self):
        assert Severity.P1_CRITICAL.value == "P1"
        assert Severity.P2_DEGRADED.value == "P2"
        assert Severity.P3_ATTENTION.value == "P3"
        assert Severity.P4_INFO.value == "P4"

    def test_severity_ordering(self):
        """P1 is erger dan P4 — we gebruiken de enum name voor vergelijking."""
        severities = [
            Severity.P4_INFO,
            Severity.P1_CRITICAL,
            Severity.P3_ATTENTION,
            Severity.P2_DEGRADED,
        ]
        sorted_by_value = sorted(severities, key=lambda s: s.value)
        assert sorted_by_value[0] == Severity.P1_CRITICAL
        assert sorted_by_value[-1] == Severity.P4_INFO


class TestHealthStatus:
    def test_status_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.ATTENTION.value == "attention"
        assert HealthStatus.CRITICAL.value == "critical"


class TestHealthFinding:
    def test_valid_finding(self):
        f = HealthFinding(
            component="tests",
            severity=Severity.P1_CRITICAL,
            message="5 tests failed",
            detail="test_foo, test_bar, ...",
            recommended_action="Fix failing tests",
        )
        assert f.component == "tests"
        assert f.severity == Severity.P1_CRITICAL
        assert f.message == "5 tests failed"

    def test_frozen(self):
        f = HealthFinding(component="tests", severity=Severity.P1_CRITICAL, message="fail")
        with pytest.raises(AttributeError):
            f.component = "lint"  # type: ignore[misc]

    def test_empty_component_raises(self):
        with pytest.raises(ValueError, match="component"):
            HealthFinding(component="", severity=Severity.P1_CRITICAL, message="fail")

    def test_empty_message_raises(self):
        with pytest.raises(ValueError, match="message"):
            HealthFinding(component="tests", severity=Severity.P1_CRITICAL, message="")

    def test_defaults(self):
        f = HealthFinding(component="tests", severity=Severity.P3_ATTENTION, message="minor")
        assert f.detail == ""
        assert f.recommended_action == ""


class TestHealthCheckResult:
    def test_valid_check(self):
        r = HealthCheckResult(
            dimension="code_quality",
            status=HealthStatus.HEALTHY,
            summary="All tests pass",
        )
        assert r.dimension == "code_quality"
        assert r.status == HealthStatus.HEALTHY
        assert r.findings == ()

    def test_check_with_findings(self):
        f = HealthFinding(component="lint", severity=Severity.P2_DEGRADED, message="errors")
        r = HealthCheckResult(
            dimension="code_quality",
            status=HealthStatus.ATTENTION,
            summary="Lint errors",
            findings=(f,),
        )
        assert len(r.findings) == 1

    def test_empty_dimension_raises(self):
        with pytest.raises(ValueError, match="dimension"):
            HealthCheckResult(dimension="", status=HealthStatus.HEALTHY, summary="ok")


class TestFullHealthReport:
    def test_empty_report(self):
        r = FullHealthReport(
            node_id="test-node",
            timestamp="2026-03-23T10:00:00Z",
        )
        assert r.overall == HealthStatus.HEALTHY
        assert r.checks == ()

    def test_overall_auto_computed_attention(self):
        checks = (
            HealthCheckResult(dimension="tests", status=HealthStatus.HEALTHY, summary="ok"),
            HealthCheckResult(dimension="deps", status=HealthStatus.ATTENTION, summary="issues"),
        )
        r = FullHealthReport(
            node_id="test-node",
            timestamp="2026-03-23T10:00:00Z",
            checks=checks,
        )
        assert r.overall == HealthStatus.ATTENTION

    def test_overall_auto_computed_critical(self):
        checks = (
            HealthCheckResult(dimension="tests", status=HealthStatus.CRITICAL, summary="fail"),
            HealthCheckResult(dimension="deps", status=HealthStatus.ATTENTION, summary="issues"),
        )
        r = FullHealthReport(
            node_id="test-node",
            timestamp="2026-03-23T10:00:00Z",
            checks=checks,
        )
        assert r.overall == HealthStatus.CRITICAL

    def test_overall_all_healthy(self):
        checks = (
            HealthCheckResult(dimension="a", status=HealthStatus.HEALTHY, summary="ok"),
            HealthCheckResult(dimension="b", status=HealthStatus.HEALTHY, summary="ok"),
        )
        r = FullHealthReport(
            node_id="test-node",
            timestamp="2026-03-23T10:00:00Z",
            checks=checks,
        )
        assert r.overall == HealthStatus.HEALTHY

    def test_empty_node_id_raises(self):
        with pytest.raises(ValueError, match="node_id"):
            FullHealthReport(node_id="", timestamp="2026-03-23T10:00:00Z")

    def test_p1_findings(self):
        f1 = HealthFinding(component="a", severity=Severity.P1_CRITICAL, message="crit")
        f2 = HealthFinding(component="b", severity=Severity.P2_DEGRADED, message="deg")
        f3 = HealthFinding(component="c", severity=Severity.P1_CRITICAL, message="crit2")
        checks = (
            HealthCheckResult(
                dimension="x", status=HealthStatus.CRITICAL, summary="bad", findings=(f1, f2)
            ),
            HealthCheckResult(
                dimension="y", status=HealthStatus.CRITICAL, summary="bad", findings=(f3,)
            ),
        )
        r = FullHealthReport(node_id="t", timestamp="now", checks=checks)
        assert len(r.p1_findings) == 2
        assert len(r.p2_findings) == 1
        assert len(r.alert_findings) == 3

    def test_frozen(self):
        r = FullHealthReport(node_id="t", timestamp="now")
        with pytest.raises(AttributeError):
            r.node_id = "other"  # type: ignore[misc]
