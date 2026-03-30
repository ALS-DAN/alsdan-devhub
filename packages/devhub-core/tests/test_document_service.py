"""Tests voor DocumentService — pipeline orchestrator."""

from pathlib import Path

import pytest

from devhub_documents.contracts import (
    DocumentCategory,
)
from devhub_documents.factory import DocumentFactory
from devhub_core.agents.document_service import DocumentService
from devhub_core.agents.folder_router import FolderRouter
from devhub_core.contracts.event_contracts import (
    DocumentPublished,
    Event,
)
from devhub_core.contracts.pipeline_contracts import (
    DocumentProductionRequest,
    PublishStatus,
)
from devhub_core.events.in_memory_bus import InMemoryEventBus

# Paden
CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "documents.yml"


# ---------------------------------------------------------------------------
# Fake Storage
# ---------------------------------------------------------------------------


class FakeStorage:
    """In-memory storage voor tests. Implementeert put() en get()."""

    def __init__(self) -> None:
        self._files: dict[str, bytes] = {}
        self._hashes: dict[str, str] = {}

    def put(self, path: str, content: bytes) -> "FakeWriteResult":
        self._files[path] = content
        return FakeWriteResult(success=True, path=path, bytes_written=len(content))

    def get(self, path: str) -> "FakeStorageItem":
        if path not in self._files:
            raise FileNotFoundError(f"Not found: {path}")
        return FakeStorageItem(
            path=path,
            content_hash=self._hashes.get(path),
            size_bytes=len(self._files[path]),
        )

    def set_hash(self, path: str, hash_val: str) -> None:
        """Set een checksum voor dedup-tests."""
        self._hashes[path] = hash_val


class FakeWriteResult:
    def __init__(self, success: bool, path: str, bytes_written: int = 0) -> None:
        self.success = success
        self.path = path
        self.bytes_written = bytes_written


class FakeStorageItem:
    def __init__(self, path: str, content_hash: str | None = None, size_bytes: int = 0) -> None:
        self.path = path
        self.content_hash = content_hash
        self.size_bytes = size_bytes


# ---------------------------------------------------------------------------
# Fake VectorStore
# ---------------------------------------------------------------------------


class FakeChunk:
    def __init__(self, content: str, source_id: str = "") -> None:
        self.content = content
        self.source_id = source_id


class FakeSearchResult:
    def __init__(self, chunk: FakeChunk, score: float = 0.9) -> None:
        self.chunk = chunk
        self.score = score


class FakeRetrievalResponse:
    def __init__(self, results: list[FakeSearchResult], total_found: int = 0) -> None:
        self.results = results
        self.total_found = total_found


class FakeVectorStore:
    """In-memory vectorstore voor tests."""

    def __init__(self, results: list[FakeSearchResult] | None = None) -> None:
        self._results = results or []
        self.last_query: object | None = None

    def query(self, request: object) -> FakeRetrievalResponse:
        self.last_query = request
        return FakeRetrievalResponse(
            results=self._results,
            total_found=len(self._results),
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def factory() -> DocumentFactory:
    return DocumentFactory(config_path=CONFIG_PATH)


@pytest.fixture
def router() -> FolderRouter:
    return FolderRouter(config_path=CONFIG_PATH)


@pytest.fixture
def service(factory: DocumentFactory, router: FolderRouter) -> DocumentService:
    """DocumentService zonder storage en vectorstore."""
    return DocumentService(document_factory=factory, folder_router=router)


@pytest.fixture
def service_with_storage(
    factory: DocumentFactory, router: FolderRouter
) -> tuple[DocumentService, FakeStorage]:
    storage = FakeStorage()
    svc = DocumentService(document_factory=factory, folder_router=router, storage=storage)
    return svc, storage


@pytest.fixture
def service_with_vectorstore(
    factory: DocumentFactory, router: FolderRouter
) -> tuple[DocumentService, FakeVectorStore]:
    chunks = [
        FakeSearchResult(FakeChunk("Kennis chunk 1", source_id="src-1")),
        FakeSearchResult(FakeChunk("Kennis chunk 2", source_id="src-2")),
    ]
    vs = FakeVectorStore(results=chunks)
    svc = DocumentService(document_factory=factory, folder_router=router, vectorstore=vs)
    return svc, vs


# ---------------------------------------------------------------------------
# Tests: produce() basics
# ---------------------------------------------------------------------------


class TestProduceBasics:
    def test_produce_skip_vectorstore(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="Test Document",
            category=DocumentCategory.PATTERN,
            skip_vectorstore=True,
        )
        result = service.produce(req)
        assert result.storage_path == "DevHub/process/pattern/test-document.md"
        assert result.publish_status == PublishStatus.SKIPPED
        assert result.node_id == "devhub"
        assert result.knowledge_context is None

    def test_produce_returns_document_result(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="Shape Up in DevHub",
            category=DocumentCategory.METHODOLOGY,
            skip_vectorstore=True,
        )
        result = service.produce(req)
        assert result.document_result.path.endswith(".md")
        assert result.document_result.size_bytes > 0
        assert result.document_result.checksum != ""

    def test_produce_disallowed_category_raises(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="Test",
            category=DocumentCategory.METHODOLOGY,
            target_node="boris-buurts",
            skip_vectorstore=True,
        )
        with pytest.raises(ValueError, match="not allowed"):
            service.produce(req)

    def test_produce_correct_storage_path_boris(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="Eerste Stappen",
            category=DocumentCategory.TUTORIAL,
            target_node="boris-buurts",
            skip_vectorstore=True,
        )
        result = service.produce(req)
        assert result.storage_path == "BORIS/product/tutorial/eerste-stappen.md"


# ---------------------------------------------------------------------------
# Tests: storage integration
# ---------------------------------------------------------------------------


class TestStorageIntegration:
    def test_produce_with_storage_publishes(
        self, service_with_storage: tuple[DocumentService, FakeStorage]
    ):
        svc, storage = service_with_storage
        req = DocumentProductionRequest(
            topic="Test Publish",
            category=DocumentCategory.PATTERN,
            skip_vectorstore=True,
        )
        result = svc.produce(req)
        assert result.publish_status == PublishStatus.PUBLISHED
        assert "DevHub/process/pattern/test-publish.md" in storage._files

    def test_produce_dedup_skips_on_same_checksum(
        self, service_with_storage: tuple[DocumentService, FakeStorage]
    ):
        svc, storage = service_with_storage
        req = DocumentProductionRequest(
            topic="Dedup Test",
            category=DocumentCategory.TUTORIAL,
            skip_vectorstore=True,
        )
        # Eerste keer: publiceer
        result1 = svc.produce(req)
        assert result1.publish_status == PublishStatus.PUBLISHED

        # Zet de checksum in fake storage zodat dedup werkt
        path = result1.storage_path
        storage.set_hash(path, result1.document_result.checksum)

        # Tweede keer: skip
        result2 = svc.produce(req)
        assert result2.publish_status == PublishStatus.SKIPPED


# ---------------------------------------------------------------------------
# Tests: vectorstore integration
# ---------------------------------------------------------------------------


class TestVectorstoreIntegration:
    def test_produce_with_vectorstore_populates_context(
        self, service_with_vectorstore: tuple[DocumentService, FakeVectorStore]
    ):
        svc, vs = service_with_vectorstore
        req = DocumentProductionRequest(
            topic="Knowledge Test",
            category=DocumentCategory.EXPLANATION,
        )
        result = svc.produce(req)
        assert result.knowledge_context is not None
        assert result.knowledge_context.has_content is True
        assert len(result.knowledge_context.chunks) == 2
        assert "src-1" in result.knowledge_context.sources

    def test_produce_uses_effective_query(
        self, service_with_vectorstore: tuple[DocumentService, FakeVectorStore]
    ):
        svc, vs = service_with_vectorstore
        req = DocumentProductionRequest(
            topic="My Topic",
            category=DocumentCategory.REFERENCE,
            knowledge_query="specific search",
        )
        svc.produce(req)
        assert vs.last_query is not None
        assert vs.last_query.query_text == "specific search"  # type: ignore[union-attr]

    def test_produce_without_vectorstore_no_context(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="No VS",
            category=DocumentCategory.HOWTO,
        )
        result = service.produce(req)
        assert result.knowledge_context is None


# ---------------------------------------------------------------------------
# Tests: document content
# ---------------------------------------------------------------------------


class TestDocumentContent:
    def test_produce_metadata_has_category(self, service: DocumentService, tmp_path: Path):
        req = DocumentProductionRequest(
            topic="Meta Test",
            category=DocumentCategory.DECISION,
            skip_vectorstore=True,
        )
        result = service.produce(req)
        content = Path(result.document_result.path).read_text()
        assert "category: decision" in content

    def test_produce_metadata_has_grade(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="Grade Test",
            category=DocumentCategory.ANALYSIS,
            skip_vectorstore=True,
        )
        result = service.produce(req)
        content = Path(result.document_result.path).read_text()
        assert "grade: BRONZE" in content

    def test_produce_has_sections(self, service: DocumentService):
        req = DocumentProductionRequest(
            topic="Section Test",
            category=DocumentCategory.PATTERN,
            skip_vectorstore=True,
        )
        result = service.produce(req)
        content = Path(result.document_result.path).read_text()
        # Pattern-specifieke secties
        assert "Context" in content
        assert "Probleem" in content
        assert "Oplossing" in content


# ---------------------------------------------------------------------------
# Tests: event bus integration
# ---------------------------------------------------------------------------


@pytest.fixture
def service_with_event_bus(
    factory: DocumentFactory, router: FolderRouter
) -> tuple[DocumentService, FakeStorage, InMemoryEventBus]:
    storage = FakeStorage()
    bus = InMemoryEventBus()
    svc = DocumentService(
        document_factory=factory,
        folder_router=router,
        storage=storage,
        event_bus=bus,
    )
    return svc, storage, bus


class TestEventBusIntegration:
    def test_publish_event_on_successful_storage(
        self, service_with_event_bus: tuple[DocumentService, FakeStorage, InMemoryEventBus]
    ):
        svc, _storage, bus = service_with_event_bus
        received: list[Event] = []
        bus.subscribe(DocumentPublished, received.append)

        req = DocumentProductionRequest(
            topic="Event Test",
            category=DocumentCategory.PATTERN,
            skip_vectorstore=True,
        )
        result = svc.produce(req)

        assert result.publish_status == PublishStatus.PUBLISHED
        assert len(received) == 1
        evt = received[0]
        assert isinstance(evt, DocumentPublished)
        assert evt.source_agent == "document-service"
        assert evt.category == "pattern"
        assert evt.node_id == "devhub"
        assert evt.storage_path == result.storage_path

    def test_no_event_without_storage(self, factory: DocumentFactory, router: FolderRouter):
        bus = InMemoryEventBus()
        svc = DocumentService(document_factory=factory, folder_router=router, event_bus=bus)
        received: list[Event] = []
        bus.subscribe(DocumentPublished, received.append)

        req = DocumentProductionRequest(
            topic="No Storage",
            category=DocumentCategory.HOWTO,
            skip_vectorstore=True,
        )
        result = svc.produce(req)

        assert result.publish_status == PublishStatus.SKIPPED
        assert len(received) == 0

    def test_no_event_without_bus(self, service_with_storage: tuple[DocumentService, FakeStorage]):
        svc, _storage = service_with_storage
        req = DocumentProductionRequest(
            topic="No Bus",
            category=DocumentCategory.PATTERN,
            skip_vectorstore=True,
        )
        # Should not raise — graceful degradation
        result = svc.produce(req)
        assert result.publish_status == PublishStatus.PUBLISHED

    def test_event_has_correct_document_path(
        self, service_with_event_bus: tuple[DocumentService, FakeStorage, InMemoryEventBus]
    ):
        svc, _storage, bus = service_with_event_bus
        received: list[Event] = []
        bus.subscribe(DocumentPublished, received.append)

        req = DocumentProductionRequest(
            topic="Path Check",
            category=DocumentCategory.ANALYSIS,
            skip_vectorstore=True,
        )
        result = svc.produce(req)

        assert len(received) == 1
        evt = received[0]
        assert isinstance(evt, DocumentPublished)
        assert evt.document_path == result.document_result.path
