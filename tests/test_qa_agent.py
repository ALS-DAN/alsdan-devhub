"""Tests voor QA Agent — adversarial review."""


from devhub.agents.qa_agent import QAAgent, CODE_REVIEW_CHECKS, DOC_REVIEW_CHECKS
from devhub.contracts.dev_contracts import DevTaskResult, DocGenRequest, QAFinding


class TestQAAgentCodeReview:
    """Code review tests."""

    def test_no_files_changed(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        result = DevTaskResult(task_id="T1", files_changed=[])
        findings = agent.review_code(result)
        assert len(findings) == 1
        assert findings[0].severity == "INFO"

    def test_no_tests_added_warning(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        result = DevTaskResult(
            task_id="T1",
            files_changed=["devhub/agents/new_feature.py"],
            tests_added=0,
        )
        findings = agent.review_code(result)
        has_cr01 = any("CR-01" in f.description for f in findings)
        assert has_cr01

    def test_lint_not_clean_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        result = DevTaskResult(
            task_id="T1",
            files_changed=["a.py"],
            lint_clean=False,
        )
        findings = agent.review_code(result)
        has_cr02 = any("CR-02" in f.description for f in findings)
        assert has_cr02

    def test_detects_hardcoded_secret(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        # Create a file with a hardcoded secret
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        bad_file = code_dir / "bad.py"
        bad_file.write_text('API_KEY = "sk-1234567890abcdefghijklmno"\n')

        result = DevTaskResult(task_id="T1", files_changed=["src/bad.py"])
        findings = agent.review_code(result, project_root=tmp_path)

        has_cr03 = any("CR-03" in f.description for f in findings)
        assert has_cr03
        critical = [f for f in findings if f.severity == "CRITICAL"]
        assert len(critical) >= 1

    def test_detects_print_statement(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        (code_dir / "printer.py").write_text('def foo():\n    print("debug")\n')

        result = DevTaskResult(task_id="T1", files_changed=["src/printer.py"])
        findings = agent.review_code(result, project_root=tmp_path)

        has_cr09 = any("CR-09" in f.description for f in findings)
        assert has_cr09

    def test_ignores_print_in_tests(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_thing.py").write_text('def test_x():\n    print("ok")\n')

        result = DevTaskResult(task_id="T1", files_changed=["tests/test_thing.py"])
        findings = agent.review_code(result, project_root=tmp_path)

        has_cr09 = any("CR-09" in f.description for f in findings)
        assert not has_cr09

    def test_detects_long_function(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        long_func = "def long_function():\n" + "    x = 1\n" * 55 + "def short():\n    pass\n"
        (code_dir / "long.py").write_text(long_func)

        result = DevTaskResult(task_id="T1", files_changed=["src/long.py"])
        findings = agent.review_code(result, project_root=tmp_path)

        has_cr12 = any("CR-12" in f.description for f in findings)
        assert has_cr12

    def test_clean_code_no_findings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        (code_dir / "clean.py").write_text(
            '"""Clean module."""\n\nimport logging\n\nlogger = logging.getLogger(__name__)\n\n'
            'def clean_function() -> str:\n    """Do something clean."""\n    return "ok"\n'
        )

        result = DevTaskResult(
            task_id="T1",
            files_changed=["src/clean.py"],
            tests_added=3,
            lint_clean=True,
        )
        findings = agent.review_code(result, project_root=tmp_path)
        # Should only have non-critical findings at most
        critical = [f for f in findings if f.severity in ("CRITICAL", "ERROR")]
        assert len(critical) == 0


class TestQAAgentDocReview:
    """Doc review tests."""

    def test_missing_doc_error(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        request = DocGenRequest(
            task_id="T1",
            target_files=["nonexistent.md"],
            diataxis_category="reference",
            audience="developer",
        )
        findings = agent.review_docs([request], docs_root=tmp_path / "docs")
        assert len(findings) >= 1
        assert findings[0].severity == "ERROR"

    def test_missing_diataxis_header(self, tmp_path):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "no_header.md").write_text("# Just a title\n\nSome content.\n")

        agent = QAAgent(reports_path=tmp_path / "reports")
        request = DocGenRequest(
            task_id="T1",
            target_files=["no_header.md"],
            diataxis_category="reference",
            audience="developer",
        )
        findings = agent.review_docs([request], docs_root=docs_root)
        has_dr01 = any("DR-01" in f.description for f in findings)
        assert has_dr01

    def test_doc_with_todos(self, tmp_path):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "todo_doc.md").write_text(
            "# Doc\n\n> **Type:** Reference\n\nTODO: fill this in\n"
        )

        agent = QAAgent(reports_path=tmp_path / "reports")
        request = DocGenRequest(
            task_id="T1",
            target_files=["todo_doc.md"],
            diataxis_category="reference",
            audience="developer",
        )
        findings = agent.review_docs([request], docs_root=docs_root)
        has_dr05 = any("DR-05" in f.description for f in findings)
        assert has_dr05

    def test_complete_doc_passes(self, tmp_path):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "good.md").write_text(
            "# Good Doc\n\n> **Type:** Reference\n> **Doelgroep:** developer\n\n"
            "Real content here without placeholders.\n"
        )

        agent = QAAgent(reports_path=tmp_path / "reports")
        request = DocGenRequest(
            task_id="T1",
            target_files=["good.md"],
            diataxis_category="reference",
            audience="developer",
        )
        findings = agent.review_docs([request], docs_root=docs_root)
        # May have INFO findings but no ERROR/CRITICAL
        serious = [f for f in findings if f.severity in ("ERROR", "CRITICAL")]
        assert len(serious) == 0


class TestQAAgentReport:
    """Report production tests."""

    def test_produce_clean_report(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        report = agent.produce_report("T1")
        assert report.verdict == "PASS"
        assert report.is_clean

    def test_produce_report_with_warnings(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = [QAFinding(severity="WARNING", category="code", description="Minor issue")]
        report = agent.produce_report("T1", code_findings=findings)
        assert report.verdict == "PASS"  # Warnings don't block

    def test_produce_report_with_errors(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = [QAFinding(severity="ERROR", category="docs", description="Missing doc")]
        report = agent.produce_report("T1", doc_findings=findings)
        assert report.verdict == "NEEDS_WORK"

    def test_produce_report_with_critical(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        findings = [QAFinding(severity="CRITICAL", category="code", description="Secret!")]
        report = agent.produce_report("T1", code_findings=findings)
        assert report.verdict == "BLOCK"

    def test_report_saved_to_scratchpad(self, tmp_path):
        reports_dir = tmp_path / "reports"
        agent = QAAgent(reports_path=reports_dir)
        agent.produce_report("T1")
        assert (reports_dir / "T1.json").exists()

    def test_get_saved_report(self, tmp_path):
        reports_dir = tmp_path / "reports"
        agent = QAAgent(reports_path=reports_dir)
        agent.produce_report("T1", code_findings=[
            QAFinding(severity="WARNING", category="code", description="Test finding")
        ])

        loaded = agent.get_report("T1")
        assert loaded is not None
        assert loaded.task_id == "T1"
        assert len(loaded.code_findings) == 1

    def test_get_nonexistent_report(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        assert agent.get_report("NONEXISTENT") is None

    def test_list_reports(self, tmp_path):
        reports_dir = tmp_path / "reports"
        agent = QAAgent(reports_path=reports_dir)
        agent.produce_report("T1")
        agent.produce_report("T2")
        reports = agent.list_reports()
        assert set(reports) == {"T1", "T2"}


class TestQAAgentFullReview:
    """End-to-end review tests."""

    def test_full_review_code_only(self, tmp_path):
        agent = QAAgent(reports_path=tmp_path / "reports")
        task_result = DevTaskResult(
            task_id="T1",
            files_changed=["a.py"],
            tests_added=5,
            lint_clean=True,
        )
        report = agent.full_review("T1", task_result)
        assert report.task_id == "T1"
        assert isinstance(report.verdict, str)

    def test_full_review_code_and_docs(self, tmp_path):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "ref.md").write_text(
            "# Ref\n\n> **Type:** Reference\n> **Doelgroep:** dev\n\nContent.\n"
        )

        agent = QAAgent(reports_path=tmp_path / "reports")
        task_result = DevTaskResult(
            task_id="T1",
            files_changed=["a.py"],
            tests_added=2,
            lint_clean=True,
        )
        doc_requests = [DocGenRequest(
            task_id="T1",
            target_files=["ref.md"],
            diataxis_category="reference",
            audience="dev",
        )]

        report = agent.full_review(
            "T1", task_result, doc_requests=doc_requests, docs_root=docs_root
        )
        assert report.task_id == "T1"


class TestQAAgentChecklist:
    """Checklist completeness tests."""

    def test_code_checklist_has_12_items(self):
        assert len(CODE_REVIEW_CHECKS) == 12

    def test_doc_checklist_has_6_items(self):
        assert len(DOC_REVIEW_CHECKS) == 6

    def test_all_checks_have_required_fields(self):
        for check in CODE_REVIEW_CHECKS + DOC_REVIEW_CHECKS:
            assert "id" in check
            assert "name" in check
            assert "desc" in check
