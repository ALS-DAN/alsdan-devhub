"""Research Queue Manager — CRUD via LocalAdapter, status-tracking per request.

Slaat research requests op als JSON-bestanden.
Drie stromen: agent-voorstellen, Niels-verzoeken, auto-kennis log.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from devhub_dashboard.config import DashboardConfig


class RequestStatus(Enum):
    """Status van een research request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"


class RequestStream(Enum):
    """De drie stromen voor research requests."""

    AUTO = "auto"  # Stroom 1: auto-kennis (KWP DEV)
    AGENT = "agent"  # Stroom 2: agent-voorstellen
    USER = "user"  # Stroom 3: Niels-verzoeken


@dataclass
class ResearchQueueItem:
    """Een item in de research queue — v2 met uitgebreide metadata."""

    # === v1 velden (bestaand, ongewijzigd) ===
    item_id: str
    stream: str  # "auto" | "agent" | "user"
    status: str  # RequestStatus value
    topic: str
    domain: str
    depth: str = "STANDARD"  # QUICK | STANDARD | DEEP
    document_category: str = ""  # Optioneel: DocumentCategory value
    source_agent: str = ""
    priority: int = 5
    description: str = ""
    created_at: str = ""
    updated_at: str = ""

    # === v2 velden (nieuw, alle met defaults voor backwards-compat) ===
    background: str = ""  # Motivatie/achtergrond
    research_questions: list[str] = field(default_factory=list)
    scope_in: str = ""  # Wat valt erin
    scope_out: str = ""  # Wat valt erbuiten
    expected_grade: str = ""  # Verwacht EVIDENCE-niveau
    related_articles: list[str] = field(default_factory=list)
    deadline: str = ""  # Optionele deadline (ISO 8601)
    rejection_reason: str = ""  # Reden bij REJECTED status
    completed_articles: list[str] = field(default_factory=list)
    review_notes: str = ""  # Opmerkingen bij REVIEW status
    status_history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ResearchQueueItem:
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        # Zorg dat list-velden altijd list zijn, niet None
        for list_field in (
            "research_questions",
            "related_articles",
            "completed_articles",
            "status_history",
        ):
            if list_field in filtered and filtered[list_field] is None:
                filtered[list_field] = []
        return cls(**filtered)


class ResearchQueueManager:
    """Beheert de research queue op disk via JSON-bestanden."""

    def __init__(self, config: DashboardConfig) -> None:
        self._dir = config.devhub_root / "data" / "research_queue"

    def _ensure_dir(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)

    def add_item(self, item: ResearchQueueItem) -> Path:
        """Voeg een item toe aan de queue."""
        self._ensure_dir()
        if not item.created_at:
            item.created_at = datetime.now(UTC).isoformat()
        item.updated_at = datetime.now(UTC).isoformat()
        path = self._dir / f"{item.item_id}.json"
        path.write_text(json.dumps(item.to_dict(), indent=2), encoding="utf-8")
        return path

    def create_user_request(
        self,
        topic: str,
        domain: str,
        depth: str = "STANDARD",
        document_category: str = "",
    ) -> ResearchQueueItem:
        """Maak een nieuw Niels-verzoek (stroom 3)."""
        item = ResearchQueueItem(
            item_id=str(uuid.uuid4())[:8],
            stream=RequestStream.USER.value,
            status=RequestStatus.PENDING.value,
            topic=topic,
            domain=domain,
            depth=depth,
            document_category=document_category,
            source_agent="niels",
            created_at=datetime.now(UTC).isoformat(),
        )
        self.add_item(item)
        return item

    def create_agent_proposal(
        self,
        topic: str,
        domain: str,
        source_agent: str,
        description: str = "",
        priority: int = 5,
    ) -> ResearchQueueItem:
        """Maak een agent-voorstel (stroom 2) vanuit een KnowledgeGapDetected event."""
        item = ResearchQueueItem(
            item_id=str(uuid.uuid4())[:8],
            stream=RequestStream.AGENT.value,
            status=RequestStatus.PENDING.value,
            topic=topic,
            domain=domain,
            source_agent=source_agent,
            description=description,
            priority=priority,
            created_at=datetime.now(UTC).isoformat(),
        )
        self.add_item(item)
        return item

    def update_status(
        self, item_id: str, new_status: RequestStatus, *, actor: str = "niels"
    ) -> bool:
        """Wijzig de status van een item met history tracking."""
        path = self._dir / f"{item_id}.json"
        if not path.exists():
            return False

        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = new_status.value
        data["updated_at"] = datetime.now(UTC).isoformat()

        # Status-history tracking
        history = data.get("status_history") or []
        history.append(
            {
                "status": new_status.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "actor": actor,
            }
        )
        data["status_history"] = history

        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def list_items(
        self,
        stream: str | None = None,
        status: str | None = None,
    ) -> list[ResearchQueueItem]:
        """Lijst alle items, optioneel gefilterd op stream en/of status."""
        if not self._dir.exists():
            return []

        items = []
        for path in sorted(self._dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                item = ResearchQueueItem.from_dict(data)
                if stream and item.stream != stream:
                    continue
                if status and item.status != status:
                    continue
                items.append(item)
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
        return items

    def get_item(self, item_id: str) -> ResearchQueueItem | None:
        """Haal een specifiek item op."""
        path = self._dir / f"{item_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ResearchQueueItem.from_dict(data)
        except (json.JSONDecodeError, TypeError, KeyError):
            return None
