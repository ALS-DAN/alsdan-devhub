"""
KnowledgeStore — Brug tussen kennisartikelen en de vectorstore.

Slaat KnowledgeArticle op als DocumentChunk in de vectorstore,
met embedding-berekening en metadata-preservatie.
"""

from __future__ import annotations

from devhub_core.contracts.curator_contracts import KnowledgeArticle, KnowledgeDomain
from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    EmbeddingProvider,
    RetrievalRequest,
    VectorStoreInterface,
)


class KnowledgeStore:
    """Slaat kennisartikelen op in de vectorstore met embedding-berekening.

    Args:
        vectorstore: VectorStoreInterface implementatie (ChromaDB of Weaviate).
        embedding_provider: EmbeddingProvider voor embedding-berekening.
    """

    def __init__(
        self,
        vectorstore: VectorStoreInterface,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._store = vectorstore
        self._embedder = embedding_provider

    def store_article(self, article: KnowledgeArticle) -> str:
        """Sla een kennisartikel op in de vectorstore.

        Berekent embedding als die niet aanwezig is, converteert naar
        DocumentChunk en slaat op. Retourneert chunk_id.
        """
        # Calculate embedding if not provided
        embedding = article.embedding
        if embedding is None:
            embedding = self._embedder.embed_text(article.content)

        # Create article with embedding
        article_with_embedding = KnowledgeArticle(
            article_id=article.article_id,
            title=article.title,
            content=article.content,
            domain=article.domain,
            grade=article.grade,
            sources=article.sources,
            verification_pct=article.verification_pct,
            date=article.date,
            author=article.author,
            embedding=embedding,
        )

        # Convert to DocumentChunk and store
        chunk = article_with_embedding.to_document_chunk()
        self._store.add_chunk(chunk)
        return chunk.chunk_id

    def search(
        self,
        query: str,
        domain: KnowledgeDomain | None = None,
        limit: int = 10,
    ) -> list[KnowledgeArticle]:
        """Zoek kennisartikelen op semantische gelijkenis.

        Args:
            query: Zoektekst.
            domain: Optioneel filter op domein.
            limit: Maximum aantal resultaten.
        """
        query_embedding = self._embedder.embed_text(query)

        metadata_filter: tuple[tuple[str, str], ...] = ()
        if domain is not None:
            metadata_filter = (("domain", domain.value),)

        request = RetrievalRequest(
            query_text=query,
            query_embedding=query_embedding,
            zone=DataZone.OPEN,
            limit=limit,
            metadata_filter=metadata_filter,
        )
        response = self._store.query(request)
        return [self._chunk_to_article(r.chunk) for r in response.results]

    def list_by_domain(self, domain: KnowledgeDomain) -> list[KnowledgeArticle]:
        """Lijst alle artikelen in een domein.

        Gebruikt een brede query om alle artikelen op te halen,
        gefilterd op domein metadata.
        """
        request = RetrievalRequest(
            query_text=domain.value,
            zone=DataZone.OPEN,
            limit=1000,
            metadata_filter=(("domain", domain.value),),
        )
        response = self._store.query(request)
        return [self._chunk_to_article(r.chunk) for r in response.results]

    def count_by_domain(self) -> dict[KnowledgeDomain, int]:
        """Tel artikelen per domein."""
        result: dict[KnowledgeDomain, int] = {}
        for domain in KnowledgeDomain:
            articles = self.list_by_domain(domain)
            result[domain] = len(articles)
        return result

    def get_all_articles(self) -> list[KnowledgeArticle]:
        """Haal alle artikelen op uit de store."""
        # Query with a broad search across all articles
        request = RetrievalRequest(
            query_text="knowledge",
            zone=DataZone.OPEN,
            limit=10000,
        )
        response = self._store.query(request)
        return [self._chunk_to_article(r.chunk) for r in response.results]

    @staticmethod
    def _chunk_to_article(chunk: DocumentChunk) -> KnowledgeArticle:
        """Converteer een DocumentChunk terug naar KnowledgeArticle."""
        meta = chunk.metadata_dict

        # Parse domain
        domain_str = meta.get("domain", "ai_engineering")
        try:
            domain = KnowledgeDomain(domain_str)
        except ValueError:
            domain = KnowledgeDomain.AI_ENGINEERING

        # Parse sources
        sources_str = meta.get("sources", "")
        sources = tuple(s for s in sources_str.split("|") if s) if sources_str else ()

        # Parse verification_pct
        try:
            verification_pct = float(meta.get("verification_pct", "0.0"))
        except ValueError:
            verification_pct = 0.0

        return KnowledgeArticle(
            article_id=chunk.chunk_id,
            title=meta.get("title", ""),
            content=chunk.content,
            domain=domain,
            grade=meta.get("grade", "SPECULATIVE"),
            sources=sources,
            verification_pct=verification_pct,
            date=meta.get("date", chunk.created_at),
            author=meta.get("author", ""),
            embedding=chunk.embedding,
        )
