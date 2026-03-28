"""
Genereer het PoC document "Wat is DevHub?" via de devhub-documents pipeline.

Dit script valideert de Diátaxis+ taxonomie door het eerste document te genereren
in zowel Markdown als ODF formaat.
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


def build_poc_request(output_format: DocumentFormat, output_dir: str) -> DocumentRequest:
    """Bouw de DocumentRequest voor het 'Wat is DevHub?' PoC document."""
    metadata = DocumentMetadata(
        author="devhub",
        category="explanation",
        date="2026-03-28",
        grade="SILVER",
        sources=(
            "docs/compliance/DEV_CONSTITUTION.md",
            ".claude/CLAUDE.md",
            "docs/architecture/OVERVIEW.md",
        ),
        tags=("architectuur", "introductie", "devhub"),
        version="1.0",
    )

    sections = (
        DocumentSection(
            heading="Context",
            content=(
                "DevHub is Niels' project-agnostisch development-systeem. "
                "Het functioneert als een Second Development Brain dat development-kennis, "
                "governance en werkwijze borgt los van individuele projecten. "
                "DevHub is de ontwikkelaar. Projecten (zoals buurts-ecosysteem/BORIS) "
                "zijn wat DevHub bouwt en onderhoudt."
            ),
        ),
        DocumentSection(
            heading="Drie-lagen Architectuur",
            content="DevHub is opgebouwd uit drie lagen die elk een specifieke rol vervullen.",
            subsections=(
                DocumentSection(
                    heading="Laag 1: Python-systeem",
                    content=(
                        "De runtime — analyseert, decomponeert, checkt kwaliteit. "
                        "Gemanaged als uv workspace met vier packages: "
                        "devhub-core (contracts, agents, registry), "
                        "devhub-storage (Local, Google Drive, SharePoint adapters), "
                        "devhub-vectorstore (ChromaDB, Weaviate, embeddings), "
                        "devhub-documents (Markdown, ODF adapters)."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="Laag 2: Claude Code Plugin",
                    content=(
                        "De AI-interface — agents en skills die Claude Code gebruikers "
                        "toegang geven tot het devhub-systeem. Bevat 7 plugin agents "
                        "(dev-lead, coder, reviewer, researcher, planner, red-team, "
                        "knowledge-curator) en 10 skills voor sprint management, "
                        "health checks, code review en meer."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="Laag 3: Second Brain",
                    content=(
                        "Het geheugen — governance, kennis, beslissingen. "
                        "Bevat de DEV_CONSTITUTION (9 artikelen), ADRs, golden paths, "
                        "runbooks en de kennisbank met EVIDENCE-grading."
                    ),
                    level=2,
                ),
            ),
        ),
        DocumentSection(
            heading="DevHub en Projecten",
            content=(
                "DevHub upgradet projecten met behoud van hun essentie. "
                "Het eerste managed project is buurts-ecosysteem (BORIS), "
                "geregistreerd als git submodule in projects/ en geconfigureerd "
                "in config/nodes.yml. De BorisAdapter (NodeInterface implementatie) "
                "geeft DevHub read-only toegang tot BORIS' codebase, tests en documentatie. "
                "Kennis stroomt in twee richtingen: DevHub leert van projecten "
                "en projecten profiteren van DevHub's SOTA-kennis."
            ),
        ),
        DocumentSection(
            heading="Kernprincipes",
            content="DevHub opereert volgens de DEV_CONSTITUTION en aanvullende werkwijzen.",
            subsections=(
                DocumentSection(
                    heading="Governance",
                    content=(
                        "De DEV_CONSTITUTION bevat 9 artikelen die altijd bindend zijn. "
                        "Art. 1: Developer beslist, DevHub voert uit. "
                        "Art. 6: Project-soevereiniteit — wanneer je in een project werkt, "
                        "gelden de regels van dat project. "
                        "Art. 8: Geen secrets, credentials of PII in commits."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="Kennisintegriteit",
                    content=(
                        "Verificatieplicht: claims verifiëren tegen primaire bronnen. "
                        "Kennisgradering: GOLD (bewezen), SILVER (gevalideerd), "
                        "BRONZE (ervaring), SPECULATIVE (aanname). "
                        "Impact-zonering: GREEN (veilig), YELLOW (review vereist), "
                        "RED (menselijke goedkeuring)."
                    ),
                    level=2,
                ),
            ),
        ),
        DocumentSection(
            heading="Werkwijze",
            content="DevHub combineert bewezen methodieken voor gestructureerde ontwikkeling.",
            subsections=(
                DocumentSection(
                    heading="Shape Up",
                    content=(
                        "Probleem → Oplossing → Grenzen → Appetite. "
                        "Sprints worden geshaped met een duidelijke scope en tijdsbox. "
                        "Hill Charts visualiseren voortgang: uphill (uitzoeken) "
                        "en downhill (uitvoeren met vertrouwen)."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="Definition of Ready",
                    content=(
                        "8-punten checklist vóór sprint-start: scope gedefinieerd, "
                        "baseline tests slagen, afhankelijkheden afgerond, "
                        "anti-patronen gedocumenteerd, acceptatiecriteria meetbaar, "
                        "risico's benoemd, mentor-review uitgevoerd, "
                        "n8n impact geanalyseerd."
                    ),
                    level=2,
                ),
                DocumentSection(
                    heading="Diátaxis+ Documentatie",
                    content=(
                        "Drielaags documentatie-taxonomie: "
                        "Laag 1 (Product): tutorial, howto, reference, explanation. "
                        "Laag 2 (Proces): pattern, analysis, decision, retrospective. "
                        "Laag 3 (Kennisbank): methodology, best_practice, sota_review, playbook."
                    ),
                    level=2,
                ),
            ),
        ),
    )

    return DocumentRequest(
        title="Wat is DevHub?",
        sections=sections,
        metadata=metadata,
        output_format=output_format,
        output_dir=output_dir,
    )


def main() -> None:
    """Genereer het PoC document in Markdown en ODF."""
    config_path = Path("config/documents.yml")
    factory = DocumentFactory(config_path=config_path)

    base_dir = "output/documents/explanation"

    # Markdown
    md_request = build_poc_request(DocumentFormat.MARKDOWN, base_dir)
    md_adapter = factory.create_adapter(DocumentFormat.MARKDOWN)
    md_result = md_adapter.create(md_request)
    print(f"Markdown: {md_result.path} ({md_result.size_bytes} bytes)")

    # ODF (indien beschikbaar)
    try:
        odf_request = build_poc_request(DocumentFormat.ODF, base_dir)
        odf_adapter = factory.create_adapter(DocumentFormat.ODF)
        odf_result = odf_adapter.create(odf_request)
        print(f"ODF: {odf_result.path} ({odf_result.size_bytes} bytes)")
    except ImportError:
        print("ODF: overgeslagen (odfpy niet geïnstalleerd)")


if __name__ == "__main__":
    main()
