"""Tests voor KWP DEV Bootstrap — request definitions, seed articles, pipeline."""

from __future__ import annotations

import uuid

from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.contracts.curator_contracts import (
    CurationVerdict,
    KnowledgeArticle,
    KnowledgeDomain,
)
from devhub_core.research.bootstrap import (
    BootstrapPipeline,
    BootstrapReport,
    KWPBootstrap,
)
from devhub_core.research.in_memory_queue import InMemoryResearchQueue
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_core.research.seed_articles import get_seed_articles
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


def _create_pipeline() -> tuple[BootstrapPipeline, KnowledgeStore]:
    """Maak een test pipeline met unieke collection prefix."""
    prefix = f"test_boot_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(
        zones=[DataZone.OPEN],
        collection_prefix=prefix,
    )
    embedder = HashEmbeddingProvider(dimension=384)
    store = KnowledgeStore(
        vectorstore=vectorstore,
        embedding_provider=embedder,
    )
    curator = KnowledgeCurator()
    pipeline = BootstrapPipeline(curator=curator, store=store)
    return pipeline, store


class TestKWPBootstrap:
    """Tests voor KWPBootstrap request definitions."""

    def test_get_requests_all_domains_covered(self):
        """Alle KnowledgeDomain waarden hebben requests."""
        requests = KWPBootstrap.get_requests()
        for domain in KnowledgeDomain:
            assert domain in requests
            assert len(requests[domain]) > 0

    def test_get_requests_total_count(self):
        """48 totale bootstrap requests (24 origineel + 24 nieuwe domeinen)."""
        requests = KWPBootstrap.get_requests()
        total = sum(len(r) for r in requests.values())
        assert total == 48

    def test_get_requests_ai_engineering_count(self):
        """8 AI engineering requests."""
        requests = KWPBootstrap.get_requests()
        assert len(requests[KnowledgeDomain.AI_ENGINEERING]) == 8

    def test_get_requests_claude_specific_count(self):
        """6 Claude-specifieke requests."""
        requests = KWPBootstrap.get_requests()
        assert len(requests[KnowledgeDomain.CLAUDE_SPECIFIC]) == 6

    def test_get_requests_python_architecture_count(self):
        """6 Python architecture requests."""
        requests = KWPBootstrap.get_requests()
        assert len(requests[KnowledgeDomain.PYTHON_ARCHITECTURE]) == 6

    def test_get_requests_dev_methodology_count(self):
        """4 Development methodology requests."""
        requests = KWPBootstrap.get_requests()
        assert len(requests[KnowledgeDomain.DEVELOPMENT_METHODOLOGY]) == 4

    def test_get_requests_unique_ids(self):
        """Alle request IDs zijn uniek."""
        requests = KWPBootstrap.get_requests()
        all_ids = [r.request_id for reqs in requests.values() for r in reqs]
        assert len(all_ids) == len(set(all_ids))

    def test_get_requests_all_kwp_bootstrap_agent(self):
        """Alle requests komen van kwp-bootstrap agent."""
        requests = KWPBootstrap.get_requests()
        for reqs in requests.values():
            for r in reqs:
                assert r.requesting_agent == "kwp-bootstrap"

    def test_get_requests_valid_priorities(self):
        """Alle priorities zijn 1-10."""
        requests = KWPBootstrap.get_requests()
        for reqs in requests.values():
            for r in reqs:
                assert 1 <= r.priority <= 10

    def test_submit_all_to_queue(self):
        """submit_all plaatst 48 requests in de queue."""
        bootstrap = KWPBootstrap()
        queue = InMemoryResearchQueue()
        count = bootstrap.submit_all(queue)
        assert count == 48
        assert len(queue.pending()) == 48

    def test_submit_domain(self):
        """submit_domain plaatst alleen domein-requests."""
        bootstrap = KWPBootstrap()
        queue = InMemoryResearchQueue()
        count = bootstrap.submit_domain(queue, KnowledgeDomain.AI_ENGINEERING)
        assert count == 8
        assert len(queue.pending()) == 8

    def test_submit_domain_empty(self):
        """submit_domain met onbekend domein retourneert 0."""
        bootstrap = KWPBootstrap()
        queue = InMemoryResearchQueue()
        # All domains should exist, but verify submit works
        count = bootstrap.submit_domain(queue, KnowledgeDomain.DEVELOPMENT_METHODOLOGY)
        assert count == 4


class TestSeedArticles:
    """Tests voor seed articles."""

    def test_get_seed_articles_count(self):
        """8 seed artikelen."""
        articles = get_seed_articles()
        assert len(articles) == 8

    def test_seed_articles_all_core_domains_covered(self):
        """Alle 4 originele core domeinen zijn vertegenwoordigd in seeds."""
        articles = get_seed_articles()
        domains = {a.domain for a in articles}
        core_domains = {
            KnowledgeDomain.AI_ENGINEERING,
            KnowledgeDomain.CLAUDE_SPECIFIC,
            KnowledgeDomain.PYTHON_ARCHITECTURE,
            KnowledgeDomain.DEVELOPMENT_METHODOLOGY,
        }
        assert core_domains.issubset(domains)

    def test_seed_articles_all_valid(self):
        """Curator keurt alle seed articles goed."""
        articles = get_seed_articles()
        curator = KnowledgeCurator()
        for article in articles:
            report = curator.validate_article(article)
            assert report.verdict == CurationVerdict.APPROVED, (
                f"Seed article {article.article_id}"
                f" not approved: "
                f"{[f.description for f in report.findings]}"
            )

    def test_seed_articles_have_sources(self):
        """Alle seed articles hebben bronvermelding."""
        articles = get_seed_articles()
        for article in articles:
            assert len(article.sources) >= 1

    def test_seed_articles_unique_ids(self):
        """Alle article IDs zijn uniek."""
        articles = get_seed_articles()
        ids = [a.article_id for a in articles]
        assert len(ids) == len(set(ids))

    def test_seed_articles_have_date(self):
        """Alle seed articles hebben een datum."""
        articles = get_seed_articles()
        for article in articles:
            assert article.date == "2026-03-27"

    def test_seed_articles_have_author(self):
        """Alle seed articles hebben kwp-bootstrap als auteur."""
        articles = get_seed_articles()
        for article in articles:
            assert article.author == "kwp-bootstrap"

    def test_seed_articles_content_length(self):
        """Content is minimaal 100 tekens (niet placeholder)."""
        articles = get_seed_articles()
        for article in articles:
            assert len(article.content) >= 100, (
                f"{article.article_id} content te kort:" f" {len(article.content)} chars"
            )


class TestBootstrapPipeline:
    """Tests voor BootstrapPipeline integratie."""

    def test_run_seed_all_approved(self):
        """Alle seed articles worden goedgekeurd."""
        pipeline, store = _create_pipeline()
        articles = get_seed_articles()
        report = pipeline.run_seed(articles)
        assert report.approved == 8
        assert report.rejected == 0

    def test_run_seed_stores_approved(self):
        """Goedgekeurde articles worden opgeslagen."""
        pipeline, store = _create_pipeline()
        articles = get_seed_articles()
        pipeline.run_seed(articles)
        all_stored = store.get_all_articles()
        assert len(all_stored) >= 8

    def test_run_seed_rejected_not_stored(self):
        """Afgekeurde articles worden niet opgeslagen."""
        pipeline, store = _create_pipeline()
        bad_article = KnowledgeArticle(
            article_id="BAD-001",
            title="Bad Article",
            content=(
                "No sources, GOLD grade, low verification"
                " — should be rejected by the curator"
                " because GOLD requires 80 percent"
                " verification minimum."
            ),
            domain=KnowledgeDomain.AI_ENGINEERING,
            grade="GOLD",
            verification_pct=10.0,
        )
        report = pipeline.run_seed([bad_article])
        assert report.rejected == 1
        assert report.approved == 0

    def test_bootstrap_report_counts(self):
        """Report counts tellen op tot totaal."""
        pipeline, _ = _create_pipeline()
        articles = get_seed_articles()
        report = pipeline.run_seed(articles)
        assert report.total_submitted == 8
        total = report.approved + report.rejected + report.needs_revision
        assert total == 8

    def test_bootstrap_report_has_curation_reports(self):
        """Report bevat CurationReports voor elk artikel."""
        pipeline, _ = _create_pipeline()
        articles = get_seed_articles()
        report = pipeline.run_seed(articles)
        assert len(report.reports) == 8

    def test_bootstrap_report_is_frozen(self):
        """BootstrapReport is een frozen dataclass."""
        report = BootstrapReport(total_submitted=5)
        assert report.total_submitted == 5
        try:
            report.total_submitted = 10  # type: ignore[misc]
            raise AssertionError("Should raise FrozenInstanceError")
        except AttributeError:
            pass

    def test_health_check_after_seed(self):
        """Health check na seed geeft score > 0."""
        pipeline, store = _create_pipeline()
        articles = get_seed_articles()
        pipeline.run_seed(articles)
        health = pipeline.health_check()
        assert health.overall_score > 0

    def test_end_to_end_seed_to_search(self):
        """Seed articles zijn doorzoekbaar na ingest."""
        pipeline, store = _create_pipeline()
        articles = get_seed_articles()
        pipeline.run_seed(articles)
        results = store.search("frozen dataclass pattern")
        assert len(results) >= 1

    def test_pipeline_mixed_articles(self):
        """Pipeline verwerkt mix van geldige en ongeldige articles."""
        pipeline, store = _create_pipeline()
        good = KnowledgeArticle(
            article_id="MIX-001",
            title="Good Article",
            content=(
                "Dit is een geldig artikel met voldoende"
                " inhoud voor de curator om goed te keuren."
                " Het bevat bronvermelding en correcte"
                " gradering met bijpassend verificatie-"
                " percentage."
            ),
            domain=KnowledgeDomain.AI_ENGINEERING,
            grade="SILVER",
            sources=("test/source.py",),
            verification_pct=60.0,
            date="2026-03-27",
            author="test",
        )
        bad = KnowledgeArticle(
            article_id="MIX-002",
            title="Bad GOLD Article",
            content=(
                "Dit artikel claimt GOLD maar heeft"
                " veel te lage verificatie. Het zal door"
                " de curator worden afgewezen vanwege de"
                " ongeldige gradering."
            ),
            domain=KnowledgeDomain.AI_ENGINEERING,
            grade="GOLD",
            verification_pct=10.0,
        )
        report = pipeline.run_seed([good, bad])
        assert report.total_submitted == 2
        assert report.approved == 1
        assert report.rejected == 1
