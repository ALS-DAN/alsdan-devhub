"""KWP DEV integratie-tests — end-to-end bootstrap, search, health, analyse pipeline."""

from __future__ import annotations

import uuid

from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.contracts.curator_contracts import CurationVerdict, KnowledgeDomain
from devhub_core.research.bootstrap import BootstrapPipeline
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_core.research.seed_articles import get_seed_articles
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


def _create_pipeline() -> tuple[BootstrapPipeline, KnowledgeStore]:
    """Maak een geïsoleerde bootstrap pipeline met unieke ChromaDB prefix."""
    prefix = f"test_kwp_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(zones=[DataZone.OPEN], collection_prefix=prefix)
    embedder = HashEmbeddingProvider(dimension=384)
    store = KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)
    curator = KnowledgeCurator()
    pipeline = BootstrapPipeline(curator, store)
    return pipeline, store


class TestKWPBootstrap:
    """Bootstrap pipeline laadt seed articles correct."""

    def test_seed_articles_exist(self) -> None:
        articles = get_seed_articles()
        assert len(articles) >= 8

    def test_bootstrap_approves_all_seeds(self) -> None:
        pipeline, _store = _create_pipeline()
        report = pipeline.run_seed(get_seed_articles())
        assert report.approved == report.total_submitted
        assert report.rejected == 0

    def test_bootstrap_curator_verdicts(self) -> None:
        pipeline, _store = _create_pipeline()
        report = pipeline.run_seed(get_seed_articles())
        for r in report.reports:
            assert r.verdict == CurationVerdict.APPROVED


class TestKWPSearch:
    """Search retourneert relevante resultaten na bootstrap."""

    def test_search_returns_results(self) -> None:
        pipeline, store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        results = store.search("multi-agent architectuur")
        assert len(results) > 0

    def test_search_by_domain(self) -> None:
        pipeline, store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        results = store.search(
            "design patterns",
            domain=KnowledgeDomain.PYTHON_ARCHITECTURE,
        )
        assert len(results) > 0

    def test_search_returns_article_metadata(self) -> None:
        pipeline, store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        results = store.search("Claude Code plugin")
        assert len(results) > 0
        first = results[0]
        assert first.article_id
        assert first.title
        assert first.grade


class TestKWPDomainCoverage:
    """Alle 4 domeinen hebben content na bootstrap."""

    def test_all_domains_populated(self) -> None:
        pipeline, store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        counts = store.count_by_domain()
        for domain in KnowledgeDomain:
            assert counts.get(domain, 0) > 0, f"Domain {domain} is leeg"

    def test_total_article_count(self) -> None:
        pipeline, store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        counts = store.count_by_domain()
        total = sum(counts.values())
        assert total == 8


class TestKWPHealth:
    """Health audit scoort >50 op verse bootstrap."""

    def test_health_score_above_threshold(self) -> None:
        pipeline, _store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        health = pipeline.health_check()
        assert health.overall_score >= 50

    def test_health_no_critical_findings(self) -> None:
        pipeline, _store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        health = pipeline.health_check()
        assert len(health.findings) == 0

    def test_health_freshness_score(self) -> None:
        pipeline, _store = _create_pipeline()
        pipeline.run_seed(get_seed_articles())
        health = pipeline.health_check()
        assert health.freshness_score >= 80
