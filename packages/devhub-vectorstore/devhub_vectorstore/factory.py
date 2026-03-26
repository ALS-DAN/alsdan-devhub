"""
VectorStore Factory — creëert vectorstore-instanties op basis van backend-type.

Conform NodeRegistry patroon: factory + lazy instantiatie.
Extensible voor toekomstige backends (Weaviate).
"""

from __future__ import annotations

from typing import Any

from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    VectorStoreInterface,
)


class VectorStoreFactory:
    """Factory voor VectorStoreInterface implementaties.

    Gebruik:
        store = VectorStoreFactory.create("chromadb", zones=[DataZone.OPEN])
    """

    _registry: dict[str, str] = {
        "chromadb": "devhub_vectorstore.adapters.chromadb_adapter.ChromaDBZonedStore",
        "weaviate": "devhub_vectorstore.adapters.weaviate_adapter.WeaviateZonedStore",
    }

    @classmethod
    def create(cls, backend: str = "chromadb", **kwargs: Any) -> VectorStoreInterface:
        """Maak een vectorstore-instantie aan.

        Args:
            backend: Backend type ("chromadb", later "weaviate").
            **kwargs: Backend-specifieke configuratie.

        Returns:
            VectorStoreInterface implementatie.

        Raises:
            ValueError: Onbekend backend type.
            ImportError: Backend dependency niet geïnstalleerd.
        """
        if backend not in cls._registry:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(f"Unknown vectorstore backend '{backend}'. " f"Available: {available}")

        module_path, class_name = cls._registry[backend].rsplit(".", 1)
        import importlib

        module = importlib.import_module(module_path)
        store_class = getattr(module, class_name)

        # Convert string zone names to DataZone enums if provided
        if "zones" in kwargs and kwargs["zones"]:
            zones = kwargs["zones"]
            if zones and isinstance(zones[0], str):
                kwargs["zones"] = [DataZone(z.lower()) for z in zones]

        return store_class(**kwargs)

    @classmethod
    def available_backends(cls) -> list[str]:
        """Lijst beschikbare backend types."""
        return sorted(cls._registry.keys())
