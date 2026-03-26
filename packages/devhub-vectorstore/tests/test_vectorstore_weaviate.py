"""Tests voor WeaviateZonedStore — mocked Weaviate client tests.

Geen Weaviate server nodig — alle interacties zijn gemocked.
Volgt zelfde structuur als test_vectorstore_chromadb.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest

from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    RetrievalRequest,
    TenantStrategy,
)
from devhub_vectorstore.adapters.weaviate_adapter import WeaviateZonedStore


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


@dataclass
class MockMetadata:
    """Mock Weaviate object metadata."""

    distance: float | None = 0.1


@dataclass
class MockObject:
    """Mock Weaviate query result object."""

    uuid: str = "test-uuid"
    properties: dict[str, Any] | None = None
    metadata: MockMetadata | None = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.metadata is None:
            self.metadata = MockMetadata()


@dataclass
class MockQueryResponse:
    """Mock Weaviate query response."""

    objects: list[MockObject] | None = None

    def __post_init__(self):
        if self.objects is None:
            self.objects = []


@dataclass
class MockAggregateResult:
    """Mock Weaviate aggregate result."""

    total_count: int = 0


class MockBatchContext:
    """Mock for Weaviate batch context manager."""

    def __init__(self):
        self.objects_added: list[dict] = []

    def add_object(self, **kwargs):
        self.objects_added.append(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MockBatch:
    """Mock for collection.batch."""

    def __init__(self):
        self._context = MockBatchContext()

    def dynamic(self):
        return self._context


class MockData:
    """Mock for collection.data operations."""

    def __init__(self):
        self.inserted: list[dict] = []

    def insert(self, **kwargs):
        self.inserted.append(kwargs)


class MockQuery:
    """Mock for collection.query operations."""

    def __init__(self, objects: list[MockObject] | None = None):
        self._objects = objects or []

    def near_vector(self, **kwargs) -> MockQueryResponse:
        return MockQueryResponse(objects=self._objects)

    def near_text(self, **kwargs) -> MockQueryResponse:
        return MockQueryResponse(objects=self._objects)


class MockAggregate:
    """Mock for collection.aggregate operations."""

    def __init__(self, count: int = 0):
        self._count = count

    def over_all(self, **kwargs) -> MockAggregateResult:
        return MockAggregateResult(total_count=self._count)


class MockCollection:
    """Mock Weaviate collection."""

    def __init__(
        self,
        name: str = "test",
        count: int = 0,
        query_objects: list[MockObject] | None = None,
    ):
        self.name = name
        self.data = MockData()
        self.batch = MockBatch()
        self.query = MockQuery(objects=query_objects)
        self.aggregate = MockAggregate(count=count)


class MockCollections:
    """Mock for client.collections."""

    def __init__(self):
        self._collections: dict[str, MockCollection] = {}

    def exists(self, name: str) -> bool:
        return name in self._collections

    def get(self, name: str) -> MockCollection:
        if name not in self._collections:
            self._collections[name] = MockCollection(name=name)
        return self._collections[name]

    def create(self, name: str, **kwargs) -> MockCollection:
        col = MockCollection(name=name)
        self._collections[name] = col
        return col

    def delete(self, name: str) -> None:
        self._collections.pop(name, None)


class MockWeaviateClient:
    """Mock Weaviate client."""

    def __init__(self):
        self.collections = MockCollections()
        self._ready = True

    def is_ready(self) -> bool:
        return self._ready

    def close(self):
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_client() -> MockWeaviateClient:
    return MockWeaviateClient()


@pytest.fixture
def store(mock_client: MockWeaviateClient) -> WeaviateZonedStore:
    """WeaviateZonedStore met mock client — alle zones."""
    return WeaviateZonedStore(
        url="http://localhost:8080",
        zones=[DataZone.RESTRICTED, DataZone.CONTROLLED, DataZone.OPEN],
        collection_prefix="test",
        _client=mock_client,
    )


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
    def test_creates_collections_for_all_zones(self, store: WeaviateZonedStore):
        assert len(store._collections) == 3

    def test_collection_names(self, store: WeaviateZonedStore):
        expected = {"test_restricted", "test_controlled", "test_open"}
        assert set(store._collections.keys()) == expected

    def test_custom_prefix(self, mock_client: MockWeaviateClient):
        s = WeaviateZonedStore(
            url="http://localhost:8080",
            collection_prefix="boris",
            _client=mock_client,
        )
        for name in s._collections:
            assert name.startswith("boris_")

    def test_custom_zones(self, mock_client: MockWeaviateClient):
        s = WeaviateZonedStore(
            url="http://localhost:8080",
            zones=[DataZone.OPEN],
            _client=mock_client,
        )
        assert len(s._collections) == 1
        assert "devhub_open" in s._collections

    def test_default_zones(self, mock_client: MockWeaviateClient):
        s = WeaviateZonedStore(url="http://localhost:8080", _client=mock_client)
        assert len(s._collections) == len(DataZone)

    def test_empty_url_raises(self, mock_client: MockWeaviateClient):
        with pytest.raises(ValueError, match="url is required"):
            WeaviateZonedStore(url="", _client=mock_client)

    def test_default_tenant_strategy(self, store: WeaviateZonedStore):
        assert store._tenant_strategy == TenantStrategy.PER_ZONE

    def test_per_kwp_strategy(self, mock_client: MockWeaviateClient):
        s = WeaviateZonedStore(
            url="http://localhost:8080",
            tenant_strategy=TenantStrategy.PER_KWP,
            _client=mock_client,
        )
        assert s._tenant_strategy == TenantStrategy.PER_KWP


# ---------------------------------------------------------------------------
# URL parsing
# ---------------------------------------------------------------------------


class TestURLParsing:
    def test_extract_host_http(self):
        assert WeaviateZonedStore._extract_host("http://localhost:8080") == "localhost"

    def test_extract_host_https(self):
        url = "https://weaviate.example.com"
        assert WeaviateZonedStore._extract_host(url) == "weaviate.example.com"

    def test_extract_port_explicit(self):
        assert WeaviateZonedStore._extract_port("http://localhost:9090") == 9090

    def test_extract_port_default_http(self):
        assert WeaviateZonedStore._extract_port("http://localhost") == 8080

    def test_extract_port_default_https(self):
        assert WeaviateZonedStore._extract_port("https://weaviate.example.com") == 443

    def test_extract_host_with_path(self):
        assert WeaviateZonedStore._extract_host("http://localhost:8080/v1") == "localhost"


# ---------------------------------------------------------------------------
# add_chunk
# ---------------------------------------------------------------------------


class TestAddChunk:
    def test_add_chunk_inserts(self, store: WeaviateZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        col = store._collections["test_open"]
        assert len(col.data.inserted) == 1

    def test_add_chunk_properties(self, store: WeaviateZonedStore, sample_chunk: DocumentChunk):
        store.add_chunk(sample_chunk)
        col = store._collections["test_open"]
        inserted = col.data.inserted[0]
        assert inserted["uuid"] == "C001"
        props = inserted["properties"]
        assert props["content"] == "Autisme-vriendelijk wonen vereist prikkelarm ontwerp."
        assert props["zone"] == "open"
        assert props["source_id"] == "doc-1"
        md = json.loads(props["chunk_metadata"])
        assert md["domain"] == "autisme"

    def test_add_chunk_with_embedding(self, store: WeaviateZonedStore):
        chunk = DocumentChunk(
            chunk_id="E001",
            content="Test with embedding",
            zone=DataZone.OPEN,
            embedding=(0.1, 0.2, 0.3),
        )
        store.add_chunk(chunk)
        col = store._collections["test_open"]
        inserted = col.data.inserted[0]
        assert inserted["vector"] == [0.1, 0.2, 0.3]

    def test_add_chunk_without_embedding(
        self,
        store: WeaviateZonedStore,
        sample_chunk: DocumentChunk,
    ):
        store.add_chunk(sample_chunk)
        col = store._collections["test_open"]
        inserted = col.data.inserted[0]
        assert "vector" not in inserted

    def test_add_restricted_chunk(self, store: WeaviateZonedStore, restricted_chunk: DocumentChunk):
        store.add_chunk(restricted_chunk)
        assert len(store._collections["test_restricted"].data.inserted) == 1
        assert len(store._collections["test_open"].data.inserted) == 0


# ---------------------------------------------------------------------------
# add_chunks batch
# ---------------------------------------------------------------------------


class TestAddChunks:
    def test_batch_add(self, store: WeaviateZonedStore):
        chunks = [
            DocumentChunk(chunk_id=f"B{i}", content=f"Batch content {i}", zone=DataZone.OPEN)
            for i in range(5)
        ]
        count = store.add_chunks(chunks)
        assert count == 5

    def test_batch_multiple_zones(self, store: WeaviateZonedStore):
        chunks = [
            DocumentChunk(chunk_id="MZ1", content="Open data", zone=DataZone.OPEN),
            DocumentChunk(chunk_id="MZ2", content="Restricted data", zone=DataZone.RESTRICTED),
            DocumentChunk(chunk_id="MZ3", content="Controlled data", zone=DataZone.CONTROLLED),
        ]
        count = store.add_chunks(chunks)
        assert count == 3

    def test_batch_with_embeddings(self, store: WeaviateZonedStore):
        chunks = [
            DocumentChunk(
                chunk_id=f"BE{i}",
                content=f"Embedded {i}",
                zone=DataZone.OPEN,
                embedding=(0.1 * i, 0.2 * i, 0.3 * i),
            )
            for i in range(3)
        ]
        count = store.add_chunks(chunks)
        assert count == 3

    def test_batch_empty_list(self, store: WeaviateZonedStore):
        count = store.add_chunks([])
        assert count == 0


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


class TestQuery:
    def test_query_with_results(self, store: WeaviateZonedStore):
        # Setup mock to return results
        mock_obj = MockObject(
            uuid="C001",
            properties={
                "content": "Test content",
                "zone": "open",
                "source_id": "doc-1",
                "created_at": "",
                "chunk_metadata": "{}",
            },
            metadata=MockMetadata(distance=0.1),
        )
        col = store._collections["test_open"]
        col.query = MockQuery(objects=[mock_obj])

        resp = store.query(
            RetrievalRequest(
                query_embedding=(0.1, 0.2, 0.3),
                zone=DataZone.OPEN,
            )
        )
        assert resp.total_found == 1
        assert resp.results[0].chunk.chunk_id == "C001"
        assert resp.results[0].score == pytest.approx(0.9)

    def test_query_empty(self, store: WeaviateZonedStore):
        resp = store.query(RetrievalRequest(query_text="iets", zone=DataZone.OPEN))
        assert resp.total_found == 0
        assert resp.results == ()

    def test_query_score_conversion(self, store: WeaviateZonedStore):
        """Weaviate distance 0.0 = perfect match = score 1.0"""
        mock_obj = MockObject(
            uuid="PERF",
            properties={
                "content": "Perfect match",
                "zone": "open",
                "source_id": "",
                "created_at": "",
                "chunk_metadata": "{}",
            },
            metadata=MockMetadata(distance=0.0),
        )
        col = store._collections["test_open"]
        col.query = MockQuery(objects=[mock_obj])

        resp = store.query(
            RetrievalRequest(
                query_embedding=(0.1,),
                zone=DataZone.OPEN,
            )
        )
        assert resp.results[0].score == 1.0

    def test_query_min_score_filter(self, store: WeaviateZonedStore):
        mock_obj = MockObject(
            uuid="LOW",
            properties={
                "content": "Low match",
                "zone": "open",
                "source_id": "",
                "created_at": "",
                "chunk_metadata": "{}",
            },
            metadata=MockMetadata(distance=0.8),  # score = 0.2
        )
        col = store._collections["test_open"]
        col.query = MockQuery(objects=[mock_obj])

        resp = store.query(
            RetrievalRequest(
                query_embedding=(0.1,),
                zone=DataZone.OPEN,
                min_score=0.5,
            )
        )
        assert resp.total_found == 0

    def test_query_all_zones(self, store: WeaviateZonedStore):
        """zone=None zoekt over alle zones."""
        for zone_name in ["test_open", "test_restricted", "test_controlled"]:
            col = store._collections[zone_name]
            col.query = MockQuery(
                objects=[
                    MockObject(
                        uuid=f"Q-{zone_name}",
                        properties={
                            "content": f"Content in {zone_name}",
                            "zone": zone_name.replace("test_", ""),
                            "source_id": "",
                            "created_at": "",
                            "chunk_metadata": "{}",
                        },
                        metadata=MockMetadata(distance=0.1),
                    ),
                ]
            )

        resp = store.query(
            RetrievalRequest(
                query_embedding=(0.1,),
                zone=None,
            )
        )
        assert resp.total_found == 3

    def test_query_duration_tracked(self, store: WeaviateZonedStore):
        resp = store.query(RetrievalRequest(query_text="test", zone=DataZone.OPEN))
        assert resp.query_duration_ms >= 0.0

    def test_query_metadata_preserved(self, store: WeaviateZonedStore):
        mock_obj = MockObject(
            uuid="MD1",
            properties={
                "content": "Test",
                "zone": "open",
                "source_id": "src-1",
                "created_at": "2026-03-26",
                "chunk_metadata": json.dumps({"domain": "ggz", "level": "3"}),
            },
            metadata=MockMetadata(distance=0.05),
        )
        col = store._collections["test_open"]
        col.query = MockQuery(objects=[mock_obj])

        resp = store.query(
            RetrievalRequest(
                query_embedding=(0.1,),
                zone=DataZone.OPEN,
            )
        )
        chunk = resp.results[0].chunk
        assert chunk.source_id == "src-1"
        assert chunk.created_at == "2026-03-26"
        md = chunk.metadata_dict
        assert md["domain"] == "ggz"
        assert md["level"] == "3"

    def test_query_metadata_filter(self, store: WeaviateZonedStore):
        obj1 = MockObject(
            uuid="F1",
            properties={
                "content": "Match",
                "zone": "open",
                "source_id": "",
                "created_at": "",
                "chunk_metadata": json.dumps({"domain": "autisme"}),
            },
            metadata=MockMetadata(distance=0.1),
        )
        obj2 = MockObject(
            uuid="F2",
            properties={
                "content": "No match",
                "zone": "open",
                "source_id": "",
                "created_at": "",
                "chunk_metadata": json.dumps({"domain": "ggz"}),
            },
            metadata=MockMetadata(distance=0.1),
        )
        col = store._collections["test_open"]
        col.query = MockQuery(objects=[obj1, obj2])

        resp = store.query(
            RetrievalRequest(
                query_embedding=(0.1,),
                zone=DataZone.OPEN,
                metadata_filter=(("domain", "autisme"),),
            )
        )
        assert resp.total_found == 1
        assert resp.results[0].chunk.chunk_id == "F1"

    def test_query_sorts_by_score_descending(self, store: WeaviateZonedStore):
        empty_props = {
            "content": "",
            "zone": "open",
            "source_id": "",
            "created_at": "",
            "chunk_metadata": "{}",
        }
        obj_low = MockObject(
            uuid="LOW",
            properties={**empty_props, "content": "Low"},
            metadata=MockMetadata(distance=0.6),
        )
        obj_high = MockObject(
            uuid="HIGH",
            properties={**empty_props, "content": "High"},
            metadata=MockMetadata(distance=0.1),
        )
        col = store._collections["test_open"]
        col.query = MockQuery(objects=[obj_low, obj_high])

        resp = store.query(RetrievalRequest(query_embedding=(0.1,), zone=DataZone.OPEN))
        assert resp.results[0].chunk.chunk_id == "HIGH"
        assert resp.results[1].chunk.chunk_id == "LOW"


# ---------------------------------------------------------------------------
# count / count_by_zone
# ---------------------------------------------------------------------------


class TestCounting:
    def test_count_empty(self, store: WeaviateZonedStore):
        assert store.count() == 0

    def test_count_by_zone_empty(self, store: WeaviateZonedStore):
        counts = store.count_by_zone()
        assert all(v == 0 for v in counts.values())
        assert len(counts) == 3

    def test_count_with_data(self, store: WeaviateZonedStore):
        col = store._collections["test_open"]
        col.aggregate = MockAggregate(count=5)
        assert store.count() == 5

    def test_count_by_zone_with_data(self, store: WeaviateZonedStore):
        store._collections["test_open"].aggregate = MockAggregate(count=3)
        store._collections["test_restricted"].aggregate = MockAggregate(count=2)
        counts = store.count_by_zone()
        assert counts[DataZone.OPEN] == 3
        assert counts[DataZone.RESTRICTED] == 2
        assert counts[DataZone.CONTROLLED] == 0


# ---------------------------------------------------------------------------
# reset
# ---------------------------------------------------------------------------


class TestReset:
    def test_reset_clears_collections(self, store: WeaviateZonedStore):
        store.reset()
        # Collections should be recreated
        assert len(store._collections) == 3

    def test_reset_clears_tenants(self, store: WeaviateZonedStore):
        store.ensure_tenant("tenant-1")
        store.reset()
        assert store.list_tenants() == []


# ---------------------------------------------------------------------------
# Tenants — PER_ZONE
# ---------------------------------------------------------------------------


class TestTenantPerZone:
    def test_ensure_tenant(self, store: WeaviateZonedStore):
        store.ensure_tenant("kwp-dev")
        assert "kwp-dev" in store.list_tenants()

    def test_list_tenants_sorted(self, store: WeaviateZonedStore):
        store.ensure_tenant("beta")
        store.ensure_tenant("alpha")
        assert store.list_tenants() == ["alpha", "beta"]

    def test_duplicate_tenant(self, store: WeaviateZonedStore):
        store.ensure_tenant("kwp-dev")
        store.ensure_tenant("kwp-dev")
        assert store.list_tenants() == ["kwp-dev"]

    def test_empty_tenant_id_raises(self, store: WeaviateZonedStore):
        with pytest.raises(ValueError, match="tenant_id"):
            store.ensure_tenant("")

    def test_list_empty(self, store: WeaviateZonedStore):
        assert store.list_tenants() == []


# ---------------------------------------------------------------------------
# Tenants — PER_KWP
# ---------------------------------------------------------------------------


class TestTenantPerKWP:
    @pytest.fixture
    def kwp_store(self, mock_client: MockWeaviateClient) -> WeaviateZonedStore:
        return WeaviateZonedStore(
            url="http://localhost:8080",
            tenant_strategy=TenantStrategy.PER_KWP,
            _client=mock_client,
        )

    def test_ensure_tenant_creates_collection(self, kwp_store: WeaviateZonedStore):
        kwp_store.ensure_tenant("autisme")
        assert "devhub_kwp_autisme" in kwp_store._collections

    def test_multiple_tenants(self, kwp_store: WeaviateZonedStore):
        kwp_store.ensure_tenant("autisme")
        kwp_store.ensure_tenant("ggz")
        assert len(kwp_store.list_tenants()) == 2

    def test_tenant_name_sanitized(self, kwp_store: WeaviateZonedStore):
        kwp_store.ensure_tenant("kwp-dev test")
        assert "devhub_kwp_kwp_dev_test" in kwp_store._collections

    def test_duplicate_tenant_no_double_create(self, kwp_store: WeaviateZonedStore):
        kwp_store.ensure_tenant("ggz")
        kwp_store.ensure_tenant("ggz")
        assert kwp_store.list_tenants() == ["ggz"]


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_healthy_store(self, store: WeaviateZonedStore):
        h = store.health()
        assert h.status == "UP"
        assert h.backend == "weaviate"
        assert h.collection_count == 3

    def test_health_down(self, store: WeaviateZonedStore, mock_client: MockWeaviateClient):
        mock_client._ready = False
        h = store.health()
        assert h.status == "DOWN"

    def test_health_with_tenants(self, store: WeaviateZonedStore):
        store.ensure_tenant("t1")
        store.ensure_tenant("t2")
        h = store.health()
        assert h.tenant_count == 2

    def test_health_with_data(self, store: WeaviateZonedStore):
        store._collections["test_open"].aggregate = MockAggregate(count=10)
        h = store.health()
        assert h.total_chunks == 10


# ---------------------------------------------------------------------------
# Close / lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:
    def test_close(self, store: WeaviateZonedStore):
        """Close should not raise."""
        store.close()

    def test_owns_client_flag_injected(self, store: WeaviateZonedStore):
        """Injected client should not be owned."""
        assert store._owns_client is False


# ---------------------------------------------------------------------------
# Properties conversion
# ---------------------------------------------------------------------------


class TestPropertyConversion:
    def test_chunk_to_properties(self, store: WeaviateZonedStore, sample_chunk: DocumentChunk):
        props = store._chunk_to_properties(sample_chunk)
        assert props["content"] == sample_chunk.content
        assert props["zone"] == "open"
        assert props["source_id"] == "doc-1"
        md = json.loads(props["chunk_metadata"])
        assert md["domain"] == "autisme"

    def test_properties_to_chunk(self, store: WeaviateZonedStore):
        props = {
            "content": "Test content",
            "zone": "open",
            "source_id": "src-1",
            "created_at": "2026-03-26",
            "chunk_metadata": json.dumps({"key": "value"}),
        }
        chunk = store._properties_to_chunk("uuid-1", props, DataZone.OPEN)
        assert chunk.chunk_id == "uuid-1"
        assert chunk.content == "Test content"
        assert chunk.zone == DataZone.OPEN
        assert chunk.source_id == "src-1"
        assert chunk.metadata_dict == {"key": "value"}

    def test_properties_to_chunk_empty_metadata(self, store: WeaviateZonedStore):
        props = {
            "content": "Test",
            "zone": "open",
            "source_id": "",
            "created_at": "",
            "chunk_metadata": "{}",
        }
        chunk = store._properties_to_chunk("uuid-2", props, DataZone.OPEN)
        assert chunk.metadata == ()

    def test_properties_to_chunk_invalid_json(self, store: WeaviateZonedStore):
        props = {
            "content": "Test",
            "zone": "open",
            "source_id": "",
            "created_at": "",
            "chunk_metadata": "not-json",
        }
        chunk = store._properties_to_chunk("uuid-3", props, DataZone.OPEN)
        assert chunk.metadata == ()

    def test_chunk_to_properties_no_metadata(self, store: WeaviateZonedStore):
        chunk = DocumentChunk(
            chunk_id="NM1",
            content="No metadata",
            zone=DataZone.OPEN,
        )
        props = store._chunk_to_properties(chunk)
        assert props["chunk_metadata"] == "{}"
