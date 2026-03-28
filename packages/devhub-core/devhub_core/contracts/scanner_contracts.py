"""
Scanner Contracts — Dataclasses voor pre-task knowledge scan en bootstrap audit.

Frozen dataclasses voor KnowledgeScanner, ConfigDrivenBootstrap en KnowledgeHealthChecker.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devhub_core.contracts.research_contracts import ResearchRequest


# Grade ordering for comparison
_GRADE_ORDER: dict[str, int] = {
    "SPECULATIVE": 0,
    "BRONZE": 1,
    "SILVER": 2,
    "GOLD": 3,
}


def grade_gte(actual: str, required: str) -> bool:
    """Check of actual grade voldoet aan of hoger is dan required grade."""
    return _GRADE_ORDER.get(actual, 0) >= _GRADE_ORDER.get(required, 0)


@dataclass(frozen=True)
class DomainScanStatus:
    """Scan-resultaat voor één kennisdomein."""

    domain: str
    required_grade: str
    actual_articles: int
    actual_best_grade: str = "SPECULATIVE"
    rq_coverage: tuple[tuple[str, bool], ...] = ()
    sufficient: bool = False

    def __post_init__(self) -> None:
        if not self.domain:
            raise ValueError("domain is required")
        if not self.required_grade:
            raise ValueError("required_grade is required")
        if self.actual_articles < 0:
            raise ValueError(f"actual_articles must be >= 0, got {self.actual_articles}")

    @property
    def covered_rqs(self) -> list[str]:
        """RQs die gedekt zijn."""
        return [rq for rq, covered in self.rq_coverage if covered]

    @property
    def missing_rqs(self) -> list[str]:
        """RQs die ontbreken."""
        return [rq for rq, covered in self.rq_coverage if not covered]

    @property
    def rq_coverage_pct(self) -> float:
        """Percentage RQ-dekking."""
        if not self.rq_coverage:
            return 100.0
        covered = sum(1 for _, c in self.rq_coverage if c)
        return (covered / len(self.rq_coverage)) * 100.0


@dataclass(frozen=True)
class KnowledgeScanResult:
    """Resultaat van een pre-task knowledge scan voor een agent."""

    agent_name: str
    domain_statuses: tuple[DomainScanStatus, ...] = ()
    overall_sufficient: bool = True
    generated_requests: tuple[ResearchRequest, ...] = ()
    scan_timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.agent_name:
            raise ValueError("agent_name is required")

    @property
    def gap_domains(self) -> list[str]:
        """Domeinen met onvoldoende kennis."""
        return [d.domain for d in self.domain_statuses if not d.sufficient]

    @property
    def gap_summary(self) -> str:
        """Menselijk leesbare samenvatting van kennislacunes."""
        gaps = self.gap_domains
        if not gaps:
            return f"Agent {self.agent_name}: alle domeinen voldoende."
        gap_details = []
        for ds in self.domain_statuses:
            if not ds.sufficient:
                missing = ds.missing_rqs
                detail = f"{ds.domain} (nodig: {ds.required_grade}"
                if missing:
                    detail += f", ontbrekend: {', '.join(missing)}"
                detail += ")"
                gap_details.append(detail)
        return f"Agent {self.agent_name}: lacunes in {', '.join(gap_details)}"


@dataclass(frozen=True)
class BootstrapDomainReport:
    """Bootstrap-resultaat voor één domein."""

    domain: str
    articles_created: int = 0
    rq_coverage: tuple[tuple[str, bool], ...] = ()
    coverage_pct: float = 0.0

    def __post_init__(self) -> None:
        if not self.domain:
            raise ValueError("domain is required")
        if self.articles_created < 0:
            raise ValueError(f"articles_created must be >= 0, got {self.articles_created}")
        if not 0.0 <= self.coverage_pct <= 100.0:
            raise ValueError(f"coverage_pct must be between 0 and 100, got {self.coverage_pct}")


@dataclass(frozen=True)
class BootstrapAuditReport:
    """Audit-rapport na bootstrap run."""

    domain_reports: tuple[BootstrapDomainReport, ...] = ()
    total_articles: int = 0
    total_domains: int = 0
    overall_coverage_pct: float = 0.0
    timestamp: str = ""

    def __post_init__(self) -> None:
        if self.total_articles < 0:
            raise ValueError(f"total_articles must be >= 0, got {self.total_articles}")
        if not 0.0 <= self.overall_coverage_pct <= 100.0:
            raise ValueError(
                f"overall_coverage_pct must be between 0 and 100, "
                f"got {self.overall_coverage_pct}"
            )
