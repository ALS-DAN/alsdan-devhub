# Sprint Intake: Kennispipeline Golf 2A — Researcher Verrijking + KnowledgeCurator

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 3
prioriteit: P1 (kritiek pad naar KWP DEV)
sprint_type: FEAT
cynefin: complex (combineert meerdere nieuwe patronen, SPIKE-elementen)
impact_zone: GEEL (wijzigt researcher agent, voegt nieuwe agent toe, Weaviate collections)
kennispipeline_golf: 2
parallel_met: geen
geblokkeerd_door: [Track C S3 (Weaviate adapter), Track C S5 (embeddings), KENNISPIPELINE_GOLF1A]
volgende_stap: KENNISPIPELINE_GOLF2B_KWP_DEV_BOOTSTRAP
---

## Doel

Verrijk de researcher agent met queue-integratie en Weaviate-output. Bouw de KnowledgeCurator agent die kennis valideert vóór ingestie in de vectorstore. Alle observaties, kennis en research requests in Weaviate collections — geen SQLite.

## Probleemstelling

De researcher agent bestaat maar heeft nooit output geproduceerd — `knowledge/` is leeg. De researcher schrijft alleen naar markdown bestanden en heeft geen vectorstore-integratie. Er is geen kwaliteitspoort tussen research-output en de vectorstore.

BORIS heeft een werkende curator maar die filtert alleen output (chunks naar gebruiker). DevHub heeft een ander probleem: we moeten kennis valideren vóór ingestie (input-curatie) én gezondheid monitoren (freshness, scope, grading).

## SOTA-onderbouwing

Combineert bewezen patronen uit drie bronnen:

**Van BORIS (geverifieerd in codebase):**
- `CuratorAgent.curate()` — chunk-validatie patroon
- 4-dimensie audit: compliance%, zone-verdeling, staleness (>18 maanden), source-ratio
- Health score berekening (gewogen penalties)
- `ObservationStore` — typed observations met severity en privacy-niveaus
- `ObservationType` enum patroon

**Van DevHub (bestaand):**
- Kennisgradering GOLD/SILVER/BRONZE/SPECULATIVE (Art. 5)
- Verificatielabels Geverifieerd/Aangenomen/Onbekend (Art. 2)
- EVIDENCE-methodiek voor bronwaardering
- Researcher bronhiërarchie (7 niveaus)

**Van SOTA (SILVER-grading):**
- Freshness monitoring → automatisch ResearchRequests genereren (The New Stack, 6 KB patterns)
- Ingest-validatie op input-kant (AutoResearcher, arxiv 2510.20844)
- Scope governance tegen kennisexplosie
- Blackboard pattern: Weaviate als gedeeld geheugen (Databricks, LangChain)

## Deliverables

### Researcher verrijking

- [ ] **RV-01** — Researcher queue-integratie
  - Leest ResearchRequests uit queue (naast directe delegatie)
  - Verwerkt requests op basis van prioriteit en diepte
  - Rapporteert ResearchResponse terug naar queue

- [ ] **RV-02** — Researcher Weaviate-output
  - Schrijft kennisartikelen naar Weaviate collection `knowledge_articles` (naast markdown in `knowledge/`)
  - Embedding bij ingestie voor semantisch zoeken
  - Metadata: domain, grade, sources, verification_pct, date, requesting_agent

- [ ] **RV-03** — Researcher agent definitie updaten
  - `agents/researcher.md` bijwerken met queue-workflow en Weaviate-output
  - Kennisdomeinen uitbreiden (zie KWP DEV scope hieronder)

### KnowledgeCurator agent

- [ ] **KC-01** — `KnowledgeCurator` klasse in `packages/devhub-core/devhub_core/agents/`
  - Aparte agent (niet QA Agent uitbreiding) — andere triggers, ander ritme
  - Drie verantwoordelijkheden: ingest-validatie, freshness monitoring, scope governance

- [ ] **KC-02** — Ingest-validatie
  - Kwaliteitspoort vóór kennis Weaviate ingaat
  - Checks: bronvermelding aanwezig? Gradering onderbouwd? Geen duplicaat? Art. 5 compliant?
  - Geïnspireerd door BORIS `CuratorAgent.curate()` maar op input-kant

- [ ] **KC-03** — Freshness monitoring
  - Periodieke scan op verouderde kennis
  - GOLD degradeert naar SILVER na 6 maanden (Art. 5.4)
  - Genereert automatisch ResearchRequests voor hervalidatie via ResearchQueue
  - Configureerbare drempels per domein (AI-engineering veroudert sneller dan methodiek)

- [ ] **KC-04** — Scope governance
  - Controleert of kennis binnen gedefinieerde KWP DEV domeinen valt
  - Signaleert scope creep
  - Configureerbaar: welke domeinen actief, hoe diep

- [ ] **KC-05** — 4-dimensie health audit (geïnspireerd door BORIS)
  - Dimensie 1: Gradering-distributie (niet >60% SPECULATIVE)
  - Dimensie 2: Freshness (niet >20% ouder dan drempel)
  - Dimensie 3: Source-ratio (niet >70% AI-generated, anti-collapse)
  - Dimensie 4: Domein-dekking (geen domeinen met 0 artikelen)
  - Health score berekening (gewogen, zoals BORIS)

### Weaviate collections (alles in Weaviate, geen SQLite)

- [ ] **WC-01** — Collection `knowledge_articles`
  - Schema: title, content, domain, grade, sources, verification_pct, date, author, embedding
  - Multi-tenancy ready (per KWP namespace)

- [ ] **WC-02** — Collection `observations`
  - Schema: observation_type, source_agent, severity, payload, timestamp, resolved
  - ObservationTypes: GRADE_DEGRADATION, FRESHNESS_ALERT, SCOPE_VIOLATION, INGEST_REJECTION, HEALTH_DEGRADED, PATTERN_DETECTED
  - Privacy-niveaus: aggregate, session_linked (patroon van BORIS)

- [ ] **WC-03** — Collection `research_requests`
  - Vervangt de in-memory queue uit Golf 1A
  - Persistent, doorzoekbaar, met status-tracking

### KnowledgeCurator agent definitie

- [ ] **KC-06** — Agent definitie `agents/knowledge-curator.md`
  - Plugin-level agent (naast dev-lead, coder, reviewer, etc.)
  - Beschrijving van triggers, verantwoordelijkheden, interactie met researcher

### Tests

- [ ] **T-01** — Tests voor researcher verrijking (queue-integratie, Weaviate-output)
- [ ] **T-02** — Tests voor KnowledgeCurator (ingest, freshness, scope, audit)
- [ ] **T-03** — Tests voor Weaviate collections (CRUD, queries, observations)
- [ ] **T-04** — Integratietest: researcher → curator → Weaviate
  - Minimum totaal: 40 tests

## KWP DEV scope (kerndomeinen voor bootstrap)

Na deze sprint kan KWP DEV gevuld worden. De kerndomeinen:

1. **AI-engineering** — prompt engineering, agent architectuur, tool use, RAG-patronen, context management
2. **Claude-specifiek** — model capabilities, Claude Code, MCP-protocol, plugin-architectuur
3. **Python/software-architectuur** — design patterns, uv, Pydantic v2, testing
4. **Development-methodiek** — Shape Up, Cynefin, DORA metrics, trunk-based development

Strategische domeinen (later toe te voegen):
5. AI-governance (OWASP ASI, EU AI Act, HITL)
6. Vectorstore/kennismanagement (embeddings, chunking, hybrid search)
7. Opkomende patronen (agentic workflows, computer use, self-improving systems)

## Afhankelijkheden

- **Geblokkeerd door:**
  - Track C S3 (Weaviate adapter) — collections vereisen werkende Weaviate
  - Track C S5 (embedding providers) — knowledge_articles hebben embeddings nodig
  - Golf 1A (ResearchQueue contracts) — curator en researcher gebruiken deze contracts
- **BORIS impact:** nee — DevHub tooling. Patronen geïnspireerd door BORIS maar onafhankelijk geïmplementeerd
- **Cross-track:** ResearchQueue in-memory (Golf 1A) wordt vervangen door Weaviate collection

## Fase-context

Fase 3 (Knowledge & Memory). Dit is het hart van de kennispipeline — zonder werkende researcher + curator kan KWP DEV niet gevuld worden.

## Open vragen voor Claude Code

1. Moet de KnowledgeCurator ook een `.claude/agents/` (project-level) variant krijgen naast `agents/` (plugin-level)?
2. Hoe verhoudt freshness monitoring zich tot n8n scheduled tasks (bestaande CI/CD infra)?
3. Moeten de Weaviate collections in `config/weaviate.yml` of in `config/nodes.yml` geconfigureerd worden?
4. Is ChromaDB (al beschikbaar via Track C S1-S2) bruikbaar als dev/test backend voor deze sprint, met Weaviate als productie-target?

## Technische richting (Claude Code mag afwijken)

- KnowledgeCurator als nieuwe klasse in `packages/devhub-core/devhub_core/agents/`
- Weaviate collection schemas als frozen dataclasses
- Configuratie via YAML (domeinen, drempels, freshness-intervallen)
- ChromaDB als test-backend, Weaviate als productie (adapter pattern al in Track C)

## DEV_CONSTITUTION impact

- **Art. 2 (Verificatieplicht):** curator verifieert researcher-output vóór ingestie
- **Art. 5 (Kennisintegriteit):** gradering en freshness-monitoring implementeren Art. 5.4
- **Art. 7 (Impact-zonering):** GEEL — nieuwe agent + Weaviate collections + researcher wijziging
