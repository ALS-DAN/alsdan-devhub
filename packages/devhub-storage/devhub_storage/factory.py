"""
Storage Factory — creëert storage-instanties op basis van backend-type.

Conform VectorStoreFactory patroon: factory + lazy instantiatie.
Extensible voor toekomstige backends (SharePoint).
"""

from __future__ import annotations

from typing import Any

from devhub_storage.interface import StorageInterface


class StorageFactory:
    """Factory voor StorageInterface implementaties.

    Gebruik:
        store = StorageFactory.create("local", root_path="/tmp/data")
        store = StorageFactory.create("google_drive", auth=auth, root_folder_id="xxx")
    """

    _registry: dict[str, str] = {
        "local": "devhub_storage.adapters.local_adapter.LocalAdapter",
        "google_drive": "devhub_storage.adapters.google_drive_adapter.GoogleDriveAdapter",
    }

    @classmethod
    def create(cls, backend: str = "local", **kwargs: Any) -> StorageInterface:
        """Maak een storage-instantie aan.

        Args:
            backend: Backend type ("local", "google_drive").
            **kwargs: Backend-specifieke configuratie.

        Returns:
            StorageInterface implementatie.

        Raises:
            ValueError: Onbekend backend type.
            ImportError: Backend dependency niet geinstalleerd.
        """
        if backend not in cls._registry:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(f"Unknown storage backend '{backend}'. " f"Available: {available}")

        module_path, class_name = cls._registry[backend].rsplit(".", 1)
        import importlib

        module = importlib.import_module(module_path)
        store_class = getattr(module, class_name)
        return store_class(**kwargs)

    @classmethod
    def available_backends(cls) -> list[str]:
        """Lijst beschikbare backend types."""
        return sorted(cls._registry.keys())
