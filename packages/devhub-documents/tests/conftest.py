"""
Shared fixtures voor devhub-documents tests.
"""

from __future__ import annotations

import pytest

from devhub_documents.contracts import (
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentSection,
)


@pytest.fixture
def sample_section() -> DocumentSection:
    """Een basis DocumentSection."""
    return DocumentSection(heading="Introductie", content="Dit is de introductie.", level=1)


@pytest.fixture
def sample_section_with_subsections() -> DocumentSection:
    """Een DocumentSection met subsecties."""
    sub1 = DocumentSection(heading="Subsectie A", content="Content A", level=2)
    sub2 = DocumentSection(heading="Subsectie B", content="Content B", level=2)
    return DocumentSection(
        heading="Hoofdsectie",
        content="Overzicht",
        level=1,
        subsections=(sub1, sub2),
    )


@pytest.fixture
def sample_metadata() -> DocumentMetadata:
    """DocumentMetadata met alle velden ingevuld."""
    return DocumentMetadata(
        author="test-author",
        date="2026-03-26",
        grade="SILVER",
        sources=("bron-1.md", "bron-2.md"),
        tags=("kennispipeline", "test"),
        version="0.1.0",
    )


@pytest.fixture
def sample_request(sample_section: DocumentSection) -> DocumentRequest:
    """Een basis DocumentRequest."""
    return DocumentRequest(
        title="Test Document",
        sections=(sample_section,),
    )


@pytest.fixture
def full_request(
    sample_section_with_subsections: DocumentSection,
    sample_metadata: DocumentMetadata,
) -> DocumentRequest:
    """Een volledig ingevulde DocumentRequest."""
    section2 = DocumentSection(heading="Conclusie", content="Samenvatting.", level=1)
    return DocumentRequest(
        title="Volledig Test Document",
        sections=(sample_section_with_subsections, section2),
        metadata=sample_metadata,
        output_format=DocumentFormat.MARKDOWN,
    )
