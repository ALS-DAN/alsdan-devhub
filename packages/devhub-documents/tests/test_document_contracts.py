"""
Tests voor devhub_documents.contracts — frozen dataclasses.
"""

from __future__ import annotations

import pytest

from devhub_documents.contracts import (
    DocumentCategory,
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentResult,
    DocumentSection,
)


class TestDocumentFormat:
    """Tests voor DocumentFormat enum."""

    def test_document_format_enum(self) -> None:
        assert DocumentFormat.ODF.value == "odf"
        assert DocumentFormat.MARKDOWN.value == "markdown"

    def test_document_format_members(self) -> None:
        assert len(DocumentFormat) == 2


class TestDocumentCategory:
    """Tests voor DocumentCategory enum."""

    def test_document_category_has_12_members(self) -> None:
        assert len(DocumentCategory) == 12

    def test_document_category_values(self) -> None:
        expected = [
            "tutorial",
            "howto",
            "reference",
            "explanation",
            "pattern",
            "analysis",
            "decision",
            "retrospective",
            "methodology",
            "best_practice",
            "sota_review",
            "playbook",
        ]
        assert [m.value for m in DocumentCategory] == expected

    def test_document_category_layer_product(self) -> None:
        product = [c for c in DocumentCategory if c.layer() == "product"]
        assert len(product) == 4
        assert {c.value for c in product} == {"tutorial", "howto", "reference", "explanation"}

    def test_document_category_layer_process(self) -> None:
        process = [c for c in DocumentCategory if c.layer() == "process"]
        assert len(process) == 4
        assert {c.value for c in process} == {"pattern", "analysis", "decision", "retrospective"}

    def test_document_category_layer_knowledge(self) -> None:
        knowledge = [c for c in DocumentCategory if c.layer() == "knowledge"]
        assert len(knowledge) == 4
        expected = {"methodology", "best_practice", "sota_review", "playbook"}
        assert {c.value for c in knowledge} == expected

    def test_document_category_from_string(self) -> None:
        assert DocumentCategory.from_string("tutorial") == DocumentCategory.TUTORIAL
        assert DocumentCategory.from_string("BEST_PRACTICE") == DocumentCategory.BEST_PRACTICE
        assert DocumentCategory.from_string("  Pattern  ") == DocumentCategory.PATTERN

    def test_document_category_from_string_invalid(self) -> None:
        with pytest.raises(ValueError, match="Unknown category"):
            DocumentCategory.from_string("nonexistent")


class TestDocumentSection:
    """Tests voor DocumentSection frozen dataclass."""

    def test_document_section_creation(self) -> None:
        section = DocumentSection(heading="Test", content="Body", level=2)
        assert section.heading == "Test"
        assert section.content == "Body"
        assert section.level == 2
        assert section.subsections == ()

    def test_document_section_heading_required(self) -> None:
        with pytest.raises(ValueError, match="heading is required"):
            DocumentSection(heading="")

    def test_document_section_heading_whitespace_only(self) -> None:
        with pytest.raises(ValueError, match="heading is required"):
            DocumentSection(heading="   ")

    def test_document_section_level_validation_too_low(self) -> None:
        with pytest.raises(ValueError, match="level must be between 1 and 6"):
            DocumentSection(heading="Test", level=0)

    def test_document_section_level_validation_too_high(self) -> None:
        with pytest.raises(ValueError, match="level must be between 1 and 6"):
            DocumentSection(heading="Test", level=7)

    def test_document_section_defaults(self) -> None:
        section = DocumentSection(heading="Minimal")
        assert section.content == ""
        assert section.level == 1
        assert section.subsections == ()

    def test_document_section_frozen(self) -> None:
        section = DocumentSection(heading="Frozen")
        with pytest.raises(AttributeError):
            section.heading = "Changed"  # type: ignore[misc]

    def test_document_section_to_dict(self) -> None:
        sub = DocumentSection(heading="Sub", level=2)
        section = DocumentSection(heading="Main", content="Body", subsections=(sub,))
        d = section.to_dict()
        assert d["heading"] == "Main"
        assert d["content"] == "Body"
        assert len(d["subsections"]) == 1
        assert d["subsections"][0]["heading"] == "Sub"

    def test_document_section_with_subsections(self) -> None:
        sub = DocumentSection(heading="Child", content="Child body", level=2)
        parent = DocumentSection(heading="Parent", subsections=(sub,))
        assert len(parent.subsections) == 1
        assert parent.subsections[0].heading == "Child"


class TestDocumentMetadata:
    """Tests voor DocumentMetadata frozen dataclass."""

    def test_document_metadata_defaults(self) -> None:
        meta = DocumentMetadata()
        assert meta.author == "devhub"
        assert meta.category is None
        assert meta.date == ""
        assert meta.grade is None
        assert meta.sources == ()
        assert meta.tags == ()
        assert meta.version == "1.0"

    def test_document_metadata_custom(self) -> None:
        meta = DocumentMetadata(
            author="niels",
            date="2026-03-26",
            grade="GOLD",
            sources=("src1",),
            tags=("tag1", "tag2"),
            version="2.0",
        )
        assert meta.author == "niels"
        assert meta.grade == "GOLD"

    def test_document_metadata_to_dict(self) -> None:
        meta = DocumentMetadata(date="2026-01-01", grade="SILVER", tags=("a",))
        d = meta.to_dict()
        assert d["author"] == "devhub"
        assert d["date"] == "2026-01-01"
        assert d["grade"] == "SILVER"
        assert d["tags"] == ["a"]

    def test_document_metadata_with_category(self) -> None:
        meta = DocumentMetadata(category="explanation")
        assert meta.category == "explanation"

    def test_document_metadata_to_dict_with_category(self) -> None:
        meta = DocumentMetadata(category="pattern")
        d = meta.to_dict()
        assert d["category"] == "pattern"

    def test_document_metadata_to_dict_minimal(self) -> None:
        meta = DocumentMetadata()
        d = meta.to_dict()
        assert "category" not in d
        assert "date" not in d
        assert "grade" not in d
        assert "sources" not in d
        assert "tags" not in d


class TestDocumentRequest:
    """Tests voor DocumentRequest frozen dataclass."""

    def test_document_request_creation(self) -> None:
        section = DocumentSection(heading="S1")
        req = DocumentRequest(title="Doc", sections=(section,))
        assert req.title == "Doc"
        assert len(req.sections) == 1
        assert req.output_format == DocumentFormat.MARKDOWN

    def test_document_request_title_required(self) -> None:
        section = DocumentSection(heading="S1")
        with pytest.raises(ValueError, match="title is required"):
            DocumentRequest(title="", sections=(section,))

    def test_document_request_sections_required(self) -> None:
        with pytest.raises(ValueError, match="sections is required"):
            DocumentRequest(title="Doc", sections=())

    def test_document_request_frozen(self) -> None:
        section = DocumentSection(heading="S1")
        req = DocumentRequest(title="Doc", sections=(section,))
        with pytest.raises(AttributeError):
            req.title = "Changed"  # type: ignore[misc]

    def test_document_request_to_dict(self) -> None:
        section = DocumentSection(heading="S1")
        req = DocumentRequest(title="Doc", sections=(section,))
        d = req.to_dict()
        assert d["title"] == "Doc"
        assert d["output_format"] == "markdown"
        assert len(d["sections"]) == 1

    def test_document_request_with_metadata(self) -> None:
        section = DocumentSection(heading="S1")
        meta = DocumentMetadata(author="test")
        req = DocumentRequest(title="Doc", sections=(section,), metadata=meta)
        assert req.metadata.author == "test"


class TestDocumentResult:
    """Tests voor DocumentResult frozen dataclass."""

    def test_document_result_creation(self) -> None:
        result = DocumentResult(path="/tmp/doc.md", format=DocumentFormat.MARKDOWN, size_bytes=100)
        assert result.path == "/tmp/doc.md"
        assert result.format == DocumentFormat.MARKDOWN
        assert result.size_bytes == 100

    def test_document_result_path_required(self) -> None:
        with pytest.raises(ValueError, match="path is required"):
            DocumentResult(path="", format=DocumentFormat.MARKDOWN)

    def test_document_result_to_dict(self) -> None:
        result = DocumentResult(
            path="/tmp/doc.odt",
            format=DocumentFormat.ODF,
            size_bytes=2048,
            checksum="abc123",
        )
        d = result.to_dict()
        assert d["path"] == "/tmp/doc.odt"
        assert d["format"] == "odf"
        assert d["checksum"] == "abc123"
