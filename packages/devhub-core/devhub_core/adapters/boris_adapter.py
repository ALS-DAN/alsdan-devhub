"""
BorisAdapter — NodeInterface implementatie voor BORIS (buurts-ecosysteem).

Read-only: leest BORIS data via LUMEN DevReport export of directe file-reads.
BORIS zelf wijzigt NIET — deze adapter consumeert alleen.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path

import yaml

from devhub_core.contracts.node_interface import (
    CoachingSignal,
    DeveloperPhase,
    DeveloperProfile,
    FullHealthReport,
    HealthCheckResult,
    HealthFinding,
    HealthStatus,
    NodeDocStatus,
    NodeHealth,
    NodeInterface,
    NodeReport,
    ReviewContext,
    Severity,
    TestResult,
)
from datetime import UTC, datetime

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
        return [f.name for f in sprint_dir.glob("SPRINT_*.md")]

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
            items.append(
                {
                    "name": f.name,
                    "type": "intake" if "SPRINT_INTAKE" in f.name else "idea",
                    "path": str(f.relative_to(self.boris_path)),
                }
            )
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

    # --- Review (F7) ---

    def get_git_diff(self, staged: bool = False) -> str:
        """Haal git diff op. staged=True voor --staged, False voor unstaged."""
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=30,
            )
            return result.stdout
        except Exception as e:
            logger.warning("BorisAdapter: git diff failed: %s", e)
            return ""

    def get_changed_files(self, staged: bool = False) -> list[str]:
        """Lijst gewijzigde bestanden (relatief aan repo root)."""
        cmd = ["git", "diff", "--name-only"]
        if staged:
            cmd.append("--staged")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=15,
            )
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except Exception:
            return []

    def scan_anti_patterns(self, files: list[str] | None = None) -> list[dict]:
        """Scan op BORIS-specifieke anti-patronen.

        Returns lijst van gevonden anti-patronen met bestand, regel en beschrijving.
        Als files=None, scant alle gewijzigde bestanden.
        """
        import re

        if files is None:
            files = self.get_changed_files() + self.get_changed_files(staged=True)
            files = list(set(files))

        if not files:
            return []

        patterns: list[tuple[str, str, str]] = [
            # (regex, severity, description)
            (
                r"ChromaDB|chromadb\.Client\(",
                "ERROR",
                "Direct ChromaDB aanroep buiten ZonedVectorStore",
            ),
            (
                r'zone\s*[=!]=\s*["\']RED["\']',
                "CRITICAL",
                "RED-zone logica buiten safety/policy.py",
            ),
            (r"EphemeralClient\((?!.*uuid)", "WARNING", "EphemeralClient zonder UUID-suffix"),
            (
                r'(?i)(password|secret|api_key|token)\s*=\s*["\'][^"\']{8,}["\']',
                "CRITICAL",
                "Hardcoded secret/credential",
            ),
            (r"^print\(", "WARNING", "print() in productie-code — gebruik logging"),
        ]

        findings: list[dict] = []
        for file_rel in files:
            if not file_rel.endswith(".py"):
                continue
            full = self.boris_path / file_rel
            if not full.exists():
                continue

            # Skip test files for some patterns
            is_test = "test_" in file_rel or "tests/" in file_rel

            try:
                content = full.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    for pattern, severity, desc in patterns:
                        # Skip print check in tests
                        if is_test and "print()" in desc:
                            continue
                        # Skip zone check if in safety/policy.py
                        if "safety/policy" in file_rel and "RED-zone" in desc:
                            continue
                        if re.search(pattern, line):
                            findings.append(
                                {
                                    "file": file_rel,
                                    "line": i,
                                    "severity": severity,
                                    "description": desc,
                                    "match": line.strip()[:100],
                                }
                            )
            except OSError:
                continue

        return findings

    def get_review_context(self) -> ReviewContext:
        """Verzamel alle review-context in één call.

        Returns ReviewContext met commits, staged files, diff, governance files.
        """
        staged = self.get_changed_files(staged=True)
        unstaged = self.get_changed_files(staged=False)
        all_files = list(set(staged + unstaged))

        # Recent commits
        commits: list[str] = []
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--format=%s"],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=10,
            )
            commits = [c.strip() for c in result.stdout.strip().split("\n") if c.strip()]
        except Exception:
            pass

        # Governance files in changed set
        governance_patterns = ["CLAUDE.md", "DEV_CONSTITUTION", "settings.json", ".claude/"]
        gov_files = [f for f in all_files if any(p in f for p in governance_patterns)]

        diff = self.get_git_diff(staged=True)
        if not diff:
            diff = self.get_git_diff(staged=False)

        return ReviewContext(
            recent_commits=tuple(commits),
            staged_files=tuple(staged),
            diff_content=diff,
            governance_files=tuple(gov_files),
        )

    # --- Sprint Prep (F6) ---

    def read_health_status(self) -> str | None:
        """Lees HEALTH_STATUS.md (compact health overzicht, <25 regels)."""
        return self.read_file("HEALTH_STATUS.md")

    def read_decisions(self) -> str | None:
        """Lees decisions.md (open/gesloten besluiten)."""
        # Probeer meerdere locaties
        for path in [
            "docs/decisions.md",
            "memory/context/decisions.md",
            "docs/planning/decisions.md",
        ]:
            content = self.read_file(path)
            if content:
                return content
        return None

    def list_adr_files(self) -> list[str]:
        """Lijst ADR bestanden in docs/adr/ of docs/architecture/."""
        for adr_dir_name in ["docs/adr", "docs/architecture"]:
            adr_dir = self.boris_path / adr_dir_name
            if adr_dir.is_dir():
                return sorted([f.name for f in adr_dir.glob("ADR-*.md")])
        return []

    def read_adr(self, name: str) -> str | None:
        """Lees een specifiek ADR document."""
        for adr_dir_name in ["docs/adr", "docs/architecture"]:
            content = self.read_file(f"{adr_dir_name}/{name}")
            if content:
                return content
        return None

    def list_health_reports(self) -> list[str]:
        """Lijst health rapporten (gesorteerd, nieuwste eerst)."""
        health_dir = self.boris_path / "docs" / "health"
        if not health_dir.is_dir():
            return []
        return sorted(
            [f.name for f in health_dir.glob("health-report-*.md")],
            reverse=True,
        )

    def read_health_report(self, name: str) -> str | None:
        """Lees een specifiek health rapport."""
        return self.read_file(f"docs/health/{name}")

    def get_sprint_prep_context(self) -> dict:
        """Verzamel alle context die sprint-prep nodig heeft in één call.

        Returns een dict met alle bronnen, zodat de skill niet 10 losse calls hoeft te doen.
        """
        profile = self.get_developer_profile(days=30)
        health_reports = self.list_health_reports()

        return {
            "health_status": self.read_health_status(),
            "health_report_latest": (
                self.read_health_report(health_reports[0]) if health_reports else None
            ),
            "developer_profile": {
                "phase": profile.current_phase.value,
                "signal": profile.coaching_signal.value,
                "streak_days": profile.streak_days,
                "blockers_open": profile.blockers_open,
                "tests_delta": profile.tests_delta_total,
            },
            "claude_md": self.read_claude_md(),
            "overdracht": self.read_overdracht(),
            "decisions": self.read_decisions(),
            "inbox": self.list_inbox(),
            "sprint_docs": self.list_sprint_docs(),
            "adr_files": self.list_adr_files(),
        }

    # --- Mentor / Developer Progress (F5) ---

    PROGRESS_DB_PATH = "data/developer_progress.db"

    def get_developer_profile(self, days: int = 30) -> DeveloperProfile:
        """Lees developer progress uit BORIS's DeveloperProgressStore (SQLite).

        Returns een DeveloperProfile met fase, streak, blockers, etc.
        Als de DB niet bestaat of leeg is, returns een conservatief ORIËNTEREN profiel.
        """
        import sqlite3
        from datetime import timedelta

        db_path = self.boris_path / self.PROGRESS_DB_PATH
        if not db_path.exists():
            return DeveloperProfile(
                current_phase=DeveloperPhase.ORIENTEREN,
                streak_days=0,
                blockers_open=0,
                tests_delta_total=0,
                recent_entry_count=0,
                coaching_signal=CoachingSignal.STAGNATION,
            )

        try:
            conn = sqlite3.connect(str(db_path))
            cutoff = (datetime.now(UTC) - timedelta(days=days)).date().isoformat()

            rows = conn.execute(
                "SELECT datum, fase, blocker, tests_delta FROM developer_entries "
                "WHERE datum >= ? ORDER BY datum DESC",
                (cutoff,),
            ).fetchall()

            if not rows:
                conn.close()
                return DeveloperProfile(
                    current_phase=DeveloperPhase.ORIENTEREN,
                    streak_days=0,
                    blockers_open=0,
                    tests_delta_total=0,
                    recent_entry_count=0,
                    coaching_signal=CoachingSignal.STAGNATION,
                )

            # Fase-detectie (conservatief: bij gelijkspel wint ORIËNTEREN)
            from collections import Counter

            fase_counts = Counter(r[1] for r in rows)
            priority = [DeveloperPhase.ORIENTEREN, DeveloperPhase.BOUWEN, DeveloperPhase.BEHEERSEN]
            max_count = max(fase_counts.values())
            current_phase = DeveloperPhase.ORIENTEREN
            for phase in priority:
                if fase_counts.get(phase.value, 0) == max_count:
                    current_phase = phase
                    break

            # Streak
            unique_dates = sorted({r[0] for r in rows}, reverse=True)
            streak = 0
            today = datetime.now(UTC).date()
            for i, d in enumerate(unique_dates):
                expected = (today - timedelta(days=i)).isoformat()
                if d == expected:
                    streak += 1
                else:
                    break

            # Blockers
            blockers_open = sum(1 for r in rows if r[2].strip().lower() != "geen")

            # Tests delta
            tests_delta = sum(r[3] for r in rows)

            # Last entry date
            last_entry = rows[0][0] if rows else None

            # Coaching signal
            days_since_last = 0
            if last_entry:
                last_date = datetime.fromisoformat(last_entry).date()
                days_since_last = (today - last_date).days

            signal = self._compute_coaching_signal(
                days_since_last=days_since_last,
                blockers_open=blockers_open,
                tests_delta=tests_delta,
                current_phase=current_phase,
                entry_count=len(rows),
                days_window=days,
            )

            conn.close()
            return DeveloperProfile(
                current_phase=current_phase,
                streak_days=streak,
                blockers_open=blockers_open,
                tests_delta_total=tests_delta,
                recent_entry_count=len(rows),
                last_entry_date=last_entry,
                coaching_signal=signal,
            )

        except Exception as e:
            logger.warning("BorisAdapter: developer_progress.db read failed: %s", e)
            return DeveloperProfile(
                current_phase=DeveloperPhase.ORIENTEREN,
                streak_days=0,
                blockers_open=0,
                tests_delta_total=0,
                recent_entry_count=0,
                coaching_signal=CoachingSignal.STAGNATION,
            )

    def get_recent_progress_entries(self, days: int = 7) -> list[dict]:
        """Lees recente developer progress entries als raw dicts.

        Handig voor de mentor-skill om concrete observaties te doen.
        """
        import sqlite3
        from datetime import timedelta

        db_path = self.boris_path / self.PROGRESS_DB_PATH
        if not db_path.exists():
            return []

        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cutoff = (datetime.now(UTC) - timedelta(days=days)).date().isoformat()
            rows = conn.execute(
                "SELECT * FROM developer_entries WHERE datum >= ? ORDER BY datum DESC, id DESC",
                (cutoff,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning("BorisAdapter: recent progress read failed: %s", e)
            return []

    @staticmethod
    def _compute_coaching_signal(
        days_since_last: int,
        blockers_open: int,
        tests_delta: int,
        current_phase: DeveloperPhase,
        entry_count: int,
        days_window: int,
    ) -> CoachingSignal:
        """Bereken coaching-signaal op basis van developer metrics.

        Regels (uit MENTOR.DEV SKILL.md):
        - STAGNATIE: geen entries >5 dagen, of ORIËNTEREN >14 dagen zonder beweging
        - AANDACHT: blocker >2 dagen open, of tests dalen
        - GROEN: actief gebouwd, tests groeien, geen blockers
        """
        # Stagnatie checks
        if days_since_last > 5:
            return CoachingSignal.STAGNATION
        if current_phase == DeveloperPhase.ORIENTEREN and days_window >= 14 and entry_count >= 14:
            return CoachingSignal.STAGNATION

        # Aandacht checks
        if blockers_open > 0:
            return CoachingSignal.ATTENTION
        if tests_delta < 0:
            return CoachingSignal.ATTENTION

        return CoachingSignal.GREEN

    # --- Health diagnostics (F4) ---

    def run_pip_audit(self) -> tuple[bool, str]:
        """Run pip-audit voor dependency security scan. Returns (clean, output)."""
        venv_python = self.boris_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            return False, "venv not found"
        try:
            result = subprocess.run(
                [str(venv_python), "-m", "pip_audit"],
                capture_output=True,
                text=True,
                cwd=str(self.boris_path),
                timeout=120,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except FileNotFoundError:
            return False, "pip-audit not installed"
        except subprocess.TimeoutExpired:
            return False, "pip-audit timed out (120s)"
        except Exception as e:
            return False, str(e)

    def get_version_info(self) -> dict[str, str | None]:
        """Lees versie-informatie uit bekende locaties.

        Returns dict met keys: main_py, pyproject, overdracht.
        Waarde is de gevonden versiestring of None.
        """
        versions: dict[str, str | None] = {
            "main_py": None,
            "pyproject": None,
            "overdracht": None,
        }
        import re

        # main.py: version="X.Y.Z"
        main_py = self.read_file("main.py")
        if main_py:
            m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', main_py)
            if m:
                versions["main_py"] = m.group(1)

        # pyproject.toml: version = "X.Y.Z"
        pyproject = self.read_file("pyproject.toml")
        if pyproject:
            m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', pyproject, re.MULTILINE)
            if m:
                versions["pyproject"] = m.group(1)

        # OVERDRACHT.md: versie in de tekst
        overdracht = self.read_overdracht()
        if overdracht:
            m = re.search(r"[Vv]ersie[:\s]+(\d+\.\d+(?:\.\d+)?)", overdracht)
            if m:
                versions["overdracht"] = m.group(1)

        return versions

    def get_architecture_scan(self) -> dict:
        """Scan de structurele integriteit van het project.

        Returns dict met:
        - modules: list van verwachte directories en of ze bestaan
        - config_files: list van verwachte configs en of ze bestaan
        - agent_count: aantal agents in agents/ directory
        - mcp_tool_count: geteld aantal MCP tool-functies
        - ci_present: of .github/workflows/ci.yml bestaat
        """
        expected_modules = [
            "agents",
            "rag",
            "safety",
            "mcp_server",
            "middleware",
            "ingest",
            "sharepoint",
            "weaviate_store",
        ]
        expected_configs = [
            ".mcp.json",
            "pyproject.toml",
            "docker-compose.yml",
            "mkdocs.yml",
        ]

        modules = {}
        for mod in expected_modules:
            modules[mod] = (self.boris_path / mod).is_dir()

        configs = {}
        for cfg in expected_configs:
            configs[cfg] = (self.boris_path / cfg).is_file()

        # Count agents
        agents_dir = self.boris_path / "agents"
        agent_count = 0
        if agents_dir.is_dir():
            agent_count = len(
                [
                    f
                    for f in agents_dir.iterdir()
                    if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"
                ]
            )

        # Count MCP tools (functions decorated with @tool or registered)
        mcp_tool_count = 0
        server_py = self.boris_path / "mcp_server" / "server.py"
        if server_py.is_file():
            import re

            content = server_py.read_text()
            mcp_tool_count = len(re.findall(r"@(?:mcp\.)?tool", content))

        # CI pipeline
        ci_present = (self.boris_path / ".github" / "workflows" / "ci.yml").is_file()

        return {
            "modules": modules,
            "config_files": configs,
            "agent_count": agent_count,
            "mcp_tool_count": mcp_tool_count,
            "ci_present": ci_present,
        }

    def check_n8n_status(self) -> dict:
        """Check n8n workflow engine status.

        Returns dict met:
        - reachable: bool
        - workflow_count: int
        - error: optional str
        """
        try:
            n8n_port = os.environ.get("N8N_PORT", "5678")
            base_url = f"http://localhost:{n8n_port}"
            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    f"{base_url}/api/v1/workflows",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            reachable = result.stdout.strip() == "200"
            workflow_count = 0

            if reachable:
                # Haal workflow count op
                count_result = subprocess.run(
                    ["curl", "-s", f"{base_url}/api/v1/workflows"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                try:
                    data = json.loads(count_result.stdout)
                    if isinstance(data, dict) and "data" in data:
                        workflow_count = len(data["data"])
                    elif isinstance(data, list):
                        workflow_count = len(data)
                except json.JSONDecodeError:
                    pass

            return {
                "reachable": reachable,
                "workflow_count": workflow_count,
                "error": None,
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {
                "reachable": False,
                "workflow_count": 0,
                "error": "n8n niet bereikbaar (offline of docker niet actief)",
            }
        except Exception as e:
            return {
                "reachable": False,
                "workflow_count": 0,
                "error": str(e),
            }

    def check_vectorstore_dirs(self) -> dict:
        """Check vectorstore data directories (offline fallback voor curator audit).

        Returns dict met zone-status.
        """
        data_dir = self.boris_path / "data"
        zones = {}
        for zone in ["chromadb_green", "chromadb_yellow", "chromadb_red"]:
            zone_path = data_dir / zone
            if zone_path.is_dir():
                # Check of er bestanden in zitten
                files = list(zone_path.iterdir())
                non_empty = [f for f in files if f.is_file() and f.stat().st_size > 0]
                zones[zone] = {
                    "exists": True,
                    "file_count": len(files),
                    "non_empty_files": len(non_empty),
                }
            else:
                zones[zone] = {"exists": False, "file_count": 0, "non_empty_files": 0}
        return zones

    def run_full_health_check(self) -> FullHealthReport:
        """Voer de volledige 7-dimensie health check uit.

        Returns een FullHealthReport met alle checks gecombineerd.
        Dit is de kern van F4: deterministisch, read-only, node-agnostisch formaat.
        """
        checks: list[HealthCheckResult] = []

        # 1. Tests & Lint
        checks.append(self._check_code_quality())

        # 2. Dependency Security
        checks.append(self._check_dependencies())

        # 3. Version Consistency
        checks.append(self._check_version_consistency())

        # 4. Architecture Integrity
        checks.append(self._check_architecture())

        # 5. Vectorstore / Curator
        checks.append(self._check_vectorstore())

        # 6. n8n Workflows
        checks.append(self._check_n8n())

        return FullHealthReport(
            node_id=self.NODE_ID,
            timestamp=datetime.now(UTC).isoformat(),
            checks=tuple(checks),
        )

    def _check_code_quality(self) -> HealthCheckResult:
        """Check tests en lint."""
        findings: list[HealthFinding] = []
        status = HealthStatus.HEALTHY

        # Tests
        test_result = self.run_tests()
        if not test_result.success:
            findings.append(
                HealthFinding(
                    component="tests",
                    severity=Severity.P1_CRITICAL,
                    message=f"{test_result.failed} tests failed, {test_result.errors} errors",
                    recommended_action="Fix failing tests before any other work",
                )
            )
            status = HealthStatus.CRITICAL
        elif test_result.total == 0:
            findings.append(
                HealthFinding(
                    component="tests",
                    severity=Severity.P2_DEGRADED,
                    message="No tests found or test runner failed",
                    recommended_action="Check pytest configuration and venv",
                )
            )
            status = HealthStatus.ATTENTION

        # Lint
        lint_clean, lint_output = self.run_lint()
        if not lint_clean:
            findings.append(
                HealthFinding(
                    component="lint",
                    severity=Severity.P2_DEGRADED,
                    message="Lint errors detected",
                    detail=lint_output[:500] if lint_output else "",
                    recommended_action="Run ruff check --fix",
                )
            )
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.ATTENTION

        lint_status = "clean" if lint_clean else "errors"
        summary = f"{test_result.passed}/{test_result.total} tests passed, lint {lint_status}"
        return HealthCheckResult(
            dimension="code_quality",
            status=status,
            summary=summary,
            findings=tuple(findings),
        )

    def _check_dependencies(self) -> HealthCheckResult:
        """Check dependency security via pip-audit."""
        findings: list[HealthFinding] = []

        clean, output = self.run_pip_audit()
        if "not installed" in output or "not found" in output:
            return HealthCheckResult(
                dimension="dependencies",
                status=HealthStatus.ATTENTION,
                summary="pip-audit niet beschikbaar — kan dependencies niet scannen",
                findings=(
                    HealthFinding(
                        component="dependencies",
                        severity=Severity.P3_ATTENTION,
                        message="pip-audit niet geïnstalleerd",
                        recommended_action="pip install pip-audit",
                    ),
                ),
            )

        if not clean:
            # Parse output for CVE count
            import re

            cve_matches = re.findall(r"(PYSEC|CVE)-\d+", output)
            cve_count = len(set(cve_matches))
            findings.append(
                HealthFinding(
                    component="dependencies",
                    severity=Severity.P2_DEGRADED if cve_count > 0 else Severity.P3_ATTENTION,
                    message=f"{cve_count} bekende kwetsbaarheden gevonden",
                    detail=output[:500],
                    recommended_action="Review CVEs en update dependencies",
                )
            )

        status = HealthStatus.HEALTHY if clean else HealthStatus.ATTENTION
        return HealthCheckResult(
            dimension="dependencies",
            status=status,
            summary=f"{'Clean' if clean else 'Issues found'} — pip-audit",
            findings=tuple(findings),
        )

    def _check_version_consistency(self) -> HealthCheckResult:
        """Check versie-consistentie tussen main.py, pyproject.toml, OVERDRACHT.md."""
        findings: list[HealthFinding] = []
        versions = self.get_version_info()

        # Filter out None values
        found = {k: v for k, v in versions.items() if v is not None}
        if len(found) < 2:
            return HealthCheckResult(
                dimension="version_consistency",
                status=HealthStatus.HEALTHY,
                summary=(
                    f"Version info found in {len(found)} location(s)"
                    " — insufficient for comparison"
                ),
            )

        unique_versions = set(found.values())
        if len(unique_versions) > 1:
            detail = ", ".join(f"{k}={v}" for k, v in found.items())
            findings.append(
                HealthFinding(
                    component="version",
                    severity=Severity.P3_ATTENTION,
                    message=f"Version mismatch: {detail}",
                    recommended_action="Sync version numbers across all locations",
                )
            )
            return HealthCheckResult(
                dimension="version_consistency",
                status=HealthStatus.ATTENTION,
                summary=f"Mismatch: {detail}",
                findings=tuple(findings),
            )

        return HealthCheckResult(
            dimension="version_consistency",
            status=HealthStatus.HEALTHY,
            summary=f"Consistent: {next(iter(unique_versions))}",
        )

    def _check_architecture(self) -> HealthCheckResult:
        """Check architectuur-integriteit."""
        findings: list[HealthFinding] = []
        scan = self.get_architecture_scan()

        # Missing modules
        missing_modules = [m for m, exists in scan["modules"].items() if not exists]
        if missing_modules:
            findings.append(
                HealthFinding(
                    component="architecture",
                    severity=Severity.P3_ATTENTION,
                    message=f"Missing modules: {', '.join(missing_modules)}",
                    recommended_action="Verify module structure matches architecture docs",
                )
            )

        # Missing configs
        missing_configs = [c for c, exists in scan["config_files"].items() if not exists]
        if missing_configs:
            findings.append(
                HealthFinding(
                    component="config",
                    severity=Severity.P3_ATTENTION,
                    message=f"Missing config files: {', '.join(missing_configs)}",
                )
            )

        # CI check
        if not scan["ci_present"]:
            findings.append(
                HealthFinding(
                    component="ci",
                    severity=Severity.P2_DEGRADED,
                    message="CI pipeline (.github/workflows/ci.yml) not found",
                    recommended_action="Set up GitHub Actions CI pipeline",
                )
            )

        present_count = sum(1 for v in scan["modules"].values() if v)
        total_count = len(scan["modules"])
        status = HealthStatus.HEALTHY
        if missing_modules or not scan["ci_present"]:
            status = HealthStatus.ATTENTION

        summary = (
            f"Modules: {present_count}/{total_count}, "
            f"Agents: {scan['agent_count']}, "
            f"MCP tools: {scan['mcp_tool_count']}, "
            f"CI: {'✓' if scan['ci_present'] else '✗'}"
        )
        return HealthCheckResult(
            dimension="architecture",
            status=status,
            summary=summary,
            findings=tuple(findings),
        )

    def _check_vectorstore(self) -> HealthCheckResult:
        """Check vectorstore status (offline-safe)."""
        findings: list[HealthFinding] = []

        # Try curator audit first
        curator_clean, curator_output = self.run_curator_audit()
        if "not found" in curator_output.lower() or "venv" in curator_output.lower():
            # Fallback: check directories
            zones = self.check_vectorstore_dirs()
            missing = [z for z, info in zones.items() if not info["exists"]]
            if missing:
                findings.append(
                    HealthFinding(
                        component="vectorstore",
                        severity=Severity.P4_INFO,
                        message=(
                            f"Data dirs not found: {', '.join(missing)}"
                            " (normaal bij eerste start)"
                        ),
                    )
                )
            return HealthCheckResult(
                dimension="vectorstore",
                status=HealthStatus.HEALTHY,
                summary="Curator niet beschikbaar — directory check uitgevoerd",
                findings=tuple(findings),
            )

        if not curator_clean:
            findings.append(
                HealthFinding(
                    component="vectorstore",
                    severity=Severity.P2_DEGRADED,
                    message="Curator audit failed",
                    detail=curator_output[:500],
                    recommended_action="Run curator_audit.py --fix",
                )
            )

        return HealthCheckResult(
            dimension="vectorstore",
            status=HealthStatus.HEALTHY if curator_clean else HealthStatus.ATTENTION,
            summary=f"Curator audit: {'passed' if curator_clean else 'issues found'}",
            findings=tuple(findings),
        )

    def _check_n8n(self) -> HealthCheckResult:
        """Check n8n workflow engine status."""
        n8n = self.check_n8n_status()

        if not n8n["reachable"]:
            return HealthCheckResult(
                dimension="n8n_workflows",
                status=HealthStatus.HEALTHY,  # Offline is niet kritiek
                summary=f"n8n: OFFLINE — {n8n.get('error', 'niet bereikbaar')}",
                findings=(
                    HealthFinding(
                        component="n8n",
                        severity=Severity.P4_INFO,
                        message="n8n niet bereikbaar",
                        detail=n8n.get("error", ""),
                        recommended_action="Start n8n via docker-compose als workflows nodig zijn",
                    ),
                ),
            )

        return HealthCheckResult(
            dimension="n8n_workflows",
            status=HealthStatus.HEALTHY,
            summary=f"n8n: online, {n8n['workflow_count']} workflows actief",
        )

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
        # Verrijk health met actuele testdata als LUMEN ontbreekt
        if health.test_count == 0:
            test_result = self.run_tests()
            if test_result.total > 0:
                health = NodeHealth(
                    status=health.status,
                    components=health.components,
                    test_count=test_result.total,
                    test_pass_rate=test_result.pass_rate,
                    coverage_pct=test_result.coverage_pct or 0.0,
                )
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
