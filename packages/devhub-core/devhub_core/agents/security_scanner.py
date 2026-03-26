"""
Security Scanner — Geautomatiseerde security checks (OWASP ASI 2026).

Read-only: scant op security issues, fixt ze niet.
Volgt het QAAgent-patroon: named check array, individual scan methods,
full_scan orchestrator, JSON persistence.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from devhub_core.contracts.security_contracts import (
    ASI_IDS,
    MitigationStatus,
    SecurityAuditReport,
    SecurityFinding,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Security check definitions
# ---------------------------------------------------------------------------

SECURITY_CHECKS: list[dict[str, str]] = [
    {
        "id": "SA-01",
        "name": "disallowed_tools_completeness",
        "desc": "Agents hebben deny-lists voor gevaarlijke tools",
        "asi": "ASI02",
    },
    {
        "id": "SA-02",
        "name": "supply_chain_deps",
        "desc": "pip-audit clean (geen bekende kwetsbaarheden)",
        "asi": "ASI04",
    },
    {
        "id": "SA-03",
        "name": "submodule_integrity",
        "desc": "Git submodules gepind op bekende commits",
        "asi": "ASI04",
    },
    {
        "id": "SA-04",
        "name": "agent_prompt_tracking",
        "desc": "Agent .md bestanden getrackt in git",
        "asi": "ASI10",
    },
]

# Destructive commands that should be in deny-lists
_DANGEROUS_COMMANDS: frozenset[str] = frozenset(
    {
        "rm -rf",
        "git push --force",
        "git reset --hard",
        "DROP TABLE",
        "DROP DATABASE",
        "chmod 777",
        "curl | bash",
        "wget | sh",
    }
)


class SecurityScanner:
    """Geautomatiseerde security scanner voor agentic systemen.

    Read-only: rapporteert bevindingen, fixt niets.
    Volgt het QAAgent-patroon.
    """

    def __init__(self, reports_path: Path | None = None) -> None:
        self._reports_path = reports_path or Path(".claude/scratchpad/security_reports")
        self._reports_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Individual scan methods
    # ------------------------------------------------------------------

    def scan_disallowed_tools(self, agents_dir: Path) -> list[SecurityFinding]:
        """SA-01: Controleer of agent .md bestanden deny-lists hebben (ASI02)."""
        findings: list[SecurityFinding] = []

        if not agents_dir.exists():
            findings.append(
                SecurityFinding(
                    asi_id="ASI02",
                    severity="P3_ATTENTION",
                    component="agents",
                    description=f"Agents directory niet gevonden: {agents_dir}",
                    attack_vector="N/A — directory ontbreekt",
                    current_mitigation="Geen",
                    recommendation=f"Maak {agents_dir} aan met agent-definities",
                )
            )
            return findings

        md_files = list(agents_dir.glob("*.md"))
        if not md_files:
            findings.append(
                SecurityFinding(
                    asi_id="ASI02",
                    severity="P3_ATTENTION",
                    component="agents",
                    description="Geen agent .md bestanden gevonden",
                    attack_vector="N/A — geen agents",
                    current_mitigation="Geen",
                    recommendation="Voeg agent-definities toe",
                )
            )
            return findings

        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8").lower()
            has_deny = any(
                kw in content
                for kw in ("disallowedtools", "deny", "forbidden", "blocked", "niet toegestaan")
            )
            if not has_deny:
                findings.append(
                    SecurityFinding(
                        asi_id="ASI02",
                        severity="P2_DEGRADED",
                        component=md_file.stem,
                        description=(
                            f"Agent '{md_file.name}' mist deny-list" " voor gevaarlijke tools"
                        ),
                        attack_vector=(
                            "Agent kan destructieve commando's" " uitvoeren zonder restrictie"
                        ),
                        current_mitigation="Geen deny-list gevonden",
                        recommendation=f"Voeg disallowedTools sectie toe aan {md_file.name}",
                    )
                )

        return findings

    @staticmethod
    def _parse_pip_audit(
        stdout: str,
    ) -> list[SecurityFinding]:
        """Parse pip-audit JSON output into SecurityFindings."""
        findings: list[SecurityFinding] = []
        try:
            data = json.loads(stdout) if stdout.strip() else []
            vulns = data if isinstance(data, list) else data.get("dependencies", [])
            for vuln in vulns:
                if not isinstance(vuln, dict) or not vuln.get("vulns"):
                    continue
                pkg = vuln.get("name", "unknown")
                ver = vuln.get("version", "")
                for v in vuln["vulns"]:
                    vid = v.get("id", "unknown")
                    desc = v.get("description", "zie advisory")
                    fix = v.get("fix_versions", ["latest"])
                    findings.append(
                        SecurityFinding(
                            asi_id="ASI04",
                            severity="P2_DEGRADED",
                            component=f"dependency:{pkg}",
                            description=(f"Kwetsbare dependency:" f" {pkg} {ver} — {vid}"),
                            attack_vector=f"Supply chain: {desc}",
                            current_mitigation="Geen",
                            recommendation=f"Update naar {fix}",
                        )
                    )
        except (json.JSONDecodeError, KeyError):
            logger.warning("Kon pip-audit output niet parsen")
        return findings

    def scan_supply_chain(self, project_root: Path) -> list[SecurityFinding]:
        """SA-02: Supply chain check via pip-audit (ASI04)."""
        findings: list[SecurityFinding] = []

        try:
            result = subprocess.run(
                ["pip-audit", "--format=json", "--output=-"],
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=60,
            )
            if result.stdout.strip():
                findings.extend(self._parse_pip_audit(result.stdout))
        except FileNotFoundError:
            findings.append(
                SecurityFinding(
                    asi_id="ASI04",
                    severity="P4_INFO",
                    component="tooling",
                    description="pip-audit niet beschikbaar — supply chain check overgeslagen",
                    attack_vector="N/A — tool ontbreekt",
                    current_mitigation="Handmatige review",
                    recommendation="Installeer pip-audit: pip install pip-audit",
                )
            )
        except subprocess.TimeoutExpired:
            findings.append(
                SecurityFinding(
                    asi_id="ASI04",
                    severity="P4_INFO",
                    component="tooling",
                    description="pip-audit timeout na 60s",
                    attack_vector="N/A",
                    current_mitigation="Handmatige review",
                    recommendation="Draai pip-audit handmatig",
                )
            )

        return findings

    def scan_submodule_integrity(self, project_root: Path) -> list[SecurityFinding]:
        """SA-03: Controleer dat git submodules gepind zijn (ASI04)."""
        findings: list[SecurityFinding] = []

        gitmodules = project_root / ".gitmodules"
        if not gitmodules.exists():
            # No submodules — nothing to check
            return findings

        try:
            result = subprocess.run(
                ["git", "submodule", "status"],
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=30,
            )
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                # Format: " <hash> <path> (<desc>)" or "-<hash> <path>" (not initialized)
                if line.startswith("-"):
                    parts = line[1:].split()
                    submodule_path = parts[1] if len(parts) > 1 else "unknown"
                    findings.append(
                        SecurityFinding(
                            asi_id="ASI04",
                            severity="P2_DEGRADED",
                            component=f"submodule:{submodule_path}",
                            description=f"Submodule '{submodule_path}' niet geïnitialiseerd",
                            attack_vector=(
                                "Niet-geïnitialiseerd submodule" " kan verkeerde code bevatten"
                            ),
                            current_mitigation="Geen",
                            recommendation=("git submodule update" f" --init {submodule_path}"),
                        )
                    )
                elif line.startswith("+"):
                    parts = line[1:].split()
                    submodule_path = parts[1] if len(parts) > 1 else "unknown"
                    findings.append(
                        SecurityFinding(
                            asi_id="ASI04",
                            severity="P3_ATTENTION",
                            component=f"submodule:{submodule_path}",
                            description=f"Submodule '{submodule_path}' wijkt af van gepinde commit",
                            attack_vector="Submodule bevat mogelijk ongecontroleerde wijzigingen",
                            current_mitigation="Git tracking",
                            recommendation=(
                                f"Verifieer en pin: cd {submodule_path}"
                                " && git checkout <expected-commit>"
                            ),
                        )
                    )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("git submodule status niet beschikbaar")

        return findings

    def scan_agent_prompts(
        self,
        agents_dir: Path,
        skills_dir: Path | None = None,
    ) -> list[SecurityFinding]:
        """SA-04: Controleer of agent/skill .md bestanden in git staan (ASI10)."""
        findings: list[SecurityFinding] = []

        md_files: list[Path] = []

        if agents_dir.exists():
            md_files.extend(agents_dir.glob("*.md"))

        if skills_dir and skills_dir.exists():
            md_files.extend(skills_dir.glob("*/SKILL.md"))

        for md_file in md_files:
            try:
                result = subprocess.run(
                    ["git", "ls-files", str(md_file)],
                    capture_output=True,
                    text=True,
                    cwd=str(md_file.parent),
                    timeout=10,
                )
                if not result.stdout.strip():
                    fname = md_file.name
                    findings.append(
                        SecurityFinding(
                            asi_id="ASI10",
                            severity="P2_DEGRADED",
                            component=fname,
                            description=(f"Agent/skill bestand '{fname}'" " niet getrackt in git"),
                            attack_vector="Ongetrackte prompt kan ongemerkt gewijzigd worden",
                            current_mitigation="Geen",
                            recommendation=f"git add {md_file}",
                        )
                    )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.warning("git ls-files niet beschikbaar voor %s", md_file)

        return findings

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    def full_scan(
        self,
        project_root: Path,
        agents_dir: Path | None = None,
        skills_dir: Path | None = None,
    ) -> SecurityAuditReport:
        """Voer alle security checks uit en produceer een SecurityAuditReport."""
        _agents_dir = agents_dir or project_root / "agents"
        _skills_dir = skills_dir or project_root / ".claude" / "skills"

        all_findings: list[SecurityFinding] = []

        # SA-01: disallowedTools
        all_findings.extend(self.scan_disallowed_tools(_agents_dir))

        # SA-02: Supply chain
        all_findings.extend(self.scan_supply_chain(project_root))

        # SA-03: Submodule integrity
        all_findings.extend(self.scan_submodule_integrity(project_root))

        # SA-04: Agent prompt tracking
        all_findings.extend(self.scan_agent_prompts(_agents_dir, _skills_dir))

        # Build ASI coverage
        asi_coverage: dict[str, MitigationStatus] = {}
        checked_asis = {c["asi"] for c in SECURITY_CHECKS}
        for asi_id in sorted(ASI_IDS):
            if asi_id in checked_asis:
                # Check if any findings for this ASI
                asi_findings = [f for f in all_findings if f.asi_id == asi_id]
                vulnerable = any(f.severity in ("P1_CRITICAL", "P2_DEGRADED") for f in asi_findings)
                if vulnerable:
                    asi_coverage[asi_id] = "VULNERABLE"
                elif asi_findings:
                    asi_coverage[asi_id] = "PARTIAL"
                else:
                    asi_coverage[asi_id] = "MITIGATED"
            else:
                asi_coverage[asi_id] = "NOT_ASSESSED"

        timestamp = datetime.now().isoformat(timespec="seconds")
        audit_id = f"SEC-{timestamp[:10]}"

        return SecurityAuditReport(
            audit_id=audit_id,
            timestamp=timestamp,
            mode="owasp_asi",
            findings=all_findings,
            asi_coverage=asi_coverage,
        )

    # ------------------------------------------------------------------
    # Report persistence
    # ------------------------------------------------------------------

    def save_report(self, report: SecurityAuditReport) -> Path:
        """Sla SecurityAuditReport op als JSON."""
        filename = f"{report.audit_id}.json"
        filepath = self._reports_path / filename
        data = asdict(report)
        filepath.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        logger.info("Security report saved: %s", filepath)
        return filepath

    def list_reports(self) -> list[Path]:
        """Lijst alle opgeslagen security reports."""
        return sorted(self._reports_path.glob("SEC-*.json"))

    def get_report(self, report_path: Path) -> SecurityAuditReport:
        """Laad een SecurityAuditReport uit JSON."""
        data = json.loads(report_path.read_text(encoding="utf-8"))

        findings = [SecurityFinding(**f) for f in data.get("findings", [])]

        return SecurityAuditReport(
            audit_id=data["audit_id"],
            timestamp=data["timestamp"],
            mode=data["mode"],
            findings=findings,
            asi_coverage=data.get("asi_coverage", {}),
        )
