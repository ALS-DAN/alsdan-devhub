"""
VectorStore Contracts — Vendor-free interface en dataclasses voor vectordatabases.

Design: Contract-first (conform NodeInterface patroon), frozen dataclasses (immutability).
Geen externe library-types in contracts — adapters vertalen naar vendor-specifiek formaat.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class DataZone(Enum):
    """Data-isolatie zone — generiek, configureerbaar per product.

    Producten mappen hun eigen zones op deze generieke waarden.
    Voorbeeld: BORIS Red → RESTRICTED, Yellow → CONTROLLED, Green → OPEN.
    """

    RESTRICTED = "restricted"
    CONTROLLED = "controlled"
    OPEN = "open"


class TenantStrategy(Enum):
    """Multi-tenancy strategie voor vectorstore collecties.

    PER_ZONE: Elke zone is een aparte collectie (standaard).
    PER_KWP: Weaviate native tenant-sharding binnen collecties.
    """

    PER_ZONE = "per_zone"
    PER_KWP = "per_kwp"


@dataclass(frozen=True)
class DocumentChunk:
    """Een document-chunk met optionele embedding voor opslag in een vectorstore.

    Metadata is opgeslagen als tuple van key-value pairs voor echte immutability
    op frozen dataclasses. Gebruik de `metadata_dict` property voor gemak.
    """

    chunk_id: str
    content: str
    zone: DataZone
    embedding: tuple[float, ...] | None = None
    metadata: tuple[tuple[str, str], ...] = ()
    source_id: str = ""
    created_at: str = ""  # ISO 8601

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise ValueError("chunk_id is required")
        if not self.content:
            raise ValueError("content is required")

    @property
    def metadata_dict(self) -> dict[str, str]:
        """Metadata als dict voor gemakkelijke toegang."""
        return dict(self.metadata)


@dataclass(frozen=True)
class RetrievalRequest:
    """Verzoek om chunks op te halen uit de vectorstore.

    query_embedding kan None zijn als de adapter zelf embeddings berekent
    (bijv. ChromaDB met ingebouwde embeddings).
    """

    query_text: str = ""
    query_embedding: tuple[float, ...] | None = None
    zone: DataZone | None = None  # None = zoek over alle zones
    limit: int = 10
    min_score: float = 0.0
    tenant_id: str = ""
    metadata_filter: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.query_text and self.query_embedding is None:
            raise ValueError("Either query_text or query_embedding is required")
        if self.limit < 1:
            raise ValueError(f"limit must be >= 1, got {self.limit}")
        if not 0.0 <= self.min_score <= 1.0:
            raise ValueError(f"min_score must be 0.0-1.0, got {self.min_score}")


@dataclass(frozen=True)
class SearchResult:
    """Eén zoekresultaat: een chunk met relevantiescore."""

    chunk: DocumentChunk
    score: float  # 0.0 - 1.0 (cosine similarity)

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be 0.0-1.0, got {self.score}")


@dataclass(frozen=True)
class RetrievalResponse:
    """Antwoord op een RetrievalRequest."""

    results: tuple[SearchResult, ...] = ()
    total_found: int = 0
    query_duration_ms: float = 0.0

    def __post_init__(self) -> None:
        if self.total_found < 0:
            raise ValueError(f"total_found must be >= 0, got {self.total_found}")
        if self.query_duration_ms < 0.0:
            raise ValueError(f"query_duration_ms must be >= 0.0, got {self.query_duration_ms}")


@dataclass(frozen=True)
class VectorStoreHealth:
    """Gezondheidsstatus van een vectorstore backend."""

    status: Literal["UP", "DEGRADED", "DOWN"]
    backend: str  # e.g. "chromadb", "weaviate"
    collection_count: int = 0
    total_chunks: int = 0
    tenant_count: int = 0

    def __post_init__(self) -> None:
        if not self.backend:
            raise ValueError("backend is required")
        if self.collection_count < 0:
            raise ValueError(f"collection_count must be >= 0, got {self.collection_count}")
        if self.total_chunks < 0:
            raise ValueError(f"total_chunks must be >= 0, got {self.total_chunks}")


class VectorStoreInterface(ABC):
    """Abstract contract voor vectorstore backends.

    Elke vectorstore-implementatie (ChromaDB, Weaviate) implementeert
    deze interface. Conform NodeInterface patroon: vendor-free, frozen types.
    """

    @abstractmethod
    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Voeg één chunk toe aan de vectorstore."""
        ...

    @abstractmethod
    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Voeg meerdere chunks toe. Retourneert aantal succesvol toegevoegd."""
        ...

    @abstractmethod
    def query(self, request: RetrievalRequest) -> RetrievalResponse:
        """Zoek chunks op basis van een RetrievalRequest."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Tel het totaal aantal chunks in de store."""
        ...

    @abstractmethod
    def count_by_zone(self) -> dict[DataZone, int]:
        """Tel chunks per DataZone."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Wis alle data en herinitialiseer collecties."""
        ...

    @abstractmethod
    def ensure_tenant(self, tenant_id: str) -> None:
        """Zorg dat een tenant bestaat (maak aan indien nodig)."""
        ...

    @abstractmethod
    def list_tenants(self) -> list[str]:
        """Lijst alle bekende tenants."""
        ...

    @abstractmethod
    def health(self) -> VectorStoreHealth:
        """Retourneer de gezondheidsstatus van de vectorstore."""
        ...


class EmbeddingProvider(ABC):
    """Abstract contract voor embedding-berekening.

    Voorbereid voor Sprint 5. Adapters kunnen optioneel een EmbeddingProvider
    gebruiken om embeddings te berekenen vóór opslag.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensie van de embedding-vector (bijv. 384, 1024)."""
        ...

    @abstractmethod
    def embed_text(self, text: str) -> tuple[float, ...]:
        """Bereken embedding voor één tekst."""
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        """Bereken embeddings voor meerdere teksten."""
        ...
