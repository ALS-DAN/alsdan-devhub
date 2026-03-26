"""
DocumentInterface — Abstract contract voor document-generatie backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from devhub_documents.contracts import DocumentRequest, DocumentResult


class DocumentInterface(ABC):
    """Abstract contract voor document-generatie backends."""

    @abstractmethod
    def create(self, request: DocumentRequest) -> DocumentResult:
        """Genereer een document vanuit een DocumentRequest."""
        ...

    @abstractmethod
    def from_template(self, template_path: str, data: dict) -> DocumentResult:
        """Genereer een document vanuit een template met data."""
        ...

    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Lijst van ondersteunde output formaten."""
        ...
