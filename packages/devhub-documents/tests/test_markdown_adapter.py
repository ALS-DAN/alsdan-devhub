"""
Tests voor devhub_documents.adapters.markdown_adapter — MarkdownAdapter.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from devhub_documents.adapters.markdown_adapter import MarkdownAdapter
from devhub_documents.contracts import (
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentResult,
    DocumentSection,
)


@pytest.fixture
def adapter() -> MarkdownAdapter:
    return MarkdownAdapter()


class TestMarkdownAdapter:
    """Tests voor MarkdownAdapter."""

    def test_create_markdown_basic(self, adapter: MarkdownAdapter) -> None:
        section = DocumentSection(heading="Intro", content="Hello world.")
        request = DocumentRequest(title="Basic Doc", sections=(section,))
        result = adapter.create(request)

        assert isinstance(result, DocumentResult)
        assert result.format == DocumentFormat.MARKDOWN
        assert result.path.endswith(".md")
        assert result.size_bytes > 0
        assert result.checksum != ""

        content = Path(result.path).read_text(encoding="utf-8")
        assert "# Basic Doc" in content
        assert "Hello world." in content

    def test_create_markdown_with_sections(self, adapter: MarkdownAdapter) -> None:
        sections = (
            DocumentSection(heading="Sectie 1", content="Content 1"),
            DocumentSection(heading="Sectie 2", content="Content 2"),
        )
        request = DocumentRequest(title="Multi Section", sections=sections)
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "## Sectie 1" in content
        assert "## Sectie 2" in content
        assert "Content 1" in content
        assert "Content 2" in content

    def test_create_markdown_with_subsections(self, adapter: MarkdownAdapter) -> None:
        sub = DocumentSection(heading="Sub A", content="Sub content", level=2)
        parent = DocumentSection(heading="Parent", content="Parent content", subsections=(sub,))
        request = DocumentRequest(title="Nested Doc", sections=(parent,))
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "## Parent" in content
        assert "### Sub A" in content
        assert "Sub content" in content

    def test_create_markdown_with_metadata(self, adapter: MarkdownAdapter) -> None:
        meta = DocumentMetadata(
            author="niels",
            date="2026-03-26",
            grade="GOLD",
            sources=("bron1.md",),
            tags=("test", "docs"),
            version="0.2.0",
        )
        section = DocumentSection(heading="Body", content="Text.")
        request = DocumentRequest(title="Meta Doc", sections=(section,), metadata=meta)
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "author: niels" in content
        assert "date: 2026-03-26" in content
        assert "grade: GOLD" in content
        assert "version: 0.2.0" in content
        assert "- bron1.md" in content
        assert "- test" in content

    def test_create_markdown_with_output_dir(self, adapter: MarkdownAdapter) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            section = DocumentSection(heading="Test", content="Body")
            request = DocumentRequest(
                title="Output Dir Test", sections=(section,), output_dir=tmpdir
            )
            result = adapter.create(request)

            assert tmpdir in result.path
            assert Path(result.path).exists()

    def test_supported_formats(self, adapter: MarkdownAdapter) -> None:
        assert adapter.supported_formats() == ["markdown"]

    def test_from_template_not_implemented(self, adapter: MarkdownAdapter) -> None:
        with pytest.raises(NotImplementedError):
            adapter.from_template("/tmp/template.md", {"key": "value"})

    def test_create_markdown_with_category_in_frontmatter(self, adapter: MarkdownAdapter) -> None:
        meta = DocumentMetadata(category="explanation", grade="SILVER")
        section = DocumentSection(heading="Test", content="Body")
        request = DocumentRequest(title="Category Doc", sections=(section,), metadata=meta)
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "category: explanation" in content
        assert "grade: SILVER" in content

    def test_create_markdown_without_category_in_frontmatter(
        self,
        adapter: MarkdownAdapter,
    ) -> None:
        meta = DocumentMetadata()
        section = DocumentSection(heading="Test", content="Body")
        request = DocumentRequest(
            title="No Category",
            sections=(section,),
            metadata=meta,
        )
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "category:" not in content

    def test_create_markdown_frontmatter_delimiters(self, adapter: MarkdownAdapter) -> None:
        section = DocumentSection(heading="Test", content="Body")
        request = DocumentRequest(title="Frontmatter Check", sections=(section,))
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        lines = content.split("\n")
        assert lines[0] == "---"
        # Find second ---
        delimiter_count = sum(1 for line in lines if line == "---")
        assert delimiter_count >= 2
