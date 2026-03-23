"""
BorisAdapter — NodeInterface implementatie voor BORIS (buurts-ecosysteem).

Read-only: leest BORIS data via LUMEN DevReport export of directe file-reads.
BORIS zelf wijzigt NIET — deze adapter consumeert alleen.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

import yaml

from devhub.contracts.node_interface import (
    NodeDocStatus,
    NodeHealth,
    NodeInterface,
    NodeReport,
    TestResult,
)
from datetime import UTC

logger = logging.getLogger(__name__)


class BorisAdapter(NodeInterface):
    """Adapter die BORIS-data vertaalt naar het vendor-free NodeInterface contract.

    Primaire databron: LUMEN DevReport JSON export.
    Fallback: directe file-reads (mkdocs.yml, pytest output).
    """

    NODE_ID = "boris-buurts"
    LUMEN_REPORT_PATH = ".claude/scratchpad/dev_report.json"

    def __init__(self, boris_path: str) -> None:
        self.boris_path = Path(boris_path)
        if not self.boris_path.exists():
            raise FileNotFoundError(f"BORIS path does not exist: {boris_path}")

    def get_report(self) -> NodeReport:
        """Genereer NodeReport — prioriteert LUMEN export, fallback naar directe reads."""
        lumen_data = self._read_lumen_report()
        if lumen_data:
            return self._parse_lumen_report(lumen_data)
        return self._build_report_from_externals()

    def get_health(self) -> NodeHealth:
        """Gezondheidsstatus via LUMEN export of directe check."""
        lumen_data = self._read_lumen_report()
        if lumen_data and "health" in lumen_data:
            h = lumen_data["health"]
            return NodeHealth(
                status=h.get("status", "DOWN"),
                components=h.get("components", {}),
                test_count=h.get("test_count", 0),
                test_pass_rate=h.get("test_pass_rate", 0.0),
                coverage_pct=h.get("coverage_pct", 0.0),
            )
        # Fallback: check of het pad bestaat
        return NodeHealth(
            status="UP" if self.boris_path.exists() else "DOWN",
            components={},
            test_count=0,
            test_pass_rate=0.0,
            coverage_pct=0.0,
        )

    def list_docs(self) -> list[str]:
        """Scan MkDocs navigatie voor documentatie-pagina's."""
        mkdocs_path = self.boris_path / "mkdocs.yml"
        if not mkdocs_path.exists():
            return []

        try:
            data = yaml.safe_load(mkdocs_path.read_text())
            pages: list[str] = []
            self._extract_nav_pages(data.get("nav", []), pages)
            return pages
        except Exception:
            logger.warning("BorisAdapter: mkdocs.yml parse failed", exc_info=True)
            return []

    def run_tests(self) -> TestResult:
        """Voer pytest uit op BORIS en parse het resultaat."""
        venv_python = self.boris_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            return TestResult(total=0, passed=0, failed=0, errors=1, duration_seconds=0.0)

        try:
            result = subprocess.run(
                [str(venv_python), "-m", "pytest", "--tb=no", "-q", "--no-header"],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=300,
            )
            return self._parse_pytest_output(result.stdout, result.returncode)
        except subprocess.TimeoutExpired:
            return TestResult(total=0, passed=0, failed=0, errors=1, duration_seconds=300.0)
        except Exception as e:
            logger.warning("BorisAdapter: pytest execution failed: %s", e)
            return TestResult(total=0, passed=0, failed=0, errors=1, duration_seconds=0.0)

    # --- Sprint & Governance reads ---

    def read_file(self, relative_path: str) -> str | None:
        """Lees een bestand uit de BORIS repo. Read-only."""
        full = self.boris_path / relative_path
        if not full.exists():
            return None
        try:
            return full.read_text()
        except OSError:
            logger.warning("BorisAdapter: cannot read %s", full)
            return None

    def read_claude_md(self) -> str | None:
        """Lees CLAUDE.md (hot cache: actieve sprint, constraints)."""
        return self.read_file("CLAUDE.md")

    def read_overdracht(self) -> str | None:
        """Lees OVERDRACHT.md (sessie-overdracht, recente beslissingen)."""
        return self.read_file(".claude/OVERDRACHT.md")

    def read_cowork_brief(self) -> str | None:
        """Lees COWORK_BRIEF.md (sprint queue, inbox status)."""
        return self.read_file("docs/planning/COWORK_BRIEF.md")

    def list_sprint_docs(self) -> list[str]:
        """Lijst actieve sprint-documenten."""
        sprint_dir = self.boris_path / "docs" / "planning" / "sprints"
        if not sprint_dir.exists():
            return []
        return [
            f.name for f in sprint_dir.glob("SPRINT_*.md")
        ]

    def read_sprint_doc(self, name: str) -> str | None:
        """Lees een specifiek sprint-document."""
        return self.read_file(f"docs/planning/sprints/{name}")

    def list_inbox(self) -> list[dict[str, str]]:
        """Lijst inbox-bestanden (SPRINT_INTAKE_*, IDEA_*)."""
        inbox_dir = self.boris_path / "docs" / "planning" / "inbox"
        if not inbox_dir.exists():
            return []
        items = []
        for f in sorted(inbox_dir.glob("*.md")):
            items.append({
                "name": f.name,
                "type": "intake" if "SPRINT_INTAKE" in f.name else "idea",
                "path": str(f.relative_to(self.boris_path)),
            })
        return items

    def read_goals(self) -> str | None:
        """Lees GOALS.md (top-goals en roadmap-context)."""
        return self.read_file("docs/planning/GOALS.md")

    def read_backlog(self) -> str | None:
        """Lees IDEEEN_BACKLOG.md."""
        return self.read_file("docs/planning/IDEEEN_BACKLOG.md")

    def run_lint(self) -> tuple[bool, str]:
        """Voer ruff check uit. Returns (clean, output)."""
        venv_python = self.boris_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            return False, "venv not found"
        try:
            result = subprocess.run(
                [str(venv_python), "-m", "ruff", "check", "."],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=60,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def run_herald_sync(self, reason: str) -> tuple[bool, str]:
        """Trigger HERALD sync (overdracht + cowork_brief update).

        Dit is de enige WRITE-operatie — triggert een BORIS-intern script.
        """
        script = self.boris_path / "scripts" / "herald_commit.sh"
        if not script.exists():
            return False, "herald_commit.sh not found"
        try:
            result = subprocess.run(
                ["bash", str(script), reason],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=60,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def run_curator_audit(self) -> tuple[bool, str]:
        """Voer curator_audit.py uit. Returns (clean, output)."""
        venv_python = self.boris_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            return False, "venv not found"
        try:
            result = subprocess.run(
                [str(venv_python), "scripts/curator_audit.py"],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=60,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def run_sprint_deps_check(self, sprint_doc: str) -> tuple[bool, str]:
        """Voer check_sprint_deps.py uit voor een sprint-doc."""
        venv_python = self.boris_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            return False, "venv not found"
        try:
            result = subprocess.run(
                [
                    str(venv_python),
                    "scripts/check_sprint_deps.py",
                    f"docs/planning/sprints/{sprint_doc}",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=30,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    # --- Private helpers ---

    def _read_lumen_report(self) -> dict | None:
        """Lees LUMEN DevReport JSON als beschikbaar."""
        report_path = self.boris_path / self.LUMEN_REPORT_PATH
        if not report_path.exists():
            return None
        try:
            return json.loads(report_path.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("BorisAdapter: LUMEN report unreadable at %s", report_path)
            return None

    def _parse_lumen_report(self, data: dict) -> NodeReport:
        """Vertaal LUMEN JSON naar NodeReport."""
        h = data.get("health", {})
        d = data.get("doc_status", {})

        health = NodeHealth(
            status=h.get("status", "DOWN"),
            components=h.get("components", {}),
            test_count=h.get("test_count", 0),
            test_pass_rate=h.get("test_pass_rate", 0.0),
            coverage_pct=h.get("coverage_pct", 0.0),
        )
        doc_status = NodeDocStatus(
            total_pages=d.get("total_pages", 0),
            stale_pages=d.get("stale_pages", 0),
            diataxis_coverage=d.get("diataxis_coverage", {}),
        )
        return NodeReport(
            node_id=data.get("node_id", self.NODE_ID),
            timestamp=data.get("timestamp", ""),
            health=health,
            doc_status=doc_status,
            observations=data.get("observations", []),
            safety_zones=data.get("safety_zones", {}),
        )

    def _build_report_from_externals(self) -> NodeReport:
        """Fallback: bouw NodeReport uit directe file-reads."""
        from datetime import datetime

        health = self.get_health()
        docs = self.list_docs()
        doc_status = NodeDocStatus(
            total_pages=len(docs),
            stale_pages=0,
            diataxis_coverage={},
        )
        return NodeReport(
            node_id=self.NODE_ID,
            timestamp=datetime.now(UTC).isoformat(),
            health=health,
            doc_status=doc_status,
        )

    def _extract_nav_pages(self, nav: list, pages: list[str]) -> None:
        """Recursief MkDocs nav-items extraheren."""
        for item in nav:
            if isinstance(item, str):
                pages.append(item)
            elif isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, str):
                        pages.append(value)
                    elif isinstance(value, list):
                        self._extract_nav_pages(value, pages)

    def _parse_pytest_output(self, stdout: str, returncode: int) -> TestResult:
        """Parse pytest -q output naar TestResult."""
        import re

        # Pattern: "2229 passed, 3 warnings in 45.23s"
        match = re.search(
            r"(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+error)?.*?in\s+([\d.]+)s",
            stdout,
        )
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2) or 0)
            errors = int(match.group(3) or 0)
            duration = float(match.group(4))
            total = passed + failed + errors
            return TestResult(
                total=total,
                passed=passed,
                failed=failed,
                errors=errors,
                duration_seconds=duration,
            )
        # Fallback
        return TestResult(
            total=0,
            passed=0,
            failed=1 if returncode != 0 else 0,
            errors=0,
            duration_seconds=0.0,
        )
