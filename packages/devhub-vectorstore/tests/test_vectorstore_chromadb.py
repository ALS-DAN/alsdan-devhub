"""Tests voor ChromaDBZonedStore — dev/test vectorstore adapter."""

import uuid

import pytest

from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    RetrievalRequest,
)
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store() -> ChromaDBZonedStore:
    """Ephemeral ChromaDB store met alle zones — unieke prefix per test voor isolatie."""
    prefix = f"test_{uuid.uuid4().hex[:8]}"
    s = ChromaDBZonedStore(
        zones=[DataZone.RESTRICTED, DataZone.CONTROLLED, DataZone.OPEN],
        collection_prefix=prefix,
    )
    yield s
    s.reset()


@pytest.fixture
def sample_chunk() -> DocumentChunk:
    return DocumentChunk(
        chunk_id="C001",
        content="Autisme-vriendelijk wonen vereist prikkelarm ontwerp.",
        zone=DataZone.OPEN,
        source_id="doc-1",
        metadata=(("domain", "autisme"), ("author", "niels")),
    )


@pytest.fixture
def restricted_chunk() -> DocumentChunk:
    return DocumentChunk(
        chunk_id="C002",
        content="Vertrouwelijk medisch dossier — alleen voor behandelaar.",
        zone=DataZone.RESTRICTED,
        source_id="doc-2",
    )


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestInitialization:
    def test_creates_collections_for_all_zones(self, store: ChromaDBZonedStore):
        assert len(store._collections) == 3

    def test_default_zones(self):
        s = ChromaDBZonedStore()
        assert len(s._collections) == len(DataZone)

    def test_custom_prefix(self):
        s = ChromaDBZonedStore(collection_prefix="boris")
        for zone, col in s._collections.items():
            assert col.name == f"boris_{zone.value}"

    def test_custom_zones(self):
        s = ChromaDBZonedStore(zones=[DataZone.OPEN])
        assert len(s._collections) == 1
        assert DataZone.OPEN in s._collections


# ---------------------------------------------------------------------------
# add_chunk + query
# ---------------------------------------------------------------------------


class TestAddAndQuery:
    def test_add_and_retrieve(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        resp = store.query(RetrievalRequest(query_text="autisme wonen", zone=DataZone.OPEN))
        assert resp.total_found >= 1
        assert resp.results[0].chunk.chunk_id == "C001"

    def test_query_returns_metadata(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        resp = store.query(RetrievalRequest(query_text="autisme", zone=DataZone.OPEN))
        chunk = resp.results[0].chunk
        assert chunk.source_id == "doc-1"
        md = chunk.metadata_dict
        assert md.get("domain") == "autisme"
        assert md.get("author") == "niels"

    def test_score_range(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        resp = store.query(RetrievalRequest(query_text="autisme", zone=DataZone.OPEN))
        for result in resp.results:
            assert 0.0 <= result.score <= 1.0

    def test_query_empty_store(self, store: ChromaDBZonedStore):
        resp = store.query(RetrievalRequest(query_text="iets", zone=DataZone.OPEN))
        assert resp.total_found == 0
        assert resp.results == ()

    def test_upsert_updates_existing(self, store: ChromaDBZonedStore):
        chunk_v1 = DocumentChunk(chunk_id="C010", content="Versie 1", zone=DataZone.OPEN)
        chunk_v2 = DocumentChunk(chunk_id="C010", content="Versie 2 bijgewerkt", zone=DataZone.OPEN)
        store.add_chunk(chunk_v1)
        store.add_chunk(chunk_v2)
        assert store.count() == 1
        resp = store.query(RetrievalRequest(query_text="bijgewerkt", zone=DataZone.OPEN))
        assert "Versie 2" in resp.results[0].chunk.content


# ---------------------------------------------------------------------------
# Zone isolatie
# ---------------------------------------------------------------------------


class TestZoneIsolation:
    def test_chunk_not_visible_in_other_zone(
        self,
        store: ChromaDBZonedStore,
        sample_chunk: DocumentChunk,
        restricted_chunk: DocumentChunk,
    ):
        store.add_chunk(sample_chunk)  # OPEN
        store.add_chunk(restricted_chunk)  # RESTRICTED

        resp_open = store.query(RetrievalRequest(query_text="medisch dossier", zone=DataZone.OPEN))
        # The restricted chunk should NOT appear in OPEN zone results
        restricted_ids = [r.chunk.chunk_id for r in resp_open.results]
        assert "C002" not in restricted_ids

    def test_query_all_zones(
        self,
        store: ChromaDBZonedStore,
        sample_chunk: DocumentChunk,
        restricted_chunk: DocumentChunk,
    ):
        store.add_chunk(sample_chunk)
        store.add_chunk(restricted_chunk)
        # zone=None zoekt over alle zones
        resp = store.query(RetrievalRequest(query_text="dossier wonen", zone=None))
        assert resp.total_found >= 1


# ---------------------------------------------------------------------------
# add_chunks batch
# ---------------------------------------------------------------------------


class TestAddChunks:
    def test_batch_add(self, store: ChromaDBZonedStore):
        chunks = [
            DocumentChunk(chunk_id=f"B{i}", content=f"Batch content {i}", zone=DataZone.OPEN)
            for i in range(5)
        ]
        count = store.add_chunks(chunks)
        assert count == 5
        assert store.count() == 5

    def test_batch_multiple_zones(self, store: ChromaDBZonedStore):
        chunks = [
            DocumentChunk(chunk_id="MZ1", content="Open data", zone=DataZone.OPEN),
            DocumentChunk(chunk_id="MZ2", content="Restricted data", zone=DataZone.RESTRICTED),
            DocumentChunk(chunk_id="MZ3", content="Controlled data", zone=DataZone.CONTROLLED),
        ]
        count = store.add_chunks(chunks)
        assert count == 3
        counts = store.count_by_zone()
        assert counts[DataZone.OPEN] == 1
        assert counts[DataZone.RESTRICTED] == 1
        assert counts[DataZone.CONTROLLED] == 1


# ---------------------------------------------------------------------------
# count / count_by_zone
# ---------------------------------------------------------------------------


class TestCounting:
    def test_count_empty(self, store: ChromaDBZonedStore):
        assert store.count() == 0

    def test_count_by_zone_empty(self, store: ChromaDBZonedStore):
        counts = store.count_by_zone()
        assert all(v == 0 for v in counts.values())
        assert len(counts) == 3

    def test_count_after_add(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        assert store.count() == 1
        assert store.count_by_zone()[DataZone.OPEN] == 1
        assert store.count_by_zone()[DataZone.RESTRICTED] == 0


# ---------------------------------------------------------------------------
# reset
# ---------------------------------------------------------------------------


class TestReset:
    def test_reset_clears_all(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        assert store.count() == 1
        store.reset()
        assert store.count() == 0

    def test_reset_clears_tenants(self, store: ChromaDBZonedStore):
        store.ensure_tenant("tenant-1")
        store.reset()
        assert store.list_tenants() == []

    def test_usable_after_reset(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        store.reset()
        store.add_chunk(sample_chunk)
        assert store.count() == 1


# ---------------------------------------------------------------------------
# Tenants
# ---------------------------------------------------------------------------


class TestTenants:
    def test_ensure_tenant(self, store: ChromaDBZonedStore):
        store.ensure_tenant("kwp-dev")
        assert "kwp-dev" in store.list_tenants()

    def test_list_tenants_sorted(self, store: ChromaDBZonedStore):
        store.ensure_tenant("beta")
        store.ensure_tenant("alpha")
        assert store.list_tenants() == ["alpha", "beta"]

    def test_duplicate_tenant(self, store: ChromaDBZonedStore):
        store.ensure_tenant("kwp-dev")
        store.ensure_tenant("kwp-dev")
        assert store.list_tenants() == ["kwp-dev"]

    def test_empty_tenant_id_raises(self, store: ChromaDBZonedStore):
        with pytest.raises(ValueError, match="tenant_id"):
            store.ensure_tenant("")

    def test_list_empty(self, store: ChromaDBZonedStore):
        assert store.list_tenants() == []


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_healthy_store(self, store: ChromaDBZonedStore):
        h = store.health()
        assert h.status == "UP"
        assert h.backend == "chromadb"
        assert h.collection_count == 3
        assert h.total_chunks == 0

    def test_health_with_data(self, store: ChromaDBZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        h = store.health()
        assert h.total_chunks == 1

    def test_health_with_tenants(self, store: ChromaDBZonedStore):
        store.ensure_tenant("t1")
        store.ensure_tenant("t2")
        h = store.health()
        assert h.tenant_count == 2


# ---------------------------------------------------------------------------
# Query met min_score filter
# ---------------------------------------------------------------------------


class TestMinScoreFilter:
    def test_min_score_filters_low_matches(self, store: ChromaDBZonedStore):
        store.add_chunk(
            DocumentChunk(chunk_id="MS1", content="Python programming language", zone=DataZone.OPEN)
        )
        # Query met hoge min_score
        resp = store.query(
            RetrievalRequest(
                query_text="completely unrelated topic xyz",
                zone=DataZone.OPEN,
                min_score=0.99,
            )
        )
        # Met zo'n hoge drempel zou er weinig/niets moeten matchen
        for r in resp.results:
            assert r.score >= 0.99
