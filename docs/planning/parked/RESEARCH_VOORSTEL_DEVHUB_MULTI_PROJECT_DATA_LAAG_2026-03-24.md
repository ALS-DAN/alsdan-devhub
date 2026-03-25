# RESEARCH_VOORSTEL_DEVHUB_MULTI_PROJECT_DATA_LAAG_2026-03-24

---
gegenereerd_door: Cowork — alsdan-devhub
status: INBOX
fase: "2-3"
---

## Kennislacune

| Veld | Waarde |
|------|--------|
| **Domein** | AI-engineering / database-architectuur / multi-project governance |
| **Gat** | DevHub multi-project data-laag niet gedefinieerd; cross-project aggregatie ontbreekt; KWP DEV opslagstrategie niet bepaald; Golden Path template voor BNS-patroon ontbreekt |
| **Huidige grading** | SPECULATIVE — NodeRegistry + adapters bestaan maar cross-project laag is niet geïmplementeerd |

## Onderzoeksvraag

> Wat is de optimale data-laag voor DevHub als multi-project development-systeem, gegeven de huidige schaal (1 project, uitbreidend naar 5+), teamgrootte (solo + AI-agents) en roadmap (Fase 2-3)?

## Context & Probleemstelling

### Waarom nu

DevHub schaalt naar meerdere projecten via de NodeRegistry (`config/nodes.yml`). Momenteel is alleen `boris-buurts` geregistreerd. Voordat project #2 wordt aangesloten moet de multi-project data-laag gedefinieerd zijn — anders bouwt elk project zijn eigen patroon en ontstaat fragmentatie.

### Wat er al staat (geverifieerd 2026-03-24)

- **NodeRegistry:** `config/nodes.yml` met `boris-buurts` als enige node
- **BorisAdapter:** 38 methodes, read-only, leest BORIS-data via NodeInterface ABC (13 frozen dataclasses)
- **DevOrchestrator:** taakdecompositie, doc queue
- **SQLite:** per-project via adapters (geen cross-project laag)
- **Kennisopslag:** Markdown/YAML in `docs/`, `knowledge/`
- **Plugin-laag:** 5 agents + 5 skills operationeel
- **Tests:** 299 groen (218 Python + 81 plugin)

## Voorstel: DevHub Data-architectuur

```
┌─────────────────────────────────────────────┐
│  DevHub Data-architectuur                   │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │  NodeRegistry (config/nodes.yml)     │   │
│  │  = multi-tenancy laag               │   │
│  └──────┬───────────┬──────────┬────────┘   │
│         │           │          │            │
│    ┌────▼────┐ ┌────▼────┐ ┌──▼──────┐    │
│    │Project A│ │Project B│ │Project C│    │
│    │(SQLite) │ │(SQLite) │ │(SQLite) │    │
│    │via      │ │via      │ │via      │    │
│    │Adapter  │ │Adapter  │ │Adapter  │    │
│    └────┬────┘ └────┬────┘ └────┬────┘    │
│         │           │          │            │
│         └─────┐     │    ┌─────┘            │
│               ▼     ▼    ▼                  │
│         ┌──────────────────────┐            │
│         │  Cross-project       │            │
│         │  aggregatie (SQLite) │            │
│         │  health, metrics,    │            │
│         │  governance scores   │            │
│         └──────────────────────┘            │
│                                             │
│  Kennis: Markdown/YAML (docs/, knowledge/)  │
│  Geen vectorstore, geen graaf-database      │
└─────────────────────────────────────────────┘
```

### Stack: Python + SQLite + Markdown/YAML

| Component | Technologie | Motivatie |
|-----------|------------|-----------|
| **Multi-tenancy** | NodeRegistry + adapters | Al operationeel; elke project = node + adapter. Bewezen patroon met BorisAdapter |
| **Per-project data** | SQLite per adapter | Natuurlijke isolatie; elke adapter beheert eigen data. 5 projecten = 5 SQLite bestanden |
| **Cross-project aggregatie** | 1 DevHub-level SQLite | Health scores, sprint velocity, governance compliance over alle projecten. Querybaar voor trends |
| **KWP DEV kennis** | Markdown/YAML in `docs/`, `knowledge/` | Gestructureerde kennis (Golden Path templates, ADR-patronen, governance checklists). Grep/search is sneller en transparanter dan vectorsearch voor honderden documenten |
| **Golden Path templates** | Markdown in `knowledge/golden-paths/` | Herbruikbare patronen voor projecten (o.a. BNS-stack patroon, zie BORIS research-voorstel) |

### Waarom geen vectorstore voor KWP DEV?

DevHub's kennis is fundamenteel anders dan BORIS' kennis. BORIS heeft ongestructureerde tekst (zorgprotocollen, wetenschappelijke papers) waar vectorsearch meerwaarde biedt. DevHub's kennis is gestructureerd: templates met vaste secties, ADR's met vaste structuur, governance checklists. Conventionele naamgeving + grep/search werkt hier beter, met nul extra dependencies.

### Waarom geen graaf-database?

DevHub bouwt kennisgrafen voor projecten (Het Brein in BORIS). DevHub zelf heeft geen kennisgraaf nodig. De relaties tussen DevHub-concepten (agents, skills, governance-regels, projecten) zijn hiërarchisch en statisch — perfect voor YAML-configuratie, niet voor een graaf-database.

### Schaalpunten (gedocumenteerde triggers)

| Trigger | Huidige waarde | Drempel | Actie |
|---------|---------------|---------|-------|
| Aantal projecten | 1 | >10 | Evalueer PostgreSQL als vervanging voor SQLite cross-project DB |
| Concurrent queries | ~1 (single user) | >50 | Evalueer PostgreSQL (SQLite single-writer limiet) |
| KWP DEV documenten | ~50 | >500 | Evalueer ChromaDB als embedded vectorstore voor dev-kennis retrieval |
| Adapter-complexiteit | 1 (BorisAdapter) | >5 unieke adapters | Evalueer abstracte AdapterFactory + generieke adapter-generatie |

## Cross-project aggregatie schema (voorstel)

```sql
-- DevHub cross-project metrics
CREATE TABLE project_health (
    project_id TEXT NOT NULL,        -- node_id uit nodes.yml
    dimension TEXT NOT NULL,          -- health-dimensie (tests, coverage, debt, docs, security, performance)
    score REAL NOT NULL,              -- 0.0 – 1.0
    measured_at REAL NOT NULL,        -- Unix timestamp
    measured_by TEXT NOT NULL,        -- "devhub-health" skill of agent
    PRIMARY KEY (project_id, dimension, measured_at)
);

CREATE TABLE sprint_metrics (
    project_id TEXT NOT NULL,
    sprint_id TEXT NOT NULL,
    velocity INTEGER,                 -- story points / taken afgerond
    planned INTEGER,
    completed INTEGER,
    carry_over INTEGER,
    started_at REAL,
    completed_at REAL,
    PRIMARY KEY (project_id, sprint_id)
);

CREATE TABLE governance_scores (
    project_id TEXT NOT NULL,
    check_type TEXT NOT NULL,         -- "constitution", "dor", "impact_zone", "test_baseline"
    passed BOOLEAN NOT NULL,
    details TEXT,                      -- JSON: welke checks gefaald
    checked_at REAL NOT NULL,
    PRIMARY KEY (project_id, check_type, checked_at)
);
```

## Golden Path: BNS-stack patroon

Dit research-voorstel genereert ook een Golden Path template voor toekomstige projecten die Bayesian Network Systems nodig hebben. De BORIS-implementatie (pgmpy/pyAgrum + Neo4j + Weaviate) wordt na validatie gedocumenteerd als herbruikbaar patroon in `knowledge/golden-paths/BNS_STACK.md`.

**Inhoud template (na BORIS-validatie):**
- Wanneer wel/niet een BNS gebruiken (decision tree)
- Library-keuze (pgmpy vs. pyAgrum: wanneer welke)
- Database-architectuur (wanneer Neo4j nodig, wanneer SQLite volstaat)
- CPT-persistentie patroon
- Integratiepatroon met DevHub adapters

**Afhankelijkheid:** BORIS BNS Sprint 1 (library-spike) + Sprint M (Neo4j integratie) moeten afgerond zijn voordat de Golden Path betrouwbaar is.

## Bronnen & Evidence

| Bron | Type | Relevantie | Grade |
|------|------|-----------|-------|
| [SQLite Renaissance 2025-2026](https://dev.to/pockit_tools/the-sqlite-renaissance) | Blog/analyse | SQLite productie-geschiktheid, WAL-mode, 180k reads/sec | BRONZE |
| NodeRegistry + BorisAdapter (repo, geverifieerd) | Primaire bron | Bestaand multi-tenancy patroon | GOLD (eigen code) |
| DevHub CLAUDE.md + nodes.yml (repo, geverifieerd) | Primaire bron | Huidige architectuur | GOLD (eigen code) |

## Deliverables voor Claude Code

- [ ] **Cross-project SQLite schema** — implementeer bovenstaand schema in `devhub/data/cross_project.db`
- [ ] **AdapterInterface uitbreiding** — methodes voor health/sprint/governance reporting naar cross-project DB
- [ ] **Golden Path template** — `knowledge/golden-paths/BNS_STACK.md` (na BORIS Sprint 1 + M validatie)
- [ ] **Schaalpunt-documentatie** — vastleggen in ADR wanneer SQLite → PostgreSQL migratie triggert

## Afhankelijkheden

| Afhankelijkheid | Geblokkeerd door | Impact |
|----------------|-----------------|--------|
| Cross-project SQLite | Fase 2 (DevHub) | Geen BORIS-impact |
| AdapterInterface uitbreiding | Fase 2 + cross-project schema | Geen BORIS-impact |
| Golden Path BNS | BORIS Sprint 1 + Sprint M | Wacht op BORIS-validatie |
| 2e project registratie | Fase 5 (uitbreiding) | Test van multi-project architectuur |

## Prioriteit

**Middel** — nodig voor Fase 2 maar niet blokkerend voor BORIS-sprints.

**Motivatie:** de cross-project laag wordt pas echt waardevol bij project #2. Maar het schema en de AdapterInterface-uitbreiding kunnen nu al gebouwd worden zodat de fundamenten er staan.

## DEV_CONSTITUTION Impact

| Artikel | Impact |
|---------|--------|
| Art. 4 (Transparantie) | Cross-project metrics maken governance-compliance zichtbaar over alle projecten |
| Art. 5 (Kennisintegriteit) | Golden Path templates krijgen EVIDENCE-grading na validatie |
| Art. 6 (Project-soevereiniteit) | Adapters respecteren project-eigen constraints; cross-project DB is read-only aggregatie |
| Art. 7 (Impact-zonering) | GREEN — geen destructieve operaties, alleen leesbare metrics |

## Open vragen voor Claude Code

1. Moet de cross-project SQLite in `devhub/data/` of in een dedicated `data/` root-directory?
2. Hoe triggert de health-skill het wegschrijven naar cross-project DB? Via DevOrchestrator of direct?
3. Moet de AdapterInterface ABC backward-compatible blijven met bestaande BorisAdapter?
4. Is er een bestaand test-patroon voor cross-project queries (meerdere adapters mocken)?
