"""Tests voor event_contracts.py — Event Bus contracts en typed events."""

import pytest

from devhub_core.contracts.curator_contracts import ObservationType
from devhub_core.contracts.dev_contracts import (
    DevTaskResult,
    DocGenRequest,
    QAReport,
)
from devhub_core.contracts.event_contracts import (
    DocGenRequested,
    Event,
    EventBusInterface,
    EventFilter,
    EventHandler,
    EventLoopError,
    HealthDegraded,
    KnowledgeGapDetected,
    ObservationEmitted,
    QACompleted,
    SprintClosed,
    SprintStarted,
    TaskAssigned,
    TaskCompleted,
    TaskFailed,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(task_id: str = "T-001") -> DevTaskResult:
    return DevTaskResult(task_id=task_id, files_changed=["a.py"], tests_added=3)


def _make_doc_request(task_id: str = "T-001") -> DocGenRequest:
    return DocGenRequest(
        task_id=task_id,
        target_files=["docs/ref.md"],
        diataxis_category="reference",
        audience="developer",
    )


def _make_qa_report(task_id: str = "T-001") -> QAReport:
    return QAReport(task_id=task_id)


# ---------------------------------------------------------------------------
# Event base class
# ---------------------------------------------------------------------------


class TestEvent:
    def test_event_creation(self) -> None:
        evt = Event(source_agent="test-agent")
        assert evt.source_agent == "test-agent"
        assert evt.event_id  # auto-generated uuid
        assert evt.timestamp  # auto-generated ISO timestamp

    def test_event_auto_id_unique(self) -> None:
        e1 = Event(source_agent="a")
        e2 = Event(source_agent="a")
        assert e1.event_id != e2.event_id

    def test_event_is_frozen(self) -> None:
        evt = Event(source_agent="test")
        with pytest.raises(AttributeError):
            evt.source_agent = "other"  # type: ignore[misc]

    def test_event_requires_source_agent(self) -> None:
        with pytest.raises(ValueError, match="source_agent"):
            Event(source_agent="")

    def test_event_explicit_id_and_timestamp(self) -> None:
        evt = Event(
            source_agent="test",
            event_id="custom-id",
            timestamp="2026-01-01T00:00:00+00:00",
        )
        assert evt.event_id == "custom-id"
        assert evt.timestamp == "2026-01-01T00:00:00+00:00"


# ---------------------------------------------------------------------------
# Sprint lifecycle events
# ---------------------------------------------------------------------------


class TestSprintStarted:
    def test_creation(self) -> None:
        evt = SprintStarted(
            source_agent="sprint-skill",
            sprint_id="SPRINT_41",
            node_id="devhub",
            sprint_type="FEAT",
        )
        assert evt.sprint_id == "SPRINT_41"
        assert evt.node_id == "devhub"
        assert evt.sprint_type == "FEAT"
        assert isinstance(evt, Event)

    def test_requires_sprint_id(self) -> None:
        with pytest.raises(ValueError, match="sprint_id"):
            SprintStarted(source_agent="test", node_id="devhub")

    def test_requires_node_id(self) -> None:
        with pytest.raises(ValueError, match="node_id"):
            SprintStarted(source_agent="test", sprint_id="S1")


class TestSprintClosed:
    def test_creation_without_result(self) -> None:
        evt = SprintClosed(
            source_agent="sprint-skill",
            sprint_id="SPRINT_41",
            node_id="devhub",
        )
        assert evt.result is None

    def test_creation_with_result(self) -> None:
        result = _make_result()
        evt = SprintClosed(
            source_agent="sprint-skill",
            sprint_id="SPRINT_41",
            node_id="devhub",
            result=result,
        )
        assert evt.result is result

    def test_requires_sprint_id(self) -> None:
        with pytest.raises(ValueError, match="sprint_id"):
            SprintClosed(source_agent="test", node_id="devhub")

    def test_requires_node_id(self) -> None:
        with pytest.raises(ValueError, match="node_id"):
            SprintClosed(source_agent="test", sprint_id="S1")


# ---------------------------------------------------------------------------
# Agent lifecycle events
# ---------------------------------------------------------------------------


class TestTaskAssigned:
    def test_creation(self) -> None:
        evt = TaskAssigned(
            source_agent="orchestrator",
            task_id="T-001",
            agent_id="coder",
            description="Implementeer feature X",
        )
        assert evt.task_id == "T-001"
        assert evt.agent_id == "coder"
        assert evt.description == "Implementeer feature X"

    def test_requires_task_id(self) -> None:
        with pytest.raises(ValueError, match="task_id"):
            TaskAssigned(source_agent="test")


class TestTaskCompleted:
    def test_creation_with_result(self) -> None:
        result = _make_result()
        evt = TaskCompleted(
            source_agent="coder",
            task_id="T-001",
            agent_id="coder",
            result=result,
        )
        assert evt.result is result

    def test_creation_without_result(self) -> None:
        evt = TaskCompleted(
            source_agent="coder",
            task_id="T-001",
            agent_id="coder",
        )
        assert evt.result is None

    def test_requires_task_id(self) -> None:
        with pytest.raises(ValueError, match="task_id"):
            TaskCompleted(source_agent="test")


class TestTaskFailed:
    def test_creation(self) -> None:
        evt = TaskFailed(
            source_agent="coder",
            task_id="T-001",
            agent_id="coder",
            error="ImportError: module not found",
        )
        assert evt.error == "ImportError: module not found"

    def test_requires_task_id(self) -> None:
        with pytest.raises(ValueError, match="task_id"):
            TaskFailed(source_agent="test")


class TestQACompleted:
    def test_creation(self) -> None:
        report = _make_qa_report()
        evt = QACompleted(
            source_agent="qa-agent",
            task_id="T-001",
            report=report,
        )
        assert evt.report is report

    def test_requires_task_id(self) -> None:
        with pytest.raises(ValueError, match="task_id"):
            QACompleted(source_agent="test")


class TestDocGenRequested:
    def test_creation(self) -> None:
        req = _make_doc_request()
        evt = DocGenRequested(
            source_agent="orchestrator",
            request=req,
        )
        assert evt.request is req

    def test_requires_request(self) -> None:
        with pytest.raises(ValueError, match="request"):
            DocGenRequested(source_agent="test")


# ---------------------------------------------------------------------------
# Knowledge pipeline events
# ---------------------------------------------------------------------------


class TestKnowledgeGapDetected:
    def test_creation(self) -> None:
        evt = KnowledgeGapDetected(
            source_agent="analysis-pipeline",
            domain="ai_engineering",
            gap_description="Geen artikelen over event-driven architectuur",
            requesting_agent="researcher",
        )
        assert evt.domain == "ai_engineering"
        assert evt.gap_description == "Geen artikelen over event-driven architectuur"

    def test_requires_domain(self) -> None:
        with pytest.raises(ValueError, match="domain"):
            KnowledgeGapDetected(
                source_agent="test",
                gap_description="gap",
            )

    def test_requires_gap_description(self) -> None:
        with pytest.raises(ValueError, match="gap_description"):
            KnowledgeGapDetected(
                source_agent="test",
                domain="ai_engineering",
            )


class TestHealthDegraded:
    def test_creation(self) -> None:
        evt = HealthDegraded(
            source_agent="health-checker",
            dimension="test_coverage",
            score=0.65,
            threshold=0.80,
        )
        assert evt.score == 0.65
        assert evt.threshold == 0.80

    def test_requires_dimension(self) -> None:
        with pytest.raises(ValueError, match="dimension"):
            HealthDegraded(source_agent="test", score=0.5, threshold=0.8)


class TestObservationEmitted:
    def test_creation(self) -> None:
        evt = ObservationEmitted(
            source_agent="analysis-pipeline",
            obs_type=ObservationType.ANALYSIS_COMPLETED,
            payload="Analysis done for request R-001",
            severity="INFO",
        )
        assert evt.obs_type == ObservationType.ANALYSIS_COMPLETED
        assert evt.severity == "INFO"

    def test_requires_obs_type(self) -> None:
        with pytest.raises(ValueError, match="obs_type"):
            ObservationEmitted(source_agent="test", payload="x")

    def test_default_severity(self) -> None:
        evt = ObservationEmitted(
            source_agent="test",
            obs_type=ObservationType.HEALTH_DEGRADED,
        )
        assert evt.severity == "INFO"


# ---------------------------------------------------------------------------
# Subclass relationships
# ---------------------------------------------------------------------------


class TestEventHierarchy:
    def test_all_events_are_event_subclass(self) -> None:
        event_types = [
            SprintStarted,
            SprintClosed,
            TaskAssigned,
            TaskCompleted,
            TaskFailed,
            QACompleted,
            DocGenRequested,
            KnowledgeGapDetected,
            HealthDegraded,
            ObservationEmitted,
        ]
        for cls in event_types:
            assert issubclass(cls, Event), f"{cls.__name__} is not an Event subclass"

    def test_event_count(self) -> None:
        """Verificatie dat we precies 10 event types hebben (v1 limiet)."""
        from devhub_core.contracts import event_contracts

        event_classes = [
            obj
            for name, obj in vars(event_contracts).items()
            if isinstance(obj, type) and issubclass(obj, Event) and obj is not Event
        ]
        assert len(event_classes) == 10


# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------


class TestSupportingTypes:
    def test_event_handler_is_callable_type(self) -> None:
        def handler(event: Event) -> None:
            pass

        # EventHandler is just a type alias, verify it's usable
        h: EventHandler = handler
        assert callable(h)

    def test_event_filter_is_callable_type(self) -> None:
        def f(event: Event) -> bool:
            return True

        flt: EventFilter = f
        assert callable(flt)

    def test_event_loop_error_is_exception(self) -> None:
        assert issubclass(EventLoopError, Exception)
        with pytest.raises(EventLoopError):
            raise EventLoopError("max depth exceeded")

    def test_event_bus_interface_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            EventBusInterface()  # type: ignore[abstract]
