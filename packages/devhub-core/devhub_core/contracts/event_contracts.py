"""
Event Contracts — Event Bus communicatie-contracten.

Definieert het EventBusInterface ABC, de Event base class, 10 typed event
subclasses, en ondersteunende types. Alle events zijn frozen dataclasses
(conform bestaande contract-patronen).
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from collections.abc import Callable

from devhub_core.contracts.curator_contracts import ObservationType
from devhub_core.contracts.dev_contracts import (
    DevTaskResult,
    DocGenRequest,
    QAReport,
)


# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------

EventHandler = Callable[["Event"], None]
EventFilter = Callable[["Event"], bool]


class EventLoopError(Exception):
    """Raised when event publish recursion exceeds max depth."""


# ---------------------------------------------------------------------------
# Event base class + typed subclasses
# ---------------------------------------------------------------------------


def _default_event_id() -> str:
    return str(uuid.uuid4())


def _default_timestamp() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class Event:
    """Base class voor alle DevHub events.

    Subclasses voegen domein-specifieke velden toe.
    event_id en timestamp worden automatisch gegenereerd als ze niet
    expliciet meegegeven worden.
    """

    source_agent: str
    event_id: str = field(default_factory=_default_event_id)
    timestamp: str = field(default_factory=_default_timestamp)

    def __post_init__(self) -> None:
        if not self.source_agent:
            raise ValueError("source_agent is required")


# --- Sprint lifecycle events ---


@dataclass(frozen=True)
class SprintStarted(Event):
    """Gepubliceerd wanneer een sprint start."""

    sprint_id: str = ""
    node_id: str = ""
    sprint_type: str = ""  # FEAT, SPIKE, CHORE, BUG

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.sprint_id:
            raise ValueError("sprint_id is required")
        if not self.node_id:
            raise ValueError("node_id is required")


@dataclass(frozen=True)
class SprintClosed(Event):
    """Gepubliceerd wanneer een sprint wordt afgesloten."""

    sprint_id: str = ""
    node_id: str = ""
    result: DevTaskResult | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.sprint_id:
            raise ValueError("sprint_id is required")
        if not self.node_id:
            raise ValueError("node_id is required")


# --- Agent lifecycle events ---


@dataclass(frozen=True)
class TaskAssigned(Event):
    """Gepubliceerd wanneer een taak wordt toegewezen aan een agent."""

    task_id: str = ""
    agent_id: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.task_id:
            raise ValueError("task_id is required")


@dataclass(frozen=True)
class TaskCompleted(Event):
    """Gepubliceerd wanneer een agent een taak succesvol afrondt."""

    task_id: str = ""
    agent_id: str = ""
    result: DevTaskResult | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.task_id:
            raise ValueError("task_id is required")


@dataclass(frozen=True)
class TaskFailed(Event):
    """Gepubliceerd wanneer een taak faalt."""

    task_id: str = ""
    agent_id: str = ""
    error: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.task_id:
            raise ValueError("task_id is required")


@dataclass(frozen=True)
class QACompleted(Event):
    """Gepubliceerd wanneer QA Agent een review afrondt."""

    task_id: str = ""
    report: QAReport | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.task_id:
            raise ValueError("task_id is required")


@dataclass(frozen=True)
class DocGenRequested(Event):
    """Gepubliceerd wanneer documentatie-generatie wordt aangevraagd."""

    request: DocGenRequest | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.request is None:
            raise ValueError("request is required")


# --- Knowledge pipeline events ---


@dataclass(frozen=True)
class KnowledgeGapDetected(Event):
    """Gepubliceerd wanneer een kennislacune wordt gedetecteerd."""

    domain: str = ""
    gap_description: str = ""
    requesting_agent: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.domain:
            raise ValueError("domain is required")
        if not self.gap_description:
            raise ValueError("gap_description is required")


@dataclass(frozen=True)
class HealthDegraded(Event):
    """Gepubliceerd wanneer een health-dimensie onder de drempel zakt."""

    dimension: str = ""
    score: float = 0.0
    threshold: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.dimension:
            raise ValueError("dimension is required")


@dataclass(frozen=True)
class ObservationEmitted(Event):
    """Gepubliceerd wanneer de AnalysisPipeline een observatie emit."""

    obs_type: ObservationType | None = None
    payload: str = ""
    severity: str = "INFO"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.obs_type is None:
            raise ValueError("obs_type is required")


# --- Knowledge pipeline lifecycle events ---


@dataclass(frozen=True)
class ResearchCompleted(Event):
    """Gepubliceerd wanneer de research-loop een kennisartikel afrondt."""

    domain: str = ""
    article_path: str = ""
    grade: str = ""
    source_count: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.domain:
            raise ValueError("domain is required")
        if not self.article_path:
            raise ValueError("article_path is required")


@dataclass(frozen=True)
class KnowledgeIngested(Event):
    """Gepubliceerd wanneer KnowledgeIngestor een artikel in de vectorstore plaatst."""

    article_id: str = ""
    domain: str = ""
    chunk_count: int = 0
    grade: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.article_id:
            raise ValueError("article_id is required")
        if not self.domain:
            raise ValueError("domain is required")


@dataclass(frozen=True)
class DocumentPublished(Event):
    """Gepubliceerd wanneer DocumentService een document naar storage schrijft."""

    document_path: str = ""
    category: str = ""
    storage_path: str = ""
    node_id: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.document_path:
            raise ValueError("document_path is required")


# ---------------------------------------------------------------------------
# EventBusInterface ABC — volgt ResearchQueue patroon
# ---------------------------------------------------------------------------


class EventBusInterface(ABC):
    """Abstract interface voor een event bus.

    Implementaties moeten thread-safe zijn voor concurrent publish.
    """

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Publiceer een event naar alle matching subscribers."""
        ...

    @abstractmethod
    def subscribe(
        self,
        event_type: type[Event],
        handler: EventHandler,
        event_filter: EventFilter | None = None,
    ) -> str:
        """Registreer een handler voor een event type. Retourneert subscription_id."""
        ...

    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> None:
        """Verwijder een subscription."""
        ...

    @abstractmethod
    def history(
        self,
        event_type: type[Event] | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Retourneer recente events, optioneel gefilterd op type."""
        ...
