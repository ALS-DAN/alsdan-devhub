"""In-memory implementatie van EventBusInterface.

Thread-safe via threading.Lock voor subscriber/history mutations.
Recursie-detectie via threading.local depth counter.
"""

from __future__ import annotations

import threading
import uuid
from collections import deque
from dataclasses import dataclass

from devhub_core.contracts.event_contracts import (
    Event,
    EventBusInterface,
    EventFilter,
    EventHandler,
    EventLoopError,
)


@dataclass
class _Subscription:
    """Interne representatie van een event-subscription."""

    subscription_id: str
    event_type: type[Event]
    handler: EventHandler
    event_filter: EventFilter | None = None


class InMemoryEventBus(EventBusInterface):
    """Thread-safe in-memory event bus voor development en testen.

    Features:
    - Pub/sub met typed events (inclusief base-class wildcard)
    - Thread-safe via Lock
    - Bounded event history via deque
    - Recursie-detectie via thread-local depth counter
    """

    def __init__(self, max_history: int = 1000, max_depth: int = 8) -> None:
        self._subscribers: dict[type[Event], list[_Subscription]] = {}
        self._history: deque[Event] = deque(maxlen=max_history)
        self._lock = threading.Lock()
        self._depth = threading.local()
        self._max_depth = max_depth

    def publish(self, event: Event) -> None:
        """Publiceer een event naar alle matching subscribers.

        Raises EventLoopError als recursie-diepte max_depth overschrijdt.
        """
        # Depth tracking (thread-local)
        if not hasattr(self._depth, "level"):
            self._depth.level = 0

        self._depth.level += 1
        try:
            if self._depth.level > self._max_depth:
                raise EventLoopError(
                    f"Event publish recursion depth {self._depth.level} "
                    f"exceeds max {self._max_depth}"
                )

            with self._lock:
                self._history.append(event)
                # Collect matching subscriptions
                matching: list[_Subscription] = []
                for event_type, subs in self._subscribers.items():
                    if isinstance(event, event_type):
                        matching.extend(subs)

            # Call handlers outside lock to prevent deadlocks
            for sub in matching:
                if sub.event_filter is None or sub.event_filter(event):
                    sub.handler(event)
        finally:
            self._depth.level -= 1

    def subscribe(
        self,
        event_type: type[Event],
        handler: EventHandler,
        event_filter: EventFilter | None = None,
    ) -> str:
        """Registreer een handler voor een event type. Retourneert subscription_id."""
        subscription_id = str(uuid.uuid4())
        sub = _Subscription(
            subscription_id=subscription_id,
            event_type=event_type,
            handler=handler,
            event_filter=event_filter,
        )
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(sub)
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> None:
        """Verwijder een subscription."""
        with self._lock:
            for event_type, subs in self._subscribers.items():
                self._subscribers[event_type] = [
                    s for s in subs if s.subscription_id != subscription_id
                ]

    def history(
        self,
        event_type: type[Event] | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Retourneer recente events, optioneel gefilterd op type."""
        with self._lock:
            events = list(self._history)

        if event_type is not None:
            events = [e for e in events if isinstance(e, event_type)]

        return events[-limit:]
