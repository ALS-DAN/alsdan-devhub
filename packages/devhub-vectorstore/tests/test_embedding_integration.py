"""Integratie-tests: embed → store → retrieve roundtrip met ChromaDB + HashEmbeddingProvider."""

from __future__ import annotations

import uuid

from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    RetrievalRequest,
)
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


class TestEmbeddingIntegration:
    """Roundtrip tests: embed tekst → store in ChromaDB → retrieve."""

    def _setup(self) -> tuple[HashEmbeddingProvider, ChromaDBZonedStore]:
        provider = HashEmbeddingProvider(dimension=384)
        prefix = f"test_emb_{uuid.uuid4().hex[:8]}"
        store = ChromaDBZonedStore(zones=[DataZone.OPEN], collection_prefix=prefix)
        return provider, store

    def test_embed_and_store_chunk(self) -> None:
        provider, store = self._setup()
        embedding = provider.embed_text("DevHub kennispipeline documentatie")

        chunk = DocumentChunk(
            chunk_id="int-001",
            content="DevHub kennispipeline documentatie",
            zone=DataZone.OPEN,
            embedding=embedding,
        )
        store.add_chunk(chunk)
        assert store.count() == 1

    def test_embed_and_query_similar(self) -> None:
        provider, store = self._setup()

        # Store een chunk met embedding
        text = "Python development patronen en best practices"
        embedding = provider.embed_text(text)
        chunk = DocumentChunk(
            chunk_id="int-002",
            content=text,
            zone=DataZone.OPEN,
            embedding=embedding,
        )
        store.add_chunk(chunk)

        # Query met dezelfde tekst → moet zichzelf vinden
        query_embedding = provider.embed_text(text)
        request = RetrievalRequest(
            query_text=text,
            query_embedding=query_embedding,
            zone=DataZone.OPEN,
            limit=5,
        )
        response = store.query(request)
        assert len(response.results) >= 1
        assert response.results[0].chunk.chunk_id == "int-002"

    def test_embed_batch_and_store(self) -> None:
        provider, store = self._setup()

        texts = [
            "Weaviate vectorstore configuratie",
            "ChromaDB lokale development setup",
            "Embedding providers voor NLP",
        ]
        embeddings = provider.embed_batch(texts)

        chunks = [
            DocumentChunk(
                chunk_id=f"int-batch-{i}",
                content=text,
                zone=DataZone.OPEN,
                embedding=emb,
            )
            for i, (text, emb) in enumerate(zip(texts, embeddings, strict=True))
        ]
        count = store.add_chunks(chunks)
        assert count == 3
        assert store.count() == 3

    def test_end_to_end_roundtrip(self) -> None:
        provider, store = self._setup()

        # 1. Embed
        text = "Sprint planning met Shape Up methodiek"
        embedding = provider.embed_text(text)
        assert len(embedding) == provider.dimension

        # 2. Store
        chunk = DocumentChunk(
            chunk_id="roundtrip-001",
            content=text,
            zone=DataZone.OPEN,
            embedding=embedding,
            metadata=(("domain", "shape-up"), ("grade", "SILVER")),
        )
        store.add_chunk(chunk)

        # 3. Retrieve
        query_emb = provider.embed_text(text)
        response = store.query(
            RetrievalRequest(
                query_embedding=query_emb,
                zone=DataZone.OPEN,
                limit=1,
            )
        )

        # 4. Verify
        assert len(response.results) == 1
        result = response.results[0]
        assert result.chunk.chunk_id == "roundtrip-001"
        assert result.chunk.content == text
