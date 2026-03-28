"""
devhub-documents — Document generation interface and adapters for DevHub.

Ondersteunt ODF en Markdown output via een pluggable adapter architectuur.
"""

from devhub_documents.contracts import (
    DocumentCategory,
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentResult,
    DocumentSection,
)
from devhub_documents.interface import DocumentInterface

__all__ = [
    "DocumentCategory",
    "DocumentFormat",
    "DocumentInterface",
    "DocumentMetadata",
    "DocumentRequest",
    "DocumentResult",
    "DocumentSection",
]
