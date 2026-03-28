"""
DevOrchestrator — Centrale ontwikkel-orchestrator.

Ontvangt taken, pollt NodeInterface voor context, decomposeert naar
dev + docs + qa subtaken. Enige agent die direct met de developer communiceert.

Design: Single Responsibility — orchestreert, implementeert niet.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from devhub_core.contracts.analysis_contracts import AnalysisRequest, AnalysisType
from devhub_core.contracts.dev_contracts import (
    DevTaskRequest,
    DevTaskResult,
    DocGenRequest,
    TaskType,
)
from devhub_core.contracts.node_interface import NodeReport
from devhub_core.contracts.research_contracts import ResearchDepth
from devhub_core.registry import NodeRegistry

logger = logging.getLogger(__name__)

# Diátaxis categorieën en hun doel
DIATAXIS_CATEGORIES: dict[str, str] = {
    "tutorial": "Leren — stap-voor-stap begeleide les",
    "howto": "Taken uitvoeren — probleemgerichte instructie",
    "reference": "Informatie opzoeken — technische beschrijving",
    "explanation": "Begrijpen — achtergrond en context",
}


class DevOrchestrator:
    """Centrale orchestrator voor development-time taken.

    Workflow:
    1. Ontvang taak van developer
    2. Poll NodeInterface voor huidige staat
    3. Decomposeer taak naar subtaken (dev + docs)
    4. Schrijf subtaken naar scratchpad voor agents
    5. Coördineer QA review na afronding
    """

    def __init__(
        self,
        registry: NodeRegistry,
        scratchpad_path: Path | None = None,
        event_bus: Any | None = None,  # EventBusInterface — optioneel
    ) -> None:
        self._registry = registry
        self._scratchpad = scratchpad_path or Path(".claude/scratchpad/tasks")
        self._scratchpad.mkdir(parents=True, exist_ok=True)
        self._event_bus = event_bus

    def create_task(
        self,
        description: str,
        node_id: str,
        scope_files: list[str] | None = None,
        constraints: list[str] | None = None,
        sprint_ref: str | None = None,
    ) -> DevTaskRequest:
        """Maak een nieuwe dev-taak aan en schrijf naar scratchpad.

        Args:
            description: Wat moet er gedaan worden
            node_id: Welke node betreft dit
            scope_files: Bestanden in scope
            constraints: Beperkingen (bijv. "geen main.py wijzigingen")
            sprint_ref: Sprint referentie

        Returns:
            DevTaskRequest met gegenereerd task_id
        """
        task_id = f"TASK-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"

        task = DevTaskRequest(
            task_id=task_id,
            description=description,
            node_id=node_id,
            scope_files=scope_files or [],
            constraints=constraints or [],
            sprint_ref=sprint_ref,
        )

        self._write_task(task)
        logger.info("DevOrchestrator: taak %s aangemaakt voor node %s", task_id, node_id)
        if self._event_bus is not None:
            from devhub_core.contracts.event_contracts import TaskAssigned

            self._event_bus.publish(
                TaskAssigned(
                    source_agent="orchestrator",
                    task_id=task_id,
                    agent_id="",
                    description=description,
                )
            )
        return task

    def get_node_context(self, node_id: str) -> NodeReport:
        """Haal actuele context op van een managed node.

        Wordt gebruikt vóór taakdecompositie om de huidige staat te begrijpen.
        """
        return self._registry.get_report(node_id)

    def decompose_for_docs(
        self,
        task: DevTaskRequest,
        diataxis_category: Literal["tutorial", "howto", "reference", "explanation"],
        audience: str = "developer",
        target_files: list[str] | None = None,
    ) -> DocGenRequest:
        """Decomposeer een dev-taak naar een docs-opdracht.

        Wordt parallel aan dev-werk uitgevoerd door de DocsAgent.
        """
        doc_request = DocGenRequest(
            task_id=task.task_id,
            target_files=target_files or [f"docs/{task.task_id.lower()}.md"],
            diataxis_category=diataxis_category,
            audience=audience,
            source_code_files=task.scope_files,
            node_id=task.node_id,
        )

        self._write_doc_queue(doc_request)
        logger.info(
            "DevOrchestrator: docs-opdracht voor %s (%s, %s)",
            task.task_id,
            diataxis_category,
            audience,
        )
        if self._event_bus is not None:
            from devhub_core.contracts.event_contracts import DocGenRequested

            self._event_bus.publish(
                DocGenRequested(
                    source_agent="orchestrator",
                    request=doc_request,
                )
            )
        return doc_request

    def record_task_result(
        self,
        task_id: str,
        files_changed: list[str] | None = None,
        tests_added: int = 0,
        lint_clean: bool = True,
        warnings: list[str] | None = None,
    ) -> DevTaskResult:
        """Registreer het resultaat van een afgeronde dev-taak."""
        result = DevTaskResult(
            task_id=task_id,
            files_changed=files_changed or [],
            tests_added=tests_added,
            lint_clean=lint_clean,
            warnings=warnings or [],
        )

        result_path = self._scratchpad / "results" / f"{task_id}.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(asdict(result), indent=2))
        logger.info("DevOrchestrator: resultaat voor %s opgeslagen", task_id)
        if self._event_bus is not None:
            from devhub_core.contracts.event_contracts import TaskCompleted

            self._event_bus.publish(
                TaskCompleted(
                    source_agent="orchestrator",
                    task_id=task_id,
                    agent_id="",
                    result=result,
                )
            )
        return result

    def get_current_task(self) -> DevTaskRequest | None:
        """Lees de huidige actieve taak uit scratchpad."""
        task_file = self._scratchpad / "current_task.json"
        if not task_file.exists():
            return None
        try:
            data = json.loads(task_file.read_text())
            data.setdefault("task_type", "dev")  # backward-compat voor oude JSON zonder task_type
            return DevTaskRequest(**data)
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("DevOrchestrator: current_task.json corrupt")
            return None

    def get_doc_queue(self) -> list[DocGenRequest]:
        """Lees de docs-wachtrij uit scratchpad."""
        queue_file = self._scratchpad / "doc_queue.json"
        if not queue_file.exists():
            return []
        try:
            data = json.loads(queue_file.read_text())
            return [DocGenRequest(**item) for item in data]
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("DevOrchestrator: doc_queue.json corrupt")
            return []

    def clear_task(self) -> None:
        """Verwijder de huidige taak (na succesvolle QA)."""
        task_file = self._scratchpad / "current_task.json"
        if task_file.exists():
            task_file.unlink()

    def clear_doc_queue(self) -> None:
        """Leeg de docs-wachtrij."""
        queue_file = self._scratchpad / "doc_queue.json"
        if queue_file.exists():
            queue_file.unlink()

    def create_analysis_task(
        self,
        question: str,
        title: str,
        analysis_type: str = "free",
        domains: list[str] | None = None,
        depth: str = "standard",
        skip_research: bool = False,
        sprint_ref: str | None = None,
    ) -> DevTaskRequest:
        """Maak een analyse-taak aan en schrijf naar scratchpad.

        Args:
            question: De onderzoeksvraag.
            title: Titel voor het analyse-document.
            analysis_type: Type analyse (sota/comparative/application/free).
            domains: Domeinen om te doorzoeken in KWP DEV.
            depth: Onderzoeksdiepte (quick/standard/deep).
            skip_research: Sla aanvullend onderzoek over.
            sprint_ref: Sprint referentie.

        Returns:
            DevTaskRequest met task_type=ANALYSE.
        """
        task_id = f"ANALYSE-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"

        task = DevTaskRequest(
            task_id=task_id,
            description=question,
            node_id="devhub",
            task_type=TaskType.ANALYSE.value,
            sprint_ref=sprint_ref,
        )

        try:
            analysis_type_enum = AnalysisType(analysis_type)
        except ValueError:
            analysis_type_enum = AnalysisType.FREE

        try:
            depth_enum = ResearchDepth(depth)
        except ValueError:
            depth_enum = ResearchDepth.STANDARD

        analysis_request = AnalysisRequest(
            request_id=task_id,
            title=title,
            question=question,
            analysis_type=analysis_type_enum,
            domains=tuple(domains or ["general"]),
            depth=depth_enum,
            skip_research=skip_research,
            requesting_agent="dev-orchestrator",
            created_at=datetime.now(UTC).isoformat(),
        )

        self._write_analysis_queue(analysis_request)
        self._write_task(task)
        logger.info("DevOrchestrator: analyse-taak %s aangemaakt", task_id)
        return task

    def get_analysis_queue(self) -> list[AnalysisRequest]:
        """Lees de analyse-wachtrij uit scratchpad."""
        queue_file = self._scratchpad / "analysis_queue.json"
        if not queue_file.exists():
            return []
        try:
            data = json.loads(queue_file.read_text())
            result = []
            for item in data:
                item["analysis_type"] = AnalysisType(item["analysis_type"])
                item["depth"] = ResearchDepth(item["depth"])
                item["domains"] = tuple(item["domains"])
                result.append(AnalysisRequest(**item))
            return result
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning("DevOrchestrator: analysis_queue.json corrupt")
            return []

    def clear_analysis_queue(self) -> None:
        """Leeg de analyse-wachtrij."""
        queue_file = self._scratchpad / "analysis_queue.json"
        if queue_file.exists():
            queue_file.unlink()

    # --- Privé helpers ---

    def _write_task(self, task: DevTaskRequest) -> None:
        """Schrijf taak naar scratchpad."""
        task_file = self._scratchpad / "current_task.json"
        task_file.write_text(json.dumps(asdict(task), indent=2))

    def _write_doc_queue(self, doc_request: DocGenRequest) -> None:
        """Voeg docs-opdracht toe aan wachtrij."""
        queue_file = self._scratchpad / "doc_queue.json"
        queue: list[dict] = []
        if queue_file.exists():
            try:
                queue = json.loads(queue_file.read_text())
            except json.JSONDecodeError:
                queue = []
        queue.append(asdict(doc_request))
        queue_file.write_text(json.dumps(queue, indent=2))

    def _write_analysis_queue(self, request: AnalysisRequest) -> None:
        """Voeg een analyse-opdracht toe aan de wachtrij."""
        queue_file = self._scratchpad / "analysis_queue.json"
        queue: list[dict] = []
        if queue_file.exists():
            try:
                queue = json.loads(queue_file.read_text())
            except json.JSONDecodeError:
                queue = []
        # Handmatig serialiseren: enums naar string-values
        item = {
            "request_id": request.request_id,
            "title": request.title,
            "question": request.question,
            "analysis_type": request.analysis_type.value,
            "domains": list(request.domains),
            "depth": request.depth.value,
            "skip_research": request.skip_research,
            "output_format": request.output_format,
            "output_dir": request.output_dir,
            "requesting_agent": request.requesting_agent,
            "created_at": request.created_at,
        }
        queue.append(item)
        queue_file.write_text(json.dumps(queue, indent=2))
