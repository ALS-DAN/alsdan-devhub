"""
Document Contracts — Frozen dataclasses voor document-generatie.

Conform het devhub-core frozen dataclass pattern (ADR-049).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class DocumentFormat(Enum):
    """Ondersteunde document output formaten."""

    ODF = "odf"
    MARKDOWN = "markdown"


class DocumentCategory(Enum):
    """Diátaxis+ documentatie-categorieën in drie lagen."""

    # Laag 1: Product (Diátaxis standaard)
    TUTORIAL = "tutorial"
    HOWTO = "howto"
    REFERENCE = "reference"
    EXPLANATION = "explanation"

    # Laag 2: Proces
    PATTERN = "pattern"
    ANALYSIS = "analysis"
    DECISION = "decision"
    RETROSPECTIVE = "retrospective"

    # Laag 3: Kennisbank
    METHODOLOGY = "methodology"
    BEST_PRACTICE = "best_practice"
    SOTA_REVIEW = "sota_review"
    PLAYBOOK = "playbook"

    def layer(self) -> str:
        """Geeft de laag terug waartoe deze categorie behoort."""
        _layers = {
            "tutorial": "product",
            "howto": "product",
            "reference": "product",
            "explanation": "product",
            "pattern": "process",
            "analysis": "process",
            "decision": "process",
            "retrospective": "process",
            "methodology": "knowledge",
            "best_practice": "knowledge",
            "sota_review": "knowledge",
            "playbook": "knowledge",
        }
        return _layers[self.value]

    @classmethod
    def from_string(cls, value: str) -> DocumentCategory:
        """Case-insensitive lookup van een categorie string."""
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Unknown category: '{value}'. " f"Valid: {[m.value for m in cls]}")


@dataclass(frozen=True)
class DocumentSection:
    """Een sectie binnen een document, met optionele subsecties."""

    heading: str
    content: str = ""
    level: int = 1
    subsections: tuple[DocumentSection, ...] = ()

    def __post_init__(self) -> None:
        if not self.heading or not self.heading.strip():
            raise ValueError("heading is required and cannot be empty")
        if not isinstance(self.level, int) or self.level < 1 or self.level > 6:
            raise ValueError(f"level must be between 1 and 6, got {self.level}")

    def to_dict(self) -> dict:
        """Serialiseer naar dictionary."""
        return {
            "heading": self.heading,
            "content": self.content,
            "level": self.level,
            "subsections": [s.to_dict() for s in self.subsections],
        }


@dataclass(frozen=True)
class DocumentMetadata:
    """Metadata voor een gegenereerd document."""

    author: str = "devhub"
    category: str | None = None
    date: str = ""
    grade: Literal["GOLD", "SILVER", "BRONZE", "SPECULATIVE"] | None = None
    sources: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    version: str = "1.0"

    def to_dict(self) -> dict:
        """Serialiseer naar dictionary."""
        result: dict = {
            "author": self.author,
            "version": self.version,
        }
        if self.category:
            result["category"] = self.category
        if self.date:
            result["date"] = self.date
        if self.grade:
            result["grade"] = self.grade
        if self.sources:
            result["sources"] = list(self.sources)
        if self.tags:
            result["tags"] = list(self.tags)
        return result


@dataclass(frozen=True)
class DocumentRequest:
    """Opdracht voor document-generatie."""

    title: str
    sections: tuple[DocumentSection, ...]
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    output_format: DocumentFormat = DocumentFormat.MARKDOWN
    template: str = ""
    output_dir: str = ""

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("title is required and cannot be empty")
        if not self.sections:
            raise ValueError("sections is required and cannot be empty")

    def to_dict(self) -> dict:
        """Serialiseer naar dictionary."""
        return {
            "title": self.title,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata.to_dict(),
            "output_format": self.output_format.value,
            "template": self.template,
            "output_dir": self.output_dir,
        }


@dataclass(frozen=True)
class DocumentResult:
    """Resultaat van document-generatie."""

    path: str
    format: DocumentFormat
    size_bytes: int = 0
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.path or not self.path.strip():
            raise ValueError("path is required and cannot be empty")

    def to_dict(self) -> dict:
        """Serialiseer naar dictionary."""
        return {
            "path": self.path,
            "format": self.format.value,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
        }
