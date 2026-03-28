"""Tests voor KnowledgeScanner — pre-task knowledge scan."""

from __future__ import annotations

import uuid
from pathlib import Path


from devhub_core.contracts.curator_contracts import KnowledgeArticle, KnowledgeDomain
from devhub_core.research.in_memory_queue import InMemoryResearchQueue
from devhub_core.research.knowledge_config import (
    AgentKnowledgeProfile,
    DomainConfig,
    KnowledgeConfig,
    RingConfig,
    SeedQuestion,
    load_knowledge_config,
)
from devhub_core.research.knowledge_scanner import KnowledgeScanner
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"
KNOWLEDGE_YML = CONFIG_DIR / "knowledge.yml"
AGENT_KNOWLEDGE_YML = CONFIG_DIR / "agent_knowledge.yml"


def _create_store() -> KnowledgeStore:
    """Maak een test store met unieke collection prefix."""
    prefix = f"test_scan_{uuid.uuid4().hex[:8]}"
    vectorstore = ChromaDBZonedStore(
        zones=[DataZone.OPEN],
        collection_prefix=prefix,
    )
    embedder = HashEmbeddingProvider(dimension=384)
    return KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedder)


def _make_article(
    domain: KnowledgeDomain,
    grade: str = "SILVER",
    rq_tags: tuple[str, ...] = (),
    suffix: str = "",
) -> KnowledgeArticle:
    """Hulpfunctie voor test-artikelen."""
    uid = uuid.uuid4().hex[:6]
    return KnowledgeArticle(
        article_id=f"TEST-{domain.value}-{uid}{suffix}",
        title=f"Test artikel {domain.value}",
        content=f"Inhoud voor {domain.value} ({grade})",
        domain=domain,
        grade=grade,
        sources=("test-source",),
        rq_tags=rq_tags,
        domain_ring=domain.ring,
    )


def _make_config() -> KnowledgeConfig:
    """Maak een minimale test-config."""
    return KnowledgeConfig(
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
                seed_questions=(
                    SeedQuestion(question="Test RQ1 vraag?", rq_tag="RQ1"),
                    SeedQuestion(question="Test RQ4 vraag?", rq_tag="RQ4"),
                ),
            ),
            DomainConfig(
                name="claude_specific",
                ring="core",
                rq_focus=("RQ1", "RQ4"),
                bootstrap_priority=1,
            ),
        ),
        agent_profiles=(
            AgentKnowledgeProfile(
                agent_name="dev-lead",
                domains=(("ai_engineering", "SILVER"), ("claude_specific", "BRONZE")),
                pre_task_check=True,
            ),
            AgentKnowledgeProfile(
                agent_name="coder",
                domains=(("ai_engineering", "BRONZE"),),
                pre_task_check=False,
            ),
        ),
    )


class TestKnowledgeScanner:
    """Tests voor KnowledgeScanner."""

    def test_scan_agent_sufficient_knowledge(self):
        """Pre-populate store met voldoende artikelen."""
        store = _create_store()
        config = _make_config()

        # Vul store met artikelen die aan alle vereisten voldoen
        store.store_article(
            _make_article(KnowledgeDomain.AI_ENGINEERING, "SILVER", ("RQ1", "RQ4", "RQ5"))
        )
        store.store_article(
            _make_article(KnowledgeDomain.CLAUDE_SPECIFIC, "BRONZE", ("RQ1", "RQ4"))
        )

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        assert result.overall_sufficient is True
        assert result.gap_domains == []
        assert len(result.generated_requests) == 0

    def test_scan_agent_gap_detection(self):
        """Store mist artikelen voor één domein."""
        store = _create_store()
        config = _make_config()

        # Alleen ai_engineering vullen, claude_specific leeg
        store.store_article(
            _make_article(KnowledgeDomain.AI_ENGINEERING, "SILVER", ("RQ1", "RQ4", "RQ5"))
        )

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        assert result.overall_sufficient is False
        assert "claude_specific" in result.gap_domains

    def test_scan_agent_grade_insufficient(self):
        """Store heeft BRONZE maar SILVER is vereist."""
        store = _create_store()
        config = _make_config()

        store.store_article(
            _make_article(KnowledgeDomain.AI_ENGINEERING, "BRONZE", ("RQ1", "RQ4", "RQ5"))
        )
        store.store_article(
            _make_article(KnowledgeDomain.CLAUDE_SPECIFIC, "BRONZE", ("RQ1", "RQ4"))
        )

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        assert result.overall_sufficient is False
        assert "ai_engineering" in result.gap_domains  # BRONZE < SILVER

    def test_scan_agent_rq_coverage_gap(self):
        """Artikelen aanwezig maar RQ5 mist."""
        store = _create_store()
        config = _make_config()

        store.store_article(
            _make_article(
                KnowledgeDomain.AI_ENGINEERING,
                "SILVER",
                ("RQ1", "RQ4"),  # RQ5 mist
            )
        )
        store.store_article(
            _make_article(KnowledgeDomain.CLAUDE_SPECIFIC, "BRONZE", ("RQ1", "RQ4"))
        )

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        assert result.overall_sufficient is False
        ai_status = next(s for s in result.domain_statuses if s.domain == "ai_engineering")
        assert "RQ5" in ai_status.missing_rqs

    def test_scan_agent_generates_research_requests(self):
        """Gegenereerde requests voor ontbrekende RQs."""
        store = _create_store()
        config = _make_config()

        store.store_article(
            _make_article(
                KnowledgeDomain.AI_ENGINEERING,
                "SILVER",
                ("RQ1",),  # RQ4, RQ5 missen
            )
        )
        store.store_article(
            _make_article(KnowledgeDomain.CLAUDE_SPECIFIC, "BRONZE", ("RQ1", "RQ4"))
        )

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        assert len(result.generated_requests) >= 2
        rq_tags = {rq for req in result.generated_requests for rq in req.rq_tags}
        assert "RQ4" in rq_tags
        assert "RQ5" in rq_tags

    def test_scan_agent_uses_seed_questions(self):
        """Gegenereerde requests gebruiken seed questions als template."""
        store = _create_store()
        config = _make_config()

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        # ai_engineering heeft seed questions voor RQ1 en RQ4
        rq1_req = next(
            (
                r
                for r in result.generated_requests
                if r.domain == "ai_engineering" and "RQ1" in r.rq_tags
            ),
            None,
        )
        assert rq1_req is not None
        assert "Test RQ1 vraag?" in rq1_req.question

    def test_scan_agent_submits_to_queue(self):
        """Requests worden naar queue gesubmit."""
        store = _create_store()
        config = _make_config()
        queue = InMemoryResearchQueue()

        scanner = KnowledgeScanner(config, store, queue=queue)
        result = scanner.scan_agent("dev-lead")

        assert len(result.generated_requests) > 0
        pending = queue.pending()
        assert len(pending) == len(result.generated_requests)

    def test_scan_agent_unknown_agent(self):
        """Onbekende agent retourneert leeg resultaat."""
        store = _create_store()
        config = _make_config()

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("nonexistent-agent")

        assert result.agent_name == "nonexistent-agent"
        assert result.overall_sufficient is True  # geen eisen = voldoende
        assert result.domain_statuses == ()

    def test_scan_with_real_config(self):
        """Scan met echte knowledge.yml en agent_knowledge.yml."""
        store = _create_store()
        config = load_knowledge_config(KNOWLEDGE_YML, AGENT_KNOWLEDGE_YML)

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        # Lege store = alle domeinen insufficient
        assert result.overall_sufficient is False
        assert len(result.domain_statuses) > 0
        assert len(result.generated_requests) > 0

    def test_scan_agent_request_ids_unique(self):
        """Alle gegenereerde request IDs zijn uniek."""
        store = _create_store()
        config = _make_config()

        scanner = KnowledgeScanner(config, store)
        result = scanner.scan_agent("dev-lead")

        ids = [r.request_id for r in result.generated_requests]
        assert len(ids) == len(set(ids))
