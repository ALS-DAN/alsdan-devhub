"""Tests voor event bus integraties — AnalysisPipeline, DevOrchestrator, wiring helpers."""

from devhub_core.contracts.curator_contracts import ObservationType
from devhub_core.contracts.event_contracts import (
    DocGenRequested,
    Event,
    KnowledgeGapDetected,
    ObservationEmitted,
    SprintClosed,
    TaskAssigned,
    TaskCompleted,
)
from devhub_core.events.in_memory_bus import InMemoryEventBus
from devhub_core.events.integrations import (
    wire_knowledge_pipeline,
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
