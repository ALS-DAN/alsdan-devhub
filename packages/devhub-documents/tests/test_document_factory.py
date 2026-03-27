"""
Tests voor devhub_documents.factory — DocumentFactory.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from devhub_documents.adapters.markdown_adapter import MarkdownAdapter
from devhub_documents.contracts import DocumentFormat
from devhub_documents.factory import DocumentFactory


@pytest.fixture
def config_path() -> str:
    """Pad naar de documents.yml config."""
    return str(Path(__file__).resolve().parents[3] / "config" / "documents.yml")


@pytest.fixture
def factory(config_path: str) -> DocumentFactory:
    return DocumentFactory(config_path)


class TestDocumentFactory:
    """Tests voor DocumentFactory."""

    def test_factory_creates_markdown_adapter(self, factory: DocumentFactory) -> None:
        adapter = factory.create_adapter("markdown")
        assert isinstance(adapter, MarkdownAdapter)

    def test_factory_creates_markdown_from_enum(self, factory: DocumentFactory) -> None:
        adapter = factory.create_adapter(DocumentFormat.MARKDOWN)
        assert isinstance(adapter, MarkdownAdapter)

    def test_factory_creates_odf_adapter(self, factory: DocumentFactory) -> None:
        try:
            adapter = factory.create_adapter("odf")
            from devhub_documents.adapters.odf_adapter import ODFAdapter

            assert isinstance(adapter, ODFAdapter)
        except ImportError:
            pytest.skip("odfpy not installed")

    def test_factory_default_format(self, factory: DocumentFactory) -> None:
        assert factory.default_format == "markdown"
        adapter = factory.create_adapter()  # Uses default
        assert isinstance(adapter, MarkdownAdapter)

    def test_factory_unsupported_format(self, factory: DocumentFactory) -> None:
        with pytest.raises(ValueError, match="Unsupported document format"):
            factory.create_adapter("pdf")

    def test_factory_without_config(self) -> None:
        factory = DocumentFactory()
        assert factory.default_format == "markdown"
        adapter = factory.create_adapter()
        assert isinstance(adapter, MarkdownAdapter)

    def test_factory_with_nonexistent_config(self) -> None:
        factory = DocumentFactory("/nonexistent/config.yml")
        assert factory.default_format == "markdown"

    def test_factory_config_properties(self, factory: DocumentFactory) -> None:
        assert factory.output_dir == "output/documents"
        assert factory.config.get("adapters", {}).get("markdown", {}).get("enabled") is True

    def test_factory_disabled_adapter(self) -> None:
        """Test that disabled adapters raise ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("documents:\n  adapters:\n    markdown:\n      enabled: false\n")
            f.flush()
            factory = DocumentFactory(f.name)
            with pytest.raises(ValueError, match="disabled"):
                factory.create_adapter("markdown")
