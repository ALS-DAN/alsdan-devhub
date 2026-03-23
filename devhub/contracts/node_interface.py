"""
NodeInterface — Vendor-free contract voor managed project nodes.

Elk project dat door het DEV systeem beheerd wordt, implementeert deze interface
via een adapter. De interface bevat GEEN project-specifieke types.

Design: Contract-first (Martin Fowler), frozen dataclasses (immutability).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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
