#!/usr/bin/env python3
"""DevHub Governance Check — Standalone CI script.

Implementeert een subset van de G-01 t/m G-16 checks uit devhub-governance-check SKILL.md.
Draait in GitHub Actions op elke push naar main.

Checks die hier geautomatiseerd zijn (statisch analyseerbaar):
- G-01: Destructieve patronen in diff (Art. 1)
- G-05: Destructieve git operaties in diff (Art. 3)
- G-07: Commit message kwaliteit (Art. 4)
- G-11: Project-governance wijzigingen (Art. 6)
- G-14: Secrets detectie via detect-secrets (Art. 8)
- G-15: PII-patronen in diff (Art. 8)
- G-16: .env bestanden in diff (Art. 8)

Checks die NIET geautomatiseerd zijn (vereisen LLM of sprint-context):
- G-02, G-03, G-04, G-08, G-09, G-10, G-12, G-13
  → Blijven in de handmatige /devhub-governance-check skill

Usage:
    python scripts/governance_check.py [--output-format=json|text]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Finding:
    check: str
    severity: Literal["CRITICAL", "ERROR", "WARNING", "INFO"]
    detail: str
    file: str = ""

    def to_dict(self) -> dict:
        d = {"check": self.check, "severity": self.severity, "detail": self.detail}
        if self.file:
            d["file"] = self.file
        return d


@dataclass
class GovernanceReport:
    commit_sha: str = ""
    commit_message: str = ""
    verdict: Literal["PASS", "NEEDS_REVIEW", "BLOCK"] = "PASS"
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "commit_sha": self.commit_sha,
            "commit_message": self.commit_message,
            "verdict": self.verdict,
            "findings": [f.to_dict() for f in self.findings],
        }


# ── Patronen ─────────────────────────────────────────────────────────────────

DESTRUCTIVE_PATTERNS = [
    (r"--force\b", "force flag detected"),
    (r"--hard\b", "hard reset detected"),
    (r"\brm\s+-rf\b", "recursive force delete detected"),
    (r"\brm['\",\s].*-rf\b", "recursive force delete detected"),
    (r"\bDROP\s+TABLE\b", "DROP TABLE detected"),
    (r"\bDROP\s+DATABASE\b", "DROP DATABASE detected"),
    (r"\bTRUNCATE\b", "TRUNCATE detected"),
]

DESTRUCTIVE_GIT_PATTERNS = [
    (r"force\s+push", "force push reference"),
    (r"reset\s+--hard", "git reset --hard reference"),
    (r"--no-verify\b", "--no-verify flag (skips hooks)"),
    (r"push\s+--force", "force push command"),
    (r"push\s+-f\b", "force push shorthand"),
]

# Project-governance paden (Art. 6)
PROJECT_GOVERNANCE_PATHS = [
    "projects/",  # Elke wijziging in projects/*/CLAUDE.md of projects/*/.claude/
]

PROJECT_GOVERNANCE_FILES = [
    re.compile(r"^projects/[^/]+/CLAUDE\.md$"),
    re.compile(r"^projects/[^/]+/\.claude/"),
]

# RED-zone paden (Art. 7)
RED_ZONE_PATHS = [
    re.compile(r"^docs/compliance/DEV_CONSTITUTION\.md$"),
    re.compile(r"^\.claude/agents/"),
    re.compile(r"^config/"),
    re.compile(r"^agents/"),
]

# PII patronen (Art. 8)
PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email address"),
    (r"\b\d{9}\b", "possible BSN (9 digits)"),
    (r"\b06[-\s]?\d{8}\b", "Dutch mobile number"),
    (r"\b\+31[-\s]?\d{9}\b", "Dutch phone number (+31)"),
]

# .env patronen (Art. 8)
ENV_FILE_PATTERN = re.compile(r"(^|/)\.env(\..+)?$")


# ── Helpers ──────────────────────────────────────────────────────────────────

def run_cmd(cmd: list[str]) -> tuple[int, str]:
    """Run a command and return (exit_code, stdout)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, str(e)


def get_commit_info() -> tuple[str, str]:
    """Get latest commit SHA and message."""
    _, sha = run_cmd(["git", "rev-parse", "HEAD"])
    _, msg = run_cmd(["git", "log", "-1", "--pretty=%B"])
    return sha.strip(), msg.strip()


def get_diff() -> str:
    """Get diff of latest commit."""
    _, diff = run_cmd(["git", "diff", "HEAD~1..HEAD"])
    return diff


def get_changed_files() -> list[str]:
    """Get list of files changed in latest commit."""
    _, output = run_cmd(["git", "diff", "--name-only", "HEAD~1..HEAD"])
    return [f for f in output.split("\n") if f.strip()]


# ── Checks ───────────────────────────────────────────────────────────────────

def check_g01_destructive_patterns(diff: str) -> list[Finding]:
    """G-01 (Art. 1): Scan diff voor destructieve patronen."""
    findings = []
    for pattern, desc in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, diff, re.IGNORECASE):
            findings.append(Finding(
                check="G-01",
                severity="WARNING",
                detail=f"Destructive pattern in diff: {desc}",
            ))
    return findings


def check_g05_destructive_git(diff: str) -> list[Finding]:
    """G-05 (Art. 3): Scan voor destructieve git operaties."""
    findings = []
    for pattern, desc in DESTRUCTIVE_GIT_PATTERNS:
        if re.search(pattern, diff, re.IGNORECASE):
            findings.append(Finding(
                check="G-05",
                severity="WARNING",
                detail=f"Destructive git operation: {desc}",
            ))
    return findings


def check_g07_commit_message(message: str) -> list[Finding]:
    """G-07 (Art. 4): Commit message kwaliteit."""
    findings = []
    if len(message) < 10:
        findings.append(Finding(
            check="G-07",
            severity="WARNING",
            detail=f"Commit message too short ({len(message)} chars, min 10)",
        ))

    low_quality = ["fix", "update", "wip", "temp", "test", "stuff", "changes"]
    first_line = message.split("\n")[0].strip().lower()
    if first_line in low_quality:
        findings.append(Finding(
            check="G-07",
            severity="WARNING",
            detail=f"Low-quality commit message: '{first_line}'",
        ))

    return findings


def check_g11_project_governance(changed_files: list[str]) -> list[Finding]:
    """G-11 (Art. 6): Wijzigingen aan project-governance bestanden."""
    findings = []
    for f in changed_files:
        for pattern in PROJECT_GOVERNANCE_FILES:
            if pattern.match(f):
                findings.append(Finding(
                    check="G-11",
                    severity="WARNING",
                    detail=f"Project governance file modified: {f}",
                    file=f,
                ))
    return findings


def check_g14_secrets(changed_files: list[str]) -> list[Finding]:
    """G-14 (Art. 8): Secrets detectie via detect-secrets."""
    findings = []
    if not changed_files:
        return findings

    # Draai detect-secrets scan op gewijzigde bestanden
    exit_code, output = run_cmd(
        ["detect-secrets", "scan", "--list-all-secrets"] + changed_files
    )

    if exit_code == 0 and output:
        try:
            scan_result = json.loads(output)
            results = scan_result.get("results", {})
            for filepath, secrets in results.items():
                for secret in secrets:
                    findings.append(Finding(
                        check="G-14",
                        severity="CRITICAL",
                        detail=f"Secret detected: {secret.get('type', 'unknown')} at line {secret.get('line_number', '?')}",
                        file=filepath,
                    ))
        except json.JSONDecodeError:
            pass

    return findings


def check_g15_pii(diff: str) -> list[Finding]:
    """G-15 (Art. 8): PII-patronen in diff."""
    findings = []
    # Alleen op toegevoegde regels (beginnen met +, niet +++)
    added_lines = [
        line[1:] for line in diff.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ]
    added_text = "\n".join(added_lines)

    for pattern, desc in PII_PATTERNS:
        matches = re.findall(pattern, added_text)
        if matches:
            # Filter bekende false positives
            real_matches = [
                m for m in matches
                if not m.endswith("@example.com")
                and not m.endswith("@anthropic.com")
                and not m.endswith("@gmail.com")  # In .env.example templates
                and "noreply" not in m
            ]
            if real_matches:
                findings.append(Finding(
                    check="G-15",
                    severity="WARNING",
                    detail=f"Possible PII ({desc}): {len(real_matches)} occurrence(s)",
                ))

    return findings


def check_g16_env_files(changed_files: list[str]) -> list[Finding]:
    """G-16 (Art. 8): .env bestanden in diff."""
    findings = []
    for f in changed_files:
        if ENV_FILE_PATTERN.search(f):
            # .env.example is OK — bevat templates, geen echte secrets
            if f.endswith(".example"):
                continue
            findings.append(Finding(
                check="G-16",
                severity="CRITICAL",
                detail=f".env file committed: {f}",
                file=f,
            ))
    return findings


# ── Main ─────────────────────────────────────────────────────────────────────

def run_governance_check() -> GovernanceReport:
    """Execute all governance checks and return report."""
    report = GovernanceReport()

    # Commit info
    report.commit_sha, report.commit_message = get_commit_info()

    # Diff en changed files
    diff = get_diff()
    changed_files = get_changed_files()

    # Run alle checks
    all_findings: list[Finding] = []
    all_findings.extend(check_g01_destructive_patterns(diff))
    all_findings.extend(check_g05_destructive_git(diff))
    all_findings.extend(check_g07_commit_message(report.commit_message))
    all_findings.extend(check_g11_project_governance(changed_files))
    all_findings.extend(check_g14_secrets(changed_files))
    all_findings.extend(check_g15_pii(diff))
    all_findings.extend(check_g16_env_files(changed_files))

    report.findings = all_findings

    # Verdict bepalen
    has_critical = any(f.severity == "CRITICAL" for f in all_findings)
    has_warning = any(f.severity in ("ERROR", "WARNING") for f in all_findings)

    if has_critical:
        report.verdict = "BLOCK"
    elif has_warning:
        report.verdict = "NEEDS_REVIEW"
    else:
        report.verdict = "PASS"

    return report


def main():
    output_format = "json"
    for arg in sys.argv[1:]:
        if arg.startswith("--output-format="):
            output_format = arg.split("=", 1)[1]

    report = run_governance_check()

    if output_format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"Governance Check — {report.commit_sha[:8]}")
        print(f"Verdict: {report.verdict}")
        if report.findings:
            print(f"\nFindings ({len(report.findings)}):")
            for f in report.findings:
                print(f"  [{f.severity}] {f.check}: {f.detail}")
        else:
            print("\nNo findings — all checks passed.")


if __name__ == "__main__":
    main()
