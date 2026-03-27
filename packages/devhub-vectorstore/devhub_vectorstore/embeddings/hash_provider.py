"""
HashEmbeddingProvider — deterministische embedding provider voor tests.

Genereert reproduceerbare vectoren via hashing, zonder ML-dependencies.
Geschikt voor unit tests en CI waar echte embeddings niet nodig zijn.
"""

from __future__ import annotations

import hashlib
import struct

from devhub_vectorstore.contracts.vectorstore_contracts import EmbeddingProvider


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministische embedding provider op basis van hashing.

    Zelfde input geeft altijd dezelfde output. Geen externe dependencies.

    Args:
        dimension: Dimensie van de output-vector (default 384).
    """

    def __init__(self, dimension: int = 384) -> None:
        if dimension < 1:
            raise ValueError(f"dimension must be >= 1, got {dimension}")
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> tuple[float, ...]:
        """Genereer een deterministische embedding via SHA-256 hashing."""
        result: list[float] = []
        i = 0
        while len(result) < self._dimension:
            h = hashlib.sha256(f"{text}:{i}".encode()).digest()
            # Pak 4 bytes per float, 8 floats per hash
            for offset in range(0, 32, 4):
                if len(result) >= self._dimension:
                    break
                # Unpack als unsigned int, normaliseer naar [-1, 1]
                val = struct.unpack("I", h[offset : offset + 4])[0]
                normalized = (val / (2**32 - 1)) * 2 - 1
                result.append(normalized)
            i += 1
        return tuple(result)

    def embed_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        """Genereer embeddings voor meerdere teksten."""
        return [self.embed_text(text) for text in texts]
