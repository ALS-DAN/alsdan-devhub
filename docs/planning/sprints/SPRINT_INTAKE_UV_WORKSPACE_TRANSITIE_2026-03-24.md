# Sprint Intake: uv Workspace Transitie (Track A)

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: BACKLOG
fase: 3
prioriteit: P1
sprint_type: FEAT
---

## Doel

DevHub migreert van flat Python-structuur (`devhub/` + PYTHONPATH) naar een uv workspace met geïsoleerde packages onder `packages/`. Alle 339+ tests blijven groen. Dit is het fundament voor Track B (storage) en Track C (vectorstore).

## Probleemstelling

De huidige structuur schaalt niet. `devhub/` is één monolithisch package dat via `PYTHONPATH=/Users/nielspostma/alsdan-devhub` geactiveerd wordt — hardcoded naar Niels' machine. Er is geen manier om packages onafhankelijk te versionen, te testen of te distribueren naar producten. Nieuwe packages (devhub-storage, devhub-vectorstore) kunnen niet bestaan zonder workspace-structuur.

**Waarom nu:** Track B en C zijn beide geblokkeerd door dit werk. Dit is het kritieke pad voor Fase 3.

## Deliverables

### Stap 1: Workspace fundament (GROEN)
- [ ] uv installeren (indien niet aanwezig)
- [ ] Root `pyproject.toml` uitbreiden met `[tool.uv.workspace]` configuratie
- [ ] `packages/devhub-core/` directory aanmaken
- [ ] `packages/devhub-core/pyproject.toml` schrijven (name, version, dependencies)
- [ ] `devhub/` verplaatsen naar `packages/devhub-core/devhub_core/`
- [ ] `tests/` verplaatsen naar `packages/devhub-core/tests/`
- [ ] `uv sync` — valideer dependency resolution
- [ ] `uv.lock` gegenereerd

### Stap 2: Import-migratie (GROEN)
- [ ] Alle imports updaten: `devhub.` → `devhub_core.`
- [ ] Bestanden die geraakt worden:
  - 18 testbestanden in `tests/`
  - `devhub/registry.py` (intern)
  - `devhub/agents/*.py` (orchestrator, docs_agent, qa_agent)
  - `devhub/adapters/boris_adapter.py` (intern)
  - `config/nodes.yml` (adapter pad)
- [ ] `uv run pytest packages/devhub-core/tests/` — alle 339+ tests groen
- [ ] `uv run ruff check packages/devhub-core/` — 0 fouten

### Stap 3: Agent/skill referenties updaten (GROEN)
- [ ] Agent prompts updaten (6 bestanden in `agents/`):
  - PYTHONPATH-invocaties → `uv run python -c "..."`
  - Import-paden: `devhub.` → `devhub_core.`
- [ ] Skill prompts controleren op verwijzingen naar oude paden
- [ ] DEVHUB_BRIEF.md updaten met nieuwe structuur

### Stap 4: Package-splitsing (GEEL)
- [ ] `packages/devhub-agents/` — plugin agents als installeerbaar package
- [ ] `packages/devhub-skills/` — skills als installeerbaar package
- [ ] `packages/devhub-governance/` — governance-checks als package
- [ ] Inter-package dependencies definiëren in pyproject.toml
- [ ] `uv sync` — gedeelde lockfile valideert
- [ ] Cross-package import tests

### Stap 5: Distributie validatie (GROEN)
- [ ] PEX packaging testen: `pex packages/devhub-core/ -o devhub-core.pex`
- [ ] PEX executable draait standalone
- [ ] Documenteer distributie-workflow in ADR

## Grenzen (wat we NIET doen)

- Geen Pants — beslissing genomen, uv workspaces is voldoende
- Geen remote caching — één developer, niet nodig
- Geen CI/CD pipeline wijzigingen in deze sprint — dat is n8n Foundation sprint
- Geen nieuwe functionaliteit — puur structurele migratie
- devhub-storage en devhub-vectorstore worden NIET aangemaakt — alleen lege workspace slots

## Appetite

1 sprint (FEAT). Stap 1-3 is mechanisch werk (verplaatsen + zoek-en-vervang). Stap 4 vereist architectuurkeuzes over package-grenzen. Stap 5 is validatie.

## Afhankelijkheden

- **Geblokkeerd door:** Geen
- **Blokkeert:** Track B (devhub-storage), Track C (devhub-vectorstore), alle toekomstige packages
- **BORIS impact:** Geen. BORIS' code wijzigt niet. Alleen `config/nodes.yml` adapter-pad update.

## Technische richting

(Claude Code mag afwijken)

```toml
# Root pyproject.toml
[tool.uv.workspace]
members = [
    "packages/devhub-core",
    "packages/devhub-agents",
    "packages/devhub-skills",
    "packages/devhub-governance",
]
```

```toml
# packages/devhub-core/pyproject.toml
[project]
name = "devhub-core"
version = "0.2.0"
requires-python = ">=3.11"
dependencies = ["pyyaml>=6.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Import-wijziging (alle bestanden):
```python
# Oud
from devhub.contracts.node_interface import NodeInterface
# Nieuw
from devhub_core.contracts.node_interface import NodeInterface
```

## Backward compatibility

Tijdens transitie moeten beide manieren werken:
- **Nieuw:** `uv run pytest` vanuit workspace root
- **Legacy:** Agent prompts die nog niet geüpdated zijn

Oplossing: uv installeert packages als editable. Legacy PYTHONPATH werkt nog zolang het pad klopt. Agent prompts worden in stap 3 geüpdated.

## Risico's

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Import-migratie breekt tests | Hoog | Per-bestand migratie, tests draaien na elk bestand |
| uv workspace config fout | Middel | `uv sync` faalt direct, snel te debuggen |
| Agent prompts niet allemaal gevonden | Middel | Grep op `devhub.` + `PYTHONPATH` door hele repo |
| PEX packaging faalt | Laag | Niet blokkerend, kan later opgelost |

## Open vragen voor Claude Code

1. Moet `devhub_core` of `devhub-core` als package-naam? (underscore voor Python import, hyphen voor pyproject)
2. Hoe handelen we de `__init__.py` met `__version__`? Centraal of per package?
3. Moeten we een `py.typed` marker toevoegen voor mypy/pyright support?
4. Wat doen we met `.claude/agents/` (project-level agents) vs `agents/` (plugin-level)? Beide verplaatsen of alleen plugin-level?

## DEV_CONSTITUTION impact

- **Art. 3** (Codebase-integriteit): Tests MOETEN groen blijven na elke stap. Geen big-bang migratie.
- **Art. 4** (Traceerbaarheid): Migratie in meerdere commits met duidelijke messages.
- **Art. 7** (Impact-zonering): Stap 1-3 GROEN (mechanisch, reversibel), stap 4 GEEL (architectuurkeuzes).
