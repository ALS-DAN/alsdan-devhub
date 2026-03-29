"""
Pipeline Contracts — Communicatie-contracten voor de documentatie-productie pipeline.

Verbindt devhub-vectorstore, devhub-documents en devhub-storage tot een
orkestratieketen. Frozen voor immutability (conform ADR-049 pattern).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from devhub_documents.contracts import DocumentCategory, DocumentFormat, DocumentResult


class PublishStatus(Enum):
    """Status van publicatie naar storage backend."""

    PENDING = "pending"
    PUBLISHED = "published"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class FolderRoute:
    """Mapping van categorie naar storage-pad voor een specifieke node."""

    category: str
    storage_path: str
    node_id: str = "devhub"

    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("category is required")
        if not self.storage_path:
            raise ValueError("storage_path is required")


@dataclass(frozen=True)
class DocumentProductionRequest:
    """Input voor de DocumentService productie-pipeline.

    Beschrijft wat geproduceerd moet worden: onderwerp, categorie,
    doelnode, en optionele vectorstore-query.
    """

    topic: str
    category: DocumentCategory
    target_node: str = "devhub"
    output_format: DocumentFormat = DocumentFormat.MARKDOWN
    audience: str = "developer"
    knowledge_query: str = ""
    skip_vectorstore: bool = False

    def __post_init__(self) -> None:
        if not self.topic or not self.topic.strip():
            raise ValueError("topic is required and cannot be empty")

    @property
    def effective_query(self) -> str:
        """De query voor vectorstore: knowledge_query als opgegeven, anders topic."""
        return self.knowledge_query if self.knowledge_query else self.topic


@dataclass(frozen=True)
class KnowledgeContext:
    """Kennis opgehaald uit de vectorstore als input voor document-generatie."""

    chunks: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    query_used: str = ""
    total_found: int = 0

    @property
    def has_content(self) -> bool:
        """Of er bruikbare kennis is opgehaald."""
        return len(self.chunks) > 0


@dataclass(frozen=True)
class DocumentProductionResult:
    """Output van de complete productie-pipeline.

    Bevat het gegenereerde document, de storage-locatie, publicatie-status,
    en optioneel de kennis-context die als input diende.
    """

    document_result: DocumentResult
    storage_path: str
    publish_status: PublishStatus
    knowledge_context: KnowledgeContext | None = None
    node_id: str = "devhub"
    message: str = ""

    def __post_init__(self) -> None:
        if not self.storage_path or not self.storage_path.strip():
            raise ValueError("storage_path is required and cannot be empty")


# ---------------------------------------------------------------------------
# Research Proposal — Stroom 2 governance queue item
# ---------------------------------------------------------------------------


class ProposalStatus(Enum):
    """Status van een research-voorstel in de governance queue."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


def _default_proposal_id() -> str:
    return f"rp-{uuid.uuid4().hex[:8]}"


def _default_created_at() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class ResearchProposal:
    """Voorstel voor kennisonderzoek — voor stroom 2 (goedkeuring) en stroom 3 (direct).

    Geschreven naar config/research_queue.yml, gelezen door dashboard.
    """

    topic: str
    domain: str
    requesting_agent: str = ""
    rationale: str = ""
    priority: int = 3
    proposed_depth: str = "STANDARD"  # QUICK, STANDARD, DEEP
    stream: Literal[1, 2, 3] = 2
    status: ProposalStatus = ProposalStatus.PENDING
    proposal_id: str = field(default_factory=_default_proposal_id)
    created_at: str = field(default_factory=_default_created_at)
    approved_at: str = ""
    completed_at: str = ""

    def __post_init__(self) -> None:
        if not self.topic or not self.topic.strip():
            raise ValueError("topic is required")
        if not self.domain or not self.domain.strip():
            raise ValueError("domain is required")
        if self.stream not in (1, 2, 3):
            raise ValueError(f"stream must be 1, 2, or 3, got {self.stream}")
