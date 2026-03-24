"""Tests voor Security Contracts — Red Team communicatie-contracten."""

import pytest

from devhub_core.contracts.security_contracts import (
    ASI_IDS,
    SecurityAuditReport,
    SecurityFinding,
)


# ---------------------------------------------------------------------------
# SecurityFinding
# ---------------------------------------------------------------------------


class TestSecurityFinding:
    def test_valid_finding(self):
        f = SecurityFinding(
            asi_id="ASI01",
            severity="P1_CRITICAL",
            component="dev-lead",
            description="Goal hijacking via CLAUDE.md injection",
            attack_vector="Malicious CLAUDE.md in submodule",
            current_mitigation="Art. 6 project-soevereiniteit",
            recommendation="Add CLAUDE.md content validation",
        )
        assert f.asi_id == "ASI01"
        assert f.severity == "P1_CRITICAL"
        assert f.kill_chain_stage is None

    def test_with_kill_chain_stage(self):
        f = SecurityFinding(
            asi_id="ASI06",
            severity="P3_ATTENTION",
            component="memory",
            description="Scratchpad poisoning possible",
            attack_vector="Inject poisoned QAReport",
            current_mitigation="None",
            recommendation="Add integrity check on scratchpad",
            kill_chain_stage=4,
        )
        assert f.kill_chain_stage == 4

    def test_frozen(self):
        f = SecurityFinding(
            asi_id="ASI01",
            severity="P4_INFO",
            component="coder",
            description="Test finding",
            attack_vector="N/A",
            current_mitigation="N/A",
            recommendation="N/A",
        )
        with pytest.raises(AttributeError):
            f.severity = "P1_CRITICAL"  # type: ignore[misc]

    def test_invalid_asi_id(self):
        with pytest.raises(ValueError, match="asi_id must be one of"):
            SecurityFinding(
                asi_id="ASI99",
                severity="P4_INFO",
                component="coder",
                description="Bad ID",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
            )

    def test_empty_description(self):
        with pytest.raises(ValueError, match="description is required"):
            SecurityFinding(
                asi_id="ASI01",
                severity="P4_INFO",
                component="coder",
                description="",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
            )

    def test_empty_component(self):
        with pytest.raises(ValueError, match="component is required"):
            SecurityFinding(
                asi_id="ASI01",
                severity="P4_INFO",
                component="",
                description="Test",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
            )

    def test_invalid_kill_chain_stage_zero(self):
        with pytest.raises(ValueError, match="kill_chain_stage must be 1-7"):
            SecurityFinding(
                asi_id="ASI01",
                severity="P4_INFO",
                component="coder",
                description="Test",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
                kill_chain_stage=0,
            )

    def test_invalid_kill_chain_stage_eight(self):
        with pytest.raises(ValueError, match="kill_chain_stage must be 1-7"):
            SecurityFinding(
                asi_id="ASI01",
                severity="P4_INFO",
                component="coder",
                description="Test",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
                kill_chain_stage=8,
            )

    def test_all_asi_ids_valid(self):
        """Verify all 10 ASI IDs are accepted."""
        for asi_id in sorted(ASI_IDS):
            f = SecurityFinding(
                asi_id=asi_id,
                severity="P4_INFO",
                component="system",
                description=f"Test for {asi_id}",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
            )
            assert f.asi_id == asi_id

    def test_all_severity_levels(self):
        for severity in ("P1_CRITICAL", "P2_DEGRADED", "P3_ATTENTION", "P4_INFO"):
            f = SecurityFinding(
                asi_id="ASI01",
                severity=severity,
                component="coder",
                description="Test",
                attack_vector="N/A",
                current_mitigation="N/A",
                recommendation="N/A",
            )
            assert f.severity == severity


# ---------------------------------------------------------------------------
# SecurityAuditReport
# ---------------------------------------------------------------------------


class TestSecurityAuditReport:
    def _make_finding(
        self,
        asi_id: str = "ASI01",
        severity: str = "P4_INFO",
    ) -> SecurityFinding:
        return SecurityFinding(
            asi_id=asi_id,
            severity=severity,
            component="test",
            description="Test finding",
            attack_vector="N/A",
            current_mitigation="N/A",
            recommendation="N/A",
        )

    def test_empty_report(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
        )
        assert r.total_findings == 0
        assert r.overall_risk == "LOW"
        assert r.critical_findings == []
        assert not r.has_vulnerabilities

    def test_frozen(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
        )
        with pytest.raises(AttributeError):
            r.audit_id = "changed"  # type: ignore[misc]

    def test_auto_risk_escalation_critical(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            findings=[self._make_finding(severity="P1_CRITICAL")],
            overall_risk="LOW",
        )
        assert r.overall_risk == "CRITICAL"

    def test_auto_risk_escalation_degraded(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            findings=[self._make_finding(severity="P2_DEGRADED")],
            overall_risk="LOW",
        )
        assert r.overall_risk == "HIGH"

    def test_auto_risk_no_downgrade(self):
        """If overall_risk is already CRITICAL, P4 findings don't downgrade it."""
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            findings=[self._make_finding(severity="P4_INFO")],
            overall_risk="CRITICAL",
        )
        assert r.overall_risk == "CRITICAL"

    def test_critical_findings_property(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            findings=[
                self._make_finding(severity="P1_CRITICAL"),
                self._make_finding(severity="P4_INFO"),
                self._make_finding(asi_id="ASI02", severity="P1_CRITICAL"),
            ],
        )
        assert len(r.critical_findings) == 2
        assert r.total_findings == 3

    def test_has_vulnerabilities(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            asi_coverage={"ASI01": "MITIGATED", "ASI02": "VULNERABLE"},
        )
        assert r.has_vulnerabilities

    def test_no_vulnerabilities(self):
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            asi_coverage={"ASI01": "MITIGATED", "ASI02": "PARTIAL"},
        )
        assert not r.has_vulnerabilities

    def test_invalid_audit_id(self):
        with pytest.raises(ValueError, match="audit_id is required"):
            SecurityAuditReport(
                audit_id="",
                timestamp="2026-03-24T08:00:00Z",
                mode="owasp_asi",
            )

    def test_invalid_timestamp(self):
        with pytest.raises(ValueError, match="timestamp is required"):
            SecurityAuditReport(
                audit_id="audit-001",
                timestamp="",
                mode="owasp_asi",
            )

    def test_invalid_asi_coverage_key(self):
        with pytest.raises(ValueError, match="asi_coverage key must be a valid ASI ID"):
            SecurityAuditReport(
                audit_id="audit-001",
                timestamp="2026-03-24T08:00:00Z",
                mode="owasp_asi",
                asi_coverage={"INVALID": "MITIGATED"},
            )

    def test_all_audit_modes(self):
        for mode in ("owasp_asi", "kill_chain", "deepteam"):
            r = SecurityAuditReport(
                audit_id="audit-001",
                timestamp="2026-03-24T08:00:00Z",
                mode=mode,
            )
            assert r.mode == mode

    def test_full_asi_coverage(self):
        """All 10 ASI IDs can be used as coverage keys."""
        coverage = {asi_id: "NOT_ASSESSED" for asi_id in sorted(ASI_IDS)}
        r = SecurityAuditReport(
            audit_id="audit-001",
            timestamp="2026-03-24T08:00:00Z",
            mode="owasp_asi",
            asi_coverage=coverage,
        )
        assert len(r.asi_coverage) == 10
