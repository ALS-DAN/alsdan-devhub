"""
Tests voor SentenceTransformerProvider — productie embedding provider.

Wordt overgeslagen als sentence-transformers niet geinstalleerd is.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from devhub_vectorstore.contracts.vectorstore_contracts import EmbeddingProvider


class TestSentenceTransformerProviderImport:
    """Tests die geen sentence-transformers nodig hebben."""

    def test_missing_dependency_raises_import_error(self) -> None:
        with patch.dict("sys.modules", {"sentence_transformers": None}):
            # Force re-import
            import importlib

            import devhub_vectorstore.embeddings.sentence_transformer_provider as mod

            importlib.reload(mod)
            with pytest.raises(ImportError, match="sentence-transformers is required"):
                mod.SentenceTransformerProvider()


class TestSentenceTransformerProviderMocked:
    """Tests met gemockte sentence-transformers (geen model download nodig)."""

    def _create_mocked_provider(self, dimension: int = 384) -> tuple:
        """Maak een provider met gemockt model."""
        import numpy as np

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = dimension
        mock_model.encode.side_effect = lambda x, **kw: (
            np.random.default_rng(42).random(dimension).astype(np.float32)
            if isinstance(x, str)
            else np.random.default_rng(42).random((len(x), dimension)).astype(np.float32)
        )

        mock_st_module = MagicMock()
        mock_st_module.SentenceTransformer.return_value = mock_model

        with patch.dict("sys.modules", {"sentence_transformers": mock_st_module}):
            import importlib

            import devhub_vectorstore.embeddings.sentence_transformer_provider as mod

            importlib.reload(mod)
            provider = mod.SentenceTransformerProvider()

        return provider, mock_model

    def test_implements_interface(self) -> None:
        provider, _ = self._create_mocked_provider()
        assert isinstance(provider, EmbeddingProvider)

    def test_dimension_matches_model(self) -> None:
        provider, _ = self._create_mocked_provider(dimension=384)
        assert provider.dimension == 384

    def test_custom_dimension(self) -> None:
        provider, _ = self._create_mocked_provider(dimension=768)
        assert provider.dimension == 768

    def test_embed_text_returns_tuple(self) -> None:
        provider, _ = self._create_mocked_provider()
        result = provider.embed_text("test tekst")
        assert isinstance(result, tuple)
        assert len(result) == 384
        assert all(isinstance(x, float) for x in result)

    def test_embed_batch_returns_list_of_tuples(self) -> None:
        provider, _ = self._create_mocked_provider()
        results = provider.embed_batch(["een", "twee", "drie"])
        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, tuple) for r in results)
        assert all(len(r) == 384 for r in results)

    def test_embed_batch_empty(self) -> None:
        provider, _ = self._create_mocked_provider()
        results = provider.embed_batch([])
        assert results == []

    def test_model_name_default(self) -> None:
        provider, _ = self._create_mocked_provider()
        assert provider._model_name == "paraphrase-multilingual-MiniLM-L12-v2"
