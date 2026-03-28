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
            # --- Ring 1: Governance Compliance (nieuw) ---
            KnowledgeDomain.GOVERNANCE_COMPLIANCE: [
                ResearchRequest(
                    request_id="BOOT-GC-001",
                    requesting_agent="kwp-bootstrap",
                    question="Wat zijn best practices voor ADR governance in software projecten?",
                    domain="governance_compliance",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ5", "RQ6"),
                ),
                ResearchRequest(
                    request_id="BOOT-GC-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe ontwerp je effectieve impact-zonering"
                        " (GREEN/YELLOW/RED) voor AI agents?"
                    ),
                    domain="governance_compliance",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ4", "RQ6"),
                ),
            ],
            # --- Ring 2: Agent-specifiek (8 domeinen) ---
            KnowledgeDomain.SPRINT_PLANNING: [
                ResearchRequest(
                    request_id="BOOT-SP-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke sprint planning technieken werken"
                        " bij solo AI-assisted development?"
                    ),
                    domain="sprint_planning",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ4", "RQ6"),
                ),
                ResearchRequest(
                    request_id="BOOT-SP-002",
                    requesting_agent="kwp-bootstrap",
                    question="Hoe meet je sprint velocity en cycle time voor AI-agent development?",
                    domain="sprint_planning",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    rq_tags=("RQ4", "RQ5"),
                ),
            ],
            KnowledgeDomain.CODE_REVIEW: [
                ResearchRequest(
                    request_id="BOOT-CR-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de meest effectieve code review"
                        " checklists voor Python projecten?"
                    ),
                    domain="code_review",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ1", "RQ4"),
                ),
                ResearchRequest(
                    request_id="BOOT-CR-002",
                    requesting_agent="kwp-bootstrap",
                    question="Welke anti-patronen moeten AI code reviewers prioriteren?",
                    domain="code_review",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ4",),
                ),
            ],
            KnowledgeDomain.SECURITY_APPSEC: [
                ResearchRequest(
                    request_id="BOOT-SA-001",
                    requesting_agent="kwp-bootstrap",
                    question="Wat zijn de OWASP ASI 2026 richtlijnen voor AI-systeem security?",
                    domain="security_appsec",
                    depth=ResearchDepth.STANDARD,
                    priority=2,
                    rq_tags=("RQ1", "RQ4"),
                ),
                ResearchRequest(
                    request_id="BOOT-SA-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe implementeer je secrets management" " in een AI development pipeline?"
                    ),
                    domain="security_appsec",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ4", "RQ6"),
                ),
            ],
            KnowledgeDomain.TESTING_QA: [
                ResearchRequest(
                    request_id="BOOT-TQ-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn bewezen pytest patterns voor" " grote test suites (1000+ tests)?"
                    ),
                    domain="testing_qa",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ2", "RQ4"),
                ),
                ResearchRequest(
                    request_id="BOOT-TQ-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe pas je property-based testing toe"
                        " in een frozen dataclass architectuur?"
                    ),
                    domain="testing_qa",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    rq_tags=("RQ4",),
                ),
            ],
            KnowledgeDomain.KNOWLEDGE_METHODOLOGY: [
                ResearchRequest(
                    request_id="BOOT-KM-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke RAG curation strategieen" " maximaliseren kenniskwaliteit over tijd?"
                    ),
                    domain="knowledge_methodology",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ1", "RQ5"),
                ),
                ResearchRequest(
                    request_id="BOOT-KM-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Hoe ontwerp je Research Questions (RQ)"
                        " voor systematisch kennismanagement?"
                    ),
                    domain="knowledge_methodology",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ5",),
                ),
            ],
            KnowledgeDomain.COACHING_LEARNING: [
                ResearchRequest(
                    request_id="BOOT-CL-101",
                    requesting_agent="kwp-bootstrap",
                    question="Hoe pas je het Dreyfus model toe voor AI-assisted developer groei?",
                    domain="coaching_learning",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    rq_tags=("RQ3", "RQ5"),
                ),
                ResearchRequest(
                    request_id="BOOT-CL-102",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn threshold concepts in software"
                        " engineering en hoe identificeer je ze?"
                    ),
                    domain="coaching_learning",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    rq_tags=("RQ3", "RQ4"),
                ),
            ],
            KnowledgeDomain.DOCUMENTATION: [
                ResearchRequest(
                    request_id="BOOT-DOC-001",
                    requesting_agent="kwp-bootstrap",
                    question="Hoe pas je het Diataxis framework toe op technische documentatie?",
                    domain="documentation",
                    depth=ResearchDepth.STANDARD,
                    priority=3,
                    rq_tags=("RQ2", "RQ3"),
                ),
                ResearchRequest(
                    request_id="BOOT-DOC-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn best practices voor" " geautomatiseerde docs-generatie uit code?"
                    ),
                    domain="documentation",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    rq_tags=("RQ2",),
                ),
            ],
            KnowledgeDomain.PRODUCT_OWNERSHIP: [
                ResearchRequest(
                    request_id="BOOT-PO-001",
                    requesting_agent="kwp-bootstrap",
                    question="Hoe combineer je product ownership met solo AI-assisted development?",
                    domain="product_ownership",
                    depth=ResearchDepth.STANDARD,
                    priority=4,
                    rq_tags=("RQ4", "RQ6"),
                ),
                ResearchRequest(
                    request_id="BOOT-PO-002",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke backlog management technieken"
                        " werken voor kennisintensieve projecten?"
                    ),
                    domain="product_ownership",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ4", "RQ5"),
                ),
            ],
            # --- Ring 3: Project-specifiek (3 domeinen) ---
            KnowledgeDomain.HEALTHCARE_ICT: [
                ResearchRequest(
                    request_id="BOOT-HC-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Wat zijn de HL7 FHIR standaarden" " relevant voor zorginformatiesystemen?"
                    ),
                    domain="healthcare_ict",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ1", "RQ4"),
                ),
                ResearchRequest(
                    request_id="BOOT-HC-002",
                    requesting_agent="kwp-bootstrap",
                    question="Welke NEN-normen zijn verplicht voor ICT in de Nederlandse zorg?",
                    domain="healthcare_ict",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ4", "RQ6"),
                ),
            ],
            KnowledgeDomain.PRIVACY_AVG: [
                ResearchRequest(
                    request_id="BOOT-PA-001",
                    requesting_agent="kwp-bootstrap",
                    question="Wat zijn de AVG/GDPR vereisten voor AI-systemen in de zorgsector?",
                    domain="privacy_avg",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ4", "RQ6"),
                ),
                ResearchRequest(
                    request_id="BOOT-PA-002",
                    requesting_agent="kwp-bootstrap",
                    question="Hoe voer je een DPIA uit voor een AI-kennissysteem?",
                    domain="privacy_avg",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ4", "RQ5"),
                ),
            ],
            KnowledgeDomain.MULTI_TENANCY: [
                ResearchRequest(
                    request_id="BOOT-MT-001",
                    requesting_agent="kwp-bootstrap",
                    question=(
                        "Welke tenant isolation patronen zijn er" " voor multi-tenant AI systemen?"
                    ),
                    domain="multi_tenancy",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ2", "RQ4"),
                ),
                ResearchRequest(
                    request_id="BOOT-MT-002",
                    requesting_agent="kwp-bootstrap",
                    question="Hoe implementeer je configuratie-scheiding per tenant in Python?",
                    domain="multi_tenancy",
                    depth=ResearchDepth.STANDARD,
                    priority=5,
                    rq_tags=("RQ4", "RQ6"),
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
