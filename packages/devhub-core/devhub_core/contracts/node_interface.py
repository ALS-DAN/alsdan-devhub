"""
NodeInterface — Vendor-free contract voor managed project nodes.

Elk project dat door het DEV systeem beheerd wordt, implementeert deze interface
via een adapter. De interface bevat GEEN project-specifieke types.

Design: Contract-first (Martin Fowler), frozen dataclasses (immutability).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


@dataclass(frozen=True)
class NodeHealth:
    """Gezondheidsstatus van een managed node."""

    status: Literal["UP", "DEGRADED", "DOWN"]
    components: dict[str, str]  # {"weaviate": "UP", "ollama": "DOWN"}
    test_count: int
    test_pass_rate: float  # 0.0 - 1.0
    coverage_pct: float  # 0.0 - 100.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.test_pass_rate <= 1.0:
            raise ValueError(f"test_pass_rate must be 0.0-1.0, got {self.test_pass_rate}")
        if not 0.0 <= self.coverage_pct <= 100.0:
            raise ValueError(f"coverage_pct must be 0.0-100.0, got {self.coverage_pct}")


@dataclass(frozen=True)
class NodeDocStatus:
    """Documentatiestatus van een managed node."""

    total_pages: int
    stale_pages: int  # Niet bijgewerkt >30 dagen
    diataxis_coverage: dict[str, int]  # {"tutorial": 5, "howto": 12, ...}

    def __post_init__(self) -> None:
        if self.stale_pages > self.total_pages:
            raise ValueError("stale_pages cannot exceed total_pages")


@dataclass(frozen=True)
class TestResult:
    """Resultaat van een test-run op een node."""

    total: int
    passed: int
    failed: int
    errors: int
    duration_seconds: float
    coverage_pct: float | None = None

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total

    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0


@dataclass(frozen=True)
class NodeReport:
    """Volledig vendor-free rapport van een managed node.

    Dit is het kern-contract: elke NodeInterface implementatie
    moet een geldig NodeReport kunnen produceren.
    """

    node_id: str
    timestamp: str  # ISO 8601
    health: NodeHealth
    doc_status: NodeDocStatus
    observations: list[str] = field(default_factory=list)
    safety_zones: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        if not self.timestamp:
            raise ValueError("timestamp is required")


class Severity(Enum):
    """Health finding severity level."""

    P1_CRITICAL = "P1"  # Platform broken, data loss risk
    P2_DEGRADED = "P2"  # Core functionality impaired
    P3_ATTENTION = "P3"  # Quality issues, no direct impact
    P4_INFO = "P4"  # Trends, minor deviations


class HealthStatus(Enum):
    """Overall health status."""

    HEALTHY = "healthy"  # ✅ Gezond
    ATTENTION = "attention"  # ⚠️ Actie nodig
    CRITICAL = "critical"  # ❌ Kritiek


@dataclass(frozen=True)
class HealthFinding:
    """Een bevinding uit een health check.

    Elke bevinding is actionable: het beschrijft wat er mis is,
    waarom het ertoe doet, en wat de aanbevolen actie is.
    """

    component: str  # e.g. "tests", "dependencies", "architecture"
    severity: Severity
    message: str  # Korte beschrijving
    detail: str = ""  # Uitgebreide info
    recommended_action: str = ""

    def __post_init__(self) -> None:
        if not self.component:
            raise ValueError("component is required")
        if not self.message:
            raise ValueError("message is required")


@dataclass(frozen=True)
class HealthCheckResult:
    """Resultaat van een health check dimensie (e.g. tests, deps, architecture)."""

    dimension: str  # e.g. "code_quality", "dependencies", "architecture"
    status: HealthStatus
    summary: str  # 1-zin samenvatting
    findings: tuple[HealthFinding, ...] = ()

    def __post_init__(self) -> None:
        if not self.dimension:
            raise ValueError("dimension is required")


@dataclass(frozen=True)
class FullHealthReport:
    """Volledig health rapport voor een managed node.

    Combineert alle dimensies tot een overall status.
    De overall status is de ergste status van alle dimensies.
    """

    node_id: str
    timestamp: str  # ISO 8601
    checks: tuple[HealthCheckResult, ...] = ()
    overall: HealthStatus = HealthStatus.HEALTHY

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        # Auto-compute overall from worst check status
        if self.checks:
            worst = HealthStatus.HEALTHY
            for check in self.checks:
                if check.status == HealthStatus.CRITICAL:
                    worst = HealthStatus.CRITICAL
                    break
                if check.status == HealthStatus.ATTENTION:
                    worst = HealthStatus.ATTENTION
            if worst != self.overall:
                object.__setattr__(self, "overall", worst)

    @property
    def p1_findings(self) -> list[HealthFinding]:
        """Alle P1 (kritieke) bevindingen."""
        return [f for c in self.checks for f in c.findings if f.severity == Severity.P1_CRITICAL]

    @property
    def p2_findings(self) -> list[HealthFinding]:
        """Alle P2 (degraded) bevindingen."""
        return [f for c in self.checks for f in c.findings if f.severity == Severity.P2_DEGRADED]

    @property
    def alert_findings(self) -> list[HealthFinding]:
        """P1 + P2 = findings die een GitHub Issue verdienen."""
        return self.p1_findings + self.p2_findings


class DeveloperPhase(Enum):
    """O-B-B developer coaching fase."""

    ORIENTEREN = "ORIËNTEREN"  # Lezen, begrijpen, vragen stellen
    BOUWEN = "BOUWEN"  # Implementeren, testen, PRs
    BEHEERSEN = "BEHEERSEN"  # Architectuurbeslissingen, mentoring


class CoachingSignal(Enum):
    """Coaching-signaal voor developer voortgang."""

    GREEN = "GROEN"  # Actief, tests groeien, geen blockers
    ATTENTION = "AANDACHT"  # Blocker >2 dagen, of tests dalen
    STAGNATION = "STAGNATIE"  # Geen entries >5 dagen, of lang in ORIËNTEREN


@dataclass(frozen=True)
class DeveloperProfile:
    """Developer voortgangsprofiel — node-agnostisch.

    Bevat alle data die de mentor-skill nodig heeft om fase te detecteren
    en coaching-signalen te genereren.
    """

    current_phase: DeveloperPhase
    streak_days: int  # Aaneengesloten actieve dagen
    blockers_open: int  # Entries met open blockers
    tests_delta_total: int  # Netto test-groei in periode
    recent_entry_count: int  # Aantal entries in periode
    last_entry_date: str | None = None  # ISO datum van laatst entry
    coaching_signal: CoachingSignal = CoachingSignal.GREEN

    def __post_init__(self) -> None:
        if self.streak_days < 0:
            raise ValueError("streak_days cannot be negative")
        if self.recent_entry_count < 0:
            raise ValueError("recent_entry_count cannot be negative")


@dataclass(frozen=True)
class CoachingResponse:
    """Gestructureerd coaching-antwoord.

    Bevat fase-detectie, signaal, observatie en concrete actiestappen.
    """

    date: str  # ISO datum
    phase: DeveloperPhase
    signal: CoachingSignal
    observation: str  # Wat de mentor ziet
    actions: tuple[str, ...]  # Concrete volgende stappen
    check_question: str  # Begrips-/voortgangsvraag
    risk_alert: str = ""  # Optioneel: alleen bij AANDACHT/STAGNATIE

    def __post_init__(self) -> None:
        if not self.observation:
            raise ValueError("observation is required")
        if not self.actions:
            raise ValueError("at least one action is required")
        if not self.check_question:
            raise ValueError("check_question is required")


@dataclass(frozen=True)
class ReviewContext:
    """Context voor governance review checks.

    Bevat alle data die de QA Agent nodig heeft om governance checks uit te voeren.
    """

    recent_commits: tuple[str, ...] = ()  # Recente commit messages
    staged_files: tuple[str, ...] = ()  # Staged bestanden
    diff_content: str = ""  # Git diff output
    governance_files: tuple[str, ...] = ()  # Governance-gerelateerde bestanden

    def __post_init__(self) -> None:
        # No required fields — empty ReviewContext is valid (default implementation)
        pass


class NodeInterface(ABC):
    """Abstract contract dat elke managed node moet implementeren.

    Het DEV systeem communiceert met nodes uitsluitend via deze interface.
    Nodes weten niet dat het DEV systeem bestaat — adapters vertalen
    node-specifieke data naar dit vendor-free formaat.
    """

    @abstractmethod
    def get_report(self) -> NodeReport:
        """Genereer een volledig NodeReport."""
        ...

    @abstractmethod
    def get_health(self) -> NodeHealth:
        """Haal gezondheidsstatus op."""
        ...

    @abstractmethod
    def list_docs(self) -> list[str]:
        """Lijst alle documentatie-pagina's."""
        ...

    @abstractmethod
    def run_tests(self) -> TestResult:
        """Voer tests uit en retourneer resultaat."""
        ...

    def get_review_context(self) -> ReviewContext:
        """Haal review-context op voor governance checks.

        Concrete default: retourneert lege ReviewContext.
        Adapters kunnen dit overschrijven met project-specifieke data.
        """
        return ReviewContext()
