"""
ODFAdapter — Genereert ODF (.odt) documenten vanuit DocumentRequest.

Vereist odfpy >= 1.4 als optionele dependency.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from devhub_documents.contracts import (
    DocumentFormat,
    DocumentRequest,
    DocumentResult,
    DocumentSection,
)
from devhub_documents.interface import DocumentInterface

try:
    from odf import meta as odf_meta
    from odf.opendocument import OpenDocumentText
    from odf.text import H, P

    HAS_ODFPY = True
except ImportError:
    HAS_ODFPY = False


class ODFAdapter(DocumentInterface):
    """Adapter die ODF (.odt) bestanden genereert via odfpy."""

    def __init__(self) -> None:
        if not HAS_ODFPY:
            raise ImportError(
                "odfpy is required for ODFAdapter. "
                "Install with: pip install odfpy>=1.4 or uv pip install devhub-documents[odf]"
            )

    def create(self, request: DocumentRequest) -> DocumentResult:
        """Genereer een .odt bestand vanuit een DocumentRequest."""
        doc = OpenDocumentText()

        # Metadata
        meta = request.metadata
        doc.meta.addElement(odf_meta.InitialCreator(text=meta.author))
        if meta.date:
            doc.meta.addElement(odf_meta.CreationDate(text=meta.date))
        if meta.category:
            doc.meta.addElement(odf_meta.Keyword(text=f"category:{meta.category}"))

        # Title als heading level 1
        title_heading = H(outlinelevel=1, text=request.title)
        doc.text.addElement(title_heading)

        # Secties
        for section in request.sections:
            self._render_section(doc, section)

        # Bepaal output pad
        if request.output_dir:
            output_dir = Path(request.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(tempfile.mkdtemp(prefix="devhub_docs_"))

        filename = self._slugify(request.title) + ".odt"
        output_path = output_dir / filename
        doc.save(str(output_path))

        size = output_path.stat().st_size
        file_bytes = output_path.read_bytes()
        checksum = hashlib.sha256(file_bytes).hexdigest()

        return DocumentResult(
            path=str(output_path),
            format=DocumentFormat.ODF,
            size_bytes=size,
            checksum=checksum,
        )

    def from_template(self, template_path: str, data: dict) -> DocumentResult:
        """Template-generatie is nog niet geimplementeerd."""
        raise NotImplementedError("from_template is not yet supported for ODFAdapter")

    def supported_formats(self) -> list[str]:
        """Ondersteunde formaten."""
        return ["odf"]

    def _render_section(self, doc: OpenDocumentText, section: DocumentSection) -> None:
        """Render een sectie recursief naar het ODF document."""
        heading = H(outlinelevel=section.level + 1, text=section.heading)
        doc.text.addElement(heading)

        if section.content:
            paragraph = P(text=section.content)
            doc.text.addElement(paragraph)

        for sub in section.subsections:
            self._render_section(doc, sub)

    @staticmethod
    def _slugify(text: str) -> str:
        """Maak een bestandsnaam-veilige slug van tekst."""
        slug = text.lower().strip()
        slug = slug.replace(" ", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-") or "document"
