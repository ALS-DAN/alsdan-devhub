"""
Storage Mixins — Optionele uitbreidingen voor storage-backends.

Adapters implementeren alleen de mixins die hun backend ondersteunt.
Compositie via multiple inheritance:

    class GoogleDriveAdapter(StorageInterface, Organizable, Watchable): ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from devhub_storage.contracts import (
    ChangeEvent,
    DriftReport,
    ReconcileResult,
    StorageItem,
    WriteResult,
)


class Organizable(ABC):
    """Mixin voor tagging, relaties en versioning."""

    @abstractmethod
    def tag(self, path: str, tags: list[str]) -> WriteResult:
        """Voeg tags toe aan een item."""
        ...

    @abstractmethod
    def get_tags(self, path: str) -> list[str]:
        """Haal tags op voor een item."""
        ...

    @abstractmethod
    def relate(self, source: str, target: str, relation: str) -> WriteResult:
        """Leg een relatie tussen twee items."""
        ...

    @abstractmethod
    def get_relations(self, path: str) -> list[tuple[str, str]]:
        """Haal relaties op: lijst van (target_path, relation_type)."""
        ...

    @abstractmethod
    def version(self, path: str) -> list[StorageItem]:
        """Haal versiegeschiedenis op voor een item."""
        ...


class Watchable(ABC):
    """Mixin voor change event monitoring."""

    @abstractmethod
    def watch(self, path: str = "", *, since: str | None = None) -> list[ChangeEvent]:
        """Haal wijzigingsgebeurtenissen op sinds een tijdstip."""
        ...


class Reconcilable(ABC):
    """Mixin voor declaratief state management."""

    @abstractmethod
    def drift_report(self, desired_spec: dict) -> DriftReport:
        """Vergelijk gewenste staat met actuele staat (read-only)."""
        ...

    @abstractmethod
    def reconcile(self, desired_spec: dict, *, dry_run: bool = True) -> ReconcileResult:
        """Breng actuele staat in lijn met gewenste staat."""
        ...
