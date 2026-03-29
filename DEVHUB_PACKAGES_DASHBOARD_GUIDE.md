# DevHub Packages - Dashboard Consumption Guide

## Executive Summary

The DevHub system is organized as a **4-package Python uv workspace** (devhub-core, devhub-storage, devhub-vectorstore, devhub-documents) with a frozen dataclass-based contract system. The dashboard can consume rich data from health checks, sprint tracking, document pipelines, knowledge management, and agent event streams.

---

## Workspace Structure

### Configuration: `pyproject.toml`

```toml
[tool.uv.workspace]
members = [
    "packages/devhub-core",
    "packages/devhub-storage",
    "packages/devhub-vectorstore",
    "packages/devhub-documents",
]
```

- **Test framework**: pytest (asyncio_mode = "auto")
- **Linter**: ruff (E, F, W, B, UP rules; Python 3.11+)
- **Dev dependencies**: pytest, pytest-cov, ruff, hypothesis, chromadb

---

## Package 1: devhub-core (v0.2.0)

**Purpose**: Contracts, adapters, and orchestration agents for the DevHub platform.

### Key Contracts (Frozen Dataclasses)

All contracts are in `devhub_core/contracts/` and fully immutable (frozen=True).

#### 1.1 Node Interface (`node_interface.py`)

**What it measures for dashboard:**

- **NodeHealth**: `status` (UP/DEGRADED/DOWN), `components` (dict), `test_count`, `test_pass_rate`, `coverage_pct`
- **TestResult**: `total`, `passed`, `failed`, `errors`, `duration_seconds`, `coverage_pct`, computed `pass_rate` and `success` properties
- **NodeDocStatus**: `total_pages`, `stale_pages` (>30 days old), `diataxis_coverage` (tutorial/howto/reference/explanation counts)
- **NodeReport**: Complete snapshot with node_id, timestamp, health, doc_status, observations, safety_zones
- **FullHealthReport**: Multi-dimensional health with 7 dimensions (code quality, dependencies, version, architecture, knowledge, vectorstore, n8n)

**Health Check Severity Levels:**
- P1_CRITICAL: Platform broken, data loss risk
- P2_DEGRADED: Core functionality impaired
- P3_ATTENTION: Quality issues, no direct impact
- P4_INFO: Trends, minor deviations

**Overall Status Enum:**
- HEALTHY: All dimensions OK
- ATTENTION: At least one dimension needs action
- CRITICAL: At least one dimension critical

**Developer Coaching (`DeveloperProfile`, `CoachingResponse`):**
- Phase: ORIËNTEREN (learning), BOUWEN (building), BEHEERSEN (mastering)
- Signal: GREEN (active), ATTENTION (blocker >2 days), STAGNATION (no activity >5 days)
- Streak tracking, blocker counts, test delta, coaching actions

#### 1.2 Development & QA (`dev_contracts.py`)

**DevTaskRequest/DevTaskResult**: Task execution contracts
**DocGenRequest**: Documentation generation requests
**QAReport**: Code quality findings with 12 code checks + 6 doc checks

#### 1.3 Growth Tracking (`growth_contracts.py`)

**SkillRadarProfile**: Dreyfus 5-level skill model (1=novice → 5=master)
- Per-domain tracking with evidence and ZPD (Zone of Proximal Development) tasks
- T-shaped developer profile (deep vertical + broad horizontal)

**GrowthReport**: Periodical growth metrics
- `skill_radar`: Full radar snapshot
- `challenges_completed/proposed/skipped`: Deliberate practice counts
- `learning_recommendations`: Ranked by priority (URGENT/IMPORTANT/NICE_TO_HAVE)
- `deliberate_practice_minutes`: Cumulative effort tracking
- Scaffolding reductions (support fade tracking)

#### 1.4 Research Queue (`research_contracts.py`)

**ResearchRequest**: Knowledge pipeline queries
- Domain, depth (QUICK/STANDARD/DEEP), priority (1-10)
- RQ_tags: Research Question references
- Verification required flag

**ResearchResponse**: Knowledge answers
- Status: PENDING/IN_PROGRESS/COMPLETED/FAILED
- Grade: GOLD/SILVER/BRONZE/SPECULATIVE
- Verification percentage (0-100)

**ResearchQueue ABC**: Interface for priority-based knowledge retrieval

#### 1.5 Knowledge Curation (`curator_contracts.py`)

**KnowledgeDomain**: 16 domains across 3 rings
- Ring 1 (Core): AI_ENGINEERING, CLAUDE_SPECIFIC, PYTHON_ARCHITECTURE, DEVELOPMENT_METHODOLOGY, GOVERNANCE_COMPLIANCE
- Ring 2 (Agent): SPRINT_PLANNING, CODE_REVIEW, SECURITY_APPSEC, TESTING_QA, KNOWLEDGE_METHODOLOGY, COACHING_LEARNING, DOCUMENTATION, PRODUCT_OWNERSHIP
- Ring 3 (Project): HEALTHCARE_ICT, PRIVACY_AVG, MULTI_TENANCY

**KnowledgeArticle**: Structured knowledge for vectorstore
- article_id, title, content, domain, grade (GOLD/SILVER/BRONZE/SPECULATIVE)
- Verification %, sources, RQ_tags, entity_refs
- Convertible to DocumentChunk via `to_document_chunk()`

**CurationReport**: Validation verdict (APPROVED/NEEDS_REVISION/REJECTED)
- Auto-REJECTED if CRITICAL finding, auto-NEEDS_REVISION if ERROR

**KnowledgeHealthReport**: 4-dimensional audit
- Grading distribution (GOLD/SILVER/BRONZE/SPECULATIVE counts)
- Freshness score (0-100, 100=all fresh)
- Source ratio score (0-100, 100=diverse)
- Domain coverage (articles per domain)
- Overall score (weighted average)

#### 1.6 Document Pipeline (`pipeline_contracts.py`)

**DocumentProductionRequest**: What to generate
- topic, category, target_node, output_format, audience
- knowledge_query (for vectorstore lookup)
- skip_vectorstore flag

**KnowledgeContext**: Vectorstore results
- chunks (tuple of content strings)
- sources, query_used, total_found
- `has_content` property

**DocumentProductionResult**: Complete pipeline output
- document_result (DocumentResult with path, format, size, checksum)
- storage_path, publish_status (PENDING/PUBLISHED/SKIPPED/FAILED)
- node_id, message

#### 1.7 Event Bus (`event_contracts.py`)

**10 Typed Events:**
1. SprintStarted: sprint_id, node_id, sprint_type
2. SprintClosed: sprint_id, node_id, result (DevTaskResult)
3. TaskAssigned: task_id, agent_id, description
4. TaskCompleted: task_id, agent_id, result
5. TaskFailed: task_id, agent_id, error
6. QACompleted: task_id, report (QAReport)
7. DocGenRequested: request (DocGenRequest)
8. KnowledgeGapDetected: domain, gap_description, requesting_agent
9. HealthDegraded: dimension, score, threshold
10. ObservationEmitted: obs_type (ObservationType), payload, severity

**EventBusInterface ABC**:
- `publish(event)`: Emit to subscribers
- `subscribe(event_type, handler, event_filter)`: Register listener
- `history(event_type, limit)`: Retrieve past events

#### 1.8 Sprint Tracking (`pipeline_contracts.py`)

**FolderRoute**: Category → storage path mapping per node
**PublishStatus**: Document publication states

#### 1.9 Security Scanning (`scanner_contracts.py`)

**BootstrapAuditReport**: Knowledge bootstrap audit
**KnowledgeScanResult**: Scan result with domain status

### Agents (Computational Layer)

Public API exports in `agents/__init__.py`:
- **ChallengeEngine**: Generates deliberate practice challenges (SkillDomain → challenge)
- **ScaffoldingManager**: Manages support level reduction in learning
- **SecurityScanner**: OWASP ASI 2026 compliance checks

**Internal agents (in .claude/agents/ or package internals):**
- **DocsAgent**: Diátaxis-based documentation generation
- **QAAgent**: 18-check adversarial code review
- **ResearchAdvisor**: Knowledge pipeline orchestration
- **KnowledgeCurator**: Article validation & grading
- **DevOrchestrator**: Task decomposition, doc queue management
- **AnalysisPipeline**: Multi-agent observational synthesis
- **GrowthReportGenerator**: Periodical skill radar updates
- **DocumentService**: Production pipeline orchestrator

### Node Interface Pattern

Every node implements the `NodeInterface` ABC:

```python
@abstractmethod
def get_report(self) -> NodeReport: ...
@abstractmethod
def get_health(self) -> NodeHealth: ...
@abstractmethod
def list_docs(self) -> list[str]: ...
@abstractmethod
def run_tests(self) -> TestResult: ...
def get_review_context(self) -> ReviewContext: ...  # Default: empty
```

### Registry (`registry.py`)

**NodeRegistry**: YAML-driven multi-node configuration
- Loads from `config/nodes.yml`
- Lazy instantiates adapters (cached)
- `get_adapter(node_id)` returns NodeInterface implementer
- `list_nodes()` returns all registered NodeConfigs

---

## Package 2: devhub-storage (v0.3.0)

**Purpose**: Vendor-free storage interface with Google Drive, SharePoint, and local file adapters.

### Contracts (`contracts.py`)

**StorageItem**: File or directory metadata
- path, name, item_type (FILE/DIRECTORY), size_bytes, modified_at, created_at
- content_hash (SHA-256 for files, None for directories)
- metadata dict

**StorageTree**: Recursive tree structure
- item (StorageItem), children (tuple of StorageTree)
- Constraint: FILE items cannot have children

**StorageHealth**: Backend health status
- status (UP/DEGRADED/DOWN)
- backend (string identifier)
- root_path, total_items, total_size_bytes
- readable, writable booleans

**WriteResult**: Mutation operation outcomes
- success (bool), path, operation (put/mkdir/move/delete)
- bytes_written, message

**ChangeEvent** (Watchable mixin): File change notifications
- path, event_type (created/modified/deleted/moved), timestamp
- old_path (for moved events)

**DriftItem & DriftReport** (Reconcilable mixin): State vs. expectation
- drift_type (missing/extra/wrong_type/wrong_content)
- expected, actual, path

**ReconcileResult**: Reconciliation outcomes
- dry_run flag, actions_planned, actions_executed
- drifts_resolved, errors list

**Exceptions**:
- StorageError (base)
- StorageNotFoundError, StoragePermissionError, StoragePathError, StorageAlreadyExistsError

### StorageInterface (Abstract)

```python
list(path="", recursive=False) -> list[StorageItem]
get(path) -> StorageItem
search(pattern, path="") -> list[StorageItem]
tree(path="", max_depth=-1) -> StorageTree
put(path, content: bytes) -> WriteResult
mkdir(path) -> WriteResult
move(source, dest) -> WriteResult
delete(path) -> WriteResult
health() -> StorageHealth
```

### Adapters (4 implementations)

| Adapter | Backend | Features |
|---------|---------|----------|
| LocalAdapter | Filesystem | Full CRUD, tree traversal, reconciliation |
| DriveSyncAdapter | Google Drive | Bi-directional sync, change tracking |
| GoogleDriveAdapter | Google Drive | OAuth2 + SA auth, file operations |
| SharePointAdapter | SharePoint | MSAL auth, document library access |

### Factory Pattern

```python
StorageFactory.create("local", root_path="/tmp/data")
StorageFactory.create("google_drive", auth=oauth2_auth, root_folder_id="xxx")
StorageFactory.available_backends() -> ["local", "drive_sync", "google_drive", "sharepoint"]
```

### Mixins

- **Watchable**: `watch(callback: Callable[[ChangeEvent], None])`
- **Reconcilable**: `reconcile(spec: ReconciliationSpec) -> ReconcileResult`
- **Organizable**: Folder routing, categorization helpers

---

## Package 3: devhub-vectorstore (v0.3.0)

**Purpose**: Vendor-free vector database interface with ChromaDB and Weaviate adapters.

### Contracts (`contracts/vectorstore_contracts.py`)

**DataZone** (Enum): Data isolation levels
- RESTRICTED: Locked down, RBAC required
- CONTROLLED: Access via review queue
- OPEN: Public, read-all-write-authenticated

**TenantStrategy** (Enum):
- PER_ZONE: One collection per zone (default)
- PER_KWP: Native Weaviate tenant sharding

**DocumentChunk**: Vector-ready document
- chunk_id, content, zone (DataZone)
- embedding (tuple[float, ...] | None) — pre-computed or None for adapter calculation
- metadata (tuple[tuple[str, str], ...]) — immutable metadata pairs
- source_id, created_at (ISO 8601)
- `metadata_dict` property for convenient access

**RetrievalRequest**: Query specification
- query_text (string) or query_embedding (vector)
- zone (DataZone | None) — None searches all zones
- limit (int), min_score (float 0.0-1.0)
- tenant_id (for PER_KWP strategy)
- metadata_filter (tuple of key-value pairs)

**SearchResult**: One query hit
- chunk (DocumentChunk), score (float 0.0-1.0, cosine similarity)

**RetrievalResponse**: Query results
- results (tuple[SearchResult, ...])
- total_found (int), query_duration_ms (float)

**VectorStoreHealth**: Backend health
- status (UP/DEGRADED/DOWN)
- backend (string: "chromadb", "weaviate")
- collection_count, total_chunks, tenant_count

**EmbeddingProvider** (ABC): Optional embedding calculation
- `dimension` property (int)
- `embed_text(text: str) -> tuple[float, ...]`
- `embed_batch(texts: list[str]) -> list[tuple[float, ...]]`

### VectorStoreInterface (Abstract)

```python
add_chunk(chunk: DocumentChunk) -> None
add_chunks(chunks: list[DocumentChunk]) -> int  # Returns count added
query(request: RetrievalRequest) -> RetrievalResponse
count() -> int  # Total chunks
count_by_zone() -> dict[DataZone, int]  # Per-zone breakdown
reset() -> None  # Clear all data
ensure_tenant(tenant_id: str) -> None
list_tenants() -> list[str]
health() -> VectorStoreHealth
```

### Adapters (2 implementations)

| Adapter | Backend | Features |
|---------|---------|----------|
| ChromaDBAdapter | ChromaDB | In-memory/persistent, built-in embedding support |
| WeaviateAdapter | Weaviate | Distributed, native multi-tenancy, GraphQL API |

### Embedding Providers

| Provider | Library | Dimension | Notes |
|----------|---------|-----------|-------|
| SentenceTransformerProvider | sentence-transformers | 384/768/1024 | All-MiniLM-L6-v2 default |
| HashEmbeddingProvider | Built-in | Configurable | Deterministic hashing for testing |

### Factory Pattern

```python
VectorStoreFactory.create("chromadb", persist_dir="/tmp/chroma")
VectorStoreFactory.create("weaviate", url="http://localhost:8080")
EmbeddingFactory.create("sentence_transformer", model="all-MiniLM-L6-v2")
```

### Statistics/Metrics Available to Dashboard

From **VectorStoreHealth**:
- Collection count (how many indexed collections)
- Total chunks (all documents indexed)
- Tenant count (multi-tenant instances)
- Backend status (UP/DEGRADED/DOWN)

From **RetrievalResponse**:
- Query execution time (ms)
- Result relevance (per-chunk similarity scores)
- Coverage (total_found vs. limit requested)

Custom metrics via `count_by_zone()`:
- Zone-wise document distribution (RESTRICTED/CONTROLLED/OPEN)

---

## Package 4: devhub-documents (v0.1.0)

**Purpose**: Vendor-free document generation interface with Markdown and ODF support.

### Contracts (`contracts.py`)

**DocumentFormat** (Enum):
- ODF: OpenDocument Format (odt/ods/odp)
- MARKDOWN: Plain text markdown

**DocumentCategory** (Enum): Diátaxis + Process + Knowledge

*Laag 1 (Product):*
- TUTORIAL, HOWTO, REFERENCE, EXPLANATION

*Laag 2 (Process):*
- PATTERN, ANALYSIS, DECISION, RETROSPECTIVE

*Laag 3 (Knowledge):*
- METHODOLOGY, BEST_PRACTICE, SOTA_REVIEW, PLAYBOOK

**DocumentSection**: Hierarchical content
- heading, content, level (1-6), subsections (tuple[DocumentSection, ...])
- `to_dict()` for serialization

**DocumentMetadata**: Document properties
- author, category, date, grade (GOLD/SILVER/BRONZE/SPECULATIVE | None)
- sources (tuple[str, ...]), tags, version

**DocumentRequest**: Generation input
- title, sections (tuple[DocumentSection, ...])
- metadata (DocumentMetadata)
- output_format (DocumentFormat), template (string), output_dir

**DocumentResult**: Generation output
- path (generated file path)
- format (DocumentFormat)
- size_bytes, checksum (SHA-256 hex)

### DocumentInterface (Abstract)

```python
create(request: DocumentRequest) -> DocumentResult
from_template(template_path: str, data: dict) -> DocumentResult
supported_formats() -> list[str]  # e.g., ["odf", "markdown"]
```

### Adapters (2 implementations)

| Adapter | Format | Features |
|---------|--------|----------|
| MarkdownAdapter | MARKDOWN | Pandoc integration, YAML frontmatter |
| ODFAdapter | ODF | python-odf library, formatting preservation |

### Document Pipeline Integration

The `DocumentProductionRequest` → **DocumentService** → `DocumentProductionResult` flow:

1. **KnowledgeContext** retrieved from vectorstore
2. **DocumentRequest** constructed from production request
3. **DocumentInterface.create()** generates file
4. **DocumentResult** published to storage
5. **PublishStatus** tracked (PENDING/PUBLISHED/SKIPPED/FAILED)

---

## What the Dashboard Can Import & Use

### Tier 1: Direct Data Access (Recommended)

```python
# Health Checks
from devhub_core.contracts import (
    FullHealthReport, HealthCheckResult, HealthStatus, HealthFinding, Severity,
    NodeHealth, NodeReport, NodeDocStatus, TestResult
)

# Sprint Tracking
from devhub_core.contracts import SprintStarted, SprintClosed, TaskAssigned, TaskCompleted

# Growth Tracking
from devhub_core.contracts import (
    GrowthReport, SkillRadarProfile, SkillDomain, DevelopmentChallenge,
    LearningRecommendation, DeveloperProfile, CoachingResponse
)

# Knowledge Management
from devhub_core.contracts import (
    KnowledgeArticle, CurationReport, KnowledgeHealthReport,
    KnowledgeDomain, CurationVerdict
)

# Research Pipeline
from devhub_core.contracts import (
    ResearchRequest, ResearchResponse, ResearchStatus, ResearchDepth
)

# Document Production
from devhub_core.contracts import DocumentProductionRequest, DocumentProductionResult
from devhub_documents.contracts import DocumentFormat, DocumentCategory, DocumentResult

# Events
from devhub_core.contracts import EventBusInterface, Event  # Subscribe to streams

# Storage
from devhub_storage import (
    StorageInterface, StorageHealth, StorageItem, StorageTree, WriteResult,
    StorageFactory
)

# Vectorstore
from devhub_vectorstore import (
    VectorStoreInterface, VectorStoreHealth, SearchResult, DocumentChunk,
    VectorStoreFactory
)
```

### Tier 2: Node Registry Access

```python
from devhub_core.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(Path("config/nodes.yml"))

# Get adapter for a specific node
adapter = registry.get_adapter("boris-buurts")  # NodeInterface implementer

# Get node data
report: NodeReport = adapter.get_report()
health: NodeHealth = adapter.get_health()
test_result: TestResult = adapter.run_tests()
```

### Tier 3: Agent Output Consumption

```python
# These agents produce data the dashboard can visualize
from devhub_core.agents import (
    ChallengeEngine,  # → DevelopmentChallenge
    ScaffoldingManager,  # → Scaffolding level changes
    SecurityScanner  # → SecurityAuditReport
)
```

### Tier 4: Data Structures for Display

**Health Check Dashboard:**
```python
# From FullHealthReport
checks: tuple[HealthCheckResult, ...]  # 7 dimensions
overall: HealthStatus
p1_findings: list[HealthFinding]  # Critical issues
p2_findings: list[HealthFinding]  # Degraded functionality
alert_findings: list[HealthFinding]  # P1+P2 for GitHub Issues
```

**Sprint Progress Dashboard:**
```python
# From Event history
SprintStarted events → sprint_id, sprint_type, node_id
TaskCompleted events → task_id, agent_id, result (DevTaskResult)
```

**Knowledge Health Dashboard:**
```python
# From KnowledgeHealthReport
grading_distribution: {"GOLD": 5, "SILVER": 12, "BRONZE": 3}
freshness_score: 87.5  # 0-100
source_ratio_score: 92.0  # 0-100
domain_coverage: {"ai_engineering": 8, "claude_specific": 5, ...}
overall_score: 89.2
findings: tuple[CurationFinding, ...]
```

**Developer Growth Dashboard:**
```python
# From GrowthReport
skill_radar.domains[0].level: 3  # Dreyfus 1-5
skill_radar.t_shape_deep: ("python", "system_design")
skill_radar.t_shape_broad: ("testing", "devops", "documentation")
challenges_completed: 4
deliberate_practice_minutes: 240
learning_recommendations: [LearningRecommendation(...), ...]
```

**Document Production Dashboard:**
```python
# From DocumentProductionResult
document_result.path: "docs/generated/ai_engineering_guide.md"
publish_status: PublishStatus.PUBLISHED
knowledge_context.total_found: 42
knowledge_context.chunks: tuple of source passages
```

---

## Data Flow: Health Check Example

```
Dashboard Request → NodeRegistry.get_adapter("boris-buurts")
    ↓
    Adapter (NodeInterface impl) → adapter.get_report()
    ↓
    Returns NodeReport:
      - health: NodeHealth {status: "DEGRADED", components: {...}}
      - doc_status: NodeDocStatus {total_pages: 42, stale_pages: 3}
      - observations: ["Test coverage dropped", "API docs outdated"]
    ↓
    Dashboard displays:
      - Overall status badge (DEGRADED)
      - Component health matrix
      - Test pass rate metric
      - Stale documentation count
```

---

## Data Flow: Knowledge Health Example

```
Dashboard Request → VectorStoreFactory.create("chromadb")
    ↓
    Query: RetrievalRequest(query_text="ai engineering", zone=OPEN, limit=10)
    ↓
    Returns RetrievalResponse:
      - results: tuple[SearchResult with DocumentChunk + score]
      - total_found: 8
      - query_duration_ms: 42.5
    ↓
    Parallel: KnowledgeCurator.audit()
    ↓
    Returns KnowledgeHealthReport:
      - grading_distribution: {"GOLD": 2, "SILVER": 5, ...}
      - freshness_score: 85.0
      - domain_coverage: {"ai_engineering": 8, ...}
    ↓
    Dashboard displays:
      - Knowledge quality pie chart (GOLD % / SILVER % / ...)
      - Freshness trend
      - Domain coverage matrix
      - Recent queries + response times
```

---

## Key Design Patterns for Dashboard

### 1. Immutable Contracts

All dataclasses are `frozen=True` — dashboard can cache without side effects.

### 2. Zone-Based Access Control

DocumentChunk.zone (DataZone) enables role-based visualization:
- OPEN: Public dashboard
- CONTROLLED: Review-gated display
- RESTRICTED: Admin-only

### 3. Severity Levels

Uniform severity across all findings:
- CRITICAL: Immediate alert
- ERROR: Dashboard warning
- WARNING: Dashboard notice
- INFO: Log/archive

### 4. Timestamps ISO 8601

All timestamps in contracts use ISO 8601 format — standardized parsing across frontend/backend.

### 5. Lazy Adapter Instantiation

NodeRegistry caches adapters — dashboard doesn't re-create expensive connections.

### 6. Event-Driven Architecture

Subscribe to EventBusInterface for real-time updates:
```python
bus.subscribe(HealthDegraded, lambda event: refresh_health_dashboard())
bus.subscribe(TaskCompleted, lambda event: update_sprint_progress())
```

---

## Sprint Intake Data Available

From `docs/planning/inbox/` YAML files:

```yaml
---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX  # Track intake completion
node: devhub  # Which node owns this sprint
sprint_type: FEAT  # FEAT|SPIKE|CHORE|BUG
fase: 3  # Current phase (1-5)
---
```

Dashboard can query:
- `status: INBOX` → candidates for sprint-prep
- `status: DONE` → completed intakes
- Per-node breakdown of active sprints

---

## Testing & Validation Data

From contract validation:

```python
# FullHealthReport auto-computes overall status
checks = [
    HealthCheckResult("code_quality", HEALTHY, ...),
    HealthCheckResult("dependencies", CRITICAL, ...),
]
report = FullHealthReport(node_id="...", checks=checks)
# Automatically sets overall = CRITICAL (worst of all)
```

Dashboard can trust this logic — no need to recompute.

---

## Public API Guarantees

**Never breaking:**
- Frozen dataclass fields (add-only in new versions)
- Enum values (never removed)
- Abstract method signatures (ABC contracts)

**Safe to depend on:**
- All imports from `__init__.py` files (public API)
- All `contracts` modules (vendor-free)
- All `factory` classes (extensible)

**Avoid depending on:**
- Internal modules (non-`__init__.py` imports)
- Concrete adapter implementations (use interfaces)
- Agent internals (call via registry only)

---

## Summary: Dashboard Toolkit

| Feature | Exports | Cardinality |
|---------|---------|------------|
| Health Checks | FullHealthReport, HealthCheckResult, HealthFinding | 1-to-many findings |
| Sprint Tracking | Event types (SprintStarted, TaskCompleted, etc.) | Real-time stream |
| Growth | GrowthReport, SkillRadarProfile, DevelopmentChallenge | Periodic reports |
| Knowledge | KnowledgeHealthReport, KnowledgeArticle, CurationReport | Continuous audit |
| Documents | DocumentProductionResult, DocumentCategory, DocumentFormat | On-demand generation |
| Storage | StorageHealth, StorageItem, StorageTree | Filesystem snapshots |
| Vectorstore | VectorStoreHealth, SearchResult, DocumentChunk | Query results |
| Configuration | NodeRegistry, NodeConfig | Multi-node setup |

**Total importable types**: 50+ frozen dataclasses, 8+ abstract interfaces, 10+ enums.
