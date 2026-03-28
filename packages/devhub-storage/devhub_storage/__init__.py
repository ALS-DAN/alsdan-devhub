"""DevHub Storage — interface and adapters for file storage backends."""

from devhub_storage.adapters.drive_sync_adapter import DriveSyncAdapter
from devhub_storage.adapters.local_adapter import LocalAdapter
from devhub_storage.auth import (
    OAuth2Auth,
    ServiceAccountAuth,
    StorageAuth,
    StorageAuthError,
)
from devhub_storage.contracts import (
    ChangeEvent,
    DriftItem,
    DriftReport,
    ItemType,
    ReconcileResult,
    StorageAlreadyExistsError,
    StorageError,
    StorageHealth,
    StorageItem,
    StorageNotFoundError,
    StoragePathError,
    StoragePermissionError,
    StorageTree,
    WriteResult,
)
from devhub_storage.factory import StorageFactory
from devhub_storage.interface import StorageInterface
from devhub_storage.mixins import Organizable, Reconcilable, Watchable
from devhub_storage.reconciliation import (
    ReconciliationEngine,
    ReconciliationSpec,
    SpecItem,
    parse_spec,
)

__version__ = "0.3.0"

__all__ = [
    # Interface
    "StorageInterface",
    # Factory
    "StorageFactory",
    # Adapters
    "DriveSyncAdapter",
    "LocalAdapter",
    # Auth
    "OAuth2Auth",
    "ServiceAccountAuth",
    "StorageAuth",
    "StorageAuthError",
    # Contracts
    "ChangeEvent",
    "DriftItem",
    "DriftReport",
    "ItemType",
    "ReconcileResult",
    "StorageHealth",
    "StorageItem",
    "StorageTree",
    "WriteResult",
    # Mixins
    "Organizable",
    "Reconcilable",
    "Watchable",
    # Reconciliation
    "ReconciliationEngine",
    "ReconciliationSpec",
    "SpecItem",
    "parse_spec",
    # Exceptions
    "StorageAlreadyExistsError",
    "StorageError",
    "StorageNotFoundError",
    "StoragePathError",
    "StoragePermissionError",
]
