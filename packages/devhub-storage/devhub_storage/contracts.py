"""
Storage Contracts — Vendor-free dataclasses voor storage-operaties.

Frozen dataclasses voor immutability, conform NodeInterface-patroon
(devhub_core.contracts.node_interface). Geen externe SDK-types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ItemType(Enum):
    """Type storage-item."""

    FILE = "file"
    DIRECTORY = "directory"


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StorageItem:
    """Eén bestand of directory in een storage-backend."""

    path: str
    name: str
    item_type: ItemType
    size_bytes: int
    modified_at: str  # ISO 8601
    created_at: str | None = None
    content_hash: str | None = None  # SHA-256 hex digest, None voor directories
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path is required")
        if not self.name:
            raise ValueError("name is required")
        if self.size_bytes < 0:
            raise ValueError(f"size_bytes cannot be negative, got {self.size_bytes}")


@dataclass(frozen=True)
class StorageTree:
    """Recursieve boomstructuur van storage-items."""

    item: StorageItem
    children: tuple[StorageTree, ...] = ()

    def __post_init__(self) -> None:
        if self.item.item_type == ItemType.FILE and self.children:
            raise ValueError("FILE items cannot have children")


@dataclass(frozen=True)
class StorageHealth:
    """Gezondheidsstatus van een storage-backend."""

    status: Literal["UP", "DEGRADED", "DOWN"]
    backend: str
    root_path: str
    total_items: int
    total_size_bytes: int
    readable: bool
    writable: bool
    message: str = ""

    def __post_init__(self) -> None:
        if not self.backend:
            raise ValueError("backend is required")
        if self.total_items < 0:
            raise ValueError(f"total_items cannot be negative, got {self.total_items}")
        if self.total_size_bytes < 0:
            raise ValueError(f"total_size_bytes cannot be negative, got {self.total_size_bytes}")


@dataclass(frozen=True)
class WriteResult:
    """Resultaat van een mutatie-operatie."""

    success: bool
    path: str
    operation: Literal["put", "mkdir", "move", "delete"]
    bytes_written: int = 0
    message: str = ""

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path is required")


# ---------------------------------------------------------------------------
# Mixin-gerelateerde dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChangeEvent:
    """Wijzigingsgebeurtenis voor Watchable mixin."""

    path: str
    event_type: Literal["created", "modified", "deleted", "moved"]
    timestamp: str  # ISO 8601
    old_path: str | None = None

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path is required")
        if not self.timestamp:
            raise ValueError("timestamp is required")
        if self.event_type == "moved" and not self.old_path:
            raise ValueError("old_path is required for moved events")


@dataclass(frozen=True)
class DriftItem:
    """Eén afwijking tussen gewenste en actuele staat."""

    path: str
    drift_type: Literal["missing", "extra", "wrong_type", "wrong_content"]
    expected: str = ""
    actual: str = ""

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path is required")


@dataclass(frozen=True)
class DriftReport:
    """Rapport van afwijkingen tussen gewenste en actuele staat."""

    drifts: tuple[DriftItem, ...] = ()
    in_sync: bool = True

    def __post_init__(self) -> None:
        if self.drifts and self.in_sync:
            object.__setattr__(self, "in_sync", False)


@dataclass(frozen=True)
class ReconcileResult:
    """Resultaat van een reconcile-operatie."""

    dry_run: bool
    actions_planned: int
    actions_executed: int
    drifts_resolved: tuple[DriftItem, ...] = ()
    errors: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class StorageError(Exception):
    """Basis-exceptie voor alle storage-operaties."""


class StorageNotFoundError(StorageError):
    """Item niet gevonden op het opgegeven pad."""


class StoragePermissionError(StorageError):
    """Geen toegang voor de gevraagde operatie."""


class StoragePathError(StorageError):
    """Ongeldig of onveilig pad (bijv. path traversal)."""


class StorageAlreadyExistsError(StorageError):
    """Item bestaat al op het doelpad."""
