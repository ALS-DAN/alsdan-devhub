"""Tests voor de DashboardEventListener — Event Bus integratie."""

from pathlib import Path

from devhub_core.contracts.event_contracts import KnowledgeGapDetected
from devhub_core.events.in_memory_bus import InMemoryEventBus

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.event_listener import DashboardEventListener
from devhub_dashboard.data.research_queue import ResearchQueueManager


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


class TestDashboardEventListener:
    def test_knowledge_gap_creates_proposal(self, tmp_path: Path):
        bus = InMemoryEventBus()
        mgr = ResearchQueueManager(_make_config(tmp_path))
        listener = DashboardEventListener(bus, mgr)
        listener.start()

        # Publiceer een KnowledgeGapDetected event
        event = KnowledgeGapDetected(
            source_agent="qa_agent",
            domain="security_appsec",
            gap_description="Missing OWASP ASI coverage for ASI07",
            requesting_agent="qa_agent",
        )
        bus.publish(event)

        # Controleer dat er een agent-voorstel is aangemaakt
        items = mgr.list_items(stream="agent")
        assert len(items) == 1
        assert items[0].topic == "Missing OWASP ASI coverage for ASI07"
        assert items[0].domain == "security_appsec"
        assert items[0].source_agent == "qa_agent"

    def test_multiple_events(self, tmp_path: Path):
        bus = InMemoryEventBus()
        mgr = ResearchQueueManager(_make_config(tmp_path))
        listener = DashboardEventListener(bus, mgr)
        listener.start()

        for i in range(3):
            bus.publish(
                KnowledgeGapDetected(
                    source_agent="researcher",
                    domain="ai_engineering",
                    gap_description=f"Gap {i}",
                    requesting_agent="researcher",
                )
            )

        items = mgr.list_items(stream="agent")
        assert len(items) == 3

    def test_stop_unsubscribes(self, tmp_path: Path):
        bus = InMemoryEventBus()
        mgr = ResearchQueueManager(_make_config(tmp_path))
        listener = DashboardEventListener(bus, mgr)
        listener.start()
        listener.stop()

        # Na stop geen nieuwe items
        bus.publish(
            KnowledgeGapDetected(
                source_agent="test",
                domain="ai",
                gap_description="Should not appear",
                requesting_agent="test",
            )
        )

        items = mgr.list_items(stream="agent")
        assert len(items) == 0

    def test_start_stop_start(self, tmp_path: Path):
        bus = InMemoryEventBus()
        mgr = ResearchQueueManager(_make_config(tmp_path))
        listener = DashboardEventListener(bus, mgr)

        listener.start()
        listener.stop()
        listener.start()

        bus.publish(
            KnowledgeGapDetected(
                source_agent="test",
                domain="python",
                gap_description="Re-subscribed gap",
                requesting_agent="test",
            )
        )

        items = mgr.list_items(stream="agent")
        assert len(items) == 1
