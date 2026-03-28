"""Tests voor ConfigDrivenBootstrap — Ring 1 auto-bootstrap uit config."""

from __future__ import annotations

import uuid
from pathlib import Path


from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.contracts.curator_contracts import KnowledgeDomain
from devhub_core.research.bootstrap import BootstrapPipeline
from devhub_core.research.config_bootstrap import ConfigDrivenBootstrap
from devhub_core.research.knowledge_config import (
    DomainConfig,
    KnowledgeConfig,
    RingConfig,
    SeedQuestion,
    load_knowledge_config,
)
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"
KNOWLEDGE_YML = CONFIG_DIR / "knowledge.yml"


def _create_pipeline() -> tuple[ConfigDrivenBootstrap, KnowledgeStore, KnowledgeConfig]:
    """Maak een test bootstrap setup met unieke collection prefix."""
    prefix = f"test_cboot_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(
        zones=[DataZone.OPEN],
        collection_prefix=prefix,
    )
    embedder = HashEmbeddingProvider(dimension=384)
    store = KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)
    curator = KnowledgeCurator()
    pipeline = BootstrapPipeline(curator=curator, store=store)

    config = KnowledgeConfig(
        rings=(
            RingConfig(name="core", auto_bootstrap=True),
            RingConfig(name="agent"),
        ),
        domains=(
            DomainConfig(
                name="ai_engineering",
                ring="core",
                rq_focus=("RQ1", "RQ4", "RQ5"),
                bootstrap_priority=1,
                description="AI engineering domein",
                seed_questions=(
                    SeedQuestion(question="SOTA prompt engineering?", rq_tag="RQ1"),
                    SeedQuestion(question="Multi-agent patronen?", rq_tag="RQ1"),
                    SeedQuestion(question="RAG chunking strategieën?", rq_tag="RQ4"),
                    SeedQuestion(question="Tool use patterns?", rq_tag="RQ4"),
                    SeedQuestion(question="Context window management?", rq_tag="RQ5"),
                    SeedQuestion(question="Agent memory patronen?", rq_tag="RQ5"),
                ),
            ),
            DomainConfig(
                name="python_architecture",
                ring="core",
                rq_focus=("RQ2", "RQ4"),
                bootstrap_priority=2,
                description="Python architectuur domein",
                seed_questions=(
                    SeedQuestion(question="ABC vs Protocol?", rq_tag="RQ2"),
                    SeedQuestion(question="uv workspace best practices?", rq_tag="RQ2"),
                    SeedQuestion(question="Pytest patronen?", rq_tag="RQ4"),
                    SeedQuestion(question="Factory patterns?", rq_tag="RQ4"),
                    SeedQuestion(question="Adapter design?", rq_tag="RQ2"),
                    SeedQuestion(question="Pydantic vs dataclasses?", rq_tag="RQ4"),
                ),
            ),
            DomainConfig(
                name="sprint_planning",
                ring="agent",
                rq_focus=("RQ4",),
                bootstrap_priority=2,
                description="Agent domein (geen auto-bootstrap)",
            ),
        ),
    )

    bootstrap = ConfigDrivenBootstrap(config=config, pipeline=pipeline, store=store)
    return bootstrap, store, config


class TestGetSeedRequests:
    """Tests voor get_seed_requests."""

    def test_core_domains_only(self):
        """Alleen core ring domeinen krijgen requests."""
        bootstrap, _, _ = _create_pipeline()
        requests = bootstrap.get_seed_requests()

        assert "ai_engineering" in requests
        assert "python_architecture" in requests
        assert "sprint_planning" not in requests  # agent ring

    def test_count_per_domain(self):
        """Elk domein krijgt requests per seed question."""
        bootstrap, _, _ = _create_pipeline()
        requests = bootstrap.get_seed_requests()

        assert len(requests["ai_engineering"]) == 6
        assert len(requests["python_architecture"]) == 6

    def test_rq_tags_set(self):
        """Elke request heeft rq_tag uit config."""
        bootstrap, _, _ = _create_pipeline()
        requests = bootstrap.get_seed_requests()

        for req in requests["ai_engineering"]:
            assert len(req.rq_tags) == 1
            assert req.rq_tags[0] in ("RQ1", "RQ4", "RQ5")

    def test_request_ids_unique(self):
        """Alle request IDs zijn uniek."""
        bootstrap, _, _ = _create_pipeline()
        requests = bootstrap.get_seed_requests()

        all_ids = [r.request_id for reqs in requests.values() for r in reqs]
        assert len(all_ids) == len(set(all_ids))


class TestRunBootstrap:
    """Tests voor run_bootstrap."""

    def test_creates_articles(self):
        """Na bootstrap bevat store artikelen voor core domeinen."""
        bootstrap, store, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()

        assert audit.total_articles > 0
        ai_articles = store.list_by_domain(KnowledgeDomain.AI_ENGINEERING)
        assert len(ai_articles) > 0

    def test_bronze_grade(self):
        """Alle gebootstrapte artikelen zijn BRONZE."""
        bootstrap, store, _ = _create_pipeline()
        bootstrap.run_bootstrap()

        for domain in [KnowledgeDomain.AI_ENGINEERING, KnowledgeDomain.PYTHON_ARCHITECTURE]:
            articles = store.list_by_domain(domain)
            for article in articles:
                assert article.grade == "BRONZE"

    def test_audit_report_structure(self):
        """Audit rapport heeft juiste structuur."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()

        assert audit.total_domains == 2  # ai_engineering + python_architecture
        assert len(audit.domain_reports) == 2
        assert audit.timestamp != ""

    def test_coverage_full(self):
        """Na bootstrap is RQ-dekking 100% voor alle core domeinen."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()

        for dr in audit.domain_reports:
            assert dr.coverage_pct == 100.0, f"{dr.domain} coverage not 100%"

    def test_sorted_by_priority(self):
        """Domeinen worden verwerkt op bootstrap_priority."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()

        # ai_engineering (prio 1) komt voor python_architecture (prio 2)
        domains = [dr.domain for dr in audit.domain_reports]
        assert domains.index("ai_engineering") < domains.index("python_architecture")


class TestAuditCoverage:
    """Tests voor audit_coverage (zonder nieuwe artikelen)."""

    def test_empty_store(self):
        """Lege store geeft 0% coverage."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.audit_coverage()

        assert audit.total_articles == 0
        for dr in audit.domain_reports:
            assert dr.coverage_pct == 0.0 or dr.articles_created == 0

    def test_after_bootstrap(self):
        """Na bootstrap reflecteert audit de ingevoerde artikelen."""
        bootstrap, _, _ = _create_pipeline()
        bootstrap.run_bootstrap()
        audit = bootstrap.audit_coverage()

        assert audit.total_articles > 0
        assert audit.overall_coverage_pct > 0.0


class TestFormatReport:
    """Tests voor format_report."""

    def test_contains_domain_names(self):
        """Formatted output bevat domein-namen."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()
        report = bootstrap.format_report(audit)

        assert "ai_engineering" in report
        assert "python_architecture" in report

    def test_contains_article_counts(self):
        """Formatted output bevat artikel-aantallen."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()
        report = bootstrap.format_report(audit)

        assert "artikelen" in report

    def test_contains_coverage_percentage(self):
        """Formatted output bevat dekking-percentage."""
        bootstrap, _, _ = _create_pipeline()
        audit = bootstrap.run_bootstrap()
        report = bootstrap.format_report(audit)

        assert "dekking" in report.lower() or "%" in report


class TestRealConfig:
    """Tests met echte knowledge.yml configuratie."""

    def test_seed_requests_from_real_config(self):
        """Echte config genereert requests voor alle 5 kerndomeinen."""
        config = load_knowledge_config(KNOWLEDGE_YML)
        prefix = f"test_cboot_real_{uuid.uuid4().hex[:8]}"
        vectorstore = ChromaDBZonedStore(zones=[DataZone.OPEN], collection_prefix=prefix)
        embedder = HashEmbeddingProvider(dimension=384)
        store = KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)
        curator = KnowledgeCurator()
        pipeline = BootstrapPipeline(curator=curator, store=store)

        bootstrap = ConfigDrivenBootstrap(config=config, pipeline=pipeline, store=store)
        requests = bootstrap.get_seed_requests()

        assert len(requests) == 5  # 5 core domeinen
        for domain_name, reqs in requests.items():
            assert len(reqs) >= 6, f"{domain_name} has only {len(reqs)} requests"
