"""
DocumentService — Pipeline orchestrator voor documentatie-productie.

Verbindt devhub-vectorstore (kennis ophalen), devhub-documents (genereren),
en devhub-storage (publiceren) tot één orkestratieketen.

Volgt het DevOrchestrator patroon: dependency injection, orchestreert maar
implementeert niet. Graceful degradation bij afwezigheid van storage of vectorstore.
"""

from __future__ import annotations

import logging
from datetime import date

from devhub_documents.contracts import (
    DocumentFormat,
    DocumentMetadata,
    DocumentRequest,
    DocumentResult,
    DocumentSection,
)
from devhub_documents.factory import DocumentFactory

from devhub_core.agents.folder_router import FolderRouter
from devhub_core.contracts.pipeline_contracts import (
    DocumentProductionRequest,
    DocumentProductionResult,
    KnowledgeContext,
    PublishStatus,
)

logger = logging.getLogger(__name__)


# --- Diátaxis+ sectie-templates per categorie ---
# Lichtgewicht structuur die sections opbouwt per categorie.
# Gebaseerd op DocsAgent DIATAXIS_TEMPLATES maar als DocumentSection tuples.

_CATEGORY_SECTIONS: dict[str, tuple[tuple[str, str], ...]] = {
    "tutorial": (
        ("Leerdoel", "Wat je leert na het volgen van deze tutorial."),
        ("Vereisten", "Wat je nodig hebt om te beginnen."),
        ("Stappen", ""),
        ("Samenvatting", "Wat je geleerd hebt."),
    ),
    "howto": (
        ("Probleem", "Het probleem dat deze handleiding oplost."),
        ("Oplossing", ""),
        ("Verificatie", "Hoe je controleert dat het gelukt is."),
    ),
    "reference": (
        ("Overzicht", ""),
        ("API / Interface", ""),
        ("Configuratie", ""),
    ),
    "explanation": (
        ("Context", "Waarom dit onderwerp belangrijk is."),
        ("Uitleg", ""),
        ("Implicaties", "Wat dit betekent in de praktijk."),
    ),
    "pattern": (
        ("Context", "Wanneer dit patroon van toepassing is."),
        ("Probleem", "Het terugkerende probleem dat dit patroon oplost."),
        ("Oplossing", "Het patroon beschreven."),
        ("Consequenties", "Trade-offs en gevolgen."),
        ("Voorbeelden", "Concrete toepassingen."),
    ),
    "analysis": (
        ("Onderzoeksvraag", ""),
        ("Methode", ""),
        ("Bevindingen", ""),
        ("Conclusie", ""),
    ),
    "decision": (
        ("Status", "Aangenomen / Voorgesteld / Vervangen"),
        ("Context", "De situatie en het probleem."),
        ("Beslissing", "Wat we besloten hebben."),
        ("Consequenties", "Positieve en negatieve gevolgen."),
    ),
    "retrospective": (
        ("Sprint overzicht", ""),
        ("Wat ging goed", ""),
        ("Wat kan beter", ""),
        ("Actiepunten", ""),
    ),
    "methodology": (
        ("Doel", "Wat deze methodiek bereikt."),
        ("Principes", "De kernprincipes."),
        ("Werkwijze", "Hoe de methodiek in de praktijk werkt."),
        ("Toepassing", "Hoe dit binnen DevHub/het project wordt ingezet."),
    ),
    "best_practice": (
        ("Richtlijn", "De kernregel."),
        ("Waarom", "Rationale achter deze best practice."),
        ("Hoe", "Concrete toepassing."),
        ("Anti-patronen", "Wat je moet vermijden."),
    ),
    "sota_review": (
        ("Onderwerp", ""),
        ("Huidige stand van zaken", ""),
        ("Relevante bronnen", ""),
        ("Toepassing voor DevHub", ""),
    ),
    "playbook": (
        ("Wanneer gebruiken", ""),
        ("Stap-voor-stap procedure", ""),
        ("Escalatie", "Wat te doen als het misgaat."),
        ("Checklist", ""),
    ),
}


def _slugify(text: str) -> str:
    """Genereer een bestandsnaam-veilige slug."""
    import re

    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class DocumentService:
    """Pipeline orchestrator die kennis, document-generatie en storage verbindt.

    Dependency injection: alle externe services worden via de constructor
    meegegeven. None-waarden activeren graceful degradation.

    Args:
        document_factory: Factory voor document-adapters (devhub-documents).
        folder_router: Routering van categorie naar storage-pad.
        storage: Storage backend (None = lokaal-only modus).
        vectorstore: Vectorstore voor kennis-ophalen (None = skip kennis).
    """

    def __init__(
        self,
        document_factory: DocumentFactory,
        folder_router: FolderRouter,
        storage: object | None = None,  # StorageInterface, lazy import
        vectorstore: object | None = None,  # VectorStoreInterface, lazy import
    ) -> None:
        self._factory = document_factory
        self._router = folder_router
        self._storage = storage
        self._vectorstore = vectorstore

    def produce(self, request: DocumentProductionRequest) -> DocumentProductionResult:
        """Produceer een document via de volledige pipeline.

        1. Valideer categorie voor target_node
        2. Query vectorstore (optioneel)
        3. Bouw DocumentRequest
        4. Genereer document
        5. Publiceer naar storage (optioneel)
        6. Return resultaat

        Args:
            request: DocumentProductionRequest met topic, category, etc.

        Returns:
            DocumentProductionResult met document, storage-pad en status.

        Raises:
            ValueError: Als de categorie niet toegestaan is voor de node.
        """
        logger.info(
            "Producing document: topic='%s', category=%s, node=%s",
            request.topic,
            request.category.value,
            request.target_node,
        )

        # 1. Valideer categorie
        if not self._router.is_category_allowed(request.category, request.target_node):
            raise ValueError(
                f"Category '{request.category.value}' is not allowed "
                f"for node '{request.target_node}'"
            )

        # 2. Kennis ophalen
        knowledge: KnowledgeContext | None = None
        if not request.skip_vectorstore and self._vectorstore is not None:
            knowledge = self._query_knowledge(request)

        # 3. Document request bouwen
        doc_request = self._build_document_request(request, knowledge)

        # 4. Document genereren
        adapter = self._factory.create_adapter(request.output_format)
        doc_result = adapter.create(doc_request)

        # 5. Storage-pad bepalen
        ext = ".md" if request.output_format == DocumentFormat.MARKDOWN else ".odt"
        filename = _slugify(request.topic) + ext
        storage_path = self._router.resolve_path(
            request.category, filename, node_id=request.target_node
        )

        # 6. Publiceren
        publish_status = PublishStatus.SKIPPED
        message = ""

        if self._storage is not None:
            publish_status, message = self._publish_to_storage(doc_result, storage_path)
        else:
            message = f"No storage configured, document at {doc_result.path}"

        return DocumentProductionResult(
            document_result=doc_result,
            storage_path=storage_path,
            publish_status=publish_status,
            knowledge_context=knowledge,
            node_id=request.target_node,
            message=message,
        )

    def _query_knowledge(self, request: DocumentProductionRequest) -> KnowledgeContext:
        """Haal relevante kennis op uit de vectorstore."""
        from devhub_vectorstore.contracts.vectorstore_contracts import (
            RetrievalRequest,
        )

        query = request.effective_query
        retrieval = RetrievalRequest(query_text=query, limit=5)

        try:
            response = self._vectorstore.query(retrieval)  # type: ignore[union-attr]
            chunks = tuple(r.chunk.content for r in response.results)
            sources = tuple(r.chunk.source_id for r in response.results if r.chunk.source_id)
            return KnowledgeContext(
                chunks=chunks,
                sources=sources,
                query_used=query,
                total_found=response.total_found,
            )
        except Exception:
            logger.warning("Vectorstore query failed for '%s', continuing without", query)
            return KnowledgeContext(query_used=query)

    def _build_document_request(
        self,
        request: DocumentProductionRequest,
        knowledge: KnowledgeContext | None,
    ) -> DocumentRequest:
        """Bouw een DocumentRequest op basis van categorie-template en kennis."""
        category = request.category
        section_defs = _CATEGORY_SECTIONS.get(category.value, (("Inhoud", ""),))

        sections: list[DocumentSection] = []
        for heading, default_content in section_defs:
            content = default_content
            # Voeg kennis-chunks toe aan de eerste inhouds-sectie
            if knowledge and knowledge.has_content and not content and not sections:
                content = "\n\n".join(knowledge.chunks)
            sections.append(DocumentSection(heading=heading, content=content, level=1))

        # Bronnen uit kennis-context
        sources: tuple[str, ...] = ()
        if knowledge and knowledge.sources:
            sources = knowledge.sources

        metadata = DocumentMetadata(
            author="devhub",
            category=category.value,
            date=date.today().isoformat(),
            grade="BRONZE",
            sources=sources,
            tags=(category.layer(), request.target_node),
        )

        return DocumentRequest(
            title=request.topic,
            sections=tuple(sections),
            metadata=metadata,
            output_format=request.output_format,
        )

    def _publish_to_storage(
        self,
        doc_result: DocumentResult,
        storage_path: str,
    ) -> tuple[PublishStatus, str]:
        """Publiceer naar storage met checksum-dedup."""
        try:
            # Check duplicate
            if self._check_duplicate(storage_path, doc_result.checksum):
                return PublishStatus.SKIPPED, "Duplicate checksum, skipped"

            # Lees gegenereerd bestand
            content = _read_file_bytes(doc_result.path)

            # Publiceer
            result = self._storage.put(storage_path, content)  # type: ignore[union-attr]
            if result.success:
                logger.info("Published to %s", storage_path)
                return PublishStatus.PUBLISHED, f"Published to {storage_path}"
            else:
                return PublishStatus.FAILED, "Storage put failed"
        except Exception as e:
            logger.warning("Publish failed: %s", e)
            return PublishStatus.FAILED, str(e)

    def _check_duplicate(self, storage_path: str, checksum: str) -> bool:
        """Controleer of een bestand met dezelfde checksum al bestaat."""
        if not checksum:
            return False
        try:
            existing = self._storage.get(storage_path)  # type: ignore[union-attr]
            return existing.content_hash == checksum
        except Exception:
            return False


def _read_file_bytes(path: str) -> bytes:
    """Lees een bestand als bytes."""
    from pathlib import Path

    return Path(path).read_bytes()
