# devhub-health — Node-Agnostische Gezondheidscheck Skill

## Trigger
Activeer bij: "health check", "systeem status", "gezondheidscheck", "is alles ok", "hoe gezond is het systeem", "draai een check", "audit", "check de node".

## Doel
Volledige gezondheidscheck van een managed node via de NodeInterface/BorisAdapter. Produceert een gestructureerd rapport met drempelwaarden (gezond/aandacht/kritiek), concrete bevindingen en alert routing. Deterministisch, read-only, node-agnostisch.

De kracht: (1) het vaste contract (`FullHealthReport`) met severity levels zorgt voor consistente, vergelijkbare rapporten, (2) de 7-dimensie workflow dekt alle aspecten, (3) alert routing (P1/P2 → GitHub Issues) voorkomt dat kritieke issues onopgemerkt blijven.

---

## Setup

De target node moet geregistreerd zijn in `config/nodes.yml`.

```python
from devhub_core.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")
```

---

## Workflow

### Stap 0: Node-context laden

```python
report = adapter.get_report()  # NodeReport: health, doc_status, observaties
claude_md = adapter.read_claude_md()  # Actieve sprint, constraints
overdracht = adapter.read_overdracht()  # Recente beslissingen
```

Noteer de laatst gerapporteerde testcount uit OVERDRACHT.md voor vergelijking.

### Stap 1: Geautomatiseerde Health Check

De kern van deze skill — roep de geïntegreerde health check aan:

```python
from devhub_core.contracts.node_interface import FullHealthReport

health_report: FullHealthReport = adapter.run_full_health_check()
```

Dit voert 7 dimensies uit in volgorde:
1. **Code Quality** — tests (`run_tests()`) + lint (`run_lint()`)
2. **Dependencies** — CVE scan (`run_pip_audit()`)
3. **Version Consistency** — versie-sync check (`get_version_info()`)
4. **Architecture** — module/config/CI integriteit (`get_architecture_scan()`)
5. **Knowledge Health** — domein-dekking, RQ-dekking, grading, freshness (Sprint 35)
6. **Vectorstore** — curator audit of directory fallback
7. **n8n Workflows** — bereikbaarheid en workflow count

#### Stap 1.5: Knowledge Health (optioneel, als vectorstore beschikbaar)

```python
from devhub_core.research.knowledge_health import KnowledgeHealthChecker
from devhub_core.research.knowledge_config import load_knowledge_config
from devhub_core.research.knowledge_store import KnowledgeStore

config = load_knowledge_config(
    Path("config/knowledge.yml"),
    Path("config/agent_knowledge.yml"),
)
# Alleen als vectorstore beschikbaar:
checker = KnowledgeHealthChecker(config, store)
health_dim = checker.check()
```

Als vectorstore offline: rapporteer "Knowledge Health: niet testbaar — vectorstore offline".

Beoordeling:
| Aspect | Gezond | Aandacht | Kritiek |
|--------|--------|----------|---------|
| Domein-dekking | Alle domeinen ≥1 artikel | >50% domeinen leeg | >80% domeinen leeg |
| RQ-dekking | ≥80% gemiddeld | 50-79% | <50% |
| Grading | ≥30% SILVER+GOLD | 10-29% | <10% |
| Freshness | Geen stale domeinen | 1-2 stale | ≥3 stale |

### Stap 2: MCP Services (optioneel, als backend draait)

Als de node een MCP backend heeft:
- Roep `buurts_health_check` MCP tool aan (als beschikbaar)
- Als backend offline: noteer als "niet testbaar — backend offline"
- Ga door met lokale checks

Beoordeling:
| Component | Gezond | Aandacht | Kritiek |
|-----------|--------|----------|---------|
| ChromaDB | Bereikbaar, collections aanwezig | < verwacht | Niet bereikbaar |
| Weaviate | Bereikbaar, tenants actief | Geen tenants | Niet bereikbaar |
| Ollama | Bereikbaar, model geladen | Geen model | Niet bereikbaar |
| HITL queue | ≤ 10 items | 11-50 items | > 50 items |

### Stap 3: Rapport genereren

Gebruik het `FullHealthReport` object:

```python
# Overall status
print(f"Overall: {health_report.overall.value}")  # healthy/attention/critical

# Per dimensie
for check in health_report.checks:
    print(f"{check.dimension}: {check.status.value} — {check.summary}")
    for finding in check.findings:
        print(f"  [{finding.severity.value}] {finding.message}")
```

Genereer het rapport in dit format:

```
## Health Report — [node_id] — [datum]

### Overall: [✅ Gezond | ⚠️ Actie nodig | ❌ Kritiek]

| Dimensie | Status | Samenvatting |
|----------|--------|-------------|
| Code Quality | [✅/⚠️/❌] | [summary] |
| Dependencies | [✅/⚠️/❌] | [summary] |
| Version Consistency | [✅/⚠️/❌] | [summary] |
| Architecture | [✅/⚠️/❌] | [summary] |
| Knowledge Health | [✅/⚠️/❌] | [summary] |
| Vectorstore | [✅/⚠️/❌] | [summary] |
| n8n Workflows | [✅/⚠️/❌] | [summary] |

### Bevindingen
[Genummerde lijst per severity: P1 > P2 > P3 > P4]

### Aanbevelingen
[Concrete acties per bevinding]
```

### Stap 4: HEALTH_STATUS.md bijwerken

Schrijf een compact statusbestand (< 25 regels) naar de node's project root:

```markdown
# [Node ID] System Status
_Laatste check: [DATUM] [TIJD]_

## Overall: [✅ Gezond | ⚠️ Actie nodig | ❌ Kritiek]

| Dimensie | Status | Kernbevinding |
|----------|--------|---------------|
| Code Quality | [✅/⚠️/❌] | [1 zin] |
| Dependencies | [✅/⚠️/❌] | [1 zin] |
| Architecture | [✅/⚠️/❌] | [1 zin] |
| Vectorstore | [✅/⚠️/❌] | [1 zin] |
| n8n | [✅/⚠️/❌] | [1 zin] |

## Open Health Issues
[Lijst van actieve issues, of: geen]
```

### Stap 5: Alert Routing

Gebruik de severity niveaus uit het contract:

| Severity | Definitie | Actie |
|----------|-----------|-------|
| P1 — Critical | Platform werkt niet, data verlies mogelijk | GitHub Issue (label: `health-alert`, `P1`) |
| P2 — Degraded | Kern-functionaliteit beperkt | GitHub Issue (label: `health-alert`, `P2`) |
| P3 — Attention | Kwaliteitsproblemen, geen directe impact | Alleen in rapport |
| P4 — Info | Trends, kleine afwijkingen | Alleen in volledig rapport |

```python
# Check voor alert-waardige bevindingen
alerts = health_report.alert_findings  # P1 + P2

for finding in alerts:
    # Deduplicatie: check eerst of er al een open issue bestaat
    # mcp__github__search_issues(q=f"repo:ORG/REPO [HEALTH {finding.severity.value}] is:open")
    # Als geen duplicate: mcp__github__create_issue(...)
    pass
```

**GitHub Issue format:**
- Title: `[HEALTH P1] [korte beschrijving]` of `[HEALTH P2] [korte beschrijving]`
- Body: bevinding + drempelwaarde + aanbevolen actie
- Labels: `["health-alert", "P1"]` of `["health-alert", "P2"]`

### Stap 6: Architectuur-audit (optioneel)

Alleen als de developer expliciet vraagt, of als er ≥2 P2-bevindingen zijn:

1. Laad de audit-prompt (als aanwezig in de node)
2. Voer 6-dimensie audit uit (Content, Agents, Safety, Arch, Governance, TELOS)
3. Sla op als `docs/reports/SYSTEM_AUDIT_<DATUM>.md`
4. Delta-berekening tegen vorig rapport (als beschikbaar)
5. Presenteer top-5 bevindingen + max 3 aanbevelingen

---

## Regels (altijd van toepassing)

- Health check is **ALTIJD read-only** — nooit corrigerende acties zonder akkoord
- Bij ❌ Kritiek: **direct melden** aan developer, geen automatische fixes
- **Deterministisch**: geen LLM-aanroepen in het health check proces zelf
- Backend offline → voer alle lokale checks uit, noteer wat niet testbaar was
- Vergelijk testcount met laatst gerapporteerde count in OVERDRACHT.md
- HEALTH_STATUS.md wordt **ALTIJD bijgewerkt**, ook als overall ✅ Gezond
- GitHub Issues alleen voor P1/P2 — niet voor P3/P4
- **Developer beslist. DevHub voert uit.**

## Contract Referentie

Alle dataklassen in `devhub/contracts/node_interface.py`:

| Contract | Doel |
|----------|------|
| `FullHealthReport` | Volledig rapport met alle dimensies |
| `HealthCheckResult` | Resultaat per dimensie |
| `HealthFinding` | Individuele bevinding met severity |
| `HealthStatus` | Enum: HEALTHY / ATTENTION / CRITICAL |
| `Severity` | Enum: P1_CRITICAL / P2_DEGRADED / P3_ATTENTION / P4_INFO |
