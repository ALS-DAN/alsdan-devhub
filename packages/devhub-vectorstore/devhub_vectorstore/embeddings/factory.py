"""
EmbeddingFactory — creëert EmbeddingProvider instanties op basis van provider-type.

Conform VectorStoreFactory patroon: registry + lazy instantiatie.
"""

from __future__ import annotations

import importlib
from typing import Any

from devhub_vectorstore.contracts.vectorstore_contracts import EmbeddingProvider


class EmbeddingFactory:
    """Factory voor EmbeddingProvider implementaties.

    Gebruik:
        provider = EmbeddingFactory.create("hash", dimension=384)
        provider = EmbeddingFactory.create("sentence-transformer")
    """

    _registry: dict[str, str] = {
        "hash": "devhub_vectorstore.embeddings.hash_provider.HashEmbeddingProvider",
        "sentence-transformer": (
            "devhub_vectorstore.embeddings.sentence_transformer_provider"
            ".SentenceTransformerProvider"
        ),
    }

    @classmethod
    def create(cls, provider: str = "hash", **kwargs: Any) -> EmbeddingProvider:
        """Maak een EmbeddingProvider instantie aan.

        Args:
            provider: Provider type ("hash", "sentence-transformer").
            **kwargs: Provider-specifieke configuratie.

        Returns:
            EmbeddingProvider implementatie.

        Raises:
            ValueError: Onbekend provider type.
            ImportError: Provider dependency niet geïnstalleerd.
        """
        if provider not in cls._registry:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(f"Unknown embedding provider '{provider}'. Available: {available}")

        module_path, class_name = cls._registry[provider].rsplit(".", 1)
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)

        return provider_class(**kwargs)

    @classmethod
    def available_providers(cls) -> list[str]:
        """Lijst beschikbare provider types."""
        return sorted(cls._registry.keys())
