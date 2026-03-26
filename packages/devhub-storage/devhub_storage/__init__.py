"""DevHub Storage — interface and adapters for file storage backends."""

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

__version__ = "0.3.0"

__all__ = [
    # Interface
    "StorageInterface",
    # Factory
    "StorageFactory",
    # Adapters
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
    # Exceptions
    "StorageAlreadyExistsError",
    "StorageError",
    "StorageNotFoundError",
    "StoragePathError",
    "StoragePermissionError",
]
