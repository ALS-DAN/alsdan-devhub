"""
ResearchProposalQueue — YAML-backed queue voor Stroom 2 governance.

Beheert research-voorstellen die menselijke goedkeuring vereisen (Art. 1).
Dashboard leest/schrijft config/research_queue.yml direct.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from devhub_core.contracts.pipeline_contracts import ProposalStatus, ResearchProposal


class ResearchProposalQueue:
    """YAML-backed queue voor research-voorstellen.

    Args:
        queue_path: Pad naar het YAML-bestand (default: config/research_queue.yml).
    """

    def __init__(self, queue_path: Path) -> None:
        self._path = queue_path
        self._ensure_file()

    def submit(self, proposal: ResearchProposal) -> str:
        """Voeg een voorstel toe aan de queue. Retourneert proposal_id."""
        proposals = self._load()
        proposals.append(proposal)
        self._save(proposals)
        return proposal.proposal_id

    def pending(self) -> list[ResearchProposal]:
        """Retourneer alle voorstellen met status PENDING."""
        return [p for p in self._load() if p.status == ProposalStatus.PENDING]

    def approved(self) -> list[ResearchProposal]:
        """Retourneer alle voorstellen met status APPROVED."""
        return [p for p in self._load() if p.status == ProposalStatus.APPROVED]

    def get(self, proposal_id: str) -> ResearchProposal | None:
        """Zoek een voorstel op ID."""
        for p in self._load():
            if p.proposal_id == proposal_id:
                return p
        return None

    def all(self) -> list[ResearchProposal]:
        """Retourneer alle voorstellen."""
        return self._load()

    def approve(self, proposal_id: str) -> bool:
        """Keur een voorstel goed. Retourneert True als gevonden."""
        return self._update_status(
            proposal_id,
            ProposalStatus.APPROVED,
            approved_at=datetime.now(UTC).isoformat(),
        )

    def reject(self, proposal_id: str) -> bool:
        """Wijs een voorstel af. Retourneert True als gevonden."""
        return self._update_status(proposal_id, ProposalStatus.REJECTED)

    def start(self, proposal_id: str) -> bool:
        """Markeer een voorstel als IN_PROGRESS."""
        return self._update_status(proposal_id, ProposalStatus.IN_PROGRESS)

    def complete(self, proposal_id: str) -> bool:
        """Markeer een voorstel als COMPLETED."""
        return self._update_status(
            proposal_id,
            ProposalStatus.COMPLETED,
            completed_at=datetime.now(UTC).isoformat(),
        )

    def _update_status(
        self,
        proposal_id: str,
        new_status: ProposalStatus,
        **extra_fields: str,
    ) -> bool:
        """Werk de status van een voorstel bij."""
        proposals = self._load()
        for i, p in enumerate(proposals):
            if p.proposal_id == proposal_id:
                # Frozen dataclass → maak nieuw object
                updates = {"status": new_status}
                updates.update(extra_fields)
                proposals[i] = ResearchProposal(
                    topic=p.topic,
                    domain=p.domain,
                    requesting_agent=p.requesting_agent,
                    rationale=p.rationale,
                    priority=p.priority,
                    proposed_depth=p.proposed_depth,
                    stream=p.stream,
                    status=updates.get("status", p.status),
                    proposal_id=p.proposal_id,
                    created_at=p.created_at,
                    approved_at=updates.get("approved_at", p.approved_at),
                    completed_at=updates.get("completed_at", p.completed_at),
                )
                self._save(proposals)
                return True
        return False

    def _load(self) -> list[ResearchProposal]:
        """Laad proposals uit YAML."""
        if not self._path.exists():
            return []

        raw = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        if not raw or not isinstance(raw, dict):
            return []

        items = raw.get("research_queue", [])
        if not items:
            return []

        proposals: list[ResearchProposal] = []
        for item in items:
            try:
                status_str = item.get("status", "PENDING")
                status = ProposalStatus(status_str)
                proposals.append(
                    ResearchProposal(
                        topic=item["topic"],
                        domain=item["domain"],
                        requesting_agent=item.get("requesting_agent", ""),
                        rationale=item.get("rationale", ""),
                        priority=item.get("priority", 3),
                        proposed_depth=item.get("proposed_depth", "STANDARD"),
                        stream=item.get("stream", 2),
                        status=status,
                        proposal_id=item.get("proposal_id", ""),
                        created_at=item.get("created_at", ""),
                        approved_at=item.get("approved_at", "") or "",
                        completed_at=item.get("completed_at", "") or "",
                    )
                )
            except (KeyError, ValueError):
                continue  # Skip malformed entries

        return proposals

    def _save(self, proposals: list[ResearchProposal]) -> None:
        """Sla proposals op als YAML."""
        items = []
        for p in proposals:
            items.append(
                {
                    "proposal_id": p.proposal_id,
                    "topic": p.topic,
                    "domain": p.domain,
                    "requesting_agent": p.requesting_agent,
                    "rationale": p.rationale,
                    "priority": p.priority,
                    "proposed_depth": p.proposed_depth,
                    "stream": p.stream,
                    "status": p.status.value,
                    "created_at": p.created_at,
                    "approved_at": p.approved_at or None,
                    "completed_at": p.completed_at or None,
                }
            )

        data = {"research_queue": items}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def _ensure_file(self) -> None:
        """Maak het YAML-bestand aan als het niet bestaat."""
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._save([])
