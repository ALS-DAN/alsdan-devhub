"""Tests voor QA Agent — Governance Review Checks (GA-01 t/m GA-05)."""

from devhub_core.agents.qa_agent import (
    GOVERNANCE_REVIEW_CHECKS,
    QAAgent,
)
from devhub_core.contracts.dev_contracts import DevTaskResult


# ---------------------------------------------------------------------------
# Checklist meta-tests
# ---------------------------------------------------------------------------


class TestGovernanceChecklist:
    """Governance checklist completeness."""

    def test_governance_checklist_has_5_items(self):
        assert len(GOVERNANCE_REVIEW_CHECKS) == 5

    def test_all_governance_checks_have_required_fields(self):
        for check in GOVERNANCE_REVIEW_CHECKS:
            assert "id" in check
            assert "name" in check
            assert "desc" in check

    def test_governance_ids_are_ga_prefixed(self):
        for check in GOVERNANCE_REVIEW_CHECKS:
            assert check["id"].startswith("GA-")


# ---------------------------------------------------------------------------
# GA-01: Co-Authored-By compliance
# ---------------------------------------------------------------------------


class TestGA01CoauthorCompliance:
    """GA-01: Co-Authored-By header in commits."""

    def test_commit_with_coauthor_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        messages = ["feat: add feature\n\nCo-Authored-By: Claude <noreply@anthropic.com>"]
        findings = agent.review_coauthor_compliance(messages)
        assert len(findings) == 0

    def test_commit_without_coauthor_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        messages = ["feat: add feature without coauthor"]
        findings = agent.review_coauthor_compliance(messages)
        assert len(findings) == 1
        assert findings[0].severity == "WARNING"
        assert "GA-01" in findings[0].description

    def test_multiple_commits_mixed(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        messages = [
            "feat: first\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
            "fix: second without coauthor",
            "refactor: third also missing",
        ]
        findings = agent.review_coauthor_compliance(messages)
        assert len(findings) == 2

    def test_empty_commit_list_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_coauthor_compliance([])
        assert len(findings) == 0

    def test_coauthor_in_body_not_subject(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        messages = [
            "feat: subject line\n\nSome body text.\n\n"
            "Co-Authored-By: Claude <noreply@anthropic.com>"
        ]
        findings = agent.review_coauthor_compliance(messages)
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# GA-02: PII detection
# ---------------------------------------------------------------------------


class TestGA02PiiDetection:
    """GA-02: PII detectie in bestandsinhoud."""

    def test_email_address_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/config.py": "admin_email = 'john@example.com'"}
        findings = agent.review_pii(contents)
        email_findings = [f for f in findings if "email" in f.description]
        assert len(email_findings) >= 1
        assert email_findings[0].severity == "WARNING"

    def test_nl_phone_number_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/data.py": "phone = '0612345678'"}
        findings = agent.review_pii(contents)
        phone_findings = [
            f for f in findings if "telefoon" in f.description or "mobiel" in f.description
        ]
        assert len(phone_findings) >= 1
        assert all(f.severity == "WARNING" for f in phone_findings)

    def test_bsn_pattern_critical(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/intake.py": "bsn = 123456789"}
        findings = agent.review_pii(contents)
        bsn_findings = [f for f in findings if "BSN" in f.description]
        assert len(bsn_findings) >= 1
        assert bsn_findings[0].severity == "CRITICAL"

    def test_test_file_skipped(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"tests/test_pii.py": "email = 'test@example.com'\nbsn = 123456789"}
        findings = agent.review_pii(contents)
        assert len(findings) == 0

    def test_test_prefix_file_skipped(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/test_helpers.py": "email = 'test@example.com'"}
        findings = agent.review_pii(contents)
        assert len(findings) == 0

    def test_clean_file_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/clean.py": "x = 42\nname = 'Alice'\n"}
        findings = agent.review_pii(contents)
        assert len(findings) == 0

    def test_multiple_pii_types_in_one_file(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {
            "src/mixed.py": (
                "email = 'user@domain.nl'\n" "phone = '0612345678'\n" "bsn = 123456789\n"
            )
        }
        findings = agent.review_pii(contents)
        # Should detect at least email, phone, and BSN
        assert len(findings) >= 3

    def test_international_phone_format(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/contact.py": "phone = '0031612345678'"}
        findings = agent.review_pii(contents)
        phone_findings = [
            f for f in findings if "telefoon" in f.description or "mobiel" in f.description
        ]
        assert len(phone_findings) >= 1

    def test_finding_includes_file_path(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        contents = {"src/data.py": "email = 'a@b.com'"}
        findings = agent.review_pii(contents)
        assert any(f.file == "src/data.py" for f in findings)


# ---------------------------------------------------------------------------
# GA-03: .env file detection
# ---------------------------------------------------------------------------


class TestGA03EnvFileDetection:
    """GA-03: .env bestanden in staged changes."""

    def test_env_file_critical(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_env_files([".env"])
        assert len(findings) == 1
        assert findings[0].severity == "CRITICAL"
        assert "GA-03" in findings[0].description

    def test_env_local_critical(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_env_files([".env.local"])
        assert len(findings) == 1
        assert findings[0].severity == "CRITICAL"

    def test_env_production_critical(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_env_files([".env.production"])
        assert len(findings) == 1
        assert findings[0].severity == "CRITICAL"

    def test_environment_py_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_env_files(["src/environment.py"])
        assert len(findings) == 0

    def test_empty_list_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_env_files([])
        assert len(findings) == 0

    def test_nested_env_file(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_env_files(["config/.env"])
        assert len(findings) == 1
        assert findings[0].severity == "CRITICAL"


# ---------------------------------------------------------------------------
# GA-04: Destructive operations
# ---------------------------------------------------------------------------


class TestGA04DestructiveOps:
    """GA-04: Destructieve operaties in diff."""

    def test_git_force_push_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    git push --force origin main"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"
        assert "GA-04" in findings[0].description

    def test_rm_rf_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    os.system('rm -rf /tmp/data')"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"

    def test_drop_table_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    cursor.execute('DROP TABLE users')"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"

    def test_no_verify_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    git commit --no-verify -m 'skip hooks'"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"

    def test_git_reset_hard_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    git reset --hard HEAD~1"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"

    def test_truncate_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    TRUNCATE TABLE sessions;"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"

    def test_context_line_no_finding(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = " # This line mentions rm -rf but is context, not added"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) == 0

    def test_removed_line_no_finding(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "-    os.system('rm -rf /old')"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) == 0

    def test_clean_diff_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+    result = process_data(input_file)\n+    return result"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) == 0

    def test_diff_header_ignored(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        diff = "+++ b/src/deploy.sh\n+    echo 'deployed'"
        findings = agent.review_destructive_ops(diff)
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# GA-05: Governance file changes
# ---------------------------------------------------------------------------


class TestGA05GovernanceChanges:
    """GA-05: Governance bestanden gewijzigd."""

    def test_claude_md_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_governance_changes(["CLAUDE.md"])
        assert len(findings) == 1
        assert findings[0].severity == "WARNING"
        assert "GA-05" in findings[0].description

    def test_dev_constitution_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_governance_changes(["docs/compliance/DEV_CONSTITUTION.md"])
        assert len(findings) == 1
        assert findings[0].severity == "WARNING"

    def test_claude_settings_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_governance_changes([".claude/settings.json"])
        assert len(findings) == 1
        assert findings[0].severity == "WARNING"

    def test_normal_code_file_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_governance_changes(
            ["src/agents/orchestrator.py", "tests/test_agent.py"]
        )
        assert len(findings) == 0

    def test_finding_includes_file_reference(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.review_governance_changes(["CLAUDE.md"])
        assert findings[0].file == "CLAUDE.md"


# ---------------------------------------------------------------------------
# governance_review() orchestrator
# ---------------------------------------------------------------------------


class TestGovernanceReview:
    """governance_review() orchestratie van alle GA checks."""

    def test_all_inputs_multiple_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.governance_review(
            commit_messages=["feat: no coauthor"],
            staged_files=[".env"],
            file_contents={"src/data.py": "email = 'a@b.com'"},
            diff_content="+    git push --force",
            changed_files=["CLAUDE.md"],
        )
        # At least one from each check
        assert len(findings) >= 5
        descriptions = " ".join(f.description for f in findings)
        assert "GA-01" in descriptions
        assert "GA-02" in descriptions
        assert "GA-03" in descriptions
        assert "GA-04" in descriptions
        assert "GA-05" in descriptions

    def test_partial_inputs_commit_only(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.governance_review(commit_messages=["fix: missing coauthor"])
        assert len(findings) == 1
        assert "GA-01" in findings[0].description

    def test_no_inputs_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.governance_review()
        assert len(findings) == 0

    def test_none_inputs_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = agent.governance_review(
            commit_messages=None,
            staged_files=None,
            file_contents=None,
            diff_content=None,
            changed_files=None,
        )
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# full_review() with governance integration
# ---------------------------------------------------------------------------


class TestFullReviewGovernance:
    """full_review() met include_governance=True."""

    def test_full_review_with_governance(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        task_result = DevTaskResult(
            task_id="T1",
            files_changed=["a.py"],
            tests_added=5,
            lint_clean=True,
        )
        report = agent.full_review(
            "T1",
            task_result,
            include_governance=True,
            commit_messages=["feat: no coauthor"],
            staged_files=[".env"],
        )
        assert report.task_id == "T1"
        # Should include governance findings in code_findings
        ga_findings = [f for f in report.code_findings if "GA-" in f.description]
        assert len(ga_findings) >= 2  # GA-01 + GA-03

    def test_full_review_without_governance_flag(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        task_result = DevTaskResult(
            task_id="T1",
            files_changed=["a.py"],
            tests_added=5,
            lint_clean=True,
        )
        report = agent.full_review(
            "T1",
            task_result,
            include_governance=False,
            commit_messages=["feat: no coauthor"],
        )
        # Governance findings should NOT be included
        ga_findings = [f for f in report.code_findings if "GA-" in f.description]
        assert len(ga_findings) == 0

    def test_governance_critical_blocks_report(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        task_result = DevTaskResult(
            task_id="T1",
            files_changed=["a.py"],
            tests_added=5,
            lint_clean=True,
        )
        report = agent.full_review(
            "T1",
            task_result,
            include_governance=True,
            staged_files=[".env.production"],
        )
        assert report.verdict == "BLOCK"
