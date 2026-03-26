# devhub-sprint — Node-Agnostische Sprint Lifecycle Skill

## Trigger
Activeer bij: "sprint start", "nieuwe sprint", "sprint afsluiten", "sprint status", "volgende fase", "volgende stap", "wat moet ik nu doen", "fase overgang", "start sprint".

## Doel
Gestructureerde sprint-start, fase-overgang en sprint-afsluiting voor **elke managed node**.
Werkt via de NodeInterface/BorisAdapter — leest node-context zonder directe file-paden te kennen.

De kracht: (1) governance-gate die implementatie zonder akkoord voorkomt, (2) consistent planformat, (3) afsluiting-workflow die node-documenten up-to-date houdt.

---

## Setup

Voordat deze skill werkt, moet de target node geregistreerd zijn in `config/nodes.yml`.
De skill gebruikt de BorisAdapter (of andere NodeInterface-implementatie) om node-data te lezen.

```python
from devhub_core.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")
```

---

## Workflow: Sprint Start

### 0. Intake-scan + context (altijd eerst)

**0A — Node-context ophalen:**
- Haal NodeReport op via `adapter.get_report()` — health, doc status, observaties
- Lees CLAUDE.md via `adapter.read_claude_md()` — actieve sprint, constraints
- Lees OVERDRACHT.md via `adapter.read_overdracht()` — recente beslissingen, open werk
- Lees COWORK_BRIEF via `adapter.read_cowork_brief()` — sprint queue, inbox status

**0B — Sprint Queue tonen:**
- Toon de Sprint Queue sectie uit COWORK_BRIEF aan de developer
- Benoem de eerstvolgende sprint (status NEXT) als kandidaat

**0C — Projectleider-triage:**
- Identificeer top-3 sprint-kandidaten
- Benoem het kritiek pad (welk item blokkeert andere?)
- Check open beslissingen uit OVERDRACHT.md

**0D — Inbox scannen:**
- Haal inbox op via `adapter.list_inbox()`
- Toon SPRINT_INTAKE_* en IDEA_* bestanden aan developer
- Bij keuze voor een intake: lees via `adapter.read_file(intake_path)`

**0E — Backlog-staat:**
- Lees backlog via `adapter.read_backlog()`
- Toon telling per state: INBOX / TRIAGED / SHAPING / READY / IN_SPRINT
- Benoem aging items (>30 dagen in TRIAGED)

**0F — FASE3_TRACKER positie (DevHub-sprints):**
- Lees `docs/planning/FASE3_TRACKER.md`
- Vind de sprint in de golfplanning tabel
- Update status: 📋 KLAAR → 🔄 ACTIEF
- Update Hill Chart: ░░░░░░░░░░░░ → ▓░░░░░░░░░░░
- Rapporteer huidige golf, actieve sprints, en volgende kandidaten

### 1. Context laden

Lees altijd (via adapter):
- `adapter.read_claude_md()` — rollen, sprint status, module-map
- `adapter.read_overdracht()` — actieve sprint, recente beslissingen
- `adapter.read_goals()` — huidige top-goals en roadmap-context
- Actief sprintplan: `adapter.list_sprint_docs()` → `adapter.read_sprint_doc(name)`

### 2. Scope analyseren

- Wat is het doel van deze sprint?
- Welke deliverables zijn verwacht?
- Welke afhankelijkheden bestaan er?
- Sprint dependency check: `adapter.run_sprint_deps_check(sprint_doc)`
- Roadmap-positie: waar past deze sprint?

### 3. Plan genereren

Gebruik de DevOrchestrator voor taakdecompositie:
```python
from devhub_core.agents.orchestrator import DevOrchestrator

orch = DevOrchestrator(registry)
task = orch.create_task(
    description="Sprint scope beschrijving",
    node_id="boris-buurts",
    scope_files=[...],
    sprint_ref="SPRINT_NAAM",
)
```

Per fase: deliverables, bestanden, tests, afhankelijkheden.
Trigger DocsAgent voor parallelle docs:
```python
orch.decompose_for_docs(task, diataxis_category="reference", ...)
```

### 4. Presenteer plan — WACHT OP AKKOORD

> NOOIT implementeren zonder expliciete goedkeuring van de developer.

### 5. Implementeer fase voor fase

- Markeer huidige fase in todo-lijst
- Test na elke fase: `adapter.run_tests()` moet groen zijn
- Rapporteer resultaat vóór volgende fase
- DocsAgent draait parallel mee

### 6. Sprint afsluiting

**A — Exit-criteria-verificatie:**
- [ ] Alle deliverables groen
- [ ] `adapter.run_tests()` — testcount ≥ startpunt (geen regressie)
- [ ] `adapter.run_lint()` — 0 errors
- [ ] `adapter.run_curator_audit()` — exitcode 0
- [ ] Geen openstaande blockers of TODO's in nieuwe code

**B — QA Agent review:**
```python
from devhub_core.agents.qa_agent import QAAgent

qa = QAAgent()
task_result = orch.record_task_result(task_id=..., files_changed=[...], tests_added=N)
report = qa.full_review(task_id, task_result, doc_requests=[...])
```
- QA verdict moet PASS zijn (of NEEDS_WORK met bewuste accept door developer)
- BLOCK verdict → sprint kan NIET sluiten

**C — Gestructureerde bevestiging:**
```
Sprint <NAAM> is klaar:
- Deliverables: X/Y afgerond
- Tests: XXXX (start) → XXXX (einde), delta +XX
- Lint: ruff check 0 errors
- QA verdict: PASS
- Volgende sprint: <NAAM>

Akkoord voor afsluiting?
```
> NOOIT afsluiten zonder expliciete goedkeuring.

**D — HERALD triggeren (na akkoord):**
```python
success, output = adapter.run_herald_sync("Sprint NAAM afgerond")
```

**E — FASE3_TRACKER bijwerken (DevHub-sprints, na akkoord):**
- Update sprint status in golfplanning: 🔄 ACTIEF → ✅ DONE, Hill → ████████████
- Velocity tabel: voeg rij toe met sprint #, naam, gepland vs werkelijk, test-delta, nauwkeurigheid
- Cycle time tabel: voeg rij toe met inbox datum, sprint start, sprint klaar, cycle time
- Check of volgende sprint in golf nu unblocked is (⏳ WACHT → 📋 KLAAR als dependency opgelost)
- Update afgeleide metrics (sprints afgerond, test baseline, gemiddelde test-delta)

**F — Retrospective genereren (na akkoord):**
- Genereer sprint-retrospective op basis van `docs/golden-paths/SPRINT_RETROSPECTIVE.md` template
- Data ophalen: git log, test-delta, QA rapport, deliverable-status
- Schrijf naar `knowledge/retrospectives/RETRO_<SPRINT_NAAM>.md`
- Gradering: SILVER (gevalideerd door 1 sprint)

**G — Cleanup:**
- Orchestrator cleanup: `orch.clear_task()`, `orch.clear_doc_queue()`

---

## Workflow: Status / Volgende Fase

1. Lees context via adapter (OVERDRACHT, actief sprintplan)
2. Identificeer huidige fase en voortgang
3. Rapporteer: fase, resterende fasen, roadmap-context, blokkades

---

## Regels (altijd van toepassing)
- Één fase tegelijk — geen scope creep
- Test-first: geen feature zonder test
- Developer beslist. DevHub voert uit.
- QA Agent review vóór sprint-afsluiting
- DocsAgent draait parallel aan development
