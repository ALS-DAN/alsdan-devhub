"""Tests voor KnowledgeStore — embed → store → retrieve roundtrip."""

from __future__ import annotations

import uuid

from devhub_core.contracts.curator_contracts import KnowledgeArticle, KnowledgeDomain
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


def _create_store() -> KnowledgeStore:
    """Maak een KnowledgeStore met ChromaDB + HashEmbeddingProvider."""
    prefix = f"test_ks_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(zones=[DataZone.OPEN], collection_prefix=prefix)
    embedder = HashEmbeddingProvider(dimension=384)
    return KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)


def _sample_article(
    article_id: str = "ART-001",
    domain: KnowledgeDomain = KnowledgeDomain.AI_ENGINEERING,
    grade: str = "SILVER",
) -> KnowledgeArticle:
    return KnowledgeArticle(
        article_id=article_id,
        title="Test Article",
        content="Dit is een test kennisartikel over AI engineering patronen en best practices.",
        domain=domain,
        grade=grade,
        sources=("https://example.com/source1",),
        verification_pct=60.0,
        date="2026-03-27",
        author="test",
    )


class TestKnowledgeStore:
    def test_store_article(self) -> None:
        store = _create_store()
        article = _sample_article()
        chunk_id = store.store_article(article)
        assert chunk_id == "ART-001"

    def test_store_and_search(self) -> None:
        store = _create_store()
        article = _sample_article()
        store.store_article(article)
        results = store.search("AI engineering patronen")
        assert len(results) >= 1
        assert results[0].article_id == "ART-001"

    def test_search_by_domain(self) -> None:
        store = _create_store()
        store.store_article(_sample_article("ART-AI", KnowledgeDomain.AI_ENGINEERING))
        store.store_article(_sample_article("ART-PY", KnowledgeDomain.PYTHON_ARCHITECTURE))
        results = store.search("test", domain=KnowledgeDomain.AI_ENGINEERING)
        assert all(r.domain == KnowledgeDomain.AI_ENGINEERING for r in results)

    def test_list_by_domain(self) -> None:
        store = _create_store()
        store.store_article(_sample_article("ART-AI", KnowledgeDomain.AI_ENGINEERING))
        store.store_article(_sample_article("ART-PY", KnowledgeDomain.PYTHON_ARCHITECTURE))
        ai_articles = store.list_by_domain(KnowledgeDomain.AI_ENGINEERING)
        assert len(ai_articles) >= 1

    def test_count_by_domain(self) -> None:
        store = _create_store()
        store.store_article(_sample_article("ART-1", KnowledgeDomain.AI_ENGINEERING))
        store.store_article(_sample_article("ART-2", KnowledgeDomain.AI_ENGINEERING))
        store.store_article(_sample_article("ART-3", KnowledgeDomain.PYTHON_ARCHITECTURE))
        counts = store.count_by_domain()
        assert counts[KnowledgeDomain.AI_ENGINEERING] >= 2

    def test_metadata_preservation(self) -> None:
        store = _create_store()
        article = _sample_article()
        store.store_article(article)
        results = store.search("AI engineering")
        assert len(results) >= 1
        retrieved = results[0]
        assert retrieved.grade == "SILVER"
        assert retrieved.domain == KnowledgeDomain.AI_ENGINEERING
        assert retrieved.author == "test"

    def test_store_article_calculates_embedding(self) -> None:
        store = _create_store()
        article = _sample_article()
        assert article.embedding is None  # No embedding provided
        store.store_article(article)
        # Article stored successfully = embedding was calculated

    def test_store_article_with_existing_embedding(self) -> None:
        store = _create_store()
        embedder = HashEmbeddingProvider(dimension=384)
        embedding = embedder.embed_text("pre-computed")
        article = KnowledgeArticle(
            article_id="ART-PRE",
            title="Pre-embedded",
            content="Dit artikel heeft al een embedding.",
            domain=KnowledgeDomain.CLAUDE_SPECIFIC,
            embedding=embedding,
        )
        chunk_id = store.store_article(article)
        assert chunk_id == "ART-PRE"

    def test_get_all_articles(self) -> None:
        store = _create_store()
        store.store_article(_sample_article("ART-A"))
        store.store_article(_sample_article("ART-B"))
        all_articles = store.get_all_articles()
        assert len(all_articles) >= 2

    def test_sources_preserved(self) -> None:
        store = _create_store()
        article = KnowledgeArticle(
            article_id="ART-SRC",
            title="Multi-source",
            content="Artikel met meerdere bronnen voor test.",
            domain=KnowledgeDomain.AI_ENGINEERING,
            sources=("https://source1.com", "https://source2.com"),
            verification_pct=75.0,
            date="2026-03-27",
        )
        store.store_article(article)
        results = store.search("meerdere bronnen")
        assert len(results) >= 1
        assert len(results[0].sources) == 2
