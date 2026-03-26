"""
ChromaDB Adapter — Dev/test fallback voor de VectorStoreInterface.

Gebruikt ChromaDB als lightweight vectorstore. Geen externe services nodig.
ChromaDB is een optional dependency — import faalt met duidelijke melding
als het niet geinstalleerd is.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    RetrievalRequest,
    RetrievalResponse,
    SearchResult,
    TenantStrategy,
    VectorStoreHealth,
    VectorStoreInterface,
)

if TYPE_CHECKING:
    import chromadb


def _get_chromadb() -> type:
    """Lazy import chromadb met duidelijke error."""
    try:
        import chromadb as _chromadb

        return _chromadb
    except ImportError as e:
        if "No module named 'chromadb'" in str(e):
            raise ImportError(
                "chromadb is required for ChromaDBZonedStore. "
                "Install with: uv pip install 'devhub-vectorstore[chromadb]'"
            ) from None
        raise


class ChromaDBZonedStore(VectorStoreInterface):
    """ChromaDB-gebaseerde vectorstore met zone-isolatie.

    Elke DataZone krijgt een eigen ChromaDB collection.
    Geschikt voor development en testing — geen externe services nodig.
    """

    def __init__(
        self,
        zones: list[DataZone] | None = None,
        persist_directory: str | None = None,
        collection_prefix: str = "devhub",
        tenant_strategy: TenantStrategy = TenantStrategy.PER_ZONE,
    ) -> None:
        chromadb_mod = _get_chromadb()

        self._zones = zones or list(DataZone)
        self._prefix = collection_prefix
        self._tenant_strategy = tenant_strategy
        self._tenants: set[str] = set()

        if persist_directory:
            self._client: chromadb.ClientAPI = chromadb_mod.PersistentClient(path=persist_directory)
        else:
            self._client = chromadb_mod.EphemeralClient()

        self._collections: dict[DataZone, chromadb.Collection] = {}
        for zone in self._zones:
            col_name = f"{self._prefix}_{zone.value}"
            self._collections[zone] = self._client.get_or_create_collection(
                name=col_name,
                metadata={"hnsw:space": "cosine"},
            )

    def _collection_name(self, zone: DataZone) -> str:
        return f"{self._prefix}_{zone.value}"

    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Voeg één chunk toe aan de zone-collectie."""
        collection = self._collections[chunk.zone]
        kwargs: dict = {
            "ids": [chunk.chunk_id],
            "documents": [chunk.content],
        }
        if chunk.embedding is not None:
            kwargs["embeddings"] = [list(chunk.embedding)]
        metadata = chunk.metadata_dict
        if chunk.source_id:
            metadata["source_id"] = chunk.source_id
        if chunk.created_at:
            metadata["created_at"] = chunk.created_at
        if metadata:
            kwargs["metadatas"] = [metadata]
        collection.upsert(**kwargs)

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Voeg meerdere chunks toe, gegroepeerd per zone."""
        by_zone: dict[DataZone, list[DocumentChunk]] = {}
        for chunk in chunks:
            by_zone.setdefault(chunk.zone, []).append(chunk)

        count = 0
        for zone, zone_chunks in by_zone.items():
            collection = self._collections[zone]
            ids = [c.chunk_id for c in zone_chunks]
            documents = [c.content for c in zone_chunks]
            embeddings = None
            if any(c.embedding is not None for c in zone_chunks):
                embeddings = [
                    list(c.embedding) if c.embedding is not None else [] for c in zone_chunks
                ]
            metadatas = []
            for c in zone_chunks:
                md = c.metadata_dict
                if c.source_id:
                    md["source_id"] = c.source_id
                if c.created_at:
                    md["created_at"] = c.created_at
                metadatas.append(md if md else None)

            kwargs: dict = {"ids": ids, "documents": documents}
            if any(m is not None for m in metadatas):
                # ChromaDB rejects empty dicts, use None for chunks without metadata
                kwargs["metadatas"] = metadatas
            if embeddings:
                kwargs["embeddings"] = embeddings
            collection.upsert(**kwargs)
            count += len(zone_chunks)

        return count

    def query(self, request: RetrievalRequest) -> RetrievalResponse:
        """Zoek chunks in zone-collecties."""
        start = time.monotonic()

        target_zones = [request.zone] if request.zone else list(self._collections.keys())
        all_results: list[SearchResult] = []

        for zone in target_zones:
            collection = self._collections.get(zone)
            if collection is None:
                continue

            query_kwargs: dict = {"n_results": request.limit}

            if request.query_embedding is not None:
                query_kwargs["query_embeddings"] = [list(request.query_embedding)]
            elif request.query_text:
                query_kwargs["query_texts"] = [request.query_text]

            if request.metadata_filter:
                where = {k: v for k, v in request.metadata_filter}
                if where:
                    query_kwargs["where"] = where

            try:
                results = collection.query(**query_kwargs)
            except Exception:
                continue

            if not results or not results["ids"] or not results["ids"][0]:
                continue

            ids = results["ids"][0]
            documents = results["documents"][0] if results.get("documents") else [None] * len(ids)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)

            for i, chunk_id in enumerate(ids):
                # ChromaDB returns distances (lower = better), convert to similarity score
                distance = distances[i] if distances[i] is not None else 0.0
                score = max(0.0, min(1.0, 1.0 - distance))

                if score < request.min_score:
                    continue

                md = metadatas[i] or {}
                source_id = md.pop("source_id", "")
                created_at = md.pop("created_at", "")
                metadata_tuples = tuple((k, str(v)) for k, v in md.items())

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=documents[i] or "",
                    zone=zone,
                    metadata=metadata_tuples,
                    source_id=source_id,
                    created_at=created_at,
                )
                all_results.append(SearchResult(chunk=chunk, score=score))

        # Sort by score descending, limit
        all_results.sort(key=lambda r: r.score, reverse=True)
        limited = all_results[: request.limit]

        duration_ms = (time.monotonic() - start) * 1000

        return RetrievalResponse(
            results=tuple(limited),
            total_found=len(all_results),
            query_duration_ms=round(duration_ms, 2),
        )

    def count(self) -> int:
        """Tel totaal aantal chunks over alle collecties."""
        return sum(col.count() for col in self._collections.values())

    def count_by_zone(self) -> dict[DataZone, int]:
        """Tel chunks per zone."""
        return {zone: col.count() for zone, col in self._collections.items()}

    def reset(self) -> None:
        """Wis alle data en herinitialiseer collecties."""
        for zone, col in self._collections.items():
            col_name = col.name
            self._client.delete_collection(col_name)
            self._collections[zone] = self._client.get_or_create_collection(
                name=col_name,
                metadata={"hnsw:space": "cosine"},
            )
        self._tenants.clear()

    def ensure_tenant(self, tenant_id: str) -> None:
        """Registreer een tenant. Bij PER_ZONE strategie is dit metadata-based."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        self._tenants.add(tenant_id)

    def list_tenants(self) -> list[str]:
        """Lijst alle geregistreerde tenants."""
        return sorted(self._tenants)

    def health(self) -> VectorStoreHealth:
        """Retourneer gezondheidsstatus van de ChromaDB backend."""
        try:
            total = self.count()
            return VectorStoreHealth(
                status="UP",
                backend="chromadb",
                collection_count=len(self._collections),
                total_chunks=total,
                tenant_count=len(self._tenants),
            )
        except Exception:
            return VectorStoreHealth(
                status="DOWN",
                backend="chromadb",
            )
