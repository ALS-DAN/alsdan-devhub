"""End-to-end tests voor de volledige kennisketen.

Verifieert dat de keten van knowledge/*.md → vectorstore → events
correct werkt, inclusief de drie governance-stromen.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from devhub_core.agents.governance_router import GovernanceRouter
from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.agents.knowledge_ingestor import KnowledgeIngestor
from devhub_core.contracts.event_contracts import (
    KnowledgeGapDetected,
    KnowledgeIngested,
    ResearchCompleted,
)
from devhub_core.contracts.pipeline_contracts import ProposalStatus
from devhub_core.contracts.research_contracts import (
    ResearchQueue,
    ResearchRequest,
    ResearchResponse,
)
from devhub_core.events.in_memory_bus import InMemoryEventBus
from devhub_core.events.integrations import (
    wire_governance_router,
    wire_ingestion_pipeline,
)
from devhub_core.research.knowledge_config import DomainConfig, KnowledgeConfig, RingConfig
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_core.research.proposal_queue import ResearchProposalQueue
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class InMemoryQueue(ResearchQueue):
    """Simpele in-memory ResearchQueue voor E2E tests."""

    def __init__(self):
        self._items: list[ResearchRequest] = []

    def submit(self, request: ResearchRequest) -> str:
        self._items.append(request)
        return request.request_id

    def next(self) -> ResearchRequest | None:
        return self._items[0] if self._items else None

    def complete(self, request_id: str, response: ResearchResponse) -> None:
        pass

    def pending(self) -> list[ResearchRequest]:
        return list(self._items)

    def by_agent(self, agent_name: str) -> list[ResearchRequest]:
        return [r for r in self._items if r.requesting_agent == agent_name]

    def get_response(self, request_id: str) -> ResearchResponse | None:
        return None


def _write_knowledge_article(knowledge_dir: Path, domain: str, filename: str, **overrides) -> Path:
    """Schrijf een valide kennisartikel."""
    domain_dir = knowledge_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    path = domain_dir / filename

    defaults = {
        "title": "E2E Test Article",
        "domain": domain,
        "grade": "SILVER",
        "date": "2026-03-29",
        "author": "researcher-agent",
        "verification": 60,
    }
    defaults.update(overrides)

    lines = ["---"]
    for k, v in defaults.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f'  - "{item}"')
        else:
            lines.append(f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}")
    # Sources moet als lijst
    if "sources" not in overrides:
        lines.append("sources:")
        lines.append('  - "https://docs.example.com/e2e"')
    lines.append("---")
    lines.append("")
    lines.append("# E2E Test Article")
    lines.append("")
    lines.append("## Samenvatting")
    lines.append("")
    lines.append("Dit is een end-to-end test artikel dat de volledige kennisketen verifieert.")
    lines.append(
        "Het bevat voldoende content om meerdere chunks te genereren na heading-based splitting."
    )
    lines.append("")
    lines.append("## Inhoud")
    lines.append("")
    lines.append("De inhoud beschrijft het onderwerp in detail met verwijzingen naar bronnen.")
    lines.append("Extra paragraaf om de chunk voldoende lang te maken voor verwerking.")
    lines.append(
        "Nog meer tekst zodat de chunking correct werkt en de vectorstore iets te indexeren heeft."
    )
    lines.append("")
    lines.append("## Bronnen")
    lines.append("")
    lines.append("- https://docs.example.com/e2e")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def vectorstore():
    import uuid

    store = ChromaDBZonedStore(
        zones=[DataZone.OPEN],
        collection_prefix=f"e2e_{uuid.uuid4().hex[:8]}",
    )
    return store


@pytest.fixture
def embedding_provider():
    return HashEmbeddingProvider()


@pytest.fixture
def knowledge_store(vectorstore, embedding_provider):
    return KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedding_provider)


@pytest.fixture
def curator():
    return KnowledgeCurator()


@pytest.fixture
def event_bus():
    return InMemoryEventBus()


@pytest.fixture
def knowledge_dir(tmp_path):
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    return kdir


@pytest.fixture
def knowledge_config():
    return KnowledgeConfig(
        rings=(
            RingConfig(name="core", auto_bootstrap=True),
            RingConfig(name="agent"),
            RingConfig(name="project"),
        ),
        domains=(
            DomainConfig(name="ai_engineering", ring="core", bootstrap_priority=1),
            DomainConfig(name="python_architecture", ring="core", bootstrap_priority=2),
            DomainConfig(name="sprint_planning", ring="agent"),
        ),
    )


@pytest.fixture
def research_queue():
    return InMemoryQueue()


@pytest.fixture
def proposal_queue(tmp_path):
    return ResearchProposalQueue(tmp_path / "research_queue.yml")


# ---------------------------------------------------------------------------
# E2E: Knowledge File → Vectorstore
# ---------------------------------------------------------------------------


class TestE2EIngestion:
    """E2E: MD bestand → parse → curator → vectorstore → event."""

    def test_full_pipeline(self, knowledge_dir, knowledge_store, curator, event_bus, vectorstore):
        """Compleet pad: bestand → ingest → vectorstore bevat chunks → event gepubliceerd."""
        _write_knowledge_article(knowledge_dir, "ai_engineering", "rag_patterns.md")

        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator, event_bus)
        summary = ingestor.ingest_all()

        # Verificatie: bestand geïngest
        assert summary.ingested == 1
        assert summary.rejected == 0

        # Verificatie: chunks in vectorstore
        assert vectorstore.count() > 0

        # Verificatie: event gepubliceerd
        events = event_bus.history(KnowledgeIngested)
        assert len(events) == 1
        assert events[0].domain == "ai_engineering"
        assert events[0].chunk_count > 0

    def test_incremental_skip(self, knowledge_dir, knowledge_store, curator, vectorstore):
        """Tweede ingest van ongewijzigd bestand → skip."""
        _write_knowledge_article(knowledge_dir, "ai_engineering", "same.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)

        s1 = ingestor.ingest_all()
        assert s1.ingested == 1

        s2 = ingestor.ingest_all()
        assert s2.skipped == 1
        assert s2.ingested == 0

    def test_curator_rejection(self, knowledge_dir, knowledge_store, curator, vectorstore):
        """Artikel zonder bronnen wordt afgewezen — niet in vectorstore."""
        path = _write_knowledge_article(
            knowledge_dir,
            "ai_engineering",
            "bad.md",
            grade="GOLD",
            verification=90,
            sources=[],
        )
        # Overschrijf om sources leeg te maken
        content = path.read_text()
        content = content.replace('sources:\n  - "https://docs.example.com/e2e"', "sources: []")
        path.write_text(content)

        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)
        summary = ingestor.ingest_all()

        assert summary.rejected == 1
        assert summary.ingested == 0
        assert vectorstore.count() == 0

    def test_vectorstore_metadata_preserved(
        self, knowledge_dir, knowledge_store, curator, vectorstore
    ):
        """Metadata (domein, grade) correct opgeslagen in vectorstore."""
        _write_knowledge_article(knowledge_dir, "ai_engineering", "meta.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)
        ingestor.ingest_all()

        # Query de vectorstore
        articles = knowledge_store.search("test", limit=5)
        assert len(articles) > 0
        for article in articles:
            assert article.domain.value == "ai_engineering"
            assert article.grade == "SILVER"


# ---------------------------------------------------------------------------
# E2E: Drie-stromen governance
# ---------------------------------------------------------------------------


class TestE2EGovernanceStreams:
    """E2E: KnowledgeGapDetected → correct gerouteerd per stroom."""

    def test_stream_1_auto_research(
        self, event_bus, knowledge_config, research_queue, proposal_queue
    ):
        """Stroom 1: Ring 1 domein → direct naar research queue."""
        router = GovernanceRouter(knowledge_config, research_queue, proposal_queue)
        wire_governance_router(event_bus, router)

        event_bus.publish(
            KnowledgeGapDetected(
                source_agent="analysis-pipeline",
                domain="ai_engineering",
                gap_description="Geen artikelen over event-driven architectuur",
                requesting_agent="coder",
            )
        )

        assert len(research_queue.pending()) == 1
        assert len(proposal_queue.pending()) == 0

    def test_stream_2_queued_for_approval(
        self, event_bus, knowledge_config, research_queue, proposal_queue
    ):
        """Stroom 2: niet-Ring 1 domein → proposal queue (wacht op goedkeuring)."""
        router = GovernanceRouter(knowledge_config, research_queue, proposal_queue)
        wire_governance_router(event_bus, router)

        event_bus.publish(
            KnowledgeGapDetected(
                source_agent="analysis-pipeline",
                domain="sprint_planning",
                gap_description="Capacity planning methodologie onbekend",
                requesting_agent="planner",
            )
        )

        assert len(research_queue.pending()) == 0
        assert len(proposal_queue.pending()) == 1
        assert proposal_queue.pending()[0].status == ProposalStatus.PENDING

    def test_stream_3_direct_request(self, knowledge_config, research_queue, proposal_queue):
        """Stroom 3: Niels directe request → priority 1, meteen in queue."""
        router = GovernanceRouter(knowledge_config, research_queue, proposal_queue)

        decision = router.handle_direct_request(
            topic="Vergelijk RAG strategieen",
            domain="ai_engineering",
        )

        assert decision.stream == 3
        assert len(research_queue.pending()) == 1
        assert research_queue.pending()[0].priority == 1


# ---------------------------------------------------------------------------
# E2E: Event-driven wiring
# ---------------------------------------------------------------------------


class TestE2EEventWiring:
    """E2E: Events koppelen componenten aan elkaar."""

    def test_research_completed_triggers_ingest(
        self, knowledge_dir, knowledge_store, curator, event_bus, vectorstore
    ):
        """ResearchCompleted event → KnowledgeIngestor → vectorstore."""
        _write_knowledge_article(knowledge_dir, "ai_engineering", "wired.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator, event_bus)
        wire_ingestion_pipeline(event_bus, ingestor)

        event_bus.publish(
            ResearchCompleted(
                source_agent="researcher",
                domain="ai_engineering",
                article_path=str(knowledge_dir / "ai_engineering" / "wired.md"),
                grade="SILVER",
                source_count=1,
            )
        )

        # KnowledgeIngestor is getriggerd via event
        assert vectorstore.count() > 0

    def test_full_event_chain(
        self,
        knowledge_dir,
        knowledge_store,
        curator,
        event_bus,
        vectorstore,
        knowledge_config,
        research_queue,
        proposal_queue,
    ):
        """Volledige event chain: gap → router → (stroom 1 auto) + research completed → ingest."""
        _write_knowledge_article(knowledge_dir, "ai_engineering", "chain.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator, event_bus)
        router = GovernanceRouter(knowledge_config, research_queue, proposal_queue)

        # Wire alles
        wire_governance_router(event_bus, router)
        wire_ingestion_pipeline(event_bus, ingestor)

        # Trigger gap → router plaatst in research queue (stroom 1)
        event_bus.publish(
            KnowledgeGapDetected(
                source_agent="analysis-pipeline",
                domain="ai_engineering",
                gap_description="Event-driven patterns ontbreken",
            )
        )

        # Verifieer: research queue heeft request
        assert len(research_queue.pending()) == 1

        # Simuleer research completion
        event_bus.publish(
            ResearchCompleted(
                source_agent="researcher",
                domain="ai_engineering",
                article_path=str(knowledge_dir / "ai_engineering" / "chain.md"),
                grade="SILVER",
                source_count=2,
            )
        )

        # Verifieer: vectorstore bevat het artikel
        assert vectorstore.count() > 0

        # Verifieer: KnowledgeIngested event is gepubliceerd
        ingested_events = event_bus.history(KnowledgeIngested)
        assert len(ingested_events) == 1
