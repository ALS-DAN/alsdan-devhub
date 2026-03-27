"""
KWP DEV Bootstrap — Voorgedefinieerde research requests en pipeline runner.

Vult de kennisbank met een initiële set onderzoeksvragen en seed-artikelen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from devhub_core.contracts.curator_contracts import (
    CurationReport,
    CurationVerdict,
    KnowledgeArticle,
    KnowledgeDomain,
    KnowledgeHealthReport,
)
from devhub_core.contracts.research_contracts import (
    ResearchDepth,
    ResearchQueue,
    ResearchRequest,
)

if TYPE_CHECKING:
    from devhub_core.agents.knowledge_curator import KnowledgeCurator
    from devhub_core.research.knowledge_store import KnowledgeStore


class KWPBootstrap:
    """Voorgedefinieerde research requests voor KWP DEV bootstrap."""

    @staticmethod
    def get_requests() -> dict[KnowledgeDomain, list[ResearchRequest]]:
        """Retourneer alle voorgedefinieerde research requests per domein."""
        return {
            KnowledgeDomain.AI_ENGINEERING: [
                ResearchRequest(
                    request_id="BOOT-AI-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de huidige SOTA prompt engineering"
                        " technieken en anti-patronen?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=2,
                    context=("Kerdomein AI engineering — fundamenteel" " voor DevHub agents"),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke multi-agent architectuur patronen"
                        " zijn bewezen effectief (orchestrator,"
                        " blackboard, event-driven)?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=2,
                    context=(
                        "DevHub gebruikt orchestrator pattern —" " vergelijk met alternatieven"
                    ),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-003",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de beste RAG chunking"
                        " strategieen en wanneer gebruik je"
                        " hybrid search vs. pure vector search?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("Relevant voor KWP DEV vectorstore" " inrichting"),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-004",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn bewezen tool use patterns en" " best practices voor LLM agents?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("DevHub agents gebruiken tools —" " optimalisatie patronen"),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-005",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe optimaliseer je context window" " management bij grote codebases?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("DevHub werkt met grote projecten —" " context budget management"),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-006",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke agent memory patronen zijn er"
                        " voor korte en lange termijn"
                        " persistentie?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("KWP DEV IS het lange-termijn geheugen" " — wat zijn alternatieven?"),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-007",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de risico's en mitigaties van"
                        " AI model collapse bij"
                        " zelf-gegenereerde trainingsdata?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    context=("KWP DEV bevat AI-gegenereerde kennis" " — anti-collapse patronen"),
                ),
                ResearchRequest(
                    request_id="BOOT-AI-008",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe implementeer je effectieve evaluatie"
                        " en testing van LLM-based agents?"
                    ),
                    domain="ai_engineering",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    context=("DevHub heeft QA Agent — hoe test je" " AI-agent kwaliteit?"),
                ),
            ],
            KnowledgeDomain.CLAUDE_SPECIFIC: [
                ResearchRequest(
                    request_id="BOOT-CL-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de actuele capabilities en" " beperkingen van Claude modellen?"
                    ),
                    domain="claude_specific",
                    depth=ResearchDepth.STANDARD,
                    priority=2,
                    context=("Fundamenteel voor effectief gebruik" " in DevHub"),
                ),
                ResearchRequest(
                    request_id="BOOT-CL-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn bewezen Claude Code best" " practices en workflow patronen?"
                    ),
                    domain="claude_specific",
                    depth=ResearchDepth.STANDARD,
                    priority=2,
                    context=("DevHub IS een Claude Code plugin" " — meta-kennis"),
                ),
                ResearchRequest(
                    request_id="BOOT-CL-003",
                    requesting_agent="kwp-bootstrap",
                    question=("Hoe werkt het MCP protocol en wat" " zijn security best practices?"),
                    domain="claude_specific",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("DevHub gebruikt MCP tools — protocol" " begrip essentieel"),
                ),
                ResearchRequest(
                    request_id="BOOT-CL-004",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat is de optimale structuur voor"
                        " Claude Code plugins (agents,"
                        " skills, hooks)?"
                    ),
                    domain="claude_specific",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("DevHub plugin-architectuur — valideer" " tegen best practices"),
                ),
                ResearchRequest(
                    request_id="BOOT-CL-005",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe ontwerp je effectieve system" " prompts voor complexe agent-taken?"
                    ),
                    domain="claude_specific",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("DevHub agents hebben uitgebreide" " system prompts"),
                ),
                ResearchRequest(
                    request_id="BOOT-CL-006",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de trade-offs tussen"
                        " verschillende Claude modellen"
                        " (Opus vs Sonnet vs Haiku)"
                        " voor agent-taken?"
                    ),
                    domain="claude_specific",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("DevHub agents specificeren model" " in frontmatter"),
                ),
            ],
            KnowledgeDomain.PYTHON_ARCHITECTURE: [
                ResearchRequest(
                    request_id="BOOT-PY-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wanneer gebruik je ABC + frozen"
                        " dataclass vs. Protocol + TypedDict"
                        " in Python?"
                    ),
                    domain="python_architecture",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("DevHub gebruikt ABC + frozen" " dataclass — valideer deze keuze"),
                ),
                ResearchRequest(
                    request_id="BOOT-PY-002",
                    requesting_agent="kwp-bootstrap",
                    question=("Wat zijn best practices voor uv" " workspace monorepo management?"),
                    domain="python_architecture",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("DevHub is een uv workspace met" " 4 packages"),
                ),
                ResearchRequest(
                    request_id="BOOT-PY-003",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn moderne pytest patronen:"
                        " fixture design, parametrize,"
                        " property-based testing?"
                    ),
                    domain="python_architecture",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("DevHub heeft 1000+ tests —" " optimaliseer test architectuur"),
                ),
                ResearchRequest(
                    request_id="BOOT-PY-004",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Pydantic v2 vs. frozen dataclasses:"
                        " wanneer welke,"
                        " migratie-overwegingen?"
                    ),
                    domain="python_architecture",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    context=("DevHub gebruikt frozen dataclasses" " — is Pydantic beter?"),
                ),
                ResearchRequest(
                    request_id="BOOT-PY-005",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke factory pattern varianten zijn"
                        " er in Python en wanneer past welke?"
                    ),
                    domain="python_architecture",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    context=("DevHub heeft 3 factories — is dit" " het juiste patroon?"),
                ),
                ResearchRequest(
                    request_id="BOOT-PY-006",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe ontwerp je een effectieve"
                        " adapter/interface laag voor"
                        " vendor-onafhankelijkheid?"
                    ),
                    domain="python_architecture",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("DevHub NodeInterface + adapters" " — architectuurvalidatie"),
                ),
            ],
            KnowledgeDomain.DEVELOPMENT_METHODOLOGY: [
                ResearchRequest(
                    request_id="BOOT-DM-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe pas je Shape Up toe in solo/klein"
                        " team development (appetite, betting,"
                        " hill charts)?"
                    ),
                    domain="development_methodology",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    context=("DevHub gebruikt Shape Up" " — verdieping nodig"),
                ),
                ResearchRequest(
                    request_id="BOOT-DM-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe gebruik je het Cynefin framework"
                        " voor technische beslissingen"
                        " (probe-sense-respond)?"
                    ),
                    domain="development_methodology",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    context=("DevHub sprint intakes hebben" " cynefin classificatie"),
                ),
                ResearchRequest(
                    request_id="BOOT-DM-003",
                    requesting_agent="kwp-bootstrap",
                    question=("Hoe implementeer je DORA metrics in" " een solo developer context?"),
                    domain="development_methodology",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    context=(
                        "DevHub is solo-ontwikkeld —"
                        " traditionele DORA metrics"
                        " passen niet 1:1"
                    ),
                ),
                ResearchRequest(
                    request_id="BOOT-DM-004",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Trunk-based development vs. feature"
                        " branches: wat werkt beter voor"
                        " AI-assisted solo development?"
                    ),
                    domain="development_methodology",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    context=("DevHub werkt op main — valideer" " trunk-based approach"),
                ),
            ],
        }

    def submit_all(self, queue: ResearchQueue) -> int:
        """Dien alle bootstrap requests in bij de queue."""
        count = 0
        for requests in self.get_requests().values():
            for request in requests:
                queue.submit(request)
                count += 1
        return count

    def submit_domain(self, queue: ResearchQueue, domain: KnowledgeDomain) -> int:
        """Dien requests in voor een domein."""
        requests = self.get_requests().get(domain, [])
        for request in requests:
            queue.submit(request)
        return len(requests)


@dataclass(frozen=True)
class BootstrapReport:
    """Resultaat van een bootstrap run."""

    total_submitted: int = 0
    approved: int = 0
    rejected: int = 0
    needs_revision: int = 0
    reports: tuple[CurationReport, ...] = ()


class BootstrapPipeline:
    """End-to-end pipeline: articles -> curator -> vectorstore."""

    def __init__(
        self,
        curator: KnowledgeCurator,
        store: KnowledgeStore,
    ) -> None:
        self._curator = curator
        self._store = store

    def run_seed(self, articles: list[KnowledgeArticle]) -> BootstrapReport:
        """Valideer en ingesteer seed articles via curator."""
        reports: list[CurationReport] = []
        approved = 0
        rejected = 0
        needs_revision = 0

        for article in articles:
            report = self._curator.validate_article(article)
            reports.append(report)

            if report.verdict == CurationVerdict.APPROVED:
                self._store.store_article(article)
                approved += 1
            elif report.verdict == CurationVerdict.REJECTED:
                rejected += 1
            else:
                needs_revision += 1

        return BootstrapReport(
            total_submitted=len(articles),
            approved=approved,
            rejected=rejected,
            needs_revision=needs_revision,
            reports=tuple(reports),
        )

    def health_check(self) -> KnowledgeHealthReport:
        """Draai health audit op huidige kennisbank."""
        articles = self._store.get_all_articles()
        return self._curator.audit_health(articles)
