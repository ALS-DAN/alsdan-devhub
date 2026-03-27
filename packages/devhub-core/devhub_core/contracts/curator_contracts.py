"""
Curator Contracts — KnowledgeCurator communicatie-contracten.

Dataclasses voor kennis-curatie: artikelen, bevindingen, audit-rapporten, observaties.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class KnowledgeDomain(Enum):
    """Kerndomeinen voor KWP DEV kennisbank."""

    AI_ENGINEERING = "ai_engineering"
    CLAUDE_SPECIFIC = "claude_specific"
    PYTHON_ARCHITECTURE = "python_architecture"
    DEVELOPMENT_METHODOLOGY = "development_methodology"


class ObservationType(Enum):
    """Types observaties die de curator genereert."""

    GRADE_DEGRADATION = "grade_degradation"
    FRESHNESS_ALERT = "freshness_alert"
    SCOPE_VIOLATION = "scope_violation"
    INGEST_REJECTION = "ingest_rejection"
    HEALTH_DEGRADED = "health_degraded"
    DUPLICATE_DETECTED = "duplicate_detected"


class CurationVerdict(Enum):
    """Verdict van ingest-validatie."""

    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"


@dataclass(frozen=True)
class KnowledgeArticle:
    """Een kennisartikel voor opslag in de vectorstore.

    Representeert een gestructureerd stuk kennis met gradering,
    bronvermelding en optionele embedding.
    """

    article_id: str
    title: str
    content: str
    domain: KnowledgeDomain
    grade: Literal["GOLD", "SILVER", "BRONZE", "SPECULATIVE"] = "SPECULATIVE"
    sources: tuple[str, ...] = ()
    verification_pct: float = 0.0
    date: str = ""  # ISO 8601
    author: str = "researcher-agent"
    embedding: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if not self.article_id:
            raise ValueError("article_id is required")
        if not self.title:
            raise ValueError("title is required")
        if not self.content:
            raise ValueError("content is required")
        if not 0.0 <= self.verification_pct <= 100.0:
            raise ValueError(
                f"verification_pct must be between 0.0 and 100.0, got {self.verification_pct}"
            )

    def to_dict(self) -> dict:
        """Serialiseer naar dict."""
        return {
            "article_id": self.article_id,
            "title": self.title,
            "content": self.content,
            "domain": self.domain.value,
            "grade": self.grade,
            "sources": list(self.sources),
            "verification_pct": self.verification_pct,
            "date": self.date,
            "author": self.author,
        }

    def to_document_chunk(self) -> Any:
        """Converteer naar DocumentChunk voor vectorstore opslag."""
        from devhub_vectorstore.contracts.vectorstore_contracts import (
            DataZone,
            DocumentChunk,
        )

        metadata = (
            ("domain", self.domain.value),
            ("grade", self.grade),
            ("sources", "|".join(self.sources)),
            ("verification_pct", str(self.verification_pct)),
            ("date", self.date),
            ("author", self.author),
            ("title", self.title),
        )
        return DocumentChunk(
            chunk_id=self.article_id,
            content=self.content,
            zone=DataZone.OPEN,
            embedding=self.embedding,
            metadata=metadata,
            source_id=self.article_id,
            created_at=self.date,
        )


@dataclass(frozen=True)
class CurationFinding:
    """Een bevinding van de KnowledgeCurator."""

    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    category: Literal["sources", "grade", "scope", "freshness", "duplicate", "content"]
    description: str
    article_id: str = ""

    def __post_init__(self) -> None:
        if not self.description:
            raise ValueError("description is required")


@dataclass(frozen=True)
class CurationReport:
    """Rapport van de KnowledgeCurator na validatie van een kennisartikel."""

    article_id: str
    findings: tuple[CurationFinding, ...] = ()
    verdict: CurationVerdict = CurationVerdict.APPROVED

    def __post_init__(self) -> None:
        if not self.article_id:
            raise ValueError("article_id is required")
        # Auto-REJECTED bij CRITICAL finding
        has_critical = any(f.severity == "CRITICAL" for f in self.findings)
        if has_critical and self.verdict != CurationVerdict.REJECTED:
            object.__setattr__(self, "verdict", CurationVerdict.REJECTED)
        # Auto-NEEDS_REVISION bij ERROR finding
        has_error = any(f.severity == "ERROR" for f in self.findings)
        if has_error and self.verdict == CurationVerdict.APPROVED:
            object.__setattr__(self, "verdict", CurationVerdict.NEEDS_REVISION)

    @property
    def is_approved(self) -> bool:
        return self.verdict == CurationVerdict.APPROVED


@dataclass(frozen=True)
class KnowledgeHealthReport:
    """4-dimensie health audit rapport voor de kennisbank."""

    grading_distribution: dict[str, int] = field(default_factory=dict)
    freshness_score: float = 100.0  # 0-100, 100 = alles vers
    source_ratio_score: float = 100.0  # 0-100, 100 = diverse bronnen
    domain_coverage: dict[str, int] = field(default_factory=dict)
    overall_score: float = 100.0  # gewogen gemiddelde
    findings: tuple[CurationFinding, ...] = ()
    timestamp: str = ""  # ISO 8601

    def __post_init__(self) -> None:
        if not 0.0 <= self.overall_score <= 100.0:
            raise ValueError(
                f"overall_score must be between 0.0 and 100.0, got {self.overall_score}"
            )


@dataclass(frozen=True)
class Observation:
    """Een observatie gegenereerd door de curator of andere agents."""

    observation_id: str
    observation_type: ObservationType
    source_agent: str
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    payload: str = ""
    timestamp: str = ""  # ISO 8601
    resolved: bool = False

    def __post_init__(self) -> None:
        if not self.observation_id:
            raise ValueError("observation_id is required")
        if not self.source_agent:
            raise ValueError("source_agent is required")

    def to_dict(self) -> dict:
        return {
            "observation_id": self.observation_id,
            "observation_type": self.observation_type.value,
            "source_agent": self.source_agent,
            "severity": self.severity,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
        }
