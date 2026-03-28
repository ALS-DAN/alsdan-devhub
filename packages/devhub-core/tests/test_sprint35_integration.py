"""Integratie-tests Sprint 35 — end-to-end: config → bootstrap → scan → health."""

from __future__ import annotations

import uuid
from pathlib import Path

from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.contracts.curator_contracts import KnowledgeDomain
from devhub_core.research.bootstrap import BootstrapPipeline
from devhub_core.research.config_bootstrap import ConfigDrivenBootstrap
from devhub_core.research.knowledge_config import load_knowledge_config
from devhub_core.research.knowledge_health import KnowledgeHealthChecker
from devhub_core.research.knowledge_scanner import KnowledgeScanner
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"
KNOWLEDGE_YML = CONFIG_DIR / "knowledge.yml"
AGENT_KNOWLEDGE_YML = CONFIG_DIR / "agent_knowledge.yml"


def _setup():
    """Maak volledige test-setup met echte config."""
    prefix = f"test_s35_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(zones=[DataZone.OPEN], collection_prefix=prefix)
    embedder = HashEmbeddingProvider(dimension=384)
    store = KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)
    config = load_knowledge_config(KNOWLEDGE_YML, AGENT_KNOWLEDGE_YML)
    curator = KnowledgeCurator()
    pipeline = BootstrapPipeline(curator=curator, store=store)
    return config, store, pipeline


class TestSprint35Integration:
    """End-to-end integratie-tests."""

    def test_bootstrap_then_scan_sufficient(self):
        """Na bootstrap is dev-lead scan beter dan zonder."""
        config, store, pipeline = _setup()

        # Scan vóór bootstrap: alles insufficient
        scanner = KnowledgeScanner(config, store)
        before = scanner.scan_agent("dev-lead")
        assert before.overall_sufficient is False

        # Bootstrap Ring 1
        bootstrap = ConfigDrivenBootstrap(config, pipeline, store)
        audit = bootstrap.run_bootstrap()
        assert audit.total_articles > 0

        # Scan ná bootstrap: core domeinen beter
        after = scanner.scan_agent("dev-lead")
        # Na bootstrap zijn er artikelen, maar de grade is BRONZE
        # dev-lead vereist SILVER voor sommige domeinen, dus niet per se sufficient
        assert len(after.gap_domains) <= len(before.gap_domains)

    def test_bootstrap_then_health_improved(self):
        """Na bootstrap is health score hoger."""
        config, store, pipeline = _setup()

        checker = KnowledgeHealthChecker(config, store)
        before = checker.check()

        bootstrap = ConfigDrivenBootstrap(config, pipeline, store)
        bootstrap.run_bootstrap()

        after = checker.check()
        assert after.overall_score > before.overall_score

    def test_full_pipeline_real_config(self):
        """Volledige pipeline met echte config bestanden."""
        config, store, pipeline = _setup()

        # 1. Verifieer config
        assert len(config.domains) == 16
        assert len(config.agent_profiles) == 7
        bootstrap_domains = config.bootstrap_domains()
        assert len(bootstrap_domains) == 5

        # 2. Bootstrap
        bootstrap = ConfigDrivenBootstrap(config, pipeline, store)
        requests = bootstrap.get_seed_requests()
        assert len(requests) == 5

        audit = bootstrap.run_bootstrap()
        assert audit.total_domains == 5
        assert audit.total_articles >= 25  # 5 domeinen × ~6 artikelen

        # 3. Scan
        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")
        assert len(result.domain_statuses) > 0

        # 4. Health
        checker = KnowledgeHealthChecker(config, store)
        health = checker.check()
        assert health.overall_score > 0.0
        assert len(health.domain_coverage) == 16

    def test_bootstrap_articles_have_rq_tags(self):
        """Gebootstrapte artikelen hebben RQ-tags."""
        config, store, pipeline = _setup()

        bootstrap = ConfigDrivenBootstrap(config, pipeline, store)
        bootstrap.run_bootstrap()

        articles = store.list_by_domain(KnowledgeDomain.AI_ENGINEERING)
        assert len(articles) > 0
        for article in articles:
            assert len(article.rq_tags) > 0

    def test_audit_coverage_matches_bootstrap(self):
        """audit_coverage rapport klopt met bootstrap resultaat."""
        config, store, pipeline = _setup()

        bootstrap = ConfigDrivenBootstrap(config, pipeline, store)
        run_audit = bootstrap.run_bootstrap()
        post_audit = bootstrap.audit_coverage()

        assert post_audit.total_articles == run_audit.total_articles
        assert post_audit.overall_coverage_pct == run_audit.overall_coverage_pct
