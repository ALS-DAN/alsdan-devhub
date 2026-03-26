"""Tests voor SecurityScanner — Governance S2."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from devhub_core.agents.security_scanner import (
    SECURITY_CHECKS,
    SecurityScanner,
)
from devhub_core.contracts.security_contracts import (
    SecurityAuditReport,
    SecurityFinding,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def scanner(tmp_path: Path) -> SecurityScanner:
    return SecurityScanner(reports_path=tmp_path / "reports")


@pytest.fixture()
def agents_dir(tmp_path: Path) -> Path:
    d = tmp_path / "agents"
    d.mkdir()
    return d


@pytest.fixture()
def skills_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".claude" / "skills" / "test-skill"
    d.mkdir(parents=True)
    return d


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestInit:
    def test_creates_reports_dir(self, tmp_path: Path) -> None:
        reports = tmp_path / "sec_reports"
        assert not reports.exists()
        SecurityScanner(reports_path=reports)
        assert reports.exists()

    def test_default_reports_path(self) -> None:
        scanner = SecurityScanner()
        assert scanner._reports_path.name == "security_reports"


# ---------------------------------------------------------------------------
# SA-01: disallowedTools (ASI02)
# ---------------------------------------------------------------------------


class TestScanDisallowedTools:
    def test_missing_agents_dir(self, scanner: SecurityScanner, tmp_path: Path) -> None:
        findings = scanner.scan_disallowed_tools(tmp_path / "nonexistent")
        assert len(findings) == 1
        assert findings[0].asi_id == "ASI02"

    def test_empty_agents_dir(self, scanner: SecurityScanner, agents_dir: Path) -> None:
        findings = scanner.scan_disallowed_tools(agents_dir)
        assert len(findings) == 1
        assert "Geen agent .md bestanden" in findings[0].description

    def test_agent_with_deny_list_passes(self, scanner: SecurityScanner, agents_dir: Path) -> None:
        (agents_dir / "coder.md").write_text("# Coder\n\n## disallowedTools\n- rm -rf")
        findings = scanner.scan_disallowed_tools(agents_dir)
        assert len(findings) == 0

    def test_agent_without_deny_list_fails(
        self, scanner: SecurityScanner, agents_dir: Path
    ) -> None:
        (agents_dir / "coder.md").write_text("# Coder\n\nJust code stuff")
        findings = scanner.scan_disallowed_tools(agents_dir)
        assert len(findings) == 1
        assert findings[0].severity == "P2_DEGRADED"
        assert "deny-list" in findings[0].description

    def test_multiple_agents_mixed(self, scanner: SecurityScanner, agents_dir: Path) -> None:
        (agents_dir / "good.md").write_text("# Good\n## disallowedTools\n- rm")
        (agents_dir / "bad.md").write_text("# Bad\nNo restrictions")
        findings = scanner.scan_disallowed_tools(agents_dir)
        assert len(findings) == 1
        assert findings[0].component == "bad"

    def test_dutch_deny_keyword_detected(self, scanner: SecurityScanner, agents_dir: Path) -> None:
        (agents_dir / "agent.md").write_text("# Agent\n\nNiet toegestaan: rm -rf")
        findings = scanner.scan_disallowed_tools(agents_dir)
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# SA-02: Supply chain (ASI04)
# ---------------------------------------------------------------------------


class TestScanSupplyChain:
    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_clean_scan(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="[]")
        findings = scanner.scan_supply_chain(tmp_path)
        assert len(findings) == 0

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_vulnerability_found(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        vuln_data = [
            {
                "name": "requests",
                "version": "2.25.0",
                "vulns": [
                    {
                        "id": "CVE-2023-001",
                        "description": "Test vuln",
                        "fix_versions": ["2.31.0"],
                    }
                ],
            }
        ]
        mock_run.return_value = MagicMock(returncode=1, stdout=json.dumps(vuln_data))
        findings = scanner.scan_supply_chain(tmp_path)
        assert len(findings) == 1
        assert findings[0].asi_id == "ASI04"
        assert "requests" in findings[0].description

    @patch(
        "devhub_core.agents.security_scanner.subprocess.run",
        side_effect=FileNotFoundError,
    )
    def test_pip_audit_unavailable(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        findings = scanner.scan_supply_chain(tmp_path)
        assert len(findings) == 1
        assert findings[0].severity == "P4_INFO"
        assert "pip-audit niet beschikbaar" in findings[0].description

    @patch(
        "devhub_core.agents.security_scanner.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="pip-audit", timeout=60),
    )
    def test_pip_audit_timeout(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        findings = scanner.scan_supply_chain(tmp_path)
        assert len(findings) == 1
        assert "timeout" in findings[0].description


# ---------------------------------------------------------------------------
# SA-03: Submodule integrity (ASI04)
# ---------------------------------------------------------------------------


class TestScanSubmoduleIntegrity:
    def test_no_gitmodules_passes(self, scanner: SecurityScanner, tmp_path: Path) -> None:
        findings = scanner.scan_submodule_integrity(tmp_path)
        assert len(findings) == 0

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_pinned_submodule_passes(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        (tmp_path / ".gitmodules").write_text("[submodule]")
        mock_run.return_value = MagicMock(returncode=0, stdout=" abc1234 projects/sub (v1.0)\n")
        findings = scanner.scan_submodule_integrity(tmp_path)
        assert len(findings) == 0

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_uninitialized_submodule(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        (tmp_path / ".gitmodules").write_text("[submodule]")
        mock_run.return_value = MagicMock(returncode=0, stdout="-abc1234 projects/sub\n")
        findings = scanner.scan_submodule_integrity(tmp_path)
        assert len(findings) == 1
        assert "niet geïnitialiseerd" in findings[0].description

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_diverged_submodule(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        (tmp_path / ".gitmodules").write_text("[submodule]")
        mock_run.return_value = MagicMock(returncode=0, stdout="+abc1234 projects/sub (v1.0)\n")
        findings = scanner.scan_submodule_integrity(tmp_path)
        assert len(findings) == 1
        assert "wijkt af" in findings[0].description


# ---------------------------------------------------------------------------
# SA-04: Agent prompt tracking (ASI10)
# ---------------------------------------------------------------------------


class TestScanAgentPrompts:
    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_tracked_agent_passes(
        self, mock_run: MagicMock, scanner: SecurityScanner, agents_dir: Path
    ) -> None:
        (agents_dir / "coder.md").write_text("# Coder")
        mock_run.return_value = MagicMock(returncode=0, stdout="coder.md\n")
        findings = scanner.scan_agent_prompts(agents_dir)
        assert len(findings) == 0

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_untracked_agent_fails(
        self, mock_run: MagicMock, scanner: SecurityScanner, agents_dir: Path
    ) -> None:
        (agents_dir / "coder.md").write_text("# Coder")
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        findings = scanner.scan_agent_prompts(agents_dir)
        assert len(findings) == 1
        assert findings[0].asi_id == "ASI10"

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_skills_dir_included(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path, skills_dir: Path
    ) -> None:
        (skills_dir / "SKILL.md").write_text("# Skill")
        agents = tmp_path / "agents"
        agents.mkdir(exist_ok=True)
        mock_run.return_value = MagicMock(returncode=0, stdout="SKILL.md\n")
        findings = scanner.scan_agent_prompts(agents, skills_dir.parent)
        assert len(findings) == 0

    def test_nonexistent_dirs_no_crash(self, scanner: SecurityScanner, tmp_path: Path) -> None:
        findings = scanner.scan_agent_prompts(tmp_path / "no_agents", tmp_path / "no_skills")
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# full_scan
# ---------------------------------------------------------------------------


class TestFullScan:
    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_produces_audit_report(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        # Setup minimal project
        agents = tmp_path / "agents"
        agents.mkdir()
        (agents / "test.md").write_text("# Test\n## disallowedTools\n- rm")

        mock_run.return_value = MagicMock(returncode=0, stdout="test.md\n")

        report = scanner.full_scan(tmp_path, agents_dir=agents)
        assert isinstance(report, SecurityAuditReport)
        assert report.audit_id.startswith("SEC-")
        assert report.mode == "owasp_asi"

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_asi_coverage_populated(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        agents = tmp_path / "agents"
        agents.mkdir()
        (agents / "test.md").write_text("# Test\n## deny\n- rm")
        mock_run.return_value = MagicMock(returncode=0, stdout="test.md\n")

        report = scanner.full_scan(tmp_path, agents_dir=agents)
        # ASI02, ASI04, ASI10 should be assessed
        assert "ASI02" in report.asi_coverage
        assert "ASI04" in report.asi_coverage
        assert "ASI10" in report.asi_coverage
        # Others should be NOT_ASSESSED
        assert report.asi_coverage["ASI01"] == "NOT_ASSESSED"

    @patch("devhub_core.agents.security_scanner.subprocess.run")
    def test_clean_scan_all_mitigated(
        self, mock_run: MagicMock, scanner: SecurityScanner, tmp_path: Path
    ) -> None:
        agents = tmp_path / "agents"
        agents.mkdir()
        (agents / "agent.md").write_text("# Agent\ndisallowedTools: rm, drop")
        mock_run.return_value = MagicMock(returncode=0, stdout="agent.md\n[]")

        report = scanner.full_scan(tmp_path, agents_dir=agents)
        assessed = {k: v for k, v in report.asi_coverage.items() if v != "NOT_ASSESSED"}
        for status in assessed.values():
            assert status in ("MITIGATED", "PARTIAL")


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------


class TestReportPersistence:
    def test_save_and_load_roundtrip(self, scanner: SecurityScanner) -> None:
        finding = SecurityFinding(
            asi_id="ASI02",
            severity="P3_ATTENTION",
            component="test",
            description="Test finding",
            attack_vector="Test",
            current_mitigation="Test",
            recommendation="Test",
        )
        report = SecurityAuditReport(
            audit_id="SEC-2026-03-26",
            timestamp="2026-03-26T12:00:00",
            mode="owasp_asi",
            findings=[finding],
            asi_coverage={"ASI02": "PARTIAL"},
        )

        path = scanner.save_report(report)
        assert path.exists()

        loaded = scanner.get_report(path)
        assert loaded.audit_id == report.audit_id
        assert len(loaded.findings) == 1
        assert loaded.findings[0].asi_id == "ASI02"
        assert loaded.asi_coverage["ASI02"] == "PARTIAL"

    def test_list_reports(self, scanner: SecurityScanner) -> None:
        report = SecurityAuditReport(
            audit_id="SEC-2026-03-26",
            timestamp="2026-03-26T12:00:00",
            mode="owasp_asi",
        )
        scanner.save_report(report)
        reports = scanner.list_reports()
        assert len(reports) == 1
        assert reports[0].name == "SEC-2026-03-26.json"

    def test_empty_report_persistence(self, scanner: SecurityScanner) -> None:
        report = SecurityAuditReport(
            audit_id="SEC-EMPTY",
            timestamp="2026-03-26T12:00:00",
            mode="owasp_asi",
        )
        path = scanner.save_report(report)
        loaded = scanner.get_report(path)
        assert loaded.findings == []
        assert loaded.overall_risk == "LOW"


# ---------------------------------------------------------------------------
# Check definitions
# ---------------------------------------------------------------------------


class TestCheckDefinitions:
    def test_all_checks_have_required_keys(self) -> None:
        for check in SECURITY_CHECKS:
            assert "id" in check
            assert "name" in check
            assert "desc" in check
            assert "asi" in check

    def test_check_ids_unique(self) -> None:
        ids = [c["id"] for c in SECURITY_CHECKS]
        assert len(ids) == len(set(ids))

    def test_check_count(self) -> None:
        assert len(SECURITY_CHECKS) == 4
