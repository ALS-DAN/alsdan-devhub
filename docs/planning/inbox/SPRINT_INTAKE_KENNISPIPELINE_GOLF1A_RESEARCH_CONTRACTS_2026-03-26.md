# Sprint Intake: Kennispipeline Golf 1A — ResearchQueue Contracts

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
prioriteit: P2 (kritiek pad naar KWP DEV)
sprint_type: FEAT
cynefin: complicated (bekende patronen, volgt bestaand ABC/dataclass patroon)
impact_zone: GROEN (nieuwe contracts, raakt geen bestaande code)
kennispipeline_golf: 1
parallel_met: [KENNISPIPELINE_GOLF1B_DOCUMENT_INTERFACE, TRACK_B_S2_GOOGLE_DRIVE]
geblokkeerd_door: geen
volgende_stap: KENNISPIPELINE_GOLF2A_RESEARCHER_VERRIJKING (na Track C S3-S5)
---

## Doel

Bouw de contractlaag voor demand-driven research: een ResearchRequest dataclass en queue-mechanisme waarmee elke agent een onderzoeksvraag kan indienen bij de researcher.

## Probleemstelling

De researcher agent bestaat maar wordt alleen handmatig getriggerd door de dev-lead. Er is geen mechanisme waarmee agents (coder, reviewer, planner) zelf kennislacunes kunnen signaleren. SOTA multi-agent systemen gebruiken een "blackboard pattern" waarbij agents research requests posten op een gedeelde queue die de researcher oppikt.

Zonder dit contract kan de kennispipeline niet demand-driven werken — alles blijft handmatig.

## SOTA-onderbouwing

- **Blackboard pattern** (multi-agent architectuur): vectorstore/queue als gedeeld geheugen waar agents naar schrijven en van lezen (SILVER — gedocumenteerd in Databricks, LangChain, The New Stack)
- **AutoResearcher** (arxiv 2510.20844): gestructureerde pipeline met transparante tussenstappen (SILVER — peer-reviewed)
- **Demand-driven retrieval**: agents herkennen zelf kennislacunes en triggeren retrieval (SILVER — gedocumenteerd door meerdere bronnen)

## Deliverables

- [ ] **RC-01** — `ResearchRequest` frozen dataclass in `packages/devhub-core/devhub_core/contracts/`
  - Verplichte velden: `requesting_agent`, `question`, `domain`, `depth` (QUICK/STANDARD/DEEP), `priority`, `context`
  - Optionele velden: `deadline`, `related_knowledge`, `output_format`
  - Volgt bestaand patroon: frozen, `__post_init__` validatie, `to_dict()`

- [ ] **RC-02** — `ResearchResponse` frozen dataclass
  - Velden: `request_id`, `status` (PENDING/IN_PROGRESS/COMPLETED/FAILED), `knowledge_refs`, `summary`, `grade`, `verification_pct`

- [ ] **RC-03** — `ResearchQueue` interface
  - Methodes: `submit(request)`, `next()`, `complete(request_id, response)`, `pending()`, `by_agent(agent_name)`
  - Initiële implementatie: in-memory (list-based), later Weaviate collection

- [ ] **RC-04** — Researcher agent definitie updaten (`agents/researcher.md`)
  - Queue-integratie beschrijven: researcher leest uit queue naast directe delegatie
  - Acceptatiecriterium: researcher kan zowel directe opdracht als queue-request verwerken

- [ ] **RC-05** — Tests voor alle contracts + queue
  - Minimum: 20 tests (dataclass validatie, queue FIFO, status transitions, edge cases)

## Afhankelijkheden

- **Geblokkeerd door:** geen — dit zijn pure contracts, onafhankelijk van Weaviate
- **BORIS impact:** nee — DevHub-interne tooling
- **Cross-track:** ResearchQueue in-memory implementatie wordt later vervangen door Weaviate collection (Golf 2A, na Track C S3-S5)

## Fase-context

Fase 3 (Knowledge & Memory). Past direct: dit is de contractlaag die de kennispipeline mogelijk maakt. Alle andere kennispipeline-stukken bouwen hierop voort.

## Open vragen voor Claude Code

1. Moet ResearchQueue een ABC zijn (voor latere Weaviate-implementatie) of begint het als concrete klasse met een migrate-pad?
2. Past het in `contracts/` of verdient het een eigen `research/` subpackage?
3. Hoe integreert de queue met de bestaande dev-lead → researcher delegatie? Aanvulling of vervanging?

## Technische richting (Claude Code mag afwijken)

- Volg het bestaande patroon uit `dev_contracts.py` en `security_contracts.py`
- `ResearchRequest` en `ResearchResponse` als frozen dataclasses met `__slots__`
- Queue als ABC met `InMemoryResearchQueue` als eerste implementatie
- Later `WeaviateResearchQueue` (Golf 2A)

## DEV_CONSTITUTION impact

- **Art. 2 (Verificatieplicht):** ResearchRequest bevat `verification_required` flag
- **Art. 5 (Kennisintegriteit):** ResearchResponse bevat `grade` veld (GOLD/SILVER/BRONZE/SPECULATIVE)
- **Art. 7 (Impact-zonering):** GROEN — nieuwe contracts, geen bestaande code geraakt
