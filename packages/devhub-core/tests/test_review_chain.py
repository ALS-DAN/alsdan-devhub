"""E2E tests voor de review chain: QA Agent → QAFindings → QAReport → verdict.

Valideert de volledige keten die de reviewer agent orkestreert (Laag C, ADR-002).
Tests dekken PASS, NEEDS_WORK en BLOCK scenarios plus anti-patroon detectie.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from devhub_core.agents.qa_agent import (
    CODE_REVIEW_CHECKS,
    DOC_REVIEW_CHECKS,
    QAAgent,
)
from devhub_core.contracts.dev_contracts import (
    DevTaskResult,
    DocGenRequest,
    QAFinding,
    QAReport,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_reports(tmp_path: Path) -> Path:
    """Tijdelijke reports directory."""
    reports = tmp_path / "qa_reports"
    reports.mkdir()
    return reports


@pytest.fixture
def qa(tmp_reports: Path) -> QAAgent:
    """QA Agent met tijdelijke opslag."""
    return QAAgent(reports_path=tmp_reports)


@pytest.fixture
def clean_python_file(tmp_path: Path) -> Path:
    """Python bestand zonder issues."""
    f = tmp_path / "clean_module.py"
    f.write_text(
        '"""Clean module without issues."""\n'
        "\n"
        "import logging\n"
        "\n"
        "logger = logging.getLogger(__name__)\n"
        "\n"
        "\n"
        "def greet(name: str) -> str:\n"
        '    """Return greeting."""\n'
        '    return f"Hello, {name}"\n'
    )
    return f


@pytest.fixture
def dirty_python_file(tmp_path: Path) -> Path:
    """Python bestand met meerdere issues."""
    f = tmp_path / "dirty_module.py"
    f.write_text(
        "import os\n"
        "\n"
        'API_KEY = "sk-1234567890abcdefghijklmnop"\n'  # pragma: allowlist secret
        "\n"
        "\n"
        "def do_stuff():\n"
        '    print("debugging")\n'
        "    pass\n"
    )
    return f


@pytest.fixture
def clean_doc(tmp_path: Path) -> Path:
    """Markdown doc die alle DR-checks doorstaat."""
    f = tmp_path / "docs" / "guide.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(
        "# Guide\n"
        "\n"
        "> **Type:** how-to\n"
        "> **Doelgroep:** developers\n"
        "\n"
        "## Stappen\n"
        "\n"
        "1. Doe dit\n"
        "2. Doe dat\n"
    )
    return f


@pytest.fixture
def incomplete_doc(tmp_path: Path) -> Path:
    """Markdown doc met ontbrekende headers en TODO's."""
    f = tmp_path / "docs" / "incomplete.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(
        "# Incomplete\n"
        "\n"
        "TODO: schrijf inhoud\n"
        "<!-- placeholder -->\n"
        "<!-- placeholder -->\n"
        "<!-- placeholder -->\n"
    )
    return f


# ---------------------------------------------------------------------------
# Checklist coverage tests
# ---------------------------------------------------------------------------


class TestChecklistCompleteness:
    """Verifieer dat alle checklists correct gedefinieerd zijn."""

    def test_code_review_has_12_checks(self) -> None:
        assert len(CODE_REVIEW_CHECKS) == 12

    def test_doc_review_has_6_checks(self) -> None:
        assert len(DOC_REVIEW_CHECKS) == 6

    def test_code_checks_have_required_fields(self) -> None:
        for check in CODE_REVIEW_CHECKS:
            assert "id" in check
            assert "name" in check
            assert "desc" in check
            assert check["id"].startswith("CR-")

    def test_doc_checks_have_required_fields(self) -> None:
        for check in DOC_REVIEW_CHECKS:
            assert "id" in check
            assert "name" in check
            assert "desc" in check
            assert check["id"].startswith("DR-")


# ---------------------------------------------------------------------------
# PASS scenario
# ---------------------------------------------------------------------------


class TestPassScenario:
    """E2E: schone code + tests → PASS verdict."""

    def test_clean_code_produces_pass(self, qa: QAAgent, clean_python_file: Path) -> None:
        result = DevTaskResult(
            task_id="pass-test",
            files_changed=[str(clean_python_file)],
            tests_added=3,
            lint_clean=True,
        )
        report = qa.full_review(
            task_id="pass-test",
            task_result=result,
            project_root=clean_python_file.parent,
        )
        assert report.verdict == "PASS"
        assert report.is_clean

    def test_pass_report_has_no_errors(self, qa: QAAgent, clean_python_file: Path) -> None:
        result = DevTaskResult(
            task_id="pass-clean",
            files_changed=[str(clean_python_file)],
            tests_added=1,
            lint_clean=True,
        )
        report = qa.full_review(
            task_id="pass-clean",
            task_result=result,
            project_root=clean_python_file.parent,
        )
        severities = [f.severity for f in report.code_findings]
        assert "ERROR" not in severities
        assert "CRITICAL" not in severities


# ---------------------------------------------------------------------------
# NEEDS_WORK scenario
# ---------------------------------------------------------------------------


class TestNeedsWorkScenario:
    """E2E: lint errors → NEEDS_WORK verdict."""

    def test_lint_errors_produce_needs_work(self, qa: QAAgent) -> None:
        result = DevTaskResult(
            task_id="nw-test",
            files_changed=["some_file.py"],
            tests_added=1,
            lint_clean=False,
        )
        findings = qa.review_code(result)
        report = qa.produce_report("nw-test", code_findings=findings)
        assert report.verdict == "NEEDS_WORK"
        assert not report.is_clean

    def test_needs_work_contains_error_findings(self, qa: QAAgent) -> None:
        result = DevTaskResult(
            task_id="nw-detail",
            files_changed=["module.py"],
            lint_clean=False,
        )
        findings = qa.review_code(result)
        error_findings = [f for f in findings if f.severity == "ERROR"]
        assert len(error_findings) >= 1
        assert any("CR-02" in f.description for f in error_findings)


# ---------------------------------------------------------------------------
# BLOCK scenario
# ---------------------------------------------------------------------------


class TestBlockScenario:
    """E2E: hardcoded secret → BLOCK verdict."""

    def test_secret_produces_block(self, qa: QAAgent, dirty_python_file: Path) -> None:
        result = DevTaskResult(
            task_id="block-test",
            files_changed=[dirty_python_file.name],
            lint_clean=True,
        )
        report = qa.full_review(
            task_id="block-test",
            task_result=result,
            project_root=dirty_python_file.parent,
        )
        assert report.verdict == "BLOCK"

    def test_block_has_critical_findings(self, qa: QAAgent, dirty_python_file: Path) -> None:
        result = DevTaskResult(
            task_id="block-detail",
            files_changed=[dirty_python_file.name],
            lint_clean=True,
        )
        report = qa.full_review(
            task_id="block-detail",
            task_result=result,
            project_root=dirty_python_file.parent,
        )
        critical = [f for f in report.code_findings if f.severity == "CRITICAL"]
        assert len(critical) >= 1
        assert any("CR-03" in f.description for f in critical)

    def test_critical_overrides_verdict_to_block(self, qa: QAAgent) -> None:
        """Zelfs met alleen INFO + 1 CRITICAL → BLOCK."""
        findings = [
            QAFinding(severity="INFO", category="code", description="ok"),
            QAFinding(
                severity="CRITICAL",
                category="code",
                description="secret found",
            ),
        ]
        report = qa.produce_report("override-test", code_findings=findings)
        assert report.verdict == "BLOCK"


# ---------------------------------------------------------------------------
# Doc review chain
# ---------------------------------------------------------------------------


class TestDocReviewChain:
    """E2E: doc review → findings → report."""

    def test_clean_doc_passes(self, qa: QAAgent, clean_doc: Path) -> None:
        request = DocGenRequest(
            task_id="doc-pass",
            target_files=["guide.md"],
            diataxis_category="howto",
            audience="developers",
        )
        findings = qa.review_docs([request], docs_root=clean_doc.parent)
        report = qa.produce_report("doc-pass", doc_findings=findings)
        assert report.verdict == "PASS"

    def test_incomplete_doc_has_warnings(self, qa: QAAgent, incomplete_doc: Path) -> None:
        request = DocGenRequest(
            task_id="doc-warn",
            target_files=["incomplete.md"],
            diataxis_category="reference",
            audience="developers",
        )
        findings = qa.review_docs([request], docs_root=incomplete_doc.parent)
        warning_findings = [f for f in findings if f.severity == "WARNING"]
        assert len(warning_findings) >= 1

    def test_missing_doc_produces_error(self, qa: QAAgent, tmp_path: Path) -> None:
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        request = DocGenRequest(
            task_id="doc-missing",
            target_files=["nonexistent.md"],
            diataxis_category="tutorial",
            audience="beginners",
        )
        findings = qa.review_docs([request], docs_root=docs_root)
        assert any(f.severity == "ERROR" for f in findings)


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------


class TestReportPersistence:
    """Verifieer dat rapporten correct opgeslagen en geladen worden."""

    def test_report_saved_to_disk(self, qa: QAAgent, tmp_reports: Path) -> None:
        qa.produce_report(
            "persist-test",
            code_findings=[QAFinding(severity="INFO", category="code", description="ok")],
        )
        report_file = tmp_reports / "persist-test.json"
        assert report_file.exists()
        data = json.loads(report_file.read_text())
        assert data["task_id"] == "persist-test"
        assert data["verdict"] == "PASS"

    def test_report_roundtrip(self, qa: QAAgent) -> None:
        original = qa.produce_report(
            "roundtrip",
            code_findings=[
                QAFinding(
                    severity="ERROR",
                    category="code",
                    description="lint fail",
                    file="x.py",
                    line=10,
                )
            ],
        )
        loaded = qa.get_report("roundtrip")
        assert loaded is not None
        assert loaded.task_id == original.task_id
        assert loaded.verdict == original.verdict
        assert len(loaded.code_findings) == len(original.code_findings)
        assert loaded.code_findings[0].severity == "ERROR"

    def test_list_reports(self, qa: QAAgent) -> None:
        qa.produce_report("r1", code_findings=[])
        qa.produce_report("r2", code_findings=[])
        reports = qa.list_reports()
        assert "r1" in reports
        assert "r2" in reports

    def test_get_nonexistent_report_returns_none(self, qa: QAAgent) -> None:
        assert qa.get_report("does-not-exist") is None


# ---------------------------------------------------------------------------
# QAReport contract validation
# ---------------------------------------------------------------------------


class TestQAReportContract:
    """Verifieer QAReport dataclass constraints."""

    def test_report_is_frozen(self) -> None:
        report = QAReport(
            task_id="frozen-test",
            code_findings=[],
            doc_findings=[],
            verdict="PASS",
        )
        with pytest.raises(AttributeError):
            report.verdict = "BLOCK"  # type: ignore[misc]

    def test_total_findings_property(self) -> None:
        report = QAReport(
            task_id="total-test",
            code_findings=[
                QAFinding(severity="INFO", category="code", description="a"),
                QAFinding(severity="WARNING", category="code", description="b"),
            ],
            doc_findings=[
                QAFinding(severity="ERROR", category="docs", description="c"),
            ],
            verdict="NEEDS_WORK",
        )
        assert report.total_findings == 3

    def test_is_clean_with_no_findings(self) -> None:
        report = QAReport(
            task_id="clean-test",
            code_findings=[],
            doc_findings=[],
            verdict="PASS",
        )
        assert report.is_clean

    def test_is_not_clean_with_findings(self) -> None:
        report = QAReport(
            task_id="dirty-test",
            code_findings=[
                QAFinding(severity="ERROR", category="code", description="fail"),
            ],
            doc_findings=[],
            verdict="NEEDS_WORK",
        )
        assert not report.is_clean


# ---------------------------------------------------------------------------
# Full chain E2E: code + docs → single report
# ---------------------------------------------------------------------------


class TestFullChainE2E:
    """Integratietest: code review + doc review → gecombineerd rapport."""

    def test_full_review_combines_code_and_docs(
        self,
        qa: QAAgent,
        clean_python_file: Path,
        incomplete_doc: Path,
    ) -> None:
        task_result = DevTaskResult(
            task_id="full-chain",
            files_changed=[str(clean_python_file)],
            tests_added=2,
            lint_clean=True,
        )
        doc_request = DocGenRequest(
            task_id="full-chain",
            target_files=["incomplete.md"],
            diataxis_category="reference",
            audience="developers",
        )
        report = qa.full_review(
            task_id="full-chain",
            task_result=task_result,
            doc_requests=[doc_request],
            project_root=clean_python_file.parent,
            docs_root=incomplete_doc.parent,
        )
        assert report.task_id == "full-chain"
        assert report.total_findings >= 1
        assert len(report.doc_findings) >= 1

    def test_empty_files_changed_produces_info(self, qa: QAAgent) -> None:
        task_result = DevTaskResult(
            task_id="empty-chain",
            files_changed=[],
        )
        report = qa.full_review(
            task_id="empty-chain",
            task_result=task_result,
        )
        assert report.verdict == "PASS"
        info_findings = [f for f in report.code_findings if f.severity == "INFO"]
        assert len(info_findings) >= 1
