"""
Seed Articles — Initiele kennisartikelen voor KWP DEV bootstrap.

Gebaseerd op kennis die al in de DevHub codebase gedocumenteerd is.
Elk artikel is SILVER-grading (gedocumenteerd in codebase, niet peer-reviewed).
"""

from __future__ import annotations

from devhub_core.contracts.curator_contracts import (
    KnowledgeArticle,
    KnowledgeDomain,
)


def get_seed_articles() -> list[KnowledgeArticle]:
    """Retourneer alle seed artikelen voor KWP DEV bootstrap."""
    return [
        _abc_frozen_dataclass(),
        _multi_agent_orchestrator(),
        _contract_first_design(),
        _factory_pattern_python(),
        _shape_up_solo(),
        _demand_driven_research(),
        _knowledge_grading(),
        _claude_code_plugin_structure(),
    ]


def _abc_frozen_dataclass() -> KnowledgeArticle:
    """ABC + Frozen Dataclass pattern artikel."""
    content = (
        "Het ABC + Frozen Dataclass pattern combineert abstract"
        " base classes voor interface-definitie met frozen"
        " dataclasses voor immutable message types. ABCs"
        " definiëren het contract: welke methodes moet een"
        " implementatie bieden. Frozen dataclasses zijn de"
        " berichten die over die interfaces gaan.\n\n"
        "Voordelen van frozen dataclasses: (1) Immutability"
        " voorkomt dat berichten na creatie worden gewijzigd,"
        " wat thread-safety garandeert en bugs voorkomt."
        " (2) __post_init__ validatie zorgt dat ongeldige"
        " objecten nooit bestaan — fail fast bij constructie."
        " (3) __slots__ kan worden toegevoegd voor"
        " geheugenoptimalisatie bij grote aantallen"
        " instanties.\n\n"
        "In DevHub past NodeInterface dit patroon toe:"
        " de ABC definieert 13 methodes (get_report,"
        " get_health, etc.) en de return types zijn frozen"
        " dataclasses zoals NodeReport en HealthStatus."
        " VectorStoreInterface volgt hetzelfde patroon met"
        " DocumentChunk en RetrievalRequest.\n\n"
        "Richtlijn: gebruik composition over inheritance."
        " Een adapter HEEFT een client, het IS geen client."
        " Houd dataclasses klein en gefocust — splits bij"
        " meer dan 7 velden. Gebruik tuple in plaats van"
        " list voor frozen-compatibiliteit."
    )
    return KnowledgeArticle(
        article_id="SEED-PY-001",
        title="ABC + Frozen Dataclass Pattern in Python",
        content=content,
        domain=KnowledgeDomain.PYTHON_ARCHITECTURE,
        grade="SILVER",
        sources=(
            "devhub_core/contracts/node_interface.py",
            "devhub_vectorstore/contracts/vectorstore_contracts.py",
        ),
        verification_pct=70.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ2", "RQ4"),
        domain_ring="core",
    )


def _multi_agent_orchestrator() -> KnowledgeArticle:
    """Multi-Agent Orchestrator pattern artikel."""
    content = (
        "Het Orchestrator pattern is een multi-agent"
        " architectuur waarbij een centraal component taken"
        " decomponeert, delegeert aan gespecialiseerde agents"
        " en resultaten aggregeert. De orchestrator kent de"
        " capabilities van elke agent maar implementeert geen"
        " domeinlogica zelf.\n\n"
        "DevHub's DevOrchestrator ontvangt DevTaskRequests,"
        " bepaalt welke documentatie nodig is (Diataxis"
        " routing), delegeert code-werk aan de developer en"
        " doc-generatie aan DocsAgent, en triggert QA Agent"
        " voor review. Communicatie verloopt via een"
        " scratchpad (file-based message passing).\n\n"
        "Vergelijking met alternatieven: (1) Blackboard"
        " pattern — agents lezen/schrijven naar gedeeld"
        " geheugen, geschikt voor iteratieve verfijning"
        " maar moeilijker te debuggen. (2) Peer-to-peer —"
        " agents communiceren direct, schaalbaar maar"
        " complex qua coördinatie. (3) Event-driven —"
        " loose coupling via events, goed voor async maar"
        " lastiger te tracen.\n\n"
        "Het orchestrator pattern past het best bij"
        " deterministische workflows met bekende stappen."
        " DevHub kiest dit omdat sprint-taken een"
        " voorspelbare flow hebben: decompose, implement,"
        " document, review."
    )
    return KnowledgeArticle(
        article_id="SEED-AI-001",
        title="Multi-Agent Orchestrator Pattern",
        content=content,
        domain=KnowledgeDomain.AI_ENGINEERING,
        grade="SILVER",
        sources=(
            "devhub_core/agents/orchestrator.py",
            "agents/dev-lead.md",
        ),
        verification_pct=65.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ1", "RQ4"),
        domain_ring="core",
    )


def _contract_first_design() -> KnowledgeArticle:
    """Contract-First Design artikel."""
    content = (
        "Contract-First Design betekent dat interfaces en"
        " message types worden gedefinieerd voordat"
        " implementaties worden geschreven. Dit garandeert"
        " vendor-onafhankelijkheid: de contracts bevatten"
        " geen vendor-specifieke types.\n\n"
        "In DevHub is NodeInterface het kerncontract: 13"
        " frozen dataclasses (NodeReport, HealthStatus,"
        " AgentManifest, etc.) plus een ABC met abstracte"
        " methodes. Project-adapters (Providers) vertalen"
        " project-specifieke data naar deze generieke types."
        " Elk project implementeert dezelfde interface"
        " zonder de contracts te wijzigen.\n\n"
        "Kernprincipes: (1) Geen vendor imports in"
        " contracts — alleen stdlib en eigen types."
        " (2) Adapters vertalen: vendor-type naar contract,"
        " nooit andersom. (3) Frozen dataclasses als"
        " message types voorkomen dat adapters interne"
        " state lekken. (4) to_dict() methodes voor"
        " serialisatie zonder externe dependencies.\n\n"
        "Voordeel: wanneer een vendor-library breekt of"
        " vervangen wordt, wijzig je alleen de adapter."
        " Alle code die contracts gebruikt blijft"
        " ongewijzigd. Dit is essentieel voor een systeem"
        " dat meerdere projecten beheert."
    )
    return KnowledgeArticle(
        article_id="SEED-PY-002",
        title=("Contract-First Design voor" " Vendor-Onafhankelijkheid"),
        content=content,
        domain=KnowledgeDomain.PYTHON_ARCHITECTURE,
        grade="SILVER",
        sources=(
            "devhub_core/contracts/node_interface.py",
            "devhub_core/registry.py",
        ),
        verification_pct=70.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ2", "RQ5"),
        domain_ring="core",
    )


def _factory_pattern_python() -> KnowledgeArticle:
    """Factory Pattern Varianten artikel."""
    content = (
        "DevHub gebruikt registry-based factories voor het"
        " aanmaken van backend-specifieke implementaties."
        " Het patroon: een class method create() accepteert"
        " een backend string en retourneert de juiste"
        " implementatie. available_backends() toont welke"
        " opties beschikbaar zijn.\n\n"
        "Drie factories in DevHub: (1) VectorStoreFactory"
        " — maakt ChromaDB of Weaviate stores op basis van"
        " backend naam en configuratie. (2) EmbeddingFactory"
        " — maakt HashEmbeddingProvider of toekomstige"
        " providers. (3) DocumentFactory — maakt document"
        " processors per bestandstype.\n\n"
        "Implementatiedetails: lazy imports voorkomen dat"
        " alle backends geladen worden bij startup. De"
        " factory importeert een backend pas wanneer die"
        " wordt aangevraagd. Dit houdt dependencies"
        " optioneel — je hoeft geen Weaviate client te"
        " installeren als je alleen ChromaDB gebruikt.\n\n"
        "Patroon-structuur: _REGISTRY dict mapt string"
        " namen naar tuples van (module_path, class_name)."
        " create() doet importlib.import_module() en"
        " getattr() voor de class. Fallback met duidelijke"
        " ValueError als backend onbekend is."
    )
    return KnowledgeArticle(
        article_id="SEED-PY-003",
        title="Factory Pattern Varianten in Python",
        content=content,
        domain=KnowledgeDomain.PYTHON_ARCHITECTURE,
        grade="SILVER",
        sources=(
            "devhub_vectorstore/factory.py",
            "devhub_vectorstore/embeddings/factory.py",
            "devhub_documents/factory.py",
        ),
        verification_pct=75.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ2", "RQ4"),
        domain_ring="core",
    )


def _shape_up_solo() -> KnowledgeArticle:
    """Shape Up solo development artikel."""
    content = (
        "Shape Up is een product development methodiek van"
        " Basecamp, aangepast voor solo AI-assisted"
        " development in DevHub. Kernconcepten: appetite"
        " (hoeveel tijd investeer je maximaal), betting"
        " (welke taken krijgen de volgende cyclus), en hill"
        " charts (voortgang van onzekerheid naar"
        " zekerheid).\n\n"
        "DevHub's aanpassing: sprint intakes fungeren als"
        " pitches — een gestructureerd document met"
        " probleem, oplossing, grenzen en appetite. Elke"
        " intake bevat een Cynefin-classificatie (Simple,"
        " Complicated, Complex, Chaotic) die bepaalt hoe"
        " de sprint wordt aangepakt.\n\n"
        "Simple taken krijgen directe implementatie."
        " Complicated taken worden opgedeeld in"
        " deeltaken. Complex taken starten met een"
        " probe — een verkennende spike om onzekerheid"
        " te reduceren. Chaotic taken krijgen een"
        " stabilisatie-eerste aanpak.\n\n"
        "Lessen uit DevHub sprints: (1) Golf-structuur"
        " (wave-based delivery) werkt goed — lever in"
        " golven van toenemende complexiteit."
        " (2) Definition of Ready (8 punten) voorkomt"
        " half-begrepen taken. (3) Hill chart tracking"
        " maakt voortgang zichtbaar voor de developer."
    )
    return KnowledgeArticle(
        article_id="SEED-DM-001",
        title=("Shape Up Toepassing bij Solo Development"),
        content=content,
        domain=KnowledgeDomain.DEVELOPMENT_METHODOLOGY,
        grade="BRONZE",
        sources=(
            "docs/planning/",
            "skills/devhub-sprint/",
        ),
        verification_pct=50.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ4", "RQ6"),
        domain_ring="core",
    )


def _demand_driven_research() -> KnowledgeArticle:
    """Demand-Driven Research artikel."""
    content = (
        "Demand-driven research past het blackboard pattern"
        " toe op kennismanagement. Agents posten"
        " ResearchRequests naar een gedeelde queue wanneer"
        " ze kennis missen. Een researcher-agent pikt"
        " opdrachten op, gerangschikt op prioriteit, en"
        " slaat resultaten op in de kennisbank.\n\n"
        "Het ResearchRequest contract bevat: request_id,"
        " requesting_agent, question, domain, depth"
        " (QUICK/STANDARD/DEEP), priority (1-10), context,"
        " en optionele deadline. De queue-interface is een"
        " ABC met submit(), next(), complete(), pending(),"
        " by_agent() en get_response() methodes.\n\n"
        "InMemoryResearchQueue is de default implementatie"
        " met een dict-based opslag. Requests worden"
        " gesorteerd op prioriteit (laag getal = hoog"
        " prioriteit). ResearchResponse bevat status,"
        " summary, knowledge_refs en een gradering.\n\n"
        "Voordelen: (1) Agents hoeven niet te weten HOE"
        " kennis wordt verkregen — ze stellen alleen de"
        " vraag. (2) Prioritering zorgt dat urgente vragen"
        " eerst worden beantwoord. (3) De queue is"
        " persistent en kan worden hervat na een"
        " onderbreking. (4) Responses zijn beschikbaar"
        " voor alle agents, niet alleen de aanvrager."
    )
    return KnowledgeArticle(
        article_id="SEED-AI-002",
        title=("Demand-Driven Research via" " Blackboard Pattern"),
        content=content,
        domain=KnowledgeDomain.AI_ENGINEERING,
        grade="SILVER",
        sources=(
            "devhub_core/contracts/research_contracts.py",
            "devhub_core/research/in_memory_queue.py",
        ),
        verification_pct=60.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ1", "RQ2"),
        domain_ring="core",
    )


def _knowledge_grading() -> KnowledgeArticle:
    """Kennisgradering artikel."""
    content = (
        "Het 4-tier graderingssysteem classificeert kennis"
        " op betrouwbaarheid. GOLD: peer-reviewed of bewezen"
        " in productie, verification_pct >= 80%. SILVER:"
        " gedocumenteerd in codebase of officiële bronnen,"
        " verification_pct >= 50%. BRONZE: ervaring-gebaseerd"
        " zonder formele verificatie. SPECULATIVE: aannames"
        " of hypotheses die nog getest moeten worden.\n\n"
        "De KnowledgeCurator bewaakt gradering bij ingest:"
        " een artikel met GOLD-claim maar lage verification"
        " wordt afgewezen (CRITICAL finding). SILVER met"
        " te lage verificatie krijgt NEEDS_REVISION."
        " Bronvermelding is verplicht — artikelen zonder"
        " sources krijgen een ERROR finding.\n\n"
        "Freshness monitoring degradeert gradering over"
        " tijd. AI Engineering kennis veroudert na 3"
        " maanden, Claude-specifiek na 6 maanden, Python"
        " en methodologie na 12 maanden. Verouderde"
        " artikelen genereren een FRESHNESS_ALERT"
        " observatie en automatisch een ResearchRequest"
        " voor hervalidatie.\n\n"
        "Health audit meet 4 dimensies: gradering-"
        " distributie (penalty bij >60% SPECULATIVE),"
        " freshness (penalty bij >20% stale), source-ratio"
        " (penalty bij >70% single-source), en domein-"
        " dekking (penalty voor lege domeinen)."
    )
    return KnowledgeArticle(
        article_id="SEED-DM-002",
        title=("Kennisgradering: GOLD/SILVER/BRONZE" "/SPECULATIVE"),
        content=content,
        domain=KnowledgeDomain.DEVELOPMENT_METHODOLOGY,
        grade="SILVER",
        sources=(
            "docs/compliance/DEV_CONSTITUTION.md",
            "devhub_core/agents/knowledge_curator.py",
        ),
        verification_pct=65.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ1", "RQ5"),
        domain_ring="core",
    )


def _zone_based_isolation() -> KnowledgeArticle:
    """Zone-Based Data Isolation artikel."""
    content = (
        "Zone-based data isolation scheidt data in drie"
        " zones met verschillende toegangsniveaus."
        " DataZone.RESTRICTED: gevoelige data die alleen"
        " beschikbaar is voor geautoriseerde agents."
        " DataZone.CONTROLLED: interne data met"
        " leesbeperking. DataZone.OPEN: publieke kennis"
        " beschikbaar voor alle agents.\n\n"
        "In de vectorstore wordt elke zone een aparte"
        " collection. ChromaDBZonedStore en"
        " WeaviateZonedStore implementeren dit: bij"
        " initialisatie worden per zone collections"
        " aangemaakt met een prefix (bijv."
        " devhub_open, devhub_controlled). Queries"
        " specificeren altijd een zone en kunnen alleen"
        " data uit die zone ophalen.\n\n"
        "Mapping naar projecten: BORIS gebruikt RED/"
        " YELLOW/GREEN zones. RED mapt naar RESTRICTED"
        " (client-data, medische info). YELLOW mapt naar"
        " CONTROLLED (interne processen, behandelplannen)."
        " GREEN mapt naar OPEN (publieke kennisbank)."
        " DevHub's KWP DEV gebruikt alleen OPEN zone"
        " voor ontwikkelkennis.\n\n"
        "Query filtering: RetrievalRequest bevat een zone"
        " veld. De store-implementatie stuurt de query"
        " alleen naar de collection van die zone."
        " Metadata filters kunnen aanvullend filteren"
        " op domein, gradering of andere attributen."
    )
    return KnowledgeArticle(
        article_id="SEED-AI-003",
        title=("Zone-Based Data Isolation voor" " AI Systemen"),
        content=content,
        domain=KnowledgeDomain.AI_ENGINEERING,
        grade="SILVER",
        sources=(
            "devhub_vectorstore/contracts/vectorstore_contracts.py",
            "devhub_vectorstore/adapters/weaviate_adapter.py",
        ),
        verification_pct=70.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ2", "RQ4"),
        domain_ring="core",
    )


def _claude_code_plugin_structure() -> KnowledgeArticle:
    """Claude Code Plugin Structuur artikel."""
    content = (
        "Claude Code plugins bestaan uit drie lagen:"
        " agents (markdown-gedefinieerde rollen met"
        " system prompts), skills (herbruikbare taken"
        " met SKILL.md definitie), en hooks (pre/post"
        " commit, pre-push triggers). Samen vormen deze"
        " lagen een uitbreidbaar development systeem.\n\n"
        "Agents worden gedefinieerd in agents/ met YAML"
        " frontmatter (model, temperature, allowed tools)"
        " en een markdown body als system prompt. DevHub"
        " heeft 6 agents: dev-lead (orchestrator), coder"
        " (implementatie), reviewer (code review),"
        " researcher (kennisverrijking), planner (sprint"
        " planning), en red-team (security audit). Elk"
        " agent-bestand specificeert welk model wordt"
        " gebruikt.\n\n"
        "Skills leven in .claude/skills/ met een SKILL.md"
        " die trigger-commando, beschrijving en gedetail-"
        " leerde instructies bevat. Skills zijn herbruikbaar"
        " en composeerbaar — een sprint-skill kan intern"
        " de health-skill aanroepen. DevHub heeft 8 skills"
        " waaronder sprint lifecycle, health check, mentor"
        " coaching en governance audit.\n\n"
        "CLAUDE.md fungeert als project-level configuratie:"
        " het definieert de architectuur, werkwijze-regels"
        " en constraints die voor alle agents gelden."
        " Project-level agents in .claude/agents/ zijn"
        " intern en worden niet gedistribueerd. Plugin-level"
        " agents in agents/ zijn voor distributie naar"
        " gebruikers. Beide mogen naast elkaar bestaan"
        " zolang de verantwoordelijkheden gescheiden blijven."
    )
    return KnowledgeArticle(
        article_id="SEED-CL-001",
        title="Claude Code Plugin Structuur",
        content=content,
        domain=KnowledgeDomain.CLAUDE_SPECIFIC,
        grade="SILVER",
        sources=(
            "agents/dev-lead.md",
            ".claude/skills/devhub-sprint/SKILL.md",
        ),
        verification_pct=60.0,
        date="2026-03-27",
        author="kwp-bootstrap",
        rq_tags=("RQ1", "RQ2"),
        domain_ring="core",
    )
