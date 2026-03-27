"""
Analysis Contracts — Communicatie-contracten voor de Analyse Pipeline.

Dataclasses voor de 6-staps analyse-pipeline: van kennisretrieval
tot document-generatie en opslag. Golf 3 van de kennispipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from devhub_core.contracts.research_contracts import ResearchDepth


class AnalysisType(Enum):
    """Type analyse dat de pipeline uitvoert."""

    SOTA = "sota"
    COMPARATIVE = "comparative"
    APPLICATION = "application"
    FREE = "free"


class AnalysisStepStatus(Enum):
    """Status van één pipeline-stap."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class AnalysisRequest:
    """Analyseopdracht voor de AnalysisPipeline.

    Bevat de volledige input voor één analyserun: de onderzoeksvraag,
    het type analyse, de scope en output-configuratie.
    """

    request_id: str
    title: str
    question: str
    analysis_type: AnalysisType
    domains: tuple[str, ...]
    depth: ResearchDepth = ResearchDepth.STANDARD
    skip_research: bool = False
    output_format: str = "markdown"
    output_dir: str = ""
    requesting_agent: str = "analysis-pipeline"
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id is required")
        if not self.title:
            raise ValueError("title is required")
        if not self.question:
            raise ValueError("question is required")
        if not self.domains:
            raise ValueError("domains may not be empty")
        if self.output_format not in ("markdown", "odf"):
            raise ValueError(
                f"output_format must be 'markdown' or 'odf', got '{self.output_format}'"
            )


@dataclass(frozen=True)
class AnalysisStepResult:
    """Resultaat van één stap in de analyse-pipeline."""

    step_name: str
    status: AnalysisStepStatus
    items_processed: int = 0
    message: str = ""
    duration_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not self.step_name:
            raise ValueError("step_name is required")


@dataclass(frozen=True)
class KnowledgeGap:
    """Een gedetecteerde kennisleemte in KWP DEV.

    Gegenereerd door de lacune-detectiestap van de pipeline.
    Kan omgezet worden naar een ResearchRequest voor aanvullend onderzoek.
    """

    gap_id: str
    description: str
    domain: str
    suggested_question: str
    priority: int = 5

    def __post_init__(self) -> None:
        if not self.gap_id:
            raise ValueError("gap_id is required")
        if not self.description:
            raise ValueError("description is required")
        if not (1 <= self.priority <= 10):
            raise ValueError(f"priority must be between 1 and 10, got {self.priority}")


@dataclass(frozen=True)
class AnalysisResult:
    """Volledig resultaat van een analyse-pipeline run.

    Bevat de synthese-tekst, gebruikte kennisartikelen, gedetecteerde
    lacunes, gegenereerd document en opslag-paden.
    """

    request_id: str
    analysis_type: AnalysisType
    title: str
    synthesis: str
    knowledge_articles_used: tuple[str, ...] = field(default_factory=tuple)
    gaps_detected: tuple[KnowledgeGap, ...] = field(default_factory=tuple)
    research_requests_created: tuple[str, ...] = field(default_factory=tuple)
    document_path: str = ""
    storage_paths: tuple[str, ...] = field(default_factory=tuple)
    step_results: tuple[AnalysisStepResult, ...] = field(default_factory=tuple)
    grade: str = "SPECULATIVE"
    completed_at: str = ""
    success: bool = False

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id is required")
        if not self.title:
            raise ValueError("title is required")

    @property
    def document_generated(self) -> bool:
        """True als er een document gegenereerd is."""
        return bool(self.document_path)

    @property
    def stored_remotely(self) -> bool:
        """True als er minstens twee opslag-paden zijn (lokaal + remote)."""
        return len(self.storage_paths) > 1
