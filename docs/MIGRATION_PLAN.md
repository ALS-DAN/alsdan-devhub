# Migratie-plan: BORIS Dev-Mechanisms → DevHub

## Doel

BORIS wordt een puur zorgproduct (runtime agents, RAG pipeline, MCP tools).
Alle development-orchestratie verhuist naar DevHub als node-agnostische capabilities.

## Principe

- **Niet kopiëren, maar herstructureren** — DevHub skills werken via NodeInterface
- **Graduele migratie** — per sprint één skill overzetten, BORIS-versie pas slopen na verificatie
- **BORIS weet niets van DevHub** — DevHub leest BORIS via BorisAdapter

---

## Fase-overzicht

| Fase | Skill | Prioriteit | Complexiteit | Status |
|------|-------|-----------|-------------|--------|
| F3 | buurts-sprint → devhub-sprint | Hoogst | Hoog | TODO |
| F4 | buurts-health → devhub-health | Hoog | Medium | TODO |
| F5 | mentor-dev → devhub-mentor | Medium | Medium | TODO |
| F6 | boris-sprint-prep → devhub-sprint-prep | Medium | Laag | TODO |
| F7 | buurts-review → (al in QA Agent) | Laag | Klaar | ✅ Fase 2 |

---

## F3: buurts-sprint → devhub-sprint

### Wat het nu doet (BORIS)
Bestand: `.claude/skills/buurts-sprint/SKILL.md`

Workflow (8 stappen):
0. Git handover (commit inbox/ files)
0B. COWORK_BRIEF lezen + Sprint Queue
0C. Projectleider triage (top-3 candidates, blockers)
1. Context laden (CLAUDE.md, OVERDRACHT.md, GOALS.md)
2. Scope analyseren vanuit sprint-intake
3. Plan genereren (technische spec, MCP specs, test-schatting)
4. Niels-goedkeuring AFWACHTEN
5. Fase-voor-fase implementatie (test na elke fase)
6. Sprint-afsluiting (exit criteria, HERALD sync)

### Wat de DevHub versie doet
Bestand: `devhub/.claude/skills/devhub-sprint/SKILL.md`

Verschil:
- Leest BORIS-context via `BorisAdapter.get_report()` i.p.v. directe file-reads
- Kan sprint-docs lezen via `boris_path / "docs/planning/sprints/"`
- Triggert DocsAgent voor parallelle docs-generatie
- Triggert QA Agent vóór sprint-afsluiting
- Kan HERALD triggeren via shell: `{boris_path}/scripts/herald_commit.sh`
- Node-agnostisch: dezelfde skill werkt voor andere nodes

### DoR voor migratie
- [ ] BorisAdapter kan sprint-docs lezen
- [ ] BorisAdapter kan OVERDRACHT.md, CLAUDE.md lezen
- [ ] DevHub kan pytest/ruff uitvoeren op BORIS (al klaar: `run_tests()`)
- [ ] DevHub kan HERALD triggeren (shell invocatie)
- [ ] devhub-sprint skill geschreven en getest

### Te slopen uit BORIS na verificatie
- `.claude/skills/buurts-sprint/SKILL.md`
- `.claude/skills/buurts-sprint/` directory

---

## F4: buurts-health → devhub-health

### Wat het nu doet (BORIS)
10-staps diagnostic:
1. MCP health check
2. Curator audit
3. Tests & lint
4. Dependency security (pip-audit)
5. Version consistency
6. Architecture scan
7. n8n workflow validation
8. Health report generatie
9. Alert routing
10. Architecture audit (optioneel)

### Wat de DevHub versie doet
- Stap 1-3: Via `NodeInterface.get_health()` + `run_tests()`
- Stap 4: Via shell `pip-audit` op node path
- Stap 5-6: Via directe file-reads op node path (CLAUDE.md, main.py)
- Stap 7: Via shell of n8n API call
- Stap 8-10: Generiek rapportage-formaat
- Node-agnostisch: werkt voor elke node die NodeInterface implementeert

### DoR
- [ ] BorisAdapter.get_health() geeft voldoende detail
- [ ] LUMEN export bevat component-status
- [ ] devhub-health skill geschreven
- [ ] Rapportage-formaat gedefinieerd

### Te slopen uit BORIS
- `.claude/skills/buurts-health/SKILL.md`
- `.claude/skills/buurts-health/` directory

---

## F5: mentor-dev → devhub-mentor

### Wat het nu doet (BORIS)
O-B-B developer coaching:
- ORIËNTEREN: conceptuele vragen, leerfase
- BOUWEN: implementatie, actief ontwikkelen
- BEHEERSEN: architectuurbeslissingen, mentoring

Fase-detectie via DeveloperProgressStore.
Coaching-signalen: GROEN / AANDACHT / STAGNATIE.

### Wat de DevHub versie doet
- Leest developer progress via LUMEN export (DeveloperProfiel in DevReport)
- O-B-B fase-detectie op basis van NodeReport data
- Coaching-aanbevelingen node-agnostisch formuleren
- Kan meerdere nodes monitoren (bijv. voortgang op BORIS vs. ander project)

### DoR
- [ ] LUMEN DevReport bevat DeveloperProfiel data
- [ ] DevHub kan O-B-B fase bepalen uit report
- [ ] devhub-mentor skill geschreven

### Te slopen uit BORIS
- `.claude/skills/mentor-dev/SKILL.md`
- `.claude/skills/mentor-dev/` directory

---

## F6: boris-sprint-prep → devhub-sprint-prep

### Wat het nu doet (BORIS)
Maandag 07:45 scheduled task:
- Leest system health, developer signals, open decisions
- Genereert SPRINT_INPUT.md met pre-read checklist

### Wat de DevHub versie doet
- Scheduled task in DevHub
- Pollt NodeInterface.get_report() voor alle geregistreerde nodes
- Genereert SPRINT_INPUT per node
- Cross-node overzicht (als er meerdere nodes zijn)

### DoR
- [ ] DevHub scheduled task framework werkend
- [ ] devhub-sprint-prep skill geschreven
- [ ] SPRINT_INPUT template gedefinieerd

### Te slopen uit BORIS
- `.claude/skills/boris-sprint-prep/SKILL.md`
- `.claude/skills/boris-sprint-prep/` directory

---

## F7: buurts-review → (al in QA Agent)

**Status: ✅ Al gemigreerd.**

De 12-punts code review checklist is geëxtraheerd naar `devhub/agents/qa_agent.py` (CR-01..12).
De 6-punts doc review checklist is nieuw (DR-01..06).

### Te slopen uit BORIS
- `.claude/skills/buurts-review/SKILL.md`
- `.claude/skills/buurts-review/` directory

---

## Governance Scripts Migratie

| Script | Actie | Reden |
|--------|-------|-------|
| `curator_audit.py` | Kopieer + generaliseer | Pad-configureerbaar maken per node |
| `audit_delta.py` | Kopieer ongewijzigd | Standalone utility |
| `inbox_curator.py` | Kopieer + generaliseer | Backlog management per node |
| `inbox_report.py` | Kopieer ongewijzigd | Analytics utility |
| `check_sprint_deps.py` | Kopieer + generaliseer | Sprint dep-check per node |
| `herald_payload_helpers.py` | Niet kopiëren | BORIS-specifiek (HERALD internals) |
| `herald_commit.sh` | Niet kopiëren | DevHub triggert dit via shell op BORIS path |

---

## Wat BLIJFT in BORIS (definitief)

### Runtime (zorgdomein)
- Alle Python agents: VERA, SCOUT, HERALD, CLAIR, CURATOR, LUMEN, ATLAS, SCRIPTOR
- Hub orchestrator (`agents/hub.py`)
- MCP server + FastAPI endpoints
- Weaviate, SQLite stores
- n8n workflows

### Runtime Safety
- `.claude/agents/vera_analyse.md` (hook validator)
- `.claude/agents/knowledge_ask.md` (hook validator)
- `.claude/agents/ingest_document.md` (hook validator)
- `.claude/agents/scriptor_generate.md` (hook validator)
- `.claude/hooks/validators/*.py` (deterministic validators)

### Repo Governance (pre-commit)
- `ruff`, `bandit`, `detect-secrets` (code quality)
- `check_doc_paths.py` (BORIS pad-structuur)
- `check_claude_md_lean.py` (CLAUDE.md limiet)
- `check_main_size.py` (main.py bescherming)
- `curator_audit.py` als pre-commit hook (BORIS-specifiek)
- Conventional commits

### HERALD System
- `herald_commit.sh` — DevHub triggert dit via shell
- `agents/herald_synthesizer.py` — BORIS-interne publicatie-engine
- `agents/herald_publisher.py` — Multi-channel output

### Documentatie-structuur
- `CLAUDE.md` — BORIS project-instructies (hot cache)
- `.claude/OVERDRACHT.md` — Sessie-overdracht (HERALD-generated)
- `docs/planning/COWORK_BRIEF.md` — Cowork briefing (HERALD-generated)
- `.claude/COWORK_INSTRUCTIES.md` — Protocol (DevHub krijgt eigen versie)
- MkDocs site + alle content

---

## Sloop-protocol

Per skill-migratie:

1. DevHub skill geschreven + getest
2. Eén sprint uitgevoerd met DevHub skill (validatie)
3. BORIS skill verwijderd: `git rm .claude/skills/{skill}/`
4. CLAUDE.md bijgewerkt (verwijs naar DevHub)
5. HERALD sync (OVERDRACHT.md reflecteert de wijziging)

**Volgorde:** F3 (sprint) → F4 (health) → F5 (mentor) → F6 (sprint-prep) → F7 (review, al klaar)

---

## BorisAdapter Uitbreidingen Nodig

De huidige BorisAdapter kan:
- ✅ LUMEN DevReport lezen
- ✅ MkDocs navigatie scannen
- ✅ Pytest uitvoeren
- ✅ Health status bepalen

Nog nodig voor skill-migratie:
- [ ] Sprint-docs lezen (`docs/planning/sprints/SPRINT_*.md`)
- [ ] OVERDRACHT.md lezen
- [ ] CLAUDE.md lezen
- [ ] Inbox lezen (`docs/planning/inbox/`)
- [ ] HERALD triggeren (`scripts/herald_commit.sh`)
- [ ] Ruff uitvoeren
- [ ] pip-audit uitvoeren
