"""Tests voor Pipeline Contracts — documentatie-productie pipeline."""

import pytest

from devhub_documents.contracts import DocumentCategory, DocumentFormat, DocumentResult
from devhub_core.contracts.pipeline_contracts import (
    DocumentProductionRequest,
    DocumentProductionResult,
    FolderRoute,
    KnowledgeContext,
    PublishStatus,
)


# ---------------------------------------------------------------------------
# PublishStatus
# ---------------------------------------------------------------------------


class TestPublishStatus:
    def test_has_four_values(self):
        assert len(PublishStatus) == 4

    def test_values(self):
        assert PublishStatus.PENDING.value == "pending"
        assert PublishStatus.PUBLISHED.value == "published"
        assert PublishStatus.SKIPPED.value == "skipped"
        assert PublishStatus.FAILED.value == "failed"


# ---------------------------------------------------------------------------
# FolderRoute
# ---------------------------------------------------------------------------


class TestFolderRoute:
    def test_valid_route(self):
        r = FolderRoute(category="pattern", storage_path="DevHub/process/pattern")
        assert r.category == "pattern"
        assert r.storage_path == "DevHub/process/pattern"
        assert r.node_id == "devhub"

    def test_custom_node(self):
        r = FolderRoute(
            category="tutorial", storage_path="BORIS/product/tutorial", node_id="boris-buurts"
        )
        assert r.node_id == "boris-buurts"

    def test_empty_category_raises(self):
        with pytest.raises(ValueError, match="category"):
            FolderRoute(category="", storage_path="some/path")

    def test_empty_storage_path_raises(self):
        with pytest.raises(ValueError, match="storage_path"):
            FolderRoute(category="pattern", storage_path="")

    def test_frozen(self):
        r = FolderRoute(category="pattern", storage_path="p")
        with pytest.raises(AttributeError):
            r.category = "tutorial"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DocumentProductionRequest
# ---------------------------------------------------------------------------


class TestDocumentProductionRequest:
    def test_valid_request(self):
        req = DocumentProductionRequest(
            topic="Shape Up in DevHub",
            category=DocumentCategory.METHODOLOGY,
        )
        assert req.topic == "Shape Up in DevHub"
        assert req.category == DocumentCategory.METHODOLOGY
        assert req.target_node == "devhub"
        assert req.output_format == DocumentFormat.MARKDOWN
        assert req.audience == "developer"
        assert req.skip_vectorstore is False

    def test_empty_topic_raises(self):
        with pytest.raises(ValueError, match="topic"):
            DocumentProductionRequest(topic="", category=DocumentCategory.TUTORIAL)

    def test_whitespace_topic_raises(self):
        with pytest.raises(ValueError, match="topic"):
            DocumentProductionRequest(topic="   ", category=DocumentCategory.TUTORIAL)

    def test_effective_query_defaults_to_topic(self):
        req = DocumentProductionRequest(topic="My Topic", category=DocumentCategory.PATTERN)
        assert req.effective_query == "My Topic"

    def test_effective_query_uses_knowledge_query(self):
        req = DocumentProductionRequest(
            topic="My Topic",
            category=DocumentCategory.PATTERN,
            knowledge_query="specific query",
        )
        assert req.effective_query == "specific query"

    def test_all_fields(self):
        req = DocumentProductionRequest(
            topic="ABC Pattern",
            category=DocumentCategory.PATTERN,
            target_node="boris-buurts",
            output_format=DocumentFormat.ODF,
            audience="medewerker",
            knowledge_query="adapter pattern",
            skip_vectorstore=True,
        )
        assert req.target_node == "boris-buurts"
        assert req.output_format == DocumentFormat.ODF
        assert req.audience == "medewerker"
        assert req.skip_vectorstore is True

    def test_frozen(self):
        req = DocumentProductionRequest(topic="X", category=DocumentCategory.TUTORIAL)
        with pytest.raises(AttributeError):
            req.topic = "Y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# KnowledgeContext
# ---------------------------------------------------------------------------


class TestKnowledgeContext:
    def test_empty_context(self):
        ctx = KnowledgeContext()
        assert ctx.chunks == ()
        assert ctx.sources == ()
        assert ctx.query_used == ""
        assert ctx.total_found == 0
        assert ctx.has_content is False

    def test_with_chunks(self):
        ctx = KnowledgeContext(
            chunks=("chunk1", "chunk2"),
            sources=("src1", "src2"),
            query_used="test query",
            total_found=5,
        )
        assert len(ctx.chunks) == 2
        assert ctx.has_content is True
        assert ctx.total_found == 5

    def test_frozen(self):
        ctx = KnowledgeContext()
        with pytest.raises(AttributeError):
            ctx.query_used = "new"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DocumentProductionResult
# ---------------------------------------------------------------------------


class TestDocumentProductionResult:
    def _make_doc_result(self) -> DocumentResult:
        return DocumentResult(
            path="/tmp/test.md",
            format=DocumentFormat.MARKDOWN,
            size_bytes=100,
            checksum="abc123",
        )

    def test_valid_result(self):
        result = DocumentProductionResult(
            document_result=self._make_doc_result(),
            storage_path="DevHub/knowledge/methodology/test.md",
            publish_status=PublishStatus.PUBLISHED,
        )
        assert result.storage_path == "DevHub/knowledge/methodology/test.md"
        assert result.publish_status == PublishStatus.PUBLISHED
        assert result.node_id == "devhub"
        assert result.knowledge_context is None
        assert result.message == ""

    def test_empty_storage_path_raises(self):
        with pytest.raises(ValueError, match="storage_path"):
            DocumentProductionResult(
                document_result=self._make_doc_result(),
                storage_path="",
                publish_status=PublishStatus.PENDING,
            )

    def test_with_knowledge_context(self):
        ctx = KnowledgeContext(chunks=("c1",), sources=("s1",), query_used="q")
        result = DocumentProductionResult(
            document_result=self._make_doc_result(),
            storage_path="path/to/doc.md",
            publish_status=PublishStatus.PUBLISHED,
            knowledge_context=ctx,
        )
        assert result.knowledge_context is not None
        assert result.knowledge_context.has_content is True

    def test_with_message(self):
        result = DocumentProductionResult(
            document_result=self._make_doc_result(),
            storage_path="path/to/doc.md",
            publish_status=PublishStatus.SKIPPED,
            message="Duplicate checksum",
        )
        assert result.message == "Duplicate checksum"

    def test_frozen(self):
        result = DocumentProductionResult(
            document_result=self._make_doc_result(),
            storage_path="p/d.md",
            publish_status=PublishStatus.PENDING,
        )
        with pytest.raises(AttributeError):
            result.storage_path = "new"  # type: ignore[misc]
