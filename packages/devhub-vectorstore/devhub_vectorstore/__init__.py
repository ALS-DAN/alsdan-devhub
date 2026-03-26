"""DevHub Vectorstore — interface and adapters for vector databases."""

from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    EmbeddingProvider,
    RetrievalRequest,
    RetrievalResponse,
    SearchResult,
    TenantStrategy,
    VectorStoreHealth,
    VectorStoreInterface,
)
from devhub_vectorstore.factory import VectorStoreFactory

__version__ = "0.3.0"

__all__ = [
    "DataZone",
    "DocumentChunk",
    "EmbeddingProvider",
    "RetrievalRequest",
    "RetrievalResponse",
    "SearchResult",
    "TenantStrategy",
    "VectorStoreFactory",
    "VectorStoreHealth",
    "VectorStoreInterface",
]
