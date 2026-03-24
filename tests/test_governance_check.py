"""Tests voor scripts/governance_check.py — DevHub Governance Check.

Test elke G-check functie met known-good en known-bad input.
"""
import sys
from pathlib import Path

# Voeg scripts/ toe aan sys.path zodat we governance_check kunnen importeren
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from governance_check import (
    Finding,
    GovernanceReport,
    check_g01_destructive_patterns,
    check_g05_destructive_git,
    check_g07_commit_message,
    check_g11_project_governance,
    check_g15_pii,
    check_g16_env_files,
)


# ── G-01: Destructieve patronen ──────────────────────────────────────────────

class TestG01DestructivePatterns:
    def test_clean_diff_no_findings(self):
        diff = "+def hello():\n+    return 'world'"
        assert check_g01_destructive_patterns(diff) == []

    def test_rm_rf_detected(self):
        diff = "+subprocess.run(['rm', '-rf', '/tmp/data'])"
        findings = check_g01_destructive_patterns(diff)
        assert len(findings) >= 1
        assert any("rm -rf" in f.detail.lower() or "recursive force delete" in f.detail.lower() for f in findings)

    def test_force_flag_detected(self):
        diff = "+git push --force origin main"
        findings = check_g01_destructive_patterns(diff)
        assert len(findings) >= 1
        assert any("force" in f.detail.lower() for f in findings)

    def test_drop_table_detected(self):
        diff = "+cursor.execute('DROP TABLE users')"
        findings = check_g01_destructive_patterns(diff)
        assert len(findings) >= 1
        assert any("drop table" in f.detail.lower() for f in findings)

    def test_hard_reset_detected(self):
        diff = "+git reset --hard HEAD~3"
        findings = check_g01_destructive_patterns(diff)
        assert len(findings) >= 1


# ── G-05: Destructieve git operaties ────────────────────────────────────────

class TestG05DestructiveGit:
    def test_clean_diff_no_findings(self):
        diff = "+git commit -m 'feat: add feature'"
        assert check_g05_destructive_git(diff) == []

    def test_force_push_detected(self):
        diff = "+# WARNING: do not force push to main"
        findings = check_g05_destructive_git(diff)
        assert len(findings) >= 1
        assert any("force push" in f.detail.lower() for f in findings)

    def test_no_verify_detected(self):
        diff = "+git commit --no-verify -m 'skip hooks'"
        findings = check_g05_destructive_git(diff)
        assert len(findings) >= 1
        assert any("no-verify" in f.detail.lower() for f in findings)

    def test_reset_hard_detected(self):
        diff = "+# Use reset --hard carefully"
        findings = check_g05_destructive_git(diff)
        assert len(findings) >= 1


# ── G-07: Commit message kwaliteit ──────────────────────────────────────────

class TestG07CommitMessage:
    def test_good_message_no_findings(self):
        msg = "feat(cicd): add governance check workflow for DEV_CONSTITUTION compliance"
        assert check_g07_commit_message(msg) == []

    def test_too_short_message(self):
        msg = "fix"
        findings = check_g07_commit_message(msg)
        assert len(findings) >= 1
        assert any("short" in f.detail.lower() or "low-quality" in f.detail.lower() for f in findings)

    def test_low_quality_message(self):
        msg = "update"
        findings = check_g07_commit_message(msg)
        assert len(findings) >= 1

    def test_wip_message(self):
        msg = "wip"
        findings = check_g07_commit_message(msg)
        assert len(findings) >= 1

    def test_short_but_meaningful(self):
        # 10+ chars en niet in low-quality list
        msg = "fix typo in README"
        assert check_g07_commit_message(msg) == []


# ── G-11: Project-governance wijzigingen ─────────────────────────────────────

class TestG11ProjectGovernance:
    def test_normal_files_no_findings(self):
        files = ["devhub/registry.py", "tests/test_registry.py"]
        assert check_g11_project_governance(files) == []

    def test_project_claude_md_detected(self):
        files = ["projects/buurts-ecosysteem/CLAUDE.md"]
        findings = check_g11_project_governance(files)
        assert len(findings) == 1
        assert "CLAUDE.md" in findings[0].detail

    def test_project_claude_dir_detected(self):
        files = ["projects/buurts-ecosysteem/.claude/agents/orchestrator.md"]
        findings = check_g11_project_governance(files)
        assert len(findings) == 1

    def test_devhub_claude_md_not_flagged(self):
        # DevHub's eigen CLAUDE.md is geen project-governance
        files = [".claude/CLAUDE.md", "CLAUDE.md"]
        assert check_g11_project_governance(files) == []


# ── G-15: PII-patronen ──────────────────────────────────────────────────────

class TestG15PII:
    def test_clean_diff_no_findings(self):
        diff = "+name = 'test'\n+count = 42"
        assert check_g15_pii(diff) == []

    def test_email_detected(self):
        diff = "+contact = 'user@company.nl'"
        findings = check_g15_pii(diff)
        assert len(findings) >= 1
        assert any("email" in f.detail.lower() for f in findings)

    def test_known_emails_filtered(self):
        # noreply@anthropic.com is een bekende false positive
        diff = "+Co-Authored-By: Claude <noreply@anthropic.com>"
        assert check_g15_pii(diff) == []

    def test_dutch_mobile_detected(self):
        diff = "+phone = '06-12345678'"
        findings = check_g15_pii(diff)
        assert len(findings) >= 1
        assert any("mobile" in f.detail.lower() or "phone" in f.detail.lower() for f in findings)

    def test_removed_lines_not_checked(self):
        # Alleen toegevoegde regels (met +) worden gecheckt
        diff = "-old_email = 'secret@company.nl'\n normal line"
        assert check_g15_pii(diff) == []


# ── G-16: .env bestanden ────────────────────────────────────────────────────

class TestG16EnvFiles:
    def test_normal_files_no_findings(self):
        files = ["devhub/registry.py", "docker-compose.yml"]
        assert check_g16_env_files(files) == []

    def test_env_file_detected(self):
        files = [".env"]
        findings = check_g16_env_files(files)
        assert len(findings) == 1
        assert findings[0].severity == "CRITICAL"

    def test_env_local_detected(self):
        files = [".env.local"]
        findings = check_g16_env_files(files)
        assert len(findings) == 1

    def test_env_example_allowed(self):
        # .env.example is OK — bevat templates, geen echte secrets
        files = [".env.example"]
        assert check_g16_env_files(files) == []

    def test_nested_env_detected(self):
        files = ["config/.env"]
        findings = check_g16_env_files(files)
        assert len(findings) == 1


# ── Report & Verdict ─────────────────────────────────────────────────────────

class TestReport:
    def test_empty_report_is_pass(self):
        report = GovernanceReport()
        assert report.verdict == "PASS"
        assert report.findings == []

    def test_to_dict(self):
        finding = Finding(check="G-01", severity="WARNING", detail="test", file="a.py")
        d = finding.to_dict()
        assert d["check"] == "G-01"
        assert d["file"] == "a.py"

    def test_report_to_dict(self):
        report = GovernanceReport(
            commit_sha="abc123",
            commit_message="test msg",
            verdict="BLOCK",
            findings=[Finding(check="G-14", severity="CRITICAL", detail="secret found")],
        )
        d = report.to_dict()
        assert d["verdict"] == "BLOCK"
        assert len(d["findings"]) == 1
