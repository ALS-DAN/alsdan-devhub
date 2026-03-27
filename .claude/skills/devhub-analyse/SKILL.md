# devhub-analyse — Kennisbank Syntheseskill

## Trigger
Activeer bij: "analyseer", "analyse", "onderzoek en rapporteer", "kennisrapport", "synthesize", "wat weet ik over".

## Doel
Synthetiseer bestaande kennis uit KWP DEV tot een gestructureerd analysedocument. Verbindt de volledige kennispipeline: KWP DEV retrieval → lacune-detectie → synthese → ODF/Markdown document → opslag.

**Verschil met `/devhub-research-loop`:**
| Aspect | research-loop | analyse |
|--------|--------------|---------|
| Focus | Nieuwe kennis vergaren | Bestaande kennis synthetiseren |
| Output | Kennisnotitie (`knowledge/`) | Analysedocument (`docs/analyses/`) |
| Claude-rol | Bronnen beoordelen + schrijven | Synthese op basis van KWP DEV |
| Opslag | `knowledge/{domein}/` | `docs/analyses/` + optioneel Drive |

---

## Setup

```python
from devhub_core.contracts.analysis_contracts import AnalysisRequest, AnalysisType
from devhub_core.contracts.research_contracts import ResearchDepth
from devhub_core.analysis.template_loader import TemplateLoader
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_core.agents.analysis_pipeline import AnalysisPipeline
```

---

## Workflow

### Stap 1: Vraag interpreteren

Bepaal op basis van de vraag:

| Aspect | Opties |
|--------|--------|
| **AnalysisType** | `sota` (stand van zaken) / `comparative` (A vs B) / `application` (hoe past X in DevHub?) / `free` (vrije vraag) |
| **Domeinen** | `ai_engineering` / `claude_specific` / `python_architecture` / `development_methodology` |
| **Diepte** | `quick` (snel overzicht) / `standard` (volledig) / `deep` (grondig) |
| **skip_research** | `False` standaard — `True` als developer alleen bestaande kennis wil exporteren |

**AnalysisType kiezen:**
- "Wat is de huidige stand van..." → `sota`
- "Vergelijk X met Y" / "trade-offs tussen..." → `comparative`
- "Hoe past X in DevHub?" / "Kunnen we X gebruiken?" → `application`
- Alles anders → `free`

### Stap 2: AnalysisRequest aanmaken

```python
from datetime import UTC, datetime

request = AnalysisRequest(
    request_id=f"ANALYSE-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
    title="<Beschrijvende titel>",
    question="<De onderzoeksvraag>",
    analysis_type=AnalysisType.FREE,  # of SOTA, COMPARATIVE, APPLICATION
    domains=("ai_engineering",),       # relevante domeinen
    skip_research=False,               # True = alleen bestaande kennis
    output_format="markdown",          # of "odf"
    output_dir="docs/analyses",
    requesting_agent="devhub-analyse-skill",
    created_at=datetime.now(UTC).isoformat(),
)
```

### Stap 3: Pipeline draaien

```python
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_core.research.in_memory_queue import InMemoryResearchQueue
from devhub_documents.factory import DocumentFactory
from devhub_storage.factory import StorageFactory

# Initialiseer backends
vectorstore = ChromaDBZonedStore()
knowledge_store = KnowledgeStore(vectorstore, HashEmbeddingProvider())
research_queue = InMemoryResearchQueue()
document_adapter = DocumentFactory().create_adapter()
local_storage = StorageFactory().create_adapter("local")

# Draai pipeline
pipeline = AnalysisPipeline(
    knowledge_store=knowledge_store,
    research_queue=research_queue,
    document_interface=document_adapter,
    local_storage=local_storage,
)
result = pipeline.run(request)
```

### Stap 4: Claude synthese (kern van de skill)

Na stap 3 rapporteer je aan de developer:
- Hoeveel artikelen gevonden (en hun graderings-mix)
- Welke lacunes gedetecteerd
- Toon de template-structuur

Schrijf dan de eigenlijke synthese-tekst per template-sectie, op basis van:
- De opgehaalde kennisartikelen
- Aanvullende bronnen indien nodig
- DEV_CONSTITUTION Art. 2 (verificatieplicht) en Art. 5 (kennisgradering)

### Stap 5: Resultaat rapporteren

```
## Analyse Rapport — [titel]

### Onderzoeksvraag
[De vraag]

### Kennisbasis
- Artikelen gebruikt: [N] (gradering: GOLD [x], SILVER [x], BRONZE [x], SPECULATIVE [x])
- Lacunes gedetecteerd: [N]
- Research-requests aangemaakt: [N]

### Document
Gegenereerd: docs/analyses/[bestandsnaam]

### Samenvatting
[2-3 zinnen kernbevinding]

### Kennisgradering
Analyse: [GOLD/SILVER/BRONZE/SPECULATIVE]
Reden: [onderbouwing op basis van gebruikte bronnen]
```

---

## Analyse-templates

| Type | Trigger | Secties |
|------|---------|---------|
| **sota** | "stand van zaken", "wat is de huidige situatie" | Context → Bevindingen → Trends → Lacunes → Conclusie |
| **comparative** | "vergelijk", "trade-offs", "A vs B" | Scope → Optie A → Optie B → Trade-offs → Lacunes → Aanbeveling |
| **application** | "hoe past", "kunnen we gebruiken", "geschikt voor" | Technologie → DevHub Context → Passendheid → Risicos → Lacunes → Conclusie |
| **free** | alles anders | Vraag → Bevindingen → Lacunes → Conclusie |

---

## Regels

- Art. 2 (Verificatieplicht): elke substantiële claim krijgt label [Geverifieerd/Aangenomen/Onbekend]
- Art. 5 (Kennisintegriteit): analysedocument vermeldt gradering + bronnen
- Analyse-output schrijft **alleen** naar `docs/analyses/` — nooit naar `knowledge/`
- Bij onvoldoende kennisartikelen (<3): lacune melden + research-request aanmaken
- Developer beslist altijd of lacunes opgevuld worden voor publicatie

## Contract Referentie

| Component | Pad |
|-----------|-----|
| `AnalysisPipeline` | `packages/devhub-core/devhub_core/agents/analysis_pipeline.py` |
| `AnalysisRequest/Result` | `packages/devhub-core/devhub_core/contracts/analysis_contracts.py` |
| `TemplateLoader` | `packages/devhub-core/devhub_core/analysis/template_loader.py` |
| Templates | `packages/devhub-core/devhub_core/templates/analysis/*.yml` |
| `KnowledgeStore.search()` | `packages/devhub-core/devhub_core/research/knowledge_store.py` |
