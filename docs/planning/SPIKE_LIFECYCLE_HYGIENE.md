# SPIKE: Sprint Lifecycle Hygiene — Analyse & Voorstellen

---
gegenereerd_door: "DevHub SPIKE Sprint — 2026-03-27"
sprint: SPIKE_SPRINT_LIFECYCLE_HYGIENE
status: DONE
datum: 2026-03-27
---

## Samenvatting

Na 24 sprints zijn er vier structurele lifecycle-problemen geïdentificeerd. Dit document bevat de analyse van de huidige staat en concrete voorstellen voor verbetering. De voorstellen zijn input voor een aparte FEAT-sprint die de daadwerkelijke wijzigingen implementeert.

---

## Analyse V1: Document-overlap en Single Source of Truth

### Gemeten staat (2026-03-27)

| Document | Bijgewerkt tot | Tests |
|----------|---------------|-------|
| `FASE3_TRACKER.md` | Sprint 24 (2026-03-27) | 1165 ✅ |
| `DEVHUB_BRIEF.md` | Sprint 10 (2026-03-26 header) | 575 ❌ |
| `TRIAGE_INDEX.md` | Sprint 12 (2026-03-26) | 662 ❌ |
| `ROADMAP.md` | Sprint 10 (2026-03-26) | 575 ❌ |

### Overlapsmatrix

| Contentveld | FASE3_TRACKER | DEVHUB_BRIEF | TRIAGE_INDEX | ROADMAP |
|-------------|:---:|:---:|:---:|:---:|
| Fase-positie | ✅ | ✅ | ✅ | ✅ |
| Actieve sprint | ✅ | ✅ | ✅ | — |
| Test-telling | ✅ | ✅ | ✅ | ✅ |
| Sprint-lijst | ✅ | ✅ | ✅ | ✅ |
| Kritiek pad | ✅ | ✅ | ✅ | — |
| Track-status (per stap) | — | ✅ | — | ✅ |
| Inbox-items lijst | — | ✅ | ✅ | — |
| Agents/skills telling | — | ✅ | — | — |
| Strategische roadmap (Fase 4-5) | — | — | — | ✅ |
| Velocity + cycle time | ✅ | — | — | — |
| Capaciteitsplanning | ✅ | — | — | — |
| Hill Charts + golfdetail | ✅ | — | — | — |

### Wie leest wat? (geverifieerd in codebase)

| Document | Lezer | Hoe |
|----------|-------|-----|
| `FASE3_TRACKER.md` | `agents/planner.md` | Verplicht bij sprint-advies |
| `FASE3_TRACKER.md` | `skills/devhub-sprint-prep` | Stap 1 van context-laden |
| `FASE3_TRACKER.md` | `skills/devhub-sprint` | Stap 0F + 6E |
| `TRIAGE_INDEX.md` | `agents/planner.md` | Verplicht bij planning-scan |
| `TRIAGE_INDEX.md` | `skills/devhub-sprint-prep` | Stap 1 van context-laden |
| `DEVHUB_BRIEF.md` | **Niemand actief** | Niet gerefereerd in skills/agents |
| `ROADMAP.md` | **Niemand actief** | Niet gerefereerd in skills/agents |

### Conclusie V1

**FASE3_TRACKER.md is de de facto SSoT.** Het is het meest actueel, het meest gelezen, en bevat de meeste unieke informatie (velocity, cycle time, capaciteit, Hill Charts).

**DEVHUB_BRIEF.md** bevat alleen overlappende informatie en wordt door geen enkele agent of skill actief gelezen. Het kan gefuseerd worden met de tracker of gearchiveerd.

**ROADMAP.md** bevat de strategische richting (Fase 4-5 roadmap) die nergens anders staat — dit is waardevol maar niet operationeel. Het kan als statisch referentiedocument bewaard blijven zonder actieve sync-plicht.

**TRIAGE_INDEX.md** heeft een unieke rol: de inbox-items lijst en gearchiveerde intakes. Dit wordt actief gelezen door planner + sprint-prep. Het heeft ALLEEN het inbox-overzicht nodig — niet de sprint-lijst of tellingen die ook in FASE3_TRACKER staan.

---

## Analyse V2: Inbox-archivering — waar in de flow?

### Huidig probleem

Sprint-close flow (stap 6) heeft deze stappen:
- ✅ 6E: FASE3_TRACKER bijwerken
- ✅ 6D: HERALD triggeren
- ❌ **Intake archiveren ontbreekt**
- ❌ **TRIAGE_INDEX bijwerken ontbreekt**

Gevolg: 7 van de 12 bestanden in `inbox/` zijn afgehandelde intakes die nog steeds worden aangeboden als "kandidaten" bij sprint-start.

### Opties

**Optie A: Verplaatsen (inbox → sprints/)**
- Pro: Inbox blijft schoon, sprint-prep hoeft niet te filteren
- Con: Verplaatsen vereist shell-commando's, risico op conflicten bij submodule-gebruik
- Con: Git history verliest context (bestand "verdwijnt" uit inbox/)

**Optie B: Status-marker in frontmatter (status: DONE)**
- Pro: Geen bestandsverplaatsing nodig, eenvoudig te implementeren in sprint-close
- Pro: Volledig traceerbaar via git, intake blijft leesbaar op originele locatie
- Con: Sprint-prep moet filteren op `status: INBOX` (kleine aanpassing)
- Pro: Consistent met de rest van het systeem (status-velden in alle frontmatters)

**Optie C: Aparte cleanup-actie (niet gebonden aan sprint-close)**
- Pro: Scheidt verantwoordelijkheden
- Con: Vereist actieve discipline, wordt vergeten

### Aanbeveling V2 — **Optie B: status-marker**

Voeg aan sprint-close flow toe (na stap 6D HERALD):

```
6F (nieuw): Intake archiveren
- Zoek de intake die bij deze sprint hoort (naam-match of verwijzing in sprint-doc)
- Wijzig frontmatter: status: INBOX → status: DONE
- Sprint-prep en planner filteren voortaan op status: INBOX
```

Dit is de minst invasieve aanpassing met directe werking. De FEAT-sprint kan dit implementeren door:
1. Sprint-close skill: toevoegen van stap 6F
2. Sprint-prep skill + planner agent: intake-scan beperken tot `status: INBOX`

---

## Analyse V3: Scope-beperking sprint-start

### Huidig probleem

De `devhub-sprint` skill laadt standaard alle BORIS-node context:
```
adapter.get_report()        → BORIS health report
adapter.read_claude_md()    → BORIS CLAUDE.md (~100 regels)
adapter.read_overdracht()   → BORIS OVERDRACHT.md (~100 regels)
adapter.read_cowork_brief() → BORIS COWORK_BRIEF.md (~200 regels)
```

Voor DevHub-eigen sprints (Kennispipeline, Governance, Mentor, Lifecycle) is dit **100% overbodig**. De sprint gaat over DevHub zelf, niet over BORIS.

### Detectiemechanisme

Intakes hebben een `fase:` veld in frontmatter maar geen `node:` veld. Een eenvoudig onderscheid:

| Criterium | DevHub-sprint | BORIS-sprint |
|-----------|--------------|--------------|
| Intake staat in `alsdan-devhub/docs/planning/inbox/` | ✅ | ❌ |
| Intake staat in `buurts-ecosysteem/docs/planning/inbox/` | ❌ | ✅ |
| `node: boris-buurts` in frontmatter | ❌ | ✅ |
| `node: devhub` in frontmatter | ✅ | ❌ |

### Aanbeveling V3 — **optioneel node-veld + conditie in skill**

Voeg `node:` veld toe aan intake-template (optioneel, default = `devhub`):

```yaml
---
node: devhub          # of: boris-buurts
sprint_type: SPIKE
---
```

In `devhub-sprint` skill: stap 0A conditie:
```
Als node == "devhub" (of niet ingevuld):
  → Skip alle adapter-calls
  → Laad alleen: FASE3_TRACKER.md + TRIAGE_INDEX.md + intake-bestand
Als node == "boris-buurts":
  → Laad adapter-context zoals nu
```

Dit is een kleine aanpassing aan de skill-tekst (geen Python-code), en een klein template-update voor toekomstige intakes.

---

## Analyse V4: Fase-agnostische tracker

### Huidig probleem

`FASE3_TRACKER.md` is hardcoded op Fase 3. Bij fase-overgang:
- Tracker wordt historisch, nieuw bestand (`FASE4_TRACKER.md`) nodig
- Skills en agents refereren naar `FASE3_TRACKER.md` hardcoded → moeten worden bijgewerkt
- Dezelfde situatie herhaalt zich bij elke fase-overgang

### Opties

**Optie A: Vaste bestandsnaam SPRINT_TRACKER.md**
- Altijd dezelfde naam, inhoud groeit mee
- Vorige fases inklappen tot samenvatting-sectie
- Skills/agents hoeven nooit bijgewerkt te worden
- Pro: Simpelste oplossing, één bestand, altijd zelfde verwijzing
- Con: Bestand wordt groter over tijd (maar beheersbaar met inklapstructuur)

**Optie B: Config-pointer in CLAUDE.md**
```yaml
actieve_tracker: docs/planning/FASE3_TRACKER.md
```
- Skills/agents lezen pointer, openen dat bestand
- Pro: Flexibel, tracker kan per fase anders heten
- Con: Extra indirectie, CLAUDE.md moet ook bijgewerkt worden

**Optie C: Auto-detect op basis van frontmatter status: ACTIEF**
- Skills zoeken naar tracker met `status: ACTIEF` in `docs/planning/`
- Pro: Volledig automatisch
- Con: Complexe detectie, kan mis gaan als meerdere trackers ACTIEF zijn

### Aanbeveling V4 — **Optie A: SPRINT_TRACKER.md**

Eenvoudigste oplossing met beste onderhoudbaarheid.

**Structuur SPRINT_TRACKER.md:**

```markdown
# Sprint Tracker — DevHub

## Fase 3 (ACTIEF)
[Huidige golfplanning, velocity, cycle time, Hill Charts]

## Fase 2 (Afgerond 2026-03-25)
Sprint 1-6 | 218 → 395 tests | 6 agents, 8 skills

## Fase 1 (Afgerond 2026-03-24)
Sprint 1-2 | 0 → 218 tests | Bootstrap

## Fase 0 (Afgerond 2026-03-23)
Fundament, architecture decisions
```

Bij fase-overgang:
1. Huidige `## Fase 3 (ACTIEF)` → `## Fase 3 (Afgerond DATUM)` inklapt tot samenvatting
2. Nieuwe `## Fase 4 (ACTIEF)` sectie toevoegen bovenaan
3. Velocity en cycle time tabellen lopen door (niet per fase resetten)

---

## Decision Record: Één tracker vs. meerdere documenten

**Beslissingsvraag:** Hoe organiseren we DevHub-planning documenten voor maximale actualiteit met minimale onderhoudslast?

**Opties:**
1. Eén levend document (SPRINT_TRACKER.md) — alle operationele info samengevoegd
2. Huidige structuur behouden — vier aparte documenten

**Afweging:**

| Criterium | Eén document | Vier documenten |
|-----------|-------------|-----------------|
| Actualiteitskans | Hoog (één update-punt) | Laag (vier update-punten) |
| Leesbaarheid | Groeit, maar beheersbaar | Gefragmenteerd |
| Skills aanpassen | Eenmalig | Bij elke sync-mismatch |
| Strategische roadmap | Aparte sectie mogelijk | Aparte ROADMAP.md bewaren |
| Inbox-overzicht | Aparte sectie mogelijk | Aparte TRIAGE_INDEX.md |

**Aanbeveling:** Voer één SPRINT_TRACKER.md in als operationele SSoT. Bewaar ROADMAP.md als strategisch referentiedocument (geen sync-plicht). Archiveer DEVHUB_BRIEF.md. Verklein TRIAGE_INDEX.md tot alleen de inbox-items lijst.

**Rationale:** Elke extra sync-plicht is technische schuld. Met 24+ sprints per Fase heeft een systeem met vier sync-punten 4× de kans op drift.

---

## Voorstel: Sprint-close flow v2

### Huidige flow (v1) — stap 6

```
6A: Exit-criteria verificatie
6B: QA Agent review
6C: Gestructureerde bevestiging (wacht op akkoord)
6D: HERALD triggeren
6E: FASE3_TRACKER bijwerken
6F: Retrospective genereren
6G: Cleanup
```

### Voorgestelde flow (v2)

```
6A: Exit-criteria verificatie
6B: QA Agent review
6C: Gestructureerde bevestiging (wacht op akkoord)
6D: HERALD triggeren (BORIS-node only)
6E: SPRINT_TRACKER bijwerken (was: FASE3_TRACKER)
6F: Intake archiveren → status: DONE in frontmatter   [NIEUW]
6G: TRIAGE_INDEX tellingen bijwerken (tellingen only)  [NIEUW, vereenvoudigd]
6H: Retrospective genereren
6I: Cleanup
```

**Wijzigingen:**
- 6D HERALD: conditioneel (alleen bij BORIS-node sprints)
- 6E: verwijzing naar `SPRINT_TRACKER.md` i.p.v. `FASE3_TRACKER.md`
- 6F nieuw: intake-archivering via status-marker
- 6G nieuw: TRIAGE_INDEX tellingen updaten (beperkt — alleen tellingen, niet sprint-lijst)

---

## Voorstel: Sprint-start flow v2

### Huidig (v0A-v0F) — bij DevHub-eigen sprint

Laadt onnodig: BORIS `adapter.get_report()`, `read_claude_md()`, `read_overdracht()`, `read_cowork_brief()`

### Voorgesteld v2

```
0A: Detecteer sprint-type
    → Als intake heeft node: devhub (of geen node-veld): DevHub-pad
    → Als intake heeft node: boris-buurts: BORIS-pad

0B (DevHub-pad): Laad DevHub-context
    → SPRINT_TRACKER.md (was: FASE3_TRACKER)
    → TRIAGE_INDEX.md (alleen status: INBOX items)
    → Intake-bestand

0B (BORIS-pad): Laad BORIS-context (huidige flow)
    → adapter.get_report()
    → adapter.read_claude_md()
    → adapter.read_overdracht()
    → adapter.read_cowork_brief()
```

---

## Migratiestappen (voor FEAT-sprint)

### Stap 1: Maak SPRINT_TRACKER.md aan
- Kopieer inhoud van FASE3_TRACKER.md
- Hernoem bestand en pas h1 aan
- Voeg `## Fase 0-2 (Afgerond)` samenvattings-sectie toe
- Archiveer FASE3_TRACKER.md als `docs/planning/archive/FASE3_TRACKER_ARCHIEF.md`

### Stap 2: Update skills/agents
- `agents/planner.md`: alle refs `FASE3_TRACKER.md` → `SPRINT_TRACKER.md`
- `skills/devhub-sprint-prep/SKILL.md`: idem
- `skills/devhub-sprint/SKILL.md`: idem + voeg stap 6F en 6G toe + conditie 6D

### Stap 3: Update intake-template
- Voeg optioneel `node:` veld toe aan sprint-intake frontmatter template
- Default: `node: devhub`

### Stap 4: Archiveer DEVHUB_BRIEF.md
- Verplaats naar `docs/planning/archive/DEVHUB_BRIEF_ARCHIEF.md`
- Geen vervanging nodig (inhoud zit in SPRINT_TRACKER + TRIAGE_INDEX)

### Stap 5: Vereenvoudig TRIAGE_INDEX.md
- Bewaar: inbox-items lijst, gearchiveerde intakes, geparkeerd-lijst
- Verwijder: sprint-lijst, tellingen-tabel, kritiek pad (dubbel met SPRINT_TRACKER)

### Stap 6: Archiveer afgehandelde intakes
- Voeg `status: DONE` toe aan 7 afgehandelde intakes in `docs/planning/inbox/`
- Dit is de eerste test van de nieuwe intake-archivering stap

---

## Samenvatting aanbevelingen

| # | Voorstel | Impact | Effort |
|---|----------|--------|--------|
| 1 | SPRINT_TRACKER.md als fase-agnostische SSoT | Elimineert tracker-migratie bij fase-overgang | Klein |
| 2 | Status-marker in intake frontmatter voor archivering | Elimineert inbox-vervuiling direct | Klein |
| 3 | Conditionele node-context in sprint-start | Elimineert onnodige BORIS-lading bij DevHub-sprints | Klein |
| 4 | Vereenvoudig TRIAGE_INDEX tot inbox-lijst | Vermindert overlap, één update-punt minder | Klein |
| 5 | Archiveer DEVHUB_BRIEF (niemand leest het) | Ruimt verwarring op | Triviaal |

Alle vijf voorstellen zijn kleine aanpassingen aan markdown-bestanden (skills, agents, docs). Geen Python-code wijzigingen nodig.
