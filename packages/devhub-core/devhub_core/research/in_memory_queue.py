"""In-memory implementatie van ResearchQueue."""

from __future__ import annotations

from devhub_core.contracts.research_contracts import (
    ResearchQueue,
    ResearchRequest,
    ResearchResponse,
)


class InMemoryResearchQueue(ResearchQueue):
    """Thread-unsafe in-memory research queue voor development en testen."""

    def __init__(self) -> None:
        self._requests: list[ResearchRequest] = []
        self._responses: dict[str, ResearchResponse] = {}

    def submit(self, request: ResearchRequest) -> str:
        """Submit een research-opdracht. Retourneert request_id."""
        self._requests.append(request)
        return request.request_id

    def next(self) -> ResearchRequest | None:
        """Retourneert de hoogste-prioriteit PENDING opdracht, of None."""
        pending = [r for r in self._requests if r.request_id not in self._responses]
        if not pending:
            return None
        return min(pending, key=lambda r: r.priority)

    def complete(self, request_id: str, response: ResearchResponse) -> None:
        """Markeer een opdracht als afgerond met response."""
        if not any(r.request_id == request_id for r in self._requests):
            raise ValueError(f"Unknown request_id: {request_id}")
        self._responses[request_id] = response

    def pending(self) -> list[ResearchRequest]:
        """Retourneert alle PENDING opdrachten."""
        return [r for r in self._requests if r.request_id not in self._responses]

    def by_agent(self, agent_name: str) -> list[ResearchRequest]:
        """Retourneert alle opdrachten van een specifieke agent."""
        return [r for r in self._requests if r.requesting_agent == agent_name]

    def get_response(self, request_id: str) -> ResearchResponse | None:
        """Retourneert de response voor een request_id, of None."""
        return self._responses.get(request_id)
