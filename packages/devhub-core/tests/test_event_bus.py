"""Tests voor InMemoryEventBus — pub/sub, filtering, history, thread-safety."""

import threading

import pytest

from devhub_core.contracts.event_contracts import (
    Event,
    EventLoopError,
    SprintStarted,
    TaskCompleted,
)
from devhub_core.events.in_memory_bus import InMemoryEventBus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sprint_started(sprint_id: str = "S1") -> SprintStarted:
    return SprintStarted(
        source_agent="test",
        sprint_id=sprint_id,
        node_id="devhub",
        sprint_type="FEAT",
    )


def _make_task_completed(task_id: str = "T1") -> TaskCompleted:
    return TaskCompleted(
        source_agent="test",
        task_id=task_id,
        agent_id="coder",
    )


# ---------------------------------------------------------------------------
# Publish / Subscribe basics
# ---------------------------------------------------------------------------


class TestPublishSubscribe:
    def test_handler_receives_published_event(self) -> None:
        bus = InMemoryEventBus()
        received: list[Event] = []
        bus.subscribe(SprintStarted, received.append)

        evt = _make_sprint_started()
        bus.publish(evt)

        assert len(received) == 1
        assert received[0] is evt

    def test_handler_not_called_for_wrong_type(self) -> None:
        bus = InMemoryEventBus()
        received: list[Event] = []
        bus.subscribe(SprintStarted, received.append)

        bus.publish(_make_task_completed())

        assert len(received) == 0

    def test_multiple_subscribers_same_type(self) -> None:
        bus = InMemoryEventBus()
        r1: list[Event] = []
        r2: list[Event] = []
        bus.subscribe(SprintStarted, r1.append)
        bus.subscribe(SprintStarted, r2.append)

        bus.publish(_make_sprint_started())

        assert len(r1) == 1
        assert len(r2) == 1

    def test_multiple_event_types(self) -> None:
        bus = InMemoryEventBus()
        starts: list[Event] = []
        tasks: list[Event] = []
        bus.subscribe(SprintStarted, starts.append)
        bus.subscribe(TaskCompleted, tasks.append)

        bus.publish(_make_sprint_started())
        bus.publish(_make_task_completed())

        assert len(starts) == 1
        assert len(tasks) == 1

    def test_base_class_wildcard_subscribe(self) -> None:
        bus = InMemoryEventBus()
        all_events: list[Event] = []
        bus.subscribe(Event, all_events.append)

        bus.publish(_make_sprint_started())
        bus.publish(_make_task_completed())

        assert len(all_events) == 2


# ---------------------------------------------------------------------------
# Unsubscribe
# ---------------------------------------------------------------------------


class TestUnsubscribe:
    def test_unsubscribe_stops_delivery(self) -> None:
        bus = InMemoryEventBus()
        received: list[Event] = []
        sub_id = bus.subscribe(SprintStarted, received.append)

        bus.publish(_make_sprint_started())
        assert len(received) == 1

        bus.unsubscribe(sub_id)
        bus.publish(_make_sprint_started("S2"))
        assert len(received) == 1  # no new events

    def test_unsubscribe_unknown_id_is_noop(self) -> None:
        bus = InMemoryEventBus()
        bus.unsubscribe("nonexistent-id")  # should not raise


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


class TestFiltering:
    def test_filter_accepts_matching_events(self) -> None:
        bus = InMemoryEventBus()
        received: list[Event] = []

        bus.subscribe(
            SprintStarted,
            received.append,
            event_filter=lambda e: isinstance(e, SprintStarted) and e.node_id == "devhub",
        )

        bus.publish(_make_sprint_started())
        assert len(received) == 1

    def test_filter_rejects_non_matching_events(self) -> None:
        bus = InMemoryEventBus()
        received: list[Event] = []

        bus.subscribe(
            SprintStarted,
            received.append,
            event_filter=lambda e: isinstance(e, SprintStarted) and e.node_id == "boris",
        )

        bus.publish(_make_sprint_started())  # node_id=devhub
        assert len(received) == 0


# ---------------------------------------------------------------------------
# Event History
# ---------------------------------------------------------------------------


class TestHistory:
    def test_history_records_published_events(self) -> None:
        bus = InMemoryEventBus()
        bus.publish(_make_sprint_started("S1"))
        bus.publish(_make_sprint_started("S2"))

        history = bus.history()
        assert len(history) == 2

    def test_history_filtered_by_type(self) -> None:
        bus = InMemoryEventBus()
        bus.publish(_make_sprint_started())
        bus.publish(_make_task_completed())

        history = bus.history(event_type=SprintStarted)
        assert len(history) == 1
        assert isinstance(history[0], SprintStarted)

    def test_history_limit(self) -> None:
        bus = InMemoryEventBus()
        for i in range(10):
            bus.publish(_make_sprint_started(f"S{i}"))

        history = bus.history(limit=3)
        assert len(history) == 3
        # Should be last 3 events
        assert isinstance(history[0], SprintStarted)

    def test_history_bounded_by_max_history(self) -> None:
        bus = InMemoryEventBus(max_history=5)
        for i in range(10):
            bus.publish(_make_sprint_started(f"S{i}"))

        history = bus.history()
        assert len(history) == 5

    def test_history_returns_copy(self) -> None:
        bus = InMemoryEventBus()
        bus.publish(_make_sprint_started())
        h1 = bus.history()
        h2 = bus.history()
        assert h1 is not h2


# ---------------------------------------------------------------------------
# Event Loop Detection
# ---------------------------------------------------------------------------


class TestEventLoopDetection:
    def test_direct_recursion_raises_event_loop_error(self) -> None:
        bus = InMemoryEventBus(max_depth=3)

        def recursive_handler(event: Event) -> None:
            bus.publish(_make_sprint_started("recursive"))

        bus.subscribe(SprintStarted, recursive_handler)

        with pytest.raises(EventLoopError, match="exceeds max 3"):
            bus.publish(_make_sprint_started())

    def test_no_error_within_depth_limit(self) -> None:
        bus = InMemoryEventBus(max_depth=3)
        counter = {"value": 0}

        def handler(event: Event) -> None:
            counter["value"] += 1
            if counter["value"] < 3:
                bus.publish(_make_task_completed(f"T{counter['value']}"))

        bus.subscribe(SprintStarted, handler)
        bus.subscribe(TaskCompleted, handler)

        bus.publish(_make_sprint_started())
        assert counter["value"] == 3


# ---------------------------------------------------------------------------
# Thread Safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_publish(self) -> None:
        bus = InMemoryEventBus()
        received: list[Event] = []
        lock = threading.Lock()

        def safe_append(event: Event) -> None:
            with lock:
                received.append(event)

        bus.subscribe(SprintStarted, safe_append)

        threads = []
        for i in range(10):
            t = threading.Thread(
                target=bus.publish,
                args=(_make_sprint_started(f"S{i}"),),
            )
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(received) == 10
        assert len(bus.history()) == 10

    def test_concurrent_subscribe_unsubscribe(self) -> None:
        bus = InMemoryEventBus()
        sub_ids: list[str] = []
        lock = threading.Lock()

        def subscribe_and_record() -> None:
            sid = bus.subscribe(SprintStarted, lambda e: None)
            with lock:
                sub_ids.append(sid)

        threads = [threading.Thread(target=subscribe_and_record) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(sub_ids) == 10

        # Unsubscribe all concurrently
        threads = [threading.Thread(target=bus.unsubscribe, args=(sid,)) for sid in sub_ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_depth_counter_is_thread_local(self) -> None:
        """Verify depth counter doesn't leak between threads."""
        bus = InMemoryEventBus(max_depth=2)
        results: list[bool] = []
        lock = threading.Lock()

        def thread_publish() -> None:
            try:
                bus.publish(_make_sprint_started())
                with lock:
                    results.append(True)
            except EventLoopError:
                with lock:
                    results.append(False)

        threads = [threading.Thread(target=thread_publish) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed (depth=1, max=2) — no cross-thread leaking
        assert all(results)
        assert len(results) == 5
