"""E2E tests voor de documentatie-productie pipeline.

Gebruikt LocalAdapter als storage en in-memory fakes voor vectorstore.
Valideert de volledige keten: produce → bestand op disk in juiste map.
"""

from pathlib import Path

import pytest

from devhub_documents.contracts import DocumentCategory
from devhub_documents.factory import DocumentFactory
from devhub_core.agents.content_builders import SPRINT_33_BUILDERS
from devhub_core.agents.document_service import DocumentService
from devhub_core.agents.folder_router import FolderRouter
from devhub_core.contracts.pipeline_contracts import (
    DocumentProductionRequest,
    PublishStatus,
)

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "documents.yml"


# ---------------------------------------------------------------------------
# Simple local storage that writes to disk
# ---------------------------------------------------------------------------


class DiskStorage:
    """Schrijft bestanden naar een directory op disk."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def put(self, path: str, content: bytes) -> "DiskWriteResult":
        target = self._root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return DiskWriteResult(success=True, path=path, bytes_written=len(content))

    def get(self, path: str) -> "DiskStorageItem":
        target = self._root / path
        if not target.exists():
            raise FileNotFoundError(f"Not found: {path}")
        import hashlib

        content_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        return DiskStorageItem(
            path=path, content_hash=content_hash, size_bytes=target.stat().st_size
        )


class DiskWriteResult:
    def __init__(self, success: bool, path: str, bytes_written: int = 0) -> None:
        self.success = success
        self.path = path
        self.bytes_written = bytes_written


class DiskStorageItem:
    def __init__(self, path: str, content_hash: str, size_bytes: int = 0) -> None:
        self.path = path
        self.content_hash = content_hash
        self.size_bytes = size_bytes


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def pipeline(tmp_path: Path) -> tuple[DocumentService, Path]:
    """Complete pipeline met DiskStorage."""
    factory = DocumentFactory(config_path=CONFIG_PATH)
    router = FolderRouter(config_path=CONFIG_PATH)
    storage = DiskStorage(root=tmp_path)
    service = DocumentService(
        document_factory=factory,
        folder_router=router,
        storage=storage,
    )
    return service, tmp_path


# ---------------------------------------------------------------------------
# E2E Tests
# ---------------------------------------------------------------------------


class TestPipelineE2E:
    def test_produce_creates_file_on_disk(self, pipeline: tuple[DocumentService, Path]):
        service, root = pipeline
        req = DocumentProductionRequest(
            topic="E2E Test Document",
            category=DocumentCategory.EXPLANATION,
            skip_vectorstore=True,
        )
        result = service.produce(req)
        assert result.publish_status == PublishStatus.PUBLISHED
        target = root / result.storage_path
        assert target.exists()
        assert target.stat().st_size > 0

    def test_three_categories_create_three_files(self, pipeline: tuple[DocumentService, Path]):
        service, root = pipeline
        categories = [
            (DocumentCategory.PATTERN, "Test Pattern"),
            (DocumentCategory.METHODOLOGY, "Test Methodology"),
            (DocumentCategory.TUTORIAL, "Test Tutorial"),
        ]
        paths = []
        for cat, topic in categories:
            req = DocumentProductionRequest(topic=topic, category=cat, skip_vectorstore=True)
            result = service.produce(req)
            paths.append(root / result.storage_path)

        # Alle drie bestanden bestaan in verschillende submappen
        assert all(p.exists() for p in paths)
        assert len(set(p.parent for p in paths)) == 3  # 3 verschillende mappen

    def test_idempotency_second_call_skips(self, pipeline: tuple[DocumentService, Path]):
        service, root = pipeline
        req = DocumentProductionRequest(
            topic="Idempotent Doc",
            category=DocumentCategory.REFERENCE,
            skip_vectorstore=True,
        )
        result1 = service.produce(req)
        assert result1.publish_status == PublishStatus.PUBLISHED

        result2 = service.produce(req)
        assert result2.publish_status == PublishStatus.SKIPPED

    def test_boris_node_limits_categories(self, pipeline: tuple[DocumentService, Path]):
        service, _ = pipeline
        # METHODOLOGY is niet in boris-buurts taxonomie
        req = DocumentProductionRequest(
            topic="Boris Test",
            category=DocumentCategory.METHODOLOGY,
            target_node="boris-buurts",
            skip_vectorstore=True,
        )
        with pytest.raises(ValueError, match="not allowed"):
            service.produce(req)

    def test_sprint_33_builders_all_produce(self, pipeline: tuple[DocumentService, Path]):
        service, root = pipeline
        results = []
        for builder in SPRINT_33_BUILDERS:
            req = builder()
            result = service.produce(req)
            results.append(result)

        assert len(results) == 4
        assert all(r.publish_status == PublishStatus.PUBLISHED for r in results)
        # Controleer dat bestanden op disk staan
        for r in results:
            assert (root / r.storage_path).exists()
