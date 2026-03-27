"""
SentenceTransformerProvider — productie embedding provider via sentence-transformers.

Gebruikt het paraphrase-multilingual-MiniLM-L12-v2 model (384-dim, multilingual).
Geschikt voor Nederlandse en Engelse tekst.
"""

from __future__ import annotations

from devhub_vectorstore.contracts.vectorstore_contracts import EmbeddingProvider


class SentenceTransformerProvider(EmbeddingProvider):
    """Embedding provider via sentence-transformers library.

    Args:
        model_name: HuggingFace model naam (default: multilingual MiniLM).
        device: Compute device ("cpu", "cuda", None voor auto-detect).
    """

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str | None = None,
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is required for SentenceTransformerProvider. "
                "Install with: uv pip install 'devhub-vectorstore[embeddings]'"
            ) from e

        self._model_name = model_name
        kwargs: dict = {}
        if device is not None:
            kwargs["device"] = device
        self._model = SentenceTransformer(model_name, **kwargs)
        self._dim: int = self._model.get_sentence_embedding_dimension()  # type: ignore[assignment]

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> tuple[float, ...]:
        """Bereken embedding voor één tekst."""
        embedding = self._model.encode(text, convert_to_numpy=True)
        return tuple(float(x) for x in embedding)

    def embed_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        """Bereken embeddings voor meerdere teksten (gebatcht voor performance)."""
        if not texts:
            return []
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return [tuple(float(x) for x in emb) for emb in embeddings]
