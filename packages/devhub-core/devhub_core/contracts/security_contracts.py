"""
Security Contracts — Red Team communicatie-contracten.

Definieert SecurityFinding en SecurityAuditReport voor de red team agent.
Gebaseerd op OWASP Top 10 for Agentic Applications (ASI 2026) en de
Votal AI 7-staps Agentic Kill Chain. Frozen voor immutability
(conform ADR-049 pattern).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# Valid OWASP ASI 2026 identifiers
ASI_IDS = frozenset(f"ASI{i:02d}" for i in range(1, 11))

# Severity levels aligned with existing health/QA conventions
Severity = Literal[
    "P1_CRITICAL",
    "P2_DEGRADED",
    "P3_ATTENTION",
    "P4_INFO",
]

# Risk levels for overall audit assessment
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Audit modes
AuditMode = Literal["owasp_asi", "kill_chain", "deepteam"]

# ASI mitigation status
MitigationStatus = Literal["MITIGATED", "PARTIAL", "VULNERABLE", "NOT_ASSESSED"]


@dataclass(frozen=True)
class SecurityFinding:
    """Eén security-bevinding van de red team agent."""

    asi_id: str  # "ASI01" t/m "ASI10"
    severity: Severity
    component: str  # "dev-lead" / "coder" / "reviewer" / "memory" / etc.
    description: str
    attack_vector: str  # Hoe het kan worden geëxploiteerd
    current_mitigation: str
    recommendation: str
    kill_chain_stage: int | None = None  # 1-7, of None

    def __post_init__(self) -> None:
        if self.asi_id not in ASI_IDS:
            raise ValueError(f"asi_id must be one of {sorted(ASI_IDS)}, got '{self.asi_id}'")
        if not self.description:
            raise ValueError("description is required")
        if not self.component:
            raise ValueError("component is required")
        if self.kill_chain_stage is not None and not (1 <= self.kill_chain_stage <= 7):
            raise ValueError(f"kill_chain_stage must be 1-7, got {self.kill_chain_stage}")


@dataclass(frozen=True)
class SecurityAuditReport:
    """Rapport van de red team agent na een security audit."""

    audit_id: str
    timestamp: str
    mode: AuditMode
    findings: list[SecurityFinding] = field(default_factory=list)
    overall_risk: RiskLevel = "LOW"
    asi_coverage: dict[str, MitigationStatus] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.audit_id:
            raise ValueError("audit_id is required")
        if not self.timestamp:
            raise ValueError("timestamp is required")
        # Auto-escalate risk based on findings
        if self.findings:
            max_severity = max(f.severity for f in self.findings)
            risk_map: dict[str, RiskLevel] = {
                "P1_CRITICAL": "CRITICAL",
                "P2_DEGRADED": "HIGH",
                "P3_ATTENTION": "MEDIUM",
                "P4_INFO": "LOW",
            }
            auto_risk = risk_map[max_severity]
            # Only escalate, never downgrade
            risk_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            if risk_order.index(auto_risk) > risk_order.index(self.overall_risk):
                object.__setattr__(self, "overall_risk", auto_risk)
        # Validate asi_coverage keys
        for key in self.asi_coverage:
            if key not in ASI_IDS:
                raise ValueError(f"asi_coverage key must be a valid ASI ID, got '{key}'")

    @property
    def critical_findings(self) -> list[SecurityFinding]:
        return [f for f in self.findings if f.severity == "P1_CRITICAL"]

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def has_vulnerabilities(self) -> bool:
        return any(v == "VULNERABLE" for v in self.asi_coverage.values())
