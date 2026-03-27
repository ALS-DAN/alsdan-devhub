"""Tests voor HashEmbeddingProvider — deterministische test-embedding provider."""

from __future__ import annotations

import pytest

from devhub_vectorstore.contracts.vectorstore_contracts import EmbeddingProvider
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


class TestHashEmbeddingProvider:
    """Tests voor HashEmbeddingProvider."""

    def test_implements_interface(self) -> None:
        provider = HashEmbeddingProvider()
        assert isinstance(provider, EmbeddingProvider)

    def test_dimension_default(self) -> None:
        provider = HashEmbeddingProvider()
        assert provider.dimension == 384

    def test_dimension_custom(self) -> None:
        provider = HashEmbeddingProvider(dimension=128)
        assert provider.dimension == 128

    def test_dimension_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="dimension must be >= 1"):
            HashEmbeddingProvider(dimension=0)

    def test_embed_text_returns_correct_dimension(self) -> None:
        provider = HashEmbeddingProvider(dimension=384)
        result = provider.embed_text("hello world")
        assert len(result) == 384
        assert isinstance(result, tuple)
        assert all(isinstance(x, float) for x in result)

    def test_embed_text_custom_dimension(self) -> None:
        provider = HashEmbeddingProvider(dimension=64)
        result = provider.embed_text("test")
        assert len(result) == 64

    def test_embed_text_deterministic(self) -> None:
        provider = HashEmbeddingProvider()
        result1 = provider.embed_text("same input")
        result2 = provider.embed_text("same input")
        assert result1 == result2

    def test_embed_text_different_inputs_differ(self) -> None:
        provider = HashEmbeddingProvider()
        result1 = provider.embed_text("input A")
        result2 = provider.embed_text("input B")
        assert result1 != result2

    def test_embed_text_values_in_range(self) -> None:
        provider = HashEmbeddingProvider()
        result = provider.embed_text("normalize check")
        assert all(-1.0 <= x <= 1.0 for x in result)

    def test_embed_batch_returns_list(self) -> None:
        provider = HashEmbeddingProvider()
        results = provider.embed_batch(["text A", "text B", "text C"])
        assert len(results) == 3
        assert all(len(r) == 384 for r in results)

    def test_embed_batch_consistency_with_single(self) -> None:
        provider = HashEmbeddingProvider()
        texts = ["alpha", "beta", "gamma"]
        batch_results = provider.embed_batch(texts)
        single_results = [provider.embed_text(t) for t in texts]
        assert batch_results == single_results

    def test_embed_batch_empty(self) -> None:
        provider = HashEmbeddingProvider()
        results = provider.embed_batch([])
        assert results == []

    def test_embed_text_empty_string(self) -> None:
        provider = HashEmbeddingProvider()
        result = provider.embed_text("")
        assert len(result) == 384
        assert isinstance(result, tuple)
