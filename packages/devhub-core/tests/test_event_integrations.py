"""Tests voor event bus integraties — AnalysisPipeline, DevOrchestrator, wiring helpers."""

from devhub_core.contracts.curator_contracts import ObservationType
from pathlib import Path

from devhub_core.contracts.event_contracts import (
    DocGenRequested,
    Event,
    KnowledgeGapDetected,
    ObservationEmitted,
    ResearchCompleted,
    SprintClosed,
    TaskAssigned,
    TaskCompleted,
)
from devhub_core.events.in_memory_bus import InMemoryEventBus
from devhub_core.contracts.event_contracts import KnowledgeIngested
from devhub_core.events.integrations import (
    produce_from_knowledge,
    wire_governance_router,
    wire_ingestion_pipeline,
    wire_knowledge_pipeline,
    wire_knowledge_to_docs,
    wire_sprint_lifecycle,
)
from devhub_core.research.in_memory_queue import InMemoryResearchQueue


# ---------------------------------------------------------------------------
# Helpers — Fake dependencies voor AnalysisPipeline en DevOrchestrator
# ---------------------------------------------------------------------------


class FakeKnowledgeStore:
    def search(self, *args, **kwargs):
        return []

    def count(self):
        return 0


class FakeDocumentInterface:
    pass


class FakeStorageInterface:
    pass


def _make_pipeline(event_bus=None):
    from devhub_core.agents.analysis_pipeline import AnalysisPipeline

    return AnalysisPipeline(
        knowledge_store=FakeKnowledgeStore(),
        research_queue=InMemoryResearchQueue(),
        document_interface=FakeDocumentInterface(),
        local_storage=FakeStorageInterface(),
        event_bus=event_bus,
    )


def _make_orchestrator(event_bus=None, scratchpad_path=None):
    from devhub_core.agents.orchestrator import DevOrchestrator
    from devhub_core.registry import NodeRegistry

    registry = NodeRegistry.__new__(NodeRegistry)
    registry._nodes = {}
    return DevOrchestrator(
        registry=registry,
        scratchpad_path=scratchpad_path,
        event_bus=event_bus,
    )


# ---------------------------------------------------------------------------
# AnalysisPipeline integratie
# ---------------------------------------------------------------------------


class TestAnalysisPipelineEventBus:
    def test_emit_observation_publishes_event_when_bus_present(self) -> None:
        bus = InMemoryEventBus()
        pipeline = _make_pipeline(event_bus=bus)
        received: list[Event] = []
        bus.subscribe(ObservationEmitted, received.append)

        pipeline._emit_observation(
            ObservationType.ANALYSIS_COMPLETED,
            "Analysis done",
            "INFO",
        )

        assert len(received) == 1
        evt = received[0]
        assert isinstance(evt, ObservationEmitted)
        assert evt.obs_type == ObservationType.ANALYSIS_COMPLETED
        assert evt.payload == "Analysis done"
        assert evt.severity == "INFO"
        assert evt.source_agent == "analysis-pipeline"

    def test_emit_observation_works_without_bus(self) -> None:
        pipeline = _make_pipeline(event_bus=None)
        # Should not raise — just logs
        pipeline._emit_observation(
            ObservationType.ANALYSIS_FAILED,
            "Something failed",
            "ERROR",
        )

    def test_emit_observation_still_logs(self, caplog) -> None:
        bus = InMemoryEventBus()
        pipeline = _make_pipeline(event_bus=bus)

        with caplog.at_level("INFO"):
            pipeline._emit_observation(
                ObservationType.HEALTH_DEGRADED,
                "Score dropped",
                "WARNING",
            )

        assert "OBSERVATION" in caplog.text
        assert "health_degraded" in caplog.text


# ---------------------------------------------------------------------------
# DevOrchestrator integratie
# ---------------------------------------------------------------------------


class TestDevOrchestratorEventBus:
    def test_create_task_publishes_task_assigned(self, tmp_path) -> None:
        bus = InMemoryEventBus()
        orch = _make_orchestrator(event_bus=bus, scratchpad_path=tmp_path)
        received: list[Event] = []
        bus.subscribe(TaskAssigned, received.append)

        task = orch.create_task(
            description="Build event bus",
            node_id="devhub",
        )

        assert len(received) == 1
        evt = received[0]
        assert isinstance(evt, TaskAssigned)
        assert evt.task_id == task.task_id
        assert evt.description == "Build event bus"

    def test_record_task_result_publishes_task_completed(self, tmp_path) -> None:
        bus = InMemoryEventBus()
        orch = _make_orchestrator(event_bus=bus, scratchpad_path=tmp_path)
        received: list[Event] = []
        bus.subscribe(TaskCompleted, received.append)

        orch.record_task_result(
            task_id="T-001",
            files_changed=["a.py"],
            tests_added=5,
        )

        assert len(received) == 1
        evt = received[0]
        assert isinstance(evt, TaskCompleted)
        assert evt.task_id == "T-001"
        assert evt.result is not None
        assert evt.result.tests_added == 5

    def test_decompose_for_docs_publishes_doc_gen_requested(self, tmp_path) -> None:
        bus = InMemoryEventBus()
        orch = _make_orchestrator(event_bus=bus, scratchpad_path=tmp_path)
        received: list[Event] = []
        bus.subscribe(DocGenRequested, received.append)

        from devhub_core.contracts.dev_contracts import DevTaskRequest

        task = DevTaskRequest(
            task_id="T-001",
            description="Test task",
            node_id="devhub",
        )
        orch.decompose_for_docs(task, "reference", "developer")

        assert len(received) == 1
        evt = received[0]
        assert isinstance(evt, DocGenRequested)
        assert evt.request.task_id == "T-001"

    def test_no_events_without_bus(self, tmp_path) -> None:
        orch = _make_orchestrator(event_bus=None, scratchpad_path=tmp_path)
        # Should not raise
        orch.create_task(description="Test", node_id="devhub")
        orch.record_task_result(task_id="T-001")


# ---------------------------------------------------------------------------
# Wiring helpers
# ---------------------------------------------------------------------------


class TestWireKnowledgePipeline:
    def test_gap_detected_creates_research_request(self) -> None:
        bus = InMemoryEventBus()
        queue = InMemoryResearchQueue()
        wire_knowledge_pipeline(bus, queue)

        bus.publish(
            KnowledgeGapDetected(
                source_agent="analysis-pipeline",
                domain="ai_engineering",
                gap_description="No articles on event-driven architecture",
                requesting_agent="researcher",
            )
        )

        pending = queue.pending()
        assert len(pending) == 1
        assert pending[0].domain == "ai_engineering"
        assert pending[0].requesting_agent == "researcher"
        assert pending[0].priority == 3

    def test_unsubscribe_stops_wiring(self) -> None:
        bus = InMemoryEventBus()
        queue = InMemoryResearchQueue()
        sub_id = wire_knowledge_pipeline(bus, queue)

        bus.unsubscribe(sub_id)
        bus.publish(
            KnowledgeGapDetected(
                source_agent="test",
                domain="dev",
                gap_description="gap",
            )
        )

        assert len(queue.pending()) == 0


class TestWireSprintLifecycle:
    def test_sprint_closed_calls_callback(self) -> None:
        bus = InMemoryEventBus()
        closed_events: list[Event] = []
        wire_sprint_lifecycle(bus, on_sprint_closed=closed_events.append)

        bus.publish(
            SprintClosed(
                source_agent="sprint-skill",
                sprint_id="S41",
                node_id="devhub",
            )
        )

        assert len(closed_events) == 1
        assert isinstance(closed_events[0], SprintClosed)

    def test_no_callback_is_noop(self) -> None:
        bus = InMemoryEventBus()
        wire_sprint_lifecycle(bus, on_sprint_closed=None)

        # Should not raise
        bus.publish(
            SprintClosed(
                source_agent="test",
                sprint_id="S1",
                node_id="devhub",
            )
        )


# ---------------------------------------------------------------------------
# wire_ingestion_pipeline
# ---------------------------------------------------------------------------


class FakeIngestor:
    """Fake KnowledgeIngestor voor tests."""

    def __init__(self):
        self.ingested_files: list[Path] = []

    def ingest_file(self, path: Path):
        self.ingested_files.append(path)


class TestWireIngestionPipeline:
    def test_research_completed_triggers_ingest(self, tmp_path) -> None:
        bus = InMemoryEventBus()
        ingestor = FakeIngestor()
        wire_ingestion_pipeline(bus, ingestor)

        # Maak een bestand aan zodat het pad bestaat
        article = tmp_path / "test_article.md"
        article.write_text("---\ntitle: Test\n---\nContent")

        bus.publish(
            ResearchCompleted(
                source_agent="researcher",
                domain="ai_engineering",
                article_path=str(article),
                grade="SILVER",
                source_count=3,
            )
        )

        assert len(ingestor.ingested_files) == 1
        assert ingestor.ingested_files[0] == article

    def test_nonexistent_path_skipped(self) -> None:
        bus = InMemoryEventBus()
        ingestor = FakeIngestor()
        wire_ingestion_pipeline(bus, ingestor)

        bus.publish(
            ResearchCompleted(
                source_agent="researcher",
                domain="ai_engineering",
                article_path="/nonexistent/path.md",
                grade="SILVER",
                source_count=1,
            )
        )

        assert len(ingestor.ingested_files) == 0

    def test_unsubscribe_stops_ingestion(self, tmp_path) -> None:
        bus = InMemoryEventBus()
        ingestor = FakeIngestor()
        sub_id = wire_ingestion_pipeline(bus, ingestor)

        bus.unsubscribe(sub_id)

        article = tmp_path / "test.md"
        article.write_text("content")
        bus.publish(
            ResearchCompleted(
                source_agent="researcher",
                domain="ai_engineering",
                article_path=str(article),
                grade="SILVER",
            )
        )

        assert len(ingestor.ingested_files) == 0


# ---------------------------------------------------------------------------
# wire_governance_router
# ---------------------------------------------------------------------------


class FakeRouter:
    """Fake GovernanceRouter voor tests."""

    def __init__(self):
        self.routed_events: list[KnowledgeGapDetected] = []

    def route_gap(self, event):
        self.routed_events.append(event)


class TestWireGovernanceRouter:
    def test_gap_detected_routes_to_router(self) -> None:
        bus = InMemoryEventBus()
        router = FakeRouter()
        wire_governance_router(bus, router)

        bus.publish(
            KnowledgeGapDetected(
                source_agent="analysis-pipeline",
                domain="ai_engineering",
                gap_description="Missing RAG patterns",
                requesting_agent="coder",
            )
        )

        assert len(router.routed_events) == 1
        assert router.routed_events[0].domain == "ai_engineering"

    def test_unsubscribe_stops_routing(self) -> None:
        bus = InMemoryEventBus()
        router = FakeRouter()
        sub_id = wire_governance_router(bus, router)

        bus.unsubscribe(sub_id)
        bus.publish(
            KnowledgeGapDetected(
                source_agent="test",
                domain="dev",
                gap_description="gap",
            )
        )

        assert len(router.routed_events) == 0

    def test_multiple_events_all_routed(self) -> None:
        bus = InMemoryEventBus()
        router = FakeRouter()
        wire_governance_router(bus, router)

        for domain in ["ai_engineering", "sprint_planning", "python_architecture"]:
            bus.publish(
                KnowledgeGapDetected(
                    source_agent="test",
                    domain=domain,
                    gap_description=f"Gap in {domain}",
                )
            )

        assert len(router.routed_events) == 3


# ---------------------------------------------------------------------------
# produce_from_knowledge
# ---------------------------------------------------------------------------


class FakeDocumentService:
    """Fake DocumentService voor tests."""

    def __init__(self):
        self.produce_calls: list[object] = []

    def produce(self, request):
        self.produce_calls.append(request)
        return FakeProductionResult(
            storage_path=f"DevHub/knowledge/{request.category.value}/test.md",
            category=request.category.value,
        )


class FakeProductionResult:
    def __init__(self, storage_path: str = "", category: str = ""):
        self.storage_path = storage_path
        self.category = category


class TestProduceFromKnowledge:
    def test_builds_correct_request(self) -> None:
        doc_svc = FakeDocumentService()
        produce_from_knowledge(doc_svc, domain="ai_engineering", category="sota_review")

        assert len(doc_svc.produce_calls) == 1
        req = doc_svc.produce_calls[0]
        assert req.knowledge_query == "ai_engineering"
        assert req.category.value == "sota_review"
        assert req.target_node == "devhub"

    def test_custom_node_id(self) -> None:
        doc_svc = FakeDocumentService()
        produce_from_knowledge(
            doc_svc, domain="testing_qa", category="best_practice", node_id="boris-buurts"
        )

        req = doc_svc.produce_calls[0]
        assert req.target_node == "boris-buurts"

    def test_returns_production_result(self) -> None:
        doc_svc = FakeDocumentService()
        result = produce_from_knowledge(doc_svc, domain="ai_engineering", category="sota_review")

        assert result is not None
        assert result.category == "sota_review"


# ---------------------------------------------------------------------------
# wire_knowledge_to_docs
# ---------------------------------------------------------------------------


class TestWireKnowledgeToDocs:
    def test_ingested_event_triggers_document_production(self) -> None:
        bus = InMemoryEventBus()
        doc_svc = FakeDocumentService()
        wire_knowledge_to_docs(bus, doc_svc)

        bus.publish(
            KnowledgeIngested(
                source_agent="knowledge-ingestor",
                article_id="ART-001",
                domain="ai_engineering",
                chunk_count=5,
                grade="SILVER",
            )
        )

        assert len(doc_svc.produce_calls) == 1
        req = doc_svc.produce_calls[0]
        assert req.knowledge_query == "ai_engineering"
        assert req.category.value == "sota_review"

    def test_custom_categories(self) -> None:
        bus = InMemoryEventBus()
        doc_svc = FakeDocumentService()
        wire_knowledge_to_docs(bus, doc_svc, auto_produce_categories=("explanation", "reference"))

        bus.publish(
            KnowledgeIngested(
                source_agent="knowledge-ingestor",
                article_id="ART-002",
                domain="python_architecture",
                chunk_count=3,
                grade="BRONZE",
            )
        )

        assert len(doc_svc.produce_calls) == 2
        categories = {req.category.value for req in doc_svc.produce_calls}
        assert categories == {"explanation", "reference"}

    def test_unsubscribe_stops_production(self) -> None:
        bus = InMemoryEventBus()
        doc_svc = FakeDocumentService()
        sub_id = wire_knowledge_to_docs(bus, doc_svc)

        bus.unsubscribe(sub_id)
        bus.publish(
            KnowledgeIngested(
                source_agent="test",
                article_id="ART-003",
                domain="ai_engineering",
                chunk_count=1,
                grade="BRONZE",
            )
        )

        assert len(doc_svc.produce_calls) == 0

    def test_production_failure_does_not_crash(self) -> None:
        """DocumentService.produce() kan falen — moet niet de event bus crashen."""
        bus = InMemoryEventBus()

        class FailingDocService:
            def produce(self, request):
                raise ValueError("Category not allowed")

        wire_knowledge_to_docs(bus, FailingDocService())

        # Should not raise
        bus.publish(
            KnowledgeIngested(
                source_agent="test",
                article_id="ART-004",
                domain="invalid_domain",
                chunk_count=1,
                grade="SPECULATIVE",
            )
        )


# ---------------------------------------------------------------------------
# Contract export verificatie
# ---------------------------------------------------------------------------


class TestContractExports:
    def test_new_events_are_exported(self) -> None:
        from devhub_core.contracts import (
            DocumentPublished,
            KnowledgeIngested,
            ResearchCompleted,
            ResearchProposal,
        )

        assert DocumentPublished is not None
        assert KnowledgeIngested is not None
        assert ResearchCompleted is not None
        assert ResearchProposal is not None

    def test_new_events_in_all(self) -> None:
        import devhub_core.contracts as contracts

        for name in [
            "DocumentPublished",
            "KnowledgeIngested",
            "ResearchCompleted",
            "ResearchProposal",
        ]:
            assert name in contracts.__all__, f"{name} not in __all__"
