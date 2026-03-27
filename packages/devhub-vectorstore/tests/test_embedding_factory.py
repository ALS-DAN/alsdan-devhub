"""Tests voor EmbeddingFactory."""

from __future__ import annotations

import pytest

from devhub_vectorstore.contracts.vectorstore_contracts import EmbeddingProvider
from devhub_vectorstore.embeddings.factory import EmbeddingFactory
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


class TestEmbeddingFactory:
    """Tests voor EmbeddingFactory."""

    def test_create_hash_provider(self) -> None:
        provider = EmbeddingFactory.create("hash")
        assert isinstance(provider, HashEmbeddingProvider)
        assert isinstance(provider, EmbeddingProvider)

    def test_create_hash_provider_with_kwargs(self) -> None:
        provider = EmbeddingFactory.create("hash", dimension=128)
        assert provider.dimension == 128

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            EmbeddingFactory.create("nonexistent")

    def test_available_providers(self) -> None:
        providers = EmbeddingFactory.available_providers()
        assert "hash" in providers
        assert "sentence-transformer" in providers
        assert providers == sorted(providers)

    def test_hash_provider_default_dimension(self) -> None:
        provider = EmbeddingFactory.create("hash")
        assert provider.dimension == 384
