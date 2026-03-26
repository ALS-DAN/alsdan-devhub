"""Tests voor VectorStore contracts — frozen dataclasses, enums, ABC's."""

import pytest

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


# ---------------------------------------------------------------------------
# DataZone Enum
# ---------------------------------------------------------------------------


class TestDataZone:
    def test_values(self):
        assert DataZone.RESTRICTED.value == "restricted"
        assert DataZone.CONTROLLED.value == "controlled"
        assert DataZone.OPEN.value == "open"

    def test_member_count(self):
        assert len(DataZone) == 3


# ---------------------------------------------------------------------------
# TenantStrategy Enum
# ---------------------------------------------------------------------------


class TestTenantStrategy:
    def test_values(self):
        assert TenantStrategy.PER_ZONE.value == "per_zone"
        assert TenantStrategy.PER_KWP.value == "per_kwp"

    def test_member_count(self):
        assert len(TenantStrategy) == 2


# ---------------------------------------------------------------------------
# DocumentChunk
# ---------------------------------------------------------------------------


class TestDocumentChunk:
    def test_valid_chunk(self):
        chunk = DocumentChunk(
            chunk_id="C001",
            content="Test content",
            zone=DataZone.OPEN,
            source_id="doc-1",
        )
        assert chunk.chunk_id == "C001"
        assert chunk.zone == DataZone.OPEN

    def test_with_embedding(self):
        chunk = DocumentChunk(
            chunk_id="C002",
            content="Test",
            zone=DataZone.RESTRICTED,
            embedding=(0.1, 0.2, 0.3),
        )
        assert chunk.embedding == (0.1, 0.2, 0.3)
        assert len(chunk.embedding) == 3

    def test_with_metadata(self):
        chunk = DocumentChunk(
            chunk_id="C003",
            content="Test",
            zone=DataZone.CONTROLLED,
            metadata=(("author", "niels"), ("version", "1.0")),
        )
        assert chunk.metadata_dict == {"author": "niels", "version": "1.0"}

    def test_empty_metadata_dict(self):
        chunk = DocumentChunk(chunk_id="C004", content="Test", zone=DataZone.OPEN)
        assert chunk.metadata_dict == {}

    def test_frozen(self):
        chunk = DocumentChunk(chunk_id="C005", content="Test", zone=DataZone.OPEN)
        with pytest.raises(AttributeError):
            chunk.chunk_id = "C999"  # type: ignore[misc]

    def test_empty_chunk_id(self):
        with pytest.raises(ValueError, match="chunk_id"):
            DocumentChunk(chunk_id="", content="Test", zone=DataZone.OPEN)

    def test_empty_content(self):
        with pytest.raises(ValueError, match="content"):
            DocumentChunk(chunk_id="C006", content="", zone=DataZone.OPEN)

    def test_defaults(self):
        chunk = DocumentChunk(chunk_id="C007", content="Test", zone=DataZone.OPEN)
        assert chunk.embedding is None
        assert chunk.metadata == ()
        assert chunk.source_id == ""
        assert chunk.created_at == ""


# ---------------------------------------------------------------------------
# RetrievalRequest
# ---------------------------------------------------------------------------


class TestRetrievalRequest:
    def test_with_query_text(self):
        req = RetrievalRequest(query_text="zoekterm")
        assert req.query_text == "zoekterm"
        assert req.limit == 10

    def test_with_query_embedding(self):
        req = RetrievalRequest(query_embedding=(0.1, 0.2, 0.3))
        assert req.query_embedding == (0.1, 0.2, 0.3)

    def test_with_zone_filter(self):
        req = RetrievalRequest(query_text="test", zone=DataZone.RESTRICTED)
        assert req.zone == DataZone.RESTRICTED

    def test_no_query_raises(self):
        with pytest.raises(ValueError, match="Either query_text or query_embedding"):
            RetrievalRequest()

    def test_invalid_limit(self):
        with pytest.raises(ValueError, match="limit"):
            RetrievalRequest(query_text="test", limit=0)

    def test_invalid_min_score_high(self):
        with pytest.raises(ValueError, match="min_score"):
            RetrievalRequest(query_text="test", min_score=1.5)

    def test_invalid_min_score_negative(self):
        with pytest.raises(ValueError, match="min_score"):
            RetrievalRequest(query_text="test", min_score=-0.1)

    def test_frozen(self):
        req = RetrievalRequest(query_text="test")
        with pytest.raises(AttributeError):
            req.limit = 5  # type: ignore[misc]

    def test_metadata_filter(self):
        req = RetrievalRequest(
            query_text="test",
            metadata_filter=(("author", "niels"),),
        )
        assert req.metadata_filter == (("author", "niels"),)


# ---------------------------------------------------------------------------
# SearchResult
# ---------------------------------------------------------------------------


class TestSearchResult:
    def test_valid(self):
        chunk = DocumentChunk(chunk_id="C001", content="Test", zone=DataZone.OPEN)
        result = SearchResult(chunk=chunk, score=0.95)
        assert result.score == 0.95
        assert result.chunk.chunk_id == "C001"

    def test_score_too_high(self):
        chunk = DocumentChunk(chunk_id="C001", content="Test", zone=DataZone.OPEN)
        with pytest.raises(ValueError, match="score"):
            SearchResult(chunk=chunk, score=1.5)

    def test_score_negative(self):
        chunk = DocumentChunk(chunk_id="C001", content="Test", zone=DataZone.OPEN)
        with pytest.raises(ValueError, match="score"):
            SearchResult(chunk=chunk, score=-0.1)

    def test_frozen(self):
        chunk = DocumentChunk(chunk_id="C001", content="Test", zone=DataZone.OPEN)
        result = SearchResult(chunk=chunk, score=0.5)
        with pytest.raises(AttributeError):
            result.score = 0.9  # type: ignore[misc]

    def test_boundary_scores(self):
        chunk = DocumentChunk(chunk_id="C001", content="Test", zone=DataZone.OPEN)
        assert SearchResult(chunk=chunk, score=0.0).score == 0.0
        assert SearchResult(chunk=chunk, score=1.0).score == 1.0


# ---------------------------------------------------------------------------
# RetrievalResponse
# ---------------------------------------------------------------------------


class TestRetrievalResponse:
    def test_empty_response(self):
        resp = RetrievalResponse()
        assert resp.results == ()
        assert resp.total_found == 0

    def test_with_results(self):
        chunk = DocumentChunk(chunk_id="C001", content="Test", zone=DataZone.OPEN)
        result = SearchResult(chunk=chunk, score=0.9)
        resp = RetrievalResponse(results=(result,), total_found=1, query_duration_ms=5.2)
        assert len(resp.results) == 1
        assert resp.query_duration_ms == 5.2

    def test_negative_total_found(self):
        with pytest.raises(ValueError, match="total_found"):
            RetrievalResponse(total_found=-1)

    def test_negative_duration(self):
        with pytest.raises(ValueError, match="query_duration_ms"):
            RetrievalResponse(query_duration_ms=-1.0)

    def test_frozen(self):
        resp = RetrievalResponse()
        with pytest.raises(AttributeError):
            resp.total_found = 5  # type: ignore[misc]


# ---------------------------------------------------------------------------
# VectorStoreHealth
# ---------------------------------------------------------------------------


class TestVectorStoreHealth:
    def test_valid(self):
        h = VectorStoreHealth(status="UP", backend="chromadb", collection_count=3, total_chunks=100)
        assert h.status == "UP"
        assert h.backend == "chromadb"

    def test_empty_backend(self):
        with pytest.raises(ValueError, match="backend"):
            VectorStoreHealth(status="UP", backend="")

    def test_negative_collection_count(self):
        with pytest.raises(ValueError, match="collection_count"):
            VectorStoreHealth(status="UP", backend="chromadb", collection_count=-1)

    def test_negative_total_chunks(self):
        with pytest.raises(ValueError, match="total_chunks"):
            VectorStoreHealth(status="UP", backend="chromadb", total_chunks=-1)

    def test_frozen(self):
        h = VectorStoreHealth(status="UP", backend="chromadb")
        with pytest.raises(AttributeError):
            h.status = "DOWN"  # type: ignore[misc]

    def test_defaults(self):
        h = VectorStoreHealth(status="DOWN", backend="weaviate")
        assert h.collection_count == 0
        assert h.total_chunks == 0
        assert h.tenant_count == 0


# ---------------------------------------------------------------------------
# VectorStoreInterface ABC
# ---------------------------------------------------------------------------


class TestVectorStoreInterface:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            VectorStoreInterface()  # type: ignore[abstract]

    def test_has_all_abstract_methods(self):
        abstract_methods = VectorStoreInterface.__abstractmethods__
        expected = {
            "add_chunk",
            "add_chunks",
            "query",
            "count",
            "count_by_zone",
            "reset",
            "ensure_tenant",
            "list_tenants",
            "health",
        }
        assert abstract_methods == expected


# ---------------------------------------------------------------------------
# EmbeddingProvider ABC
# ---------------------------------------------------------------------------


class TestEmbeddingProvider:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            EmbeddingProvider()  # type: ignore[abstract]

    def test_has_all_abstract_methods(self):
        abstract_methods = EmbeddingProvider.__abstractmethods__
        expected = {"dimension", "embed_text", "embed_batch"}
        assert abstract_methods == expected
