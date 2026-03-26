"""
Tests voor devhub_documents.interface — ABC contract.
"""

from __future__ import annotations

import pytest

from devhub_documents.contracts import DocumentFormat, DocumentRequest, DocumentResult
from devhub_documents.interface import DocumentInterface


class TestDocumentInterface:
    """Tests voor het DocumentInterface ABC."""

    def test_cannot_instantiate_abc(self) -> None:
        with pytest.raises(TypeError):
            DocumentInterface()  # type: ignore[abstract]

    def test_concrete_implementation(self) -> None:
        class StubAdapter(DocumentInterface):
            def create(self, request: DocumentRequest) -> DocumentResult:
                return DocumentResult(path="/tmp/stub.md", format=DocumentFormat.MARKDOWN)

            def from_template(self, template_path: str, data: dict) -> DocumentResult:
                return DocumentResult(path="/tmp/stub.md", format=DocumentFormat.MARKDOWN)

            def supported_formats(self) -> list[str]:
                return ["markdown"]

        adapter = StubAdapter()
        assert "markdown" in adapter.supported_formats()

    def test_interface_has_required_methods(self) -> None:
        assert hasattr(DocumentInterface, "create")
        assert hasattr(DocumentInterface, "from_template")
        assert hasattr(DocumentInterface, "supported_formats")
