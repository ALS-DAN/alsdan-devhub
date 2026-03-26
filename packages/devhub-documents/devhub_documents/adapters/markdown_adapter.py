"""
MarkdownAdapter — Genereert Markdown documenten vanuit DocumentRequest.
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


class MarkdownAdapter(DocumentInterface):
    """Adapter die Markdown (.md) bestanden genereert."""

    def create(self, request: DocumentRequest) -> DocumentResult:
        """Genereer een .md bestand vanuit een DocumentRequest."""
        content = self._build_content(request)

        # Bepaal output pad
        if request.output_dir:
            output_dir = Path(request.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(tempfile.mkdtemp(prefix="devhub_docs_"))

        filename = self._slugify(request.title) + ".md"
        output_path = output_dir / filename
        output_path.write_text(content, encoding="utf-8")

        size = output_path.stat().st_size
        checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()

        return DocumentResult(
            path=str(output_path),
            format=DocumentFormat.MARKDOWN,
            size_bytes=size,
            checksum=checksum,
        )

    def from_template(self, template_path: str, data: dict) -> DocumentResult:
        """Template-generatie is nog niet geimplementeerd."""
        raise NotImplementedError("from_template is not yet supported for MarkdownAdapter")

    def supported_formats(self) -> list[str]:
        """Ondersteunde formaten."""
        return ["markdown"]

    def _build_content(self, request: DocumentRequest) -> str:
        """Bouw de volledige Markdown content op."""
        parts: list[str] = []

        # YAML frontmatter
        meta = request.metadata
        parts.append("---")
        parts.append(f"author: {meta.author}")
        parts.append(f"version: {meta.version}")
        if meta.date:
            parts.append(f"date: {meta.date}")
        if meta.grade:
            parts.append(f"grade: {meta.grade}")
        if meta.sources:
            parts.append("sources:")
            for src in meta.sources:
                parts.append(f"  - {src}")
        if meta.tags:
            parts.append("tags:")
            for tag in meta.tags:
                parts.append(f"  - {tag}")
        parts.append("---")
        parts.append("")

        # Title als H1
        parts.append(f"# {request.title}")
        parts.append("")

        # Secties
        for section in request.sections:
            self._render_section(section, parts)

        return "\n".join(parts)

    def _render_section(self, section: DocumentSection, parts: list[str]) -> None:
        """Render een sectie recursief."""
        prefix = "#" * (section.level + 1)  # +1 want title is H1
        parts.append(f"{prefix} {section.heading}")
        parts.append("")
        if section.content:
            parts.append(section.content)
            parts.append("")
        for sub in section.subsections:
            self._render_section(sub, parts)

    @staticmethod
    def _slugify(text: str) -> str:
        """Maak een bestandsnaam-veilige slug van tekst."""
        slug = text.lower().strip()
        slug = slug.replace(" ", "-")
        # Verwijder niet-alfanumerieke tekens behalve hyphens
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        # Verwijder dubbele hyphens
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-") or "document"
