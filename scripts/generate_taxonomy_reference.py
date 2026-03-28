"""
Genereer het taxonomie-referentiedocument — de kennisbank documenteert zichzelf.

Categorie: reference | Grade: SILVER
"""

from __future__ import annotations

from pathlib import Path

from devhub_documents.contracts import (
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentSection,
)
from devhub_documents.factory import DocumentFactory


def build_taxonomy_reference(output_dir: str) -> DocumentRequest:
    """Bouw de DocumentRequest voor het taxonomie-referentiedocument."""
    metadata = DocumentMetadata(
        author="devhub",
        category="reference",
        date="2026-03-28",
        grade="SILVER",
        sources=("config/documents.yml",),
        tags=("taxonomie", "diataxis", "documentatie", "referentie"),
        version="1.0",
    )

    sections = (
        DocumentSection(
            heading="Overzicht",
            content=(
                "De Diátaxis+ taxonomie breidt het standaard Diátaxis framework "
                "(tutorial, howto, reference, explanation) uit met twee extra lagen: "
                "procesgericht en kennisbank. Samen bieden de 12 categorieën "
                "volledige dekking voor productdocumentatie, ontwikkelproces "
                "en expert knowledge."
            ),
        ),
        DocumentSection(
            heading="Laag 1: Product (Diátaxis standaard)",
            content="De vier originele Diátaxis-categorieën voor productdocumentatie.",
            subsections=(
                DocumentSection(
                    heading="tutorial",
                    content="Leren door doen. Stap-voor-stap begeleiding voor beginners.",
                    level=2,
                ),
                DocumentSection(
                    heading="howto",
                    content="Taakgericht. Beschrijft hoe je een specifiek probleem oplost.",
                    level=2,
                ),
                DocumentSection(
                    heading="reference",
                    content=(
                        "Informatie opzoeken. Technische specificaties, "
                        "API-documentatie, parameters."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="explanation",
                    content=(
                        "Achtergrond en context. Waarom iets bestaat, "
                        "hoe het werkt, design beslissingen."
                    ),
                    level=2,
                ),
            ),
        ),
        DocumentSection(
            heading="Laag 2: Proces",
            content="Categorieën gericht op het ontwikkelproces zelf.",
            subsections=(
                DocumentSection(
                    heading="pattern",
                    content=(
                        "Gevonden patronen. Beschrijft terugkerende "
                        "oplossingen met context, krachten en consequenties."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="analysis",
                    content=(
                        "Onderzoek en bevindingen. Onderzoeksvraag, "
                        "methode, bevindingen en aanbevelingen."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="decision",
                    content=(
                        "Architectuur/ontwerp-beslissingen. Context, "
                        "argumenten voor/tegen, consequenties, status."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="retrospective",
                    content=(
                        "Terugblik op een sprint of periode. Successen, "
                        "verbeterpunten, actiepunten, metrics."
                    ),
                    level=2,
                ),
            ),
        ),
        DocumentSection(
            heading="Laag 3: Kennisbank",
            content="Expert knowledge categorieën voor de kennisbank.",
            subsections=(
                DocumentSection(
                    heading="methodology",
                    content=(
                        "Werkwijzen en methodieken. Principes, proces, " "rollen en toepasbaarheid."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="best_practice",
                    content=(
                        "Bewezen werkwijzen. Principe, onderbouwing, " "toepassing en valkuilen."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="sota_review",
                    content=(
                        "State of the art reviews. Huidige stand, "
                        "trends, spelers en relevantie-beoordeling."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="playbook",
                    content=(
                        "Draaiboeken. Voorbereidingschecklist, "
                        "stappen, escalatiepunten en afronding."
                    ),
                    level=2,
                ),
            ),
        ),
        DocumentSection(
            heading="Configuratie",
            content=(
                "De taxonomie is geconfigureerd in config/documents.yml onder de "
                "'taxonomy' sectie. Per node (project) kan een subset van categorieën "
                "geactiveerd worden. De DocumentCategory enum in "
                "devhub_documents.contracts bevat alle 12 categorieën met "
                "layer() en from_string() methodes."
            ),
        ),
    )

    return DocumentRequest(
        title="Diátaxis+ Documentatie-Taxonomie",
        sections=sections,
        metadata=metadata,
        output_format=DocumentFormat.MARKDOWN,
        output_dir=output_dir,
    )


def main() -> None:
    """Genereer het taxonomie-referentiedocument."""
    output_dir = "output/documents/reference"
    request = build_taxonomy_reference(output_dir)
    factory = DocumentFactory(config_path=Path("config/documents.yml"))
    adapter = factory.create_adapter(DocumentFormat.MARKDOWN)
    result = adapter.create(request)
    print(f"Reference: {result.path} ({result.size_bytes} bytes)")


if __name__ == "__main__":
    main()
