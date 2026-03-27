"""
AnalysisPipeline — Syntheselaag van de kennispipeline.

Verbindt alle bouwblokken van Golf 1 en 2 tot één bruikbare pipeline:
kennisretrieval → lacune-detectie → onderzoek → synthese → document → opslag.

Design: Dumb orchestrator — kent de 6 stappen en volgorde, delegeert alles.
Best-effort: stap-fouten worden gelogd, pipeline gaat door.
"""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from devhub_core.contracts.curator_contracts import KnowledgeArticle

from devhub_core.analysis.template_loader import TemplateLoader
from devhub_core.contracts.analysis_contracts import (
    AnalysisRequest,
    AnalysisResult,
    AnalysisStepResult,
    AnalysisStepStatus,
    AnalysisType,
    KnowledgeGap,
)
from devhub_core.contracts.curator_contracts import ObservationType
from devhub_core.contracts.research_contracts import (
    ResearchQueue,
    ResearchRequest,
)
from devhub_core.research.knowledge_store import KnowledgeStore


logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Synchrone 6-staps analyse-pipeline.

    Orchestreert de volledige keten van kennisretrieval naar opgeslagen document.
    Externe afhankelijkheden worden geïnjecteerd voor testbaarheid.
    """

    def __init__(
        self,
        knowledge_store: KnowledgeStore,
        research_queue: ResearchQueue,
        document_interface: Any,  # DocumentInterface — duck typing voor workspace-onafhankelijkheid
        local_storage: Any,  # StorageInterface — duck typing
        remote_storage: Any | None = None,
        curator: Any | None = None,  # KnowledgeCurator — voor toekomstige observatie-integratie
        template_dir: Path | None = None,
    ) -> None:
        self._knowledge_store = knowledge_store
        self._research_queue = research_queue
        self._document_interface = document_interface
        self._local_storage = local_storage
        self._remote_storage = remote_storage
        self._curator = curator
        self._template_loader = TemplateLoader(template_dir)

    def run(self, request: AnalysisRequest) -> AnalysisResult:
        """Voer de volledige analyse-pipeline synchroon uit.

        Elke stap genereert een AnalysisStepResult. Bij een fout in een stap
        wordt die stap als FAILED gemarkeerd maar gaat de pipeline door.

        Returns:
            AnalysisResult met alle stap-resultaten, synthese en document-paden.
        """
        logger.info(
            "AnalysisPipeline: start analyse '%s' (type=%s)",
            request.title,
            request.analysis_type.value,
        )
        context: dict[str, Any] = {}
        step_results: list[AnalysisStepResult] = []

        # Stap 1: Kennisretrieval
        articles, step1 = self._step_retrieve_knowledge(request, context)
        step_results.append(step1)

        # Stap 2: Lacune-detectie
        gaps, step2 = self._step_detect_gaps(request, articles, context)
        step_results.append(step2)

        # Stap 3: Aanvullend onderzoek (optioneel)
        request_ids, step3 = self._step_research(request, gaps, context)
        step_results.append(step3)

        # Stap 4: Synthese
        template = self._load_template_safe(request.analysis_type)
        synthesis, step4 = self._step_synthesise(request, articles, template, context)
        step_results.append(step4)

        # Stap 5: Document-generatie
        doc_path, step5 = self._step_generate_document(
            request, synthesis, articles, template, context
        )
        step_results.append(step5)

        # Stap 6: Opslag
        storage_paths, step6 = self._step_store(request, doc_path, context)
        step_results.append(step6)

        # Bepaal overall success: synthese en lokale opslag moeten geslaagd zijn
        success = (
            step4.status == AnalysisStepStatus.COMPLETED
            and step6.status in (AnalysisStepStatus.COMPLETED, AnalysisStepStatus.FAILED)
            and bool(doc_path)
        )

        result = AnalysisResult(
            request_id=request.request_id,
            analysis_type=request.analysis_type,
            title=request.title,
            synthesis=synthesis,
            knowledge_articles_used=tuple(a.article_id for a in articles),
            gaps_detected=tuple(gaps),
            research_requests_created=tuple(request_ids),
            document_path=doc_path,
            storage_paths=tuple(storage_paths),
            step_results=tuple(step_results),
            grade=self._determine_grade(articles),
            completed_at=datetime.now(UTC).isoformat(),
            success=success,
        )

        # Observatie emitteren
        obs_type = (
            ObservationType.ANALYSIS_COMPLETED if success else ObservationType.ANALYSIS_FAILED
        )
        self._emit_observation(
            obs_type,
            f"analyse='{request.title}' success={success}",
            "INFO" if success else "WARNING",
        )

        logger.info("AnalysisPipeline: klaar '%s' success=%s", request.title, success)
        return result

    # -------------------------------------------------------------------------
    # Stap 1: Kennisretrieval
    # -------------------------------------------------------------------------

    def _step_retrieve_knowledge(
        self,
        request: AnalysisRequest,
        context: dict[str, Any],
    ) -> tuple[list[KnowledgeArticle], AnalysisStepResult]:
        start = time.monotonic()
        try:
            articles = self._knowledge_store.search(
                query=request.question,
                limit=20,
            )
            context["articles"] = articles
            duration = time.monotonic() - start
            return articles, AnalysisStepResult(
                step_name="knowledge_retrieval",
                status=AnalysisStepStatus.COMPLETED,
                items_processed=len(articles),
                message=f"{len(articles)} artikelen gevonden",
                duration_seconds=round(duration, 3),
            )
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 1 mislukt: %s", exc)
            context["articles"] = []
            return [], AnalysisStepResult(
                step_name="knowledge_retrieval",
                status=AnalysisStepStatus.FAILED,
                message=str(exc),
                duration_seconds=round(time.monotonic() - start, 3),
            )

    # -------------------------------------------------------------------------
    # Stap 2: Lacune-detectie
    # -------------------------------------------------------------------------

    def _step_detect_gaps(
        self,
        request: AnalysisRequest,
        articles: list[KnowledgeArticle],
        context: dict[str, Any],
    ) -> tuple[list[KnowledgeGap], AnalysisStepResult]:
        start = time.monotonic()
        gaps: list[KnowledgeGap] = []

        try:
            # Eenvoudige heuristiek: als minder dan 3 artikelen gevonden → lacune
            if len(articles) < 3:
                gap = KnowledgeGap(
                    gap_id=f"GAP-{request.request_id}-001",
                    description=f"Onvoldoende kennisartikelen voor '{request.question}'",
                    domain=request.domains[0] if request.domains else "general",
                    suggested_question=request.question,
                    priority=7,
                )
                gaps.append(gap)
                self._emit_observation(
                    ObservationType.KNOWLEDGE_GAP_DETECTED,
                    f"gap voor vraag='{request.question}' (slechts {len(articles)} artikelen)",
                    "INFO",
                )

            context["gaps"] = gaps
            duration = time.monotonic() - start
            return gaps, AnalysisStepResult(
                step_name="gap_detection",
                status=AnalysisStepStatus.COMPLETED,
                items_processed=len(gaps),
                message=f"{len(gaps)} lacunes gedetecteerd",
                duration_seconds=round(duration, 3),
            )
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 2 mislukt: %s", exc)
            context["gaps"] = []
            return [], AnalysisStepResult(
                step_name="gap_detection",
                status=AnalysisStepStatus.FAILED,
                message=str(exc),
                duration_seconds=round(time.monotonic() - start, 3),
            )

    # -------------------------------------------------------------------------
    # Stap 3: Aanvullend onderzoek
    # -------------------------------------------------------------------------

    def _step_research(
        self,
        request: AnalysisRequest,
        gaps: list[KnowledgeGap],
        context: dict[str, Any],
    ) -> tuple[list[str], AnalysisStepResult]:
        if request.skip_research:
            return [], AnalysisStepResult(
                step_name="research",
                status=AnalysisStepStatus.SKIPPED,
                message="skip_research=True",
            )

        start = time.monotonic()
        submitted_ids: list[str] = []

        try:
            for gap in gaps:
                research_req = ResearchRequest(
                    request_id=f"RR-{gap.gap_id}",
                    requesting_agent="analysis-pipeline",
                    question=gap.suggested_question,
                    domain=gap.domain,
                    depth=request.depth,
                    priority=gap.priority,
                )
                self._research_queue.submit(research_req)
                submitted_ids.append(research_req.request_id)

            duration = time.monotonic() - start
            return submitted_ids, AnalysisStepResult(
                step_name="research",
                status=AnalysisStepStatus.COMPLETED,
                items_processed=len(submitted_ids),
                message=f"{len(submitted_ids)} research-requests ingediend",
                duration_seconds=round(duration, 3),
            )
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 3 mislukt: %s", exc)
            return submitted_ids, AnalysisStepResult(
                step_name="research",
                status=AnalysisStepStatus.FAILED,
                message=str(exc),
                duration_seconds=round(time.monotonic() - start, 3),
            )

    # -------------------------------------------------------------------------
    # Stap 4: Synthese
    # -------------------------------------------------------------------------

    def _step_synthesise(
        self,
        request: AnalysisRequest,
        articles: list[KnowledgeArticle],
        template: dict,
        context: dict[str, Any],
    ) -> tuple[str, AnalysisStepResult]:
        start = time.monotonic()
        try:
            sections = template.get("sections", [])
            parts: list[str] = [f"# {request.title}", ""]

            for section in sections:
                heading = section.get("heading", "")
                if heading:
                    parts.append(f"## {heading}")
                    parts.append("")

            # Artikelen samenvatting toevoegen als er bevindingen zijn
            if articles:
                parts.append("## Kennisbasis")
                parts.append("")
                for article in articles[:10]:  # max 10
                    grade_label = article.grade if hasattr(article, "grade") else "?"
                    parts.append(f"- **{article.title}** [{grade_label}]")
                parts.append("")

            synthesis = "\n".join(parts)
            context["synthesis"] = synthesis

            duration = time.monotonic() - start
            return synthesis, AnalysisStepResult(
                step_name="synthesis",
                status=AnalysisStepStatus.COMPLETED,
                items_processed=len(articles),
                message=f"synthese gegenereerd ({len(synthesis)} tekens)",
                duration_seconds=round(duration, 3),
            )
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 4 mislukt: %s", exc)
            context["synthesis"] = ""
            return "", AnalysisStepResult(
                step_name="synthesis",
                status=AnalysisStepStatus.FAILED,
                message=str(exc),
                duration_seconds=round(time.monotonic() - start, 3),
            )

    # -------------------------------------------------------------------------
    # Stap 5: Document-generatie
    # -------------------------------------------------------------------------

    def _step_generate_document(
        self,
        request: AnalysisRequest,
        synthesis: str,
        articles: list[KnowledgeArticle],
        template: dict,
        context: dict[str, Any],
    ) -> tuple[str, AnalysisStepResult]:
        start = time.monotonic()
        try:
            from devhub_documents.contracts import (  # type: ignore[import]
                DocumentFormat,
                DocumentMetadata,
                DocumentRequest,
                DocumentSection,
            )

            sections_config = template.get("sections", [])
            doc_sections = []
            for sec in sections_config:
                heading = sec.get("heading", "Sectie")
                doc_sections.append(DocumentSection(heading=heading, content=""))

            if not doc_sections:
                doc_sections = [DocumentSection(heading="Inhoud", content=synthesis)]

            output_format = (
                DocumentFormat.ODF if request.output_format == "odf" else DocumentFormat.MARKDOWN
            )
            sources = tuple(
                src for a in articles for src in (a.sources if hasattr(a, "sources") else ())
            )

            doc_request = DocumentRequest(
                title=request.title,
                sections=tuple(doc_sections),
                metadata=DocumentMetadata(
                    author=request.requesting_agent,
                    grade=self._determine_grade(articles),  # type: ignore[arg-type]
                    sources=sources[:10],  # max 10 bronnen
                ),
                output_format=output_format,
                output_dir=request.output_dir or "docs/analyses",
            )

            doc_result = self._document_interface.create(doc_request)
            doc_path = doc_result.path
            context["doc_path"] = doc_path

            duration = time.monotonic() - start
            return doc_path, AnalysisStepResult(
                step_name="document_generation",
                status=AnalysisStepStatus.COMPLETED,
                items_processed=1,
                message=f"document gegenereerd: {doc_path}",
                duration_seconds=round(duration, 3),
            )
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 5 mislukt: %s", exc)
            context["doc_path"] = ""
            return "", AnalysisStepResult(
                step_name="document_generation",
                status=AnalysisStepStatus.FAILED,
                message=str(exc),
                duration_seconds=round(time.monotonic() - start, 3),
            )

    # -------------------------------------------------------------------------
    # Stap 6: Opslag
    # -------------------------------------------------------------------------

    def _step_store(
        self,
        request: AnalysisRequest,
        doc_path: str,
        context: dict[str, Any],
    ) -> tuple[tuple[str, ...], AnalysisStepResult]:
        if not doc_path:
            return (), AnalysisStepResult(
                step_name="storage",
                status=AnalysisStepStatus.SKIPPED,
                message="geen document om op te slaan",
            )

        start = time.monotonic()
        stored_paths: list[str] = []

        # Lees document content
        try:
            doc_bytes = Path(doc_path).read_bytes()
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 6: kan document niet lezen: %s", exc)
            return (), AnalysisStepResult(
                step_name="storage",
                status=AnalysisStepStatus.FAILED,
                message=f"document lezen mislukt: {exc}",
                duration_seconds=round(time.monotonic() - start, 3),
            )

        # Lokale opslag (altijd)
        storage_path = f"docs/analyses/{Path(doc_path).name}"
        try:
            self._local_storage.put(storage_path, doc_bytes)
            stored_paths.append(storage_path)
        except Exception as exc:
            logger.warning("AnalysisPipeline stap 6: lokale opslag mislukt: %s", exc)
            return (), AnalysisStepResult(
                step_name="storage",
                status=AnalysisStepStatus.FAILED,
                message=f"lokale opslag mislukt: {exc}",
                duration_seconds=round(time.monotonic() - start, 3),
            )

        # Remote opslag (graceful degradation)
        remote_warning = ""
        if self._remote_storage is not None:
            try:
                self._remote_storage.put(storage_path, doc_bytes)
                stored_paths.append(f"remote:{storage_path}")
            except Exception as exc:
                remote_warning = f" (remote opslag overgeslagen: {exc})"
                logger.warning("AnalysisPipeline stap 6: remote opslag mislukt (graceful): %s", exc)

        duration = time.monotonic() - start
        return tuple(stored_paths), AnalysisStepResult(
            step_name="storage",
            status=AnalysisStepStatus.COMPLETED,
            items_processed=len(stored_paths),
            message=f"opgeslagen op {len(stored_paths)} locatie(s){remote_warning}",
            duration_seconds=round(duration, 3),
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _load_template_safe(self, analysis_type: AnalysisType) -> dict:
        """Laad template, val terug op lege structuur bij fout."""
        try:
            return self._template_loader.load(analysis_type)
        except Exception as exc:
            logger.warning("AnalysisPipeline: template laden mislukt (%s), gebruik fallback", exc)
            return {
                "analysis_type": analysis_type.value,
                "title_prefix": "Analyse:",
                "sections": [
                    {"id": "findings", "heading": "Bevindingen", "required": True},
                    {"id": "conclusion", "heading": "Conclusie", "required": True},
                ],
            }

    def _determine_grade(self, articles: list[KnowledgeArticle]) -> str:
        """Bepaal kennisgradering op basis van gebruikte artikelen."""
        if not articles:
            return "SPECULATIVE"

        grade_order = {"GOLD": 4, "SILVER": 3, "BRONZE": 2, "SPECULATIVE": 1}
        grades = [getattr(a, "grade", "SPECULATIVE") for a in articles]
        min_grade = min(grades, key=lambda g: grade_order.get(g, 1))
        return min_grade

    def _emit_observation(self, obs_type: ObservationType, payload: str, severity: str) -> None:
        """Log een observatie.

        Observaties worden momenteel via het Python logging-systeem bijgehouden.
        De ObservationType waarden in curator_contracts.py (AP-05) zijn het contract
        voor toekomstige Weaviate-opslag.
        """
        logger.info(
            "OBSERVATION type=%s severity=%s payload=%s",
            obs_type.value,
            severity,
            payload,
        )
