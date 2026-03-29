"""Tests voor Research Queue en Event Listener."""

from pathlib import Path

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.research_queue import (
    RequestStatus,
    ResearchQueueItem,
    ResearchQueueManager,
)


def _make_config(tmp_path: Path) -> DashboardConfig:
    return DashboardConfig(devhub_root=tmp_path)


class TestResearchQueueItem:
    def test_roundtrip_dict(self):
        item = ResearchQueueItem(
            item_id="abc123",
            stream="user",
            status="pending",
            topic="NiceGUI performance",
            domain="python_architecture",
            depth="STANDARD",
        )
        data = item.to_dict()
        restored = ResearchQueueItem.from_dict(data)
        assert restored.item_id == "abc123"
        assert restored.topic == "NiceGUI performance"

    def test_from_dict_ignores_extra_keys(self):
        data = {
            "item_id": "x",
            "stream": "agent",
            "status": "pending",
            "topic": "test",
            "domain": "ai",
            "unknown_field": "ignored",
        }
        item = ResearchQueueItem.from_dict(data)
        assert item.item_id == "x"


class TestResearchQueueManager:
    def test_create_user_request(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(
            topic="Test topic",
            domain="ai_engineering",
            depth="DEEP",
        )
        assert item.stream == "user"
        assert item.status == "pending"
        assert item.topic == "Test topic"
        assert item.depth == "DEEP"

    def test_create_agent_proposal(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_agent_proposal(
            topic="Knowledge gap",
            domain="security_appsec",
            source_agent="qa_agent",
            description="Detected missing coverage",
            priority=8,
        )
        assert item.stream == "agent"
        assert item.source_agent == "qa_agent"
        assert item.priority == 8

    def test_list_items_empty(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        assert mgr.list_items() == []

    def test_list_items_with_filter(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        mgr.create_user_request(topic="A", domain="ai")
        mgr.create_agent_proposal(topic="B", domain="sec", source_agent="qa")

        user_items = mgr.list_items(stream="user")
        assert len(user_items) == 1
        assert user_items[0].topic == "A"

        agent_items = mgr.list_items(stream="agent")
        assert len(agent_items) == 1
        assert agent_items[0].topic == "B"

    def test_update_status(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="X", domain="ai")

        success = mgr.update_status(item.item_id, RequestStatus.APPROVED)
        assert success is True

        updated = mgr.get_item(item.item_id)
        assert updated is not None
        assert updated.status == "approved"

    def test_update_status_nonexistent(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        assert mgr.update_status("nonexistent", RequestStatus.APPROVED) is False

    def test_get_item(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Z", domain="testing")

        retrieved = mgr.get_item(item.item_id)
        assert retrieved is not None
        assert retrieved.topic == "Z"

    def test_get_item_nonexistent(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        assert mgr.get_item("nope") is None

    def test_list_items_status_filter(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="T", domain="ai")
        mgr.update_status(item.item_id, RequestStatus.APPROVED)

        pending = mgr.list_items(status="pending")
        assert len(pending) == 0

        approved = mgr.list_items(status="approved")
        assert len(approved) == 1


class TestResearchQueueItemV2:
    """v2 velden: backwards-compat, list defaults, status history."""

    def test_v2_fields_have_defaults(self):
        item = ResearchQueueItem(
            item_id="v2test",
            stream="user",
            status="pending",
            topic="Test",
            domain="ai",
        )
        assert item.background == ""
        assert item.research_questions == []
        assert item.scope_in == ""
        assert item.scope_out == ""
        assert item.expected_grade == ""
        assert item.related_articles == []
        assert item.deadline == ""
        assert item.status_history == []

    def test_v2_fields_roundtrip(self):
        item = ResearchQueueItem(
            item_id="v2rt",
            stream="user",
            status="pending",
            topic="Test",
            domain="ai",
            background="Waarom dit onderzoek?",
            research_questions=["RQ1: Hoe werkt X?", "RQ2: Waarom Y?"],
            scope_in="Alleen Python packages",
            scope_out="Geen JavaScript",
            expected_grade="SILVER",
            related_articles=["RESEARCH_AGENT_TEAMS"],
            deadline="2026-04-01",
        )
        data = item.to_dict()
        restored = ResearchQueueItem.from_dict(data)
        assert restored.background == "Waarom dit onderzoek?"
        assert len(restored.research_questions) == 2
        assert restored.scope_in == "Alleen Python packages"
        assert restored.expected_grade == "SILVER"
        assert restored.deadline == "2026-04-01"

    def test_v1_data_loads_with_v2_defaults(self):
        """Bestaande v1 JSON-data zonder v2 velden moet laden."""
        v1_data = {
            "item_id": "old",
            "stream": "user",
            "status": "pending",
            "topic": "Old Topic",
            "domain": "ai",
            "depth": "STANDARD",
        }
        item = ResearchQueueItem.from_dict(v1_data)
        assert item.background == ""
        assert item.research_questions == []
        assert item.status_history == []

    def test_none_list_fields_become_empty_lists(self):
        data = {
            "item_id": "null",
            "stream": "user",
            "status": "pending",
            "topic": "Test",
            "domain": "ai",
            "research_questions": None,
            "related_articles": None,
            "completed_articles": None,
            "status_history": None,
        }
        item = ResearchQueueItem.from_dict(data)
        assert item.research_questions == []
        assert item.related_articles == []
        assert item.completed_articles == []
        assert item.status_history == []

    def test_review_status_exists(self):
        assert RequestStatus.REVIEW.value == "review"


class TestStatusHistory:
    """Status-history tracking bij update_status."""

    def test_status_change_records_history(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Hist", domain="ai")

        mgr.update_status(item.item_id, RequestStatus.APPROVED)
        updated = mgr.get_item(item.item_id)
        assert updated is not None
        assert len(updated.status_history) == 1
        assert updated.status_history[0]["status"] == "approved"
        assert "timestamp" in updated.status_history[0]
        assert updated.status_history[0]["actor"] == "niels"

    def test_multiple_status_changes_accumulate(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Multi", domain="ai")

        mgr.update_status(item.item_id, RequestStatus.APPROVED)
        mgr.update_status(item.item_id, RequestStatus.IN_PROGRESS)
        mgr.update_status(item.item_id, RequestStatus.REVIEW)
        mgr.update_status(item.item_id, RequestStatus.COMPLETED)

        updated = mgr.get_item(item.item_id)
        assert updated is not None
        assert len(updated.status_history) == 4
        statuses = [h["status"] for h in updated.status_history]
        assert statuses == ["approved", "in_progress", "review", "completed"]

    def test_status_history_with_custom_actor(self, tmp_path: Path):
        mgr = ResearchQueueManager(_make_config(tmp_path))
        item = mgr.create_user_request(topic="Actor", domain="ai")

        mgr.update_status(item.item_id, RequestStatus.APPROVED, actor="qa_agent")
        updated = mgr.get_item(item.item_id)
        assert updated is not None
        assert updated.status_history[0]["actor"] == "qa_agent"
