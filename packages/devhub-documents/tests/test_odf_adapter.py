"""
Tests voor devhub_documents.adapters.odf_adapter — ODFAdapter.

Wordt overgeslagen als odfpy niet geinstalleerd is.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

odf = pytest.importorskip("odf", reason="odfpy not installed")

from devhub_documents.adapters.odf_adapter import ODFAdapter  # noqa: E402
from devhub_documents.contracts import (  # noqa: E402
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentResult,
    DocumentSection,
)


@pytest.fixture
def adapter() -> ODFAdapter:
    return ODFAdapter()


class TestODFAdapter:
    """Tests voor ODFAdapter."""

    def test_create_odf_basic(self, adapter: ODFAdapter) -> None:
        section = DocumentSection(heading="Intro", content="Hello ODF.")
        request = DocumentRequest(
            title="Basic ODF Doc",
            sections=(section,),
            output_format=DocumentFormat.ODF,
        )
        result = adapter.create(request)

        assert isinstance(result, DocumentResult)
        assert result.format == DocumentFormat.ODF
        assert result.path.endswith(".odt")
        assert result.size_bytes > 0
        assert result.checksum != ""
        assert Path(result.path).exists()

    def test_create_odf_with_sections(self, adapter: ODFAdapter) -> None:
        sections = (
            DocumentSection(heading="Sectie 1", content="Content 1"),
            DocumentSection(heading="Sectie 2", content="Content 2"),
        )
        request = DocumentRequest(
            title="Multi Section ODF",
            sections=sections,
            output_format=DocumentFormat.ODF,
        )
        result = adapter.create(request)
        assert Path(result.path).exists()
        assert result.size_bytes > 0

    def test_create_odf_with_metadata(self, adapter: ODFAdapter) -> None:
        meta = DocumentMetadata(
            author="niels",
            date="2026-03-26",
            grade="SILVER",
        )
        section = DocumentSection(heading="Body", content="Text.")
        request = DocumentRequest(
            title="Meta ODF",
            sections=(section,),
            metadata=meta,
            output_format=DocumentFormat.ODF,
        )
        result = adapter.create(request)
        assert Path(result.path).exists()
        assert result.size_bytes > 0

    def test_odf_file_is_valid(self, adapter: ODFAdapter) -> None:
        """Verify the generated file exists and has meaningful size."""
        section = DocumentSection(heading="Test", content="Validation test.")
        request = DocumentRequest(
            title="Valid ODF",
            sections=(section,),
            output_format=DocumentFormat.ODF,
        )
        result = adapter.create(request)
        path = Path(result.path)
        assert path.exists()
        assert path.stat().st_size > 100  # ODF files have overhead
        assert result.size_bytes == path.stat().st_size

    def test_create_odf_with_output_dir(self, adapter: ODFAdapter) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            section = DocumentSection(heading="Test", content="Body")
            request = DocumentRequest(
                title="Output Dir ODF",
                sections=(section,),
                output_format=DocumentFormat.ODF,
                output_dir=tmpdir,
            )
            result = adapter.create(request)
            assert tmpdir in result.path
            assert Path(result.path).exists()

    def test_supported_formats(self, adapter: ODFAdapter) -> None:
        assert adapter.supported_formats() == ["odf"]

    def test_from_template_not_implemented(self, adapter: ODFAdapter) -> None:
        with pytest.raises(NotImplementedError):
            adapter.from_template("/tmp/template.odt", {"key": "value"})

    def test_create_odf_with_subsections(self, adapter: ODFAdapter) -> None:
        sub = DocumentSection(heading="Sub A", content="Sub content", level=2)
        parent = DocumentSection(heading="Parent", content="Parent content", subsections=(sub,))
        request = DocumentRequest(
            title="Nested ODF",
            sections=(parent,),
            output_format=DocumentFormat.ODF,
        )
        result = adapter.create(request)
        assert Path(result.path).exists()
        assert result.size_bytes > 0
