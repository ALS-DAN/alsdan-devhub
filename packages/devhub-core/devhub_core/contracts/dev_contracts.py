"""
Dev Contracts — Interne communicatie-contracten voor het DEV systeem.

Deze dataclasses definiëren de berichten tussen DevOrchestrator, DocsAgent
en QA Agent. Frozen voor immutability (conform BORIS ADR-049 pattern).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class TaskType(Enum):
    """Type dev-taak voor DevOrchestrator routing."""

    DEV = "dev"
    DOCS = "docs"
    QA = "qa"
    ANALYSE = "analyse"


@dataclass(frozen=True)
class DevTaskRequest:
    """Taakopdracht van DevOrchestrator naar een agent of developer."""

    task_id: str
    description: str
    node_id: str  # Welke managed node betreft dit
    scope_files: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    sprint_ref: str | None = None  # e.g. "SPRINT_DEVAGENTS_F0"
    task_type: str = "dev"  # TaskType.value — string voor JSON-serializatie

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.description:
            raise ValueError("description is required")
        if not self.node_id:
            raise ValueError("node_id is required")
        valid_types = {t.value for t in TaskType}
        if self.task_type not in valid_types:
            raise ValueError(f"task_type must be one of {valid_types}, got '{self.task_type}'")


@dataclass(frozen=True)
class DevTaskResult:
    """Resultaat van een uitgevoerde dev-taak."""

    task_id: str
    files_changed: list[str] = field(default_factory=list)
    tests_added: int = 0
    lint_clean: bool = True
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")


@dataclass(frozen=True)
class DocGenRequest:
    """Opdracht van DevOrchestrator aan DocsAgent voor documentatie-generatie."""

    task_id: str
    target_files: list[str]  # Docs die gegenereerd/bijgewerkt moeten worden
    diataxis_category: Literal[
        "tutorial",
        "howto",
        "reference",
        "explanation",
        "pattern",
        "analysis",
        "decision",
        "retrospective",
        "methodology",
        "best_practice",
        "sota_review",
        "playbook",
    ]
    audience: str  # e.g. "medewerker", "ict_data", "kerngroep", "developer"
    source_code_files: list[str] = field(default_factory=list)
    node_id: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.target_files:
            raise ValueError("target_files is required")
        valid_categories = {
            "tutorial",
            "howto",
            "reference",
            "explanation",
            "pattern",
            "analysis",
            "decision",
            "retrospective",
            "methodology",
            "best_practice",
            "sota_review",
            "playbook",
        }
        if self.diataxis_category not in valid_categories:
            raise ValueError(
                f"diataxis_category must be one of {valid_categories}, "
                f"got '{self.diataxis_category}'"
            )


@dataclass(frozen=True)
class QAFinding:
    """Eén bevinding van de QA Agent."""

    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    category: Literal["code", "docs", "sync", "style"]
    description: str
    file: str | None = None
    line: int | None = None

    def __post_init__(self) -> None:
        if not self.description:
            raise ValueError("description is required")


@dataclass(frozen=True)
class QAReport:
    """Rapport van de QA Agent na review van code en/of documentatie."""

    task_id: str
    code_findings: list[QAFinding] = field(default_factory=list)
    doc_findings: list[QAFinding] = field(default_factory=list)
    verdict: Literal["PASS", "NEEDS_WORK", "BLOCK"] = "PASS"

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        # Auto-validate: BLOCK als er CRITICAL findings zijn
        has_critical = any(
            f.severity == "CRITICAL" for f in list(self.code_findings) + list(self.doc_findings)
        )
        if has_critical and self.verdict != "BLOCK":
            object.__setattr__(self, "verdict", "BLOCK")

    @property
    def total_findings(self) -> int:
        return len(self.code_findings) + len(self.doc_findings)

    @property
    def is_clean(self) -> bool:
        return self.verdict == "PASS" and self.total_findings == 0
