"""
Tests voor het PoC document "Wat is DevHub?" — valideert de Diátaxis+ pipeline.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from devhub_documents.contracts import DocumentFormat
from devhub_documents.factory import DocumentFactory

# Import de builder uit het script
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from generate_poc_document import build_poc_request


@pytest.fixture
def md_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestPocDocument:
    """Tests voor het PoC document generatie via devhub-documents pipeline."""

    def test_poc_document_markdown_generation(self, md_output_dir: str) -> None:
        request = build_poc_request(DocumentFormat.MARKDOWN, md_output_dir)
        factory = DocumentFactory()
        adapter = factory.create_adapter(DocumentFormat.MARKDOWN)
        result = adapter.create(request)

        assert result.size_bytes > 0
        content = Path(result.path).read_text(encoding="utf-8")
        assert "category: explanation" in content
        assert "grade: SILVER" in content

    def test_poc_document_metadata_complete(self, md_output_dir: str) -> None:
        request = build_poc_request(DocumentFormat.MARKDOWN, md_output_dir)
        factory = DocumentFactory()
        adapter = factory.create_adapter(DocumentFormat.MARKDOWN)
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "author: devhub" in content
        assert "version: 1.0" in content
        assert "date: 2026-03-28" in content
        assert "- architectuur" in content
        assert "- introductie" in content

    def test_poc_document_sections_complete(self, md_output_dir: str) -> None:
        request = build_poc_request(DocumentFormat.MARKDOWN, md_output_dir)
        factory = DocumentFactory()
        adapter = factory.create_adapter(DocumentFormat.MARKDOWN)
        result = adapter.create(request)

        content = Path(result.path).read_text(encoding="utf-8")
        assert "# Wat is DevHub?" in content
        assert "## Context" in content
        assert "## Drie-lagen Architectuur" in content
        assert "### Laag 1: Python-systeem" in content
        assert "## DevHub en Projecten" in content
        assert "## Kernprincipes" in content
        assert "## Werkwijze" in content

    def test_poc_document_odf_generation(self, md_output_dir: str) -> None:
        try:
            request = build_poc_request(DocumentFormat.ODF, md_output_dir)
            factory = DocumentFactory()
            adapter = factory.create_adapter(DocumentFormat.ODF)
            result = adapter.create(request)

            assert result.size_bytes > 0
            assert Path(result.path).exists()
            assert result.format == DocumentFormat.ODF
        except ImportError:
            pytest.skip("odfpy not installed")
