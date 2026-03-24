"""
QA Agent — Adversarial review van code EN documentatie.

Read-only: rapporteert issues, fixt ze niet. Produceert QAReports
met verdict (PASS/NEEDS_WORK/BLOCK). Geïnspireerd door CLAIR's
Guardian Layer (G1-G7) maar uitgebreid naar code + docs review.

Adversarial principe: zoekt actief naar tegenargumenten en edge cases.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from devhub_core.contracts.dev_contracts import (
    DevTaskResult,
    DocGenRequest,
    QAFinding,
    QAReport,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Review checklists
# ---------------------------------------------------------------------------

CODE_REVIEW_CHECKS: list[dict[str, str]] = [
    {"id": "CR-01", "name": "test_coverage", "desc": "Nieuwe code heeft tests"},
    {"id": "CR-02", "name": "lint_clean", "desc": "Geen lint errors"},
    {"id": "CR-03", "name": "no_hardcoded_secrets", "desc": "Geen hardcoded secrets"},
    {"id": "CR-04", "name": "error_handling", "desc": "Foutafhandeling aanwezig"},
    {"id": "CR-05", "name": "single_responsibility", "desc": "Eén verantwoordelijkheid"},
    {"id": "CR-06", "name": "naming_conventions", "desc": "Project-naamconventies"},
    {"id": "CR-07", "name": "no_dead_code", "desc": "Geen ongebruikte code"},
    {"id": "CR-08", "name": "type_safety", "desc": "Type hints op publieke functies"},
    {"id": "CR-09", "name": "no_print_statements", "desc": "Geen print() in productie"},
    {"id": "CR-10", "name": "frozen_contracts", "desc": "Frozen dataclasses"},
    {"id": "CR-11", "name": "docstrings", "desc": "Docstrings op publieke functies"},
    {"id": "CR-12", "name": "max_function_length", "desc": "Functies <50 regels"},
]

DOC_REVIEW_CHECKS: list[dict[str, str]] = [
    {"id": "DR-01", "name": "diataxis_category", "desc": "Diátaxis categorie"},
    {"id": "DR-02", "name": "audience_specified", "desc": "Doelgroep gespecificeerd"},
    {"id": "DR-03", "name": "no_stale_references", "desc": "Geen stale verwijzingen"},
    {"id": "DR-04", "name": "code_doc_sync", "desc": "Docs reflecteren code"},
    {"id": "DR-05", "name": "completeness", "desc": "Geen lege secties/TODO's"},
    {"id": "DR-06", "name": "readable_language", "desc": "Begrijpelijk voor doelgroep"},
]


class QAAgent:
    """Adversarial QA Agent — reviewt code en documentatie.

    Read-only: rapporteert bevindingen, fixt niets.
    Produceert QAReports met PASS/NEEDS_WORK/BLOCK verdict.
    """

    def __init__(self, reports_path: Path | None = None) -> None:
        self._reports_path = reports_path or Path(".claude/scratchpad/tasks/qa_reports")
        self._reports_path.mkdir(parents=True, exist_ok=True)

    def review_code(
        self,
        task_result: DevTaskResult,
        project_root: Path | None = None,
    ) -> list[QAFinding]:
        """Review code-wijzigingen op basis van de code review checklist.

        Scant gewijzigde bestanden op veelvoorkomende issues.
        """
        findings: list[QAFinding] = []
        root = project_root or Path(".")

        if not task_result.files_changed:
            findings.append(QAFinding(
                severity="INFO",
                category="code",
                description="Geen bestanden gewijzigd — niets te reviewen",
            ))
            return findings

        # CR-01: Test coverage
        if task_result.tests_added == 0:
            findings.append(QAFinding(
                severity="WARNING",
                category="code",
                description="CR-01: Geen nieuwe tests toegevoegd bij code-wijzigingen",
            ))

        # CR-02: Lint clean
        if not task_result.lint_clean:
            findings.append(QAFinding(
                severity="ERROR",
                category="code",
                description="CR-02: Lint errors aanwezig",
            ))

        # Per-file checks
        for file_path in task_result.files_changed:
            full_path = root / file_path
            if not full_path.exists() or not full_path.suffix == ".py":
                continue

            try:
                content = full_path.read_text()
            except OSError:
                continue

            file_findings = self._check_python_file(file_path, content)
            findings.extend(file_findings)

        return findings

    def review_docs(
        self,
        doc_requests: list[DocGenRequest],
        docs_root: Path | None = None,
    ) -> list[QAFinding]:
        """Review documentatie op Diátaxis compliance en completeness."""
        findings: list[QAFinding] = []
        root = docs_root or Path("docs")

        for request in doc_requests:
            for target in request.target_files:
                target_path = root / target if not Path(target).is_absolute() else Path(target)
                if not target_path.exists():
                    findings.append(QAFinding(
                        severity="ERROR",
                        category="docs",
                        description=f"DR-04: Verwacht document ontbreekt: {target}",
                        file=str(target),
                    ))
                    continue

                try:
                    content = target_path.read_text()
                except OSError:
                    continue

                doc_findings = self._check_doc_file(str(target), content, request)
                findings.extend(doc_findings)

        return findings

    def produce_report(
        self,
        task_id: str,
        code_findings: list[QAFinding] | None = None,
        doc_findings: list[QAFinding] | None = None,
    ) -> QAReport:
        """Produceer een QAReport en sla op in scratchpad.

        Verdict wordt automatisch bepaald:
        - BLOCK: als er CRITICAL findings zijn
        - NEEDS_WORK: als er ERROR findings zijn
        - PASS: als er alleen INFO/WARNING findings zijn
        """
        code = code_findings or []
        docs = doc_findings or []
        all_findings = code + docs

        verdict = self._determine_verdict(all_findings)

        report = QAReport(
            task_id=task_id,
            code_findings=code,
            doc_findings=docs,
            verdict=verdict,
        )

        # Schrijf naar scratchpad
        self._save_report(report)

        logger.info(
            "QA Agent: %s — %s (%d code, %d doc findings)",
            task_id,
            verdict,
            len(code),
            len(docs),
        )
        return report

    def full_review(
        self,
        task_id: str,
        task_result: DevTaskResult,
        doc_requests: list[DocGenRequest] | None = None,
        project_root: Path | None = None,
        docs_root: Path | None = None,
    ) -> QAReport:
        """Voer een volledige review uit: code + docs → QAReport.

        Dit is de hoofdmethode die de DevOrchestrator aanroept.
        """
        code_findings = self.review_code(task_result, project_root)
        doc_findings = (
            self.review_docs(doc_requests, docs_root)
            if doc_requests
            else []
        )

        return self.produce_report(task_id, code_findings, doc_findings)

    def get_report(self, task_id: str) -> QAReport | None:
        """Lees een eerder opgeslagen QAReport."""
        report_file = self._reports_path / f"{task_id}.json"
        if not report_file.exists():
            return None
        try:
            data = json.loads(report_file.read_text())
            code = [QAFinding(**f) for f in data.get("code_findings", [])]
            docs = [QAFinding(**f) for f in data.get("doc_findings", [])]
            return QAReport(
                task_id=data["task_id"],
                code_findings=code,
                doc_findings=docs,
                verdict=data.get("verdict", "PASS"),
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("QA Agent: rapport %s corrupt", task_id)
            return None

    def list_reports(self) -> list[str]:
        """Lijst alle opgeslagen QAReport task_ids."""
        return [
            f.stem for f in self._reports_path.glob("*.json")
        ]

    # --- Privé helpers ---

    def _check_python_file(self, file_path: str, content: str) -> list[QAFinding]:
        """Check een Python bestand op code review criteria."""
        findings: list[QAFinding] = []
        lines = content.split("\n")

        # CR-03: Hardcoded secrets
        secret_patterns = [
            r"(?i)(password|secret|token|api_key)\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)(sk-[a-zA-Z0-9]{20,})",
        ]
        for i, line in enumerate(lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line):
                    findings.append(QAFinding(
                        severity="CRITICAL",
                        category="code",
                        description="CR-03: Mogelijke hardcoded secret gedetecteerd",
                        file=file_path,
                        line=i,
                    ))

        # CR-09: Print statements in productie-code
        if "tests/" not in file_path and "test_" not in file_path:
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("print(") and not stripped.startswith("#"):
                    findings.append(QAFinding(
                        severity="WARNING",
                        category="code",
                        description="CR-09: print() in productie-code — gebruik logging",
                        file=file_path,
                        line=i,
                    ))

        # CR-12: Functie-lengte
        func_start: int | None = None
        func_name: str = ""
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("def "):
                if func_start and (i - func_start) > 50:
                    findings.append(QAFinding(
                        severity="WARNING",
                        category="code",
                        description=(
                            f"CR-12: Functie '{func_name}' is "
                            f"{i - func_start} regels (max 50)"
                        ),
                        file=file_path,
                        line=func_start,
                    ))
                func_start = i
                match = re.match(r"\s*def\s+(\w+)", line)
                func_name = match.group(1) if match else "unknown"

        return findings

    def _check_doc_file(
        self,
        file_path: str,
        content: str,
        request: DocGenRequest,
    ) -> list[QAFinding]:
        """Check een documentatie-bestand op doc review criteria."""
        findings: list[QAFinding] = []

        # DR-01: Diátaxis categorie
        if "> **Type:**" not in content:
            findings.append(QAFinding(
                severity="WARNING",
                category="docs",
                description="DR-01: Geen Diátaxis type header gevonden",
                file=file_path,
            ))

        # DR-02: Audience
        if "> **Doelgroep:**" not in content and request.audience not in content:
            findings.append(QAFinding(
                severity="INFO",
                category="docs",
                description="DR-02: Doelgroep niet gespecificeerd in document",
                file=file_path,
            ))

        # DR-05: Completeness — check voor lege secties
        if "<!-- " in content:
            placeholder_count = content.count("<!-- ")
            if placeholder_count > 2:
                findings.append(QAFinding(
                    severity="WARNING",
                    category="docs",
                    description=(
                        f"DR-05: {placeholder_count} placeholder-comments "
                        "gevonden — document is incompleet"
                    ),
                    file=file_path,
                ))

        # DR-05: TODO's
        if "TODO" in content or "FIXME" in content:
            findings.append(QAFinding(
                severity="WARNING",
                category="docs",
                description="DR-05: TODO/FIXME gevonden in document",
                file=file_path,
            ))

        return findings

    def _determine_verdict(
        self, findings: list[QAFinding]
    ) -> Literal["PASS", "NEEDS_WORK", "BLOCK"]:
        """Bepaal verdict op basis van bevindingen."""
        severities = [f.severity for f in findings]

        if "CRITICAL" in severities:
            return "BLOCK"
        if "ERROR" in severities:
            return "NEEDS_WORK"
        return "PASS"

    def _save_report(self, report: QAReport) -> None:
        """Sla QAReport op als JSON."""
        report_file = self._reports_path / f"{report.task_id}.json"
        data = asdict(report)
        report_file.write_text(json.dumps(data, indent=2))
