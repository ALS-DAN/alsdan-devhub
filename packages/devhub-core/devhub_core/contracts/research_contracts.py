"""
Research Contracts — Communicatie-contracten voor het kennispipeline-systeem.

Deze dataclasses definiëren de berichten tussen ResearchAgent, kennisbank
en andere agents. Frozen voor immutability (conform BORIS ADR-049 pattern).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class ResearchDepth(Enum):
    """Diepte van een research-opdracht."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class ResearchStatus(Enum):
    """Status van een research-opdracht."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


KnowledgeGrade = Literal["GOLD", "SILVER", "BRONZE", "SPECULATIVE"]


@dataclass(frozen=True)
class ResearchRequest:
    """Research-opdracht van een agent aan het kennispipeline-systeem."""

    request_id: str
    requesting_agent: str
    question: str
    domain: str
    depth: ResearchDepth = ResearchDepth.STANDARD
    priority: int = 5
    context: str = ""
    deadline: str = ""
    related_knowledge: tuple[str, ...] = ()
    output_format: str = "knowledge_note"
    verification_required: bool = True
    created_at: str = ""
    rq_tags: tuple[str, ...] = ()  # ("RQ1", "RQ4") — Research Question tags

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id is required")
        if not self.requesting_agent:
            raise ValueError("requesting_agent is required")
        if not self.question:
            raise ValueError("question is required")
        if not self.domain:
            raise ValueError("domain is required")
        if not (1 <= self.priority <= 10):
            raise ValueError(f"priority must be between 1 and 10, got {self.priority}")

    def to_dict(self) -> dict:
        """Serialiseer naar dictionary."""
        return {
            "request_id": self.request_id,
            "requesting_agent": self.requesting_agent,
            "question": self.question,
            "domain": self.domain,
            "depth": self.depth.value,
            "priority": self.priority,
            "context": self.context,
            "deadline": self.deadline,
            "related_knowledge": list(self.related_knowledge),
            "output_format": self.output_format,
            "verification_required": self.verification_required,
            "created_at": self.created_at,
            "rq_tags": list(self.rq_tags),
        }


@dataclass(frozen=True)
class ResearchResponse:
    """Antwoord op een research-opdracht."""

    request_id: str
    status: ResearchStatus = ResearchStatus.PENDING
    summary: str = ""
    knowledge_refs: tuple[str, ...] = ()
    grade: KnowledgeGrade = "SPECULATIVE"
    verification_pct: float = 0.0
    sources: tuple[str, ...] = ()
    completed_at: str = ""

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id is required")
        if not (0.0 <= self.verification_pct <= 100.0):
            raise ValueError(
                f"verification_pct must be between 0 and 100, " f"got {self.verification_pct}"
            )

    @property
    def is_complete(self) -> bool:
        """Check of het research-antwoord afgerond is."""
        return self.status == ResearchStatus.COMPLETED

    def to_dict(self) -> dict:
        """Serialiseer naar dictionary."""
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "summary": self.summary,
            "knowledge_refs": list(self.knowledge_refs),
            "grade": self.grade,
            "verification_pct": self.verification_pct,
            "sources": list(self.sources),
            "completed_at": self.completed_at,
        }


class ResearchQueue(ABC):
    """Abstract interface voor een research-queue."""

    @abstractmethod
    def submit(self, request: ResearchRequest) -> str:
        """Submit een research-opdracht. Retourneert request_id."""
        ...

    @abstractmethod
    def next(self) -> ResearchRequest | None:
        """Retourneert de hoogste-prioriteit PENDING opdracht, of None."""
        ...

    @abstractmethod
    def complete(self, request_id: str, response: ResearchResponse) -> None:
        """Markeer een opdracht als afgerond met response."""
        ...

    @abstractmethod
    def pending(self) -> list[ResearchRequest]:
        """Retourneert alle PENDING opdrachten."""
        ...

    @abstractmethod
    def by_agent(self, agent_name: str) -> list[ResearchRequest]:
        """Retourneert alle opdrachten van een specifieke agent."""
        ...

    @abstractmethod
    def get_response(self, request_id: str) -> ResearchResponse | None:
        """Retourneert de response voor een request_id, of None."""
        ...
