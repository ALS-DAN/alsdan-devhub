# alsdan-devhub — Second Development Brain

## Identiteit

alsdan-devhub is Niels' project-agnostisch development-systeem. Het functioneert als een **Claude Code plugin + repository** dat development-kennis, governance en werkwijze borgt los van individuele projecten.

DevHub is de ontwikkelaar. Projecten (zoals buurts-ecosysteem/BORIS) zijn wat DevHub bouwt en onderhoudt.

## Drie-lagen architectuur

### Laag 1: Python-systeem (`packages/devhub-core/devhub_core/`)
De runtime — analyseert, decomponeert, checkt kwaliteit. Gemanaged als uv workspace.

| Component | Pad | Functie |
|-----------|-----|---------|
| NodeInterface ABC | `packages/devhub-core/devhub_core/contracts/node_interface.py` | Vendor-free interface (13 frozen dataclasses) |
| Dev contracts | `packages/devhub-core/devhub_core/contracts/dev_contracts.py` | DevTask, QAReport, DocGenRequest |
| Security contracts | `packages/devhub-core/devhub_core/contracts/security_contracts.py` | SecurityFinding, SecurityAuditReport (OWASP ASI) |
| BorisAdapter | `packages/devhub-core/devhub_core/adapters/boris_adapter.py` | Read-only adapter voor BORIS (38 methodes) |
| DevOrchestrator | `packages/devhub-core/devhub_core/agents/orchestrator.py` | Taakdecompositie, doc queue |
| DocsAgent | `packages/devhub-core/devhub_core/agents/docs_agent.py` | Diátaxis documentatie-generatie |
| QA Agent | `packages/devhub-core/devhub_core/agents/qa_agent.py` | 12 code + 6 doc checks, adversarial |
| NodeRegistry | `packages/devhub-core/devhub_core/registry.py` | YAML-driven, multi-node (`config/nodes.yml`) |

**Workspace packages:**
| Package | Pad | Status |
|---------|-----|--------|
| devhub-core | `packages/devhub-core/` | Actief (v0.2.0) |
| devhub-storage | `packages/devhub-storage/` | Stub (v0.1.0) |
| devhub-vectorstore | `packages/devhub-vectorstore/` | Stub (v0.1.0) |

**Aanroepen vanuit agents:**
```bash
uv run python -c "
from pathlib import Path
from devhub_core.registry import NodeRegistry
registry = NodeRegistry(Path('config/nodes.yml'))
adapter = registry.get_adapter('boris-buurts')
report = adapter.get_report()
"
```

### Laag 2: Claude Code plugin (`agents/`, `skills/`, `.claude-plugin/`)
De AI-interface — agents en skills die Claude Code gebruikers toegang geven tot het devhub-systeem.

| Component | Pad |
|-----------|-----|
| dev-lead (orchestrator) | `agents/dev-lead.md` |
| coder (implementatie) | `agents/coder.md` |
| reviewer (code review) | `agents/reviewer.md` |
| researcher (kennisverrijking) | `agents/researcher.md` |
| planner (sprint planning) | `agents/planner.md` |
| red-team (security audit) | `agents/red-team.md` |
| 8 skills | `.claude/skills/devhub-*/` |

### Laag 3: Second Brain (`docs/`, `knowledge/`)
Het geheugen — governance, kennis, beslissingen.

## Project-registry

Geregistreerde projecten als git submodules in `projects/`:

| Project | Pad | Node ID |
|---------|-----|---------|
| buurts-ecosysteem (BORIS) | `projects/buurts-ecosysteem/` | `boris-buurts` |

Node-configuratie: `config/nodes.yml`

## Werkwijze-kern

- **Shape Up**: Probleem → Oplossing → Grenzen → Appetite
- **DoR (Definition of Ready)**: 8-punten checklist vóór sprint-start
- **Impact-zonering**: GREEN (veilig, tests draaien) / YELLOW (review vereist) / RED (menselijke goedkeuring)
- **Verificatieplicht**: Claims verifiëren tegen primaire bronnen. Label: Geverifieerd / Aangenomen / Onbekend
- **Kennisgradering**: GOLD (bewezen) / SILVER (gevalideerd) / BRONZE (ervaring) / SPECULATIVE (aanname)

## Governance

- **DEV_CONSTITUTION.md**: `docs/compliance/DEV_CONSTITUTION.md` — 8 artikelen, altijd bindend
- **Project-soevereiniteit** (Art. 6): Wanneer je in een project werkt, gelden de regels van DAT project. DevHub overschrijft nooit project-regels.

## Constraints

- `.claude/agents/` (project-level agents: dev_orchestrator, docs_agent, qa_agent) zijn INTERN — niet wijzigen vanuit plugin-context
- `agents/` (plugin-level agents: dev-lead, coder) zijn voor DISTRIBUTIE
- Beide mogen naast elkaar bestaan
- Bestaande tests (218+) moeten altijd groen blijven
- Geen secrets, credentials of PII in commits (Art. 8)

## Beschikbare skills

| Skill | Functie |
|-------|---------|
| `/devhub-sprint` | Sprint lifecycle management |
| `/devhub-health` | 6-dimensie health check |
| `/devhub-mentor` | O-B-B developer coaching |
| `/devhub-sprint-prep` | Sprint voorbereiding |
| `/devhub-review` | Code review + anti-patronen |
| `/devhub-research-loop` | Kennisverrijking + bronnenonderzoek |
| `/devhub-governance-check` | DEV_CONSTITUTION compliance audit |
| `/devhub-redteam` | OWASP ASI 2026 security audit |
