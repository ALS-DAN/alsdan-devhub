"""Tests voor KnowledgeHealthChecker — Knowledge Health dimensie."""

from __future__ import annotations

import uuid

import pytest

from devhub_core.contracts.curator_contracts import KnowledgeArticle, KnowledgeDomain
from devhub_core.research.knowledge_config import (
    DomainConfig,
    KnowledgeConfig,
    RingConfig,
)
from devhub_core.research.knowledge_health import (
    KnowledgeHealthChecker,
    KnowledgeHealthDimension,
)
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


def _create_store() -> KnowledgeStore:
    prefix = f"test_health_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(zones=[DataZone.OPEN], collection_prefix=prefix)
    embedder = HashEmbeddingProvider(dimension=384)
    return KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)


def _make_config() -> KnowledgeConfig:
    return KnowledgeConfig(
        rings=(RingConfig(name="core", auto_bootstrap=True),),
        domains=(
            DomainConfig(
                name="ai_engineering",
                ring="core",
                rq_focus=("RQ1", "RQ4"),
                freshness_months=3,
                bootstrap_priority=1,
            ),
            DomainConfig(
                name="python_architecture",
                ring="core",
                rq_focus=("RQ2",),
                freshness_months=12,
                bootstrap_priority=2,
            ),
        ),
    )


def _make_article(
    domain: KnowledgeDomain,
    grade: str = "SILVER",
    rq_tags: tuple[str, ...] = (),
    date: str = "2026-03-28",
) -> KnowledgeArticle:
    uid = uuid.uuid4().hex[:6]
    return KnowledgeArticle(
        article_id=f"HEALTH-{uid}",
        title=f"Test {domain.value}",
        content=f"Content {domain.value}",
        domain=domain,
        grade=grade,
        sources=("test",),
        rq_tags=rq_tags,
        date=date,
        domain_ring=domain.ring,
    )


class TestKnowledgeHealthDimension:
    """Tests voor KnowledgeHealthDimension dataclass."""

    def test_creation(self):
        dim = KnowledgeHealthDimension(overall_score=75.0)
        assert dim.overall_score == 75.0

    def test_frozen(self):
        dim = KnowledgeHealthDimension()
        with pytest.raises(AttributeError):
            dim.overall_score = 50.0  # type: ignore[misc]

    def test_invalid_score(self):
        with pytest.raises(ValueError, match="overall_score must be between 0 and 100"):
            KnowledgeHealthDimension(overall_score=101.0)


class TestKnowledgeHealthChecker:
    """Tests voor KnowledgeHealthChecker."""

    def test_empty_store(self):
        """Lege store levert lage score (freshness component kan > 0 zijn)."""
        store = _create_store()
        config = _make_config()
        checker = KnowledgeHealthChecker(config, store)

        result = checker.check()
        assert result.overall_score < 20.0  # zeer laag maar niet per se 0
        assert all(count == 0 for _, count in result.domain_coverage)

    def test_full_coverage(self):
        """Gevulde store levert hoge score."""
        store = _create_store()
        config = _make_config()

        store.store_article(_make_article(KnowledgeDomain.AI_ENGINEERING, "SILVER", ("RQ1", "RQ4")))
        store.store_article(_make_article(KnowledgeDomain.PYTHON_ARCHITECTURE, "SILVER", ("RQ2",)))

        checker = KnowledgeHealthChecker(config, store)
        result = checker.check()

        assert result.overall_score > 50.0
        ai_coverage = dict(result.domain_coverage).get("ai_engineering", 0)
        assert ai_coverage >= 1

    def test_grading_distribution(self):
        """Grading counts zijn correct."""
        store = _create_store()
        config = _make_config()

        store.store_article(_make_article(KnowledgeDomain.AI_ENGINEERING, "GOLD", ("RQ1",)))
        store.store_article(_make_article(KnowledgeDomain.AI_ENGINEERING, "BRONZE", ("RQ4",)))

        checker = KnowledgeHealthChecker(config, store)
        result = checker.check()

        dist = dict(result.grading_distribution)
        assert dist["GOLD"] == 1
        assert dist["BRONZE"] == 1

    def test_rq_coverage_calculation(self):
        """RQ-dekking percentages zijn correct."""
        store = _create_store()
        config = _make_config()

        # ai_engineering: alleen RQ1, niet RQ4 → 50%
        store.store_article(_make_article(KnowledgeDomain.AI_ENGINEERING, "SILVER", ("RQ1",)))

        checker = KnowledgeHealthChecker(config, store)
        result = checker.check()

        rq_dict = dict(result.rq_coverage)
        assert rq_dict["ai_engineering"] == 50.0

    def test_stale_domain_detection(self):
        """Artikelen ouder dan freshness_months worden gedetecteerd."""
        store = _create_store()
        config = _make_config()

        # ai_engineering heeft freshness_months=3, artikel van 6 maanden geleden
        store.store_article(
            _make_article(
                KnowledgeDomain.AI_ENGINEERING,
                "SILVER",
                ("RQ1",),
                date="2025-09-01",  # >3 maanden geleden
            )
        )

        checker = KnowledgeHealthChecker(config, store)
        result = checker.check()

        assert "ai_engineering" in result.stale_domains

    def test_fresh_domain_not_stale(self):
        """Recente artikelen worden niet als stale gemarkeerd."""
        store = _create_store()
        config = _make_config()

        store.store_article(
            _make_article(
                KnowledgeDomain.AI_ENGINEERING,
                "SILVER",
                ("RQ1",),
                date="2026-03-28",  # vandaag
            )
        )

        checker = KnowledgeHealthChecker(config, store)
        result = checker.check()

        assert "ai_engineering" not in result.stale_domains
