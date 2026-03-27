# SPRINT_INTAKE_SPIKE_SPRINT_LIFECYCLE_HYGIENE_2026-03-27

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
sprint_type: SPIKE
cynefin: complicated
---

## Doel

Onderzoek en repareer de sprint lifecycle zodat overdracht, archivering en scope-beperking betrouwbaar werken — zonder handmatige correctie.

## Probleemstelling

### Waarom nu

Bij het starten van nieuwe sprints treden drie structurele problemen op die tokens verspillen, foute context geven, en het vertrouwen in het planningssysteem ondermijnen:

1. **Stale overdracht:** DEVHUB_BRIEF.md toont sprint 10 (575 tests) terwijl er 24 sprints zijn afgerond (1082+ tests). TRIAGE_INDEX.md toont 12 sprints (662 tests). ROADMAP.md toont "Golf 2 READY" terwijl Golf 3 klaar is. Nieuwe sessies krijgen verouderde context → stellen afgeronde sprints opnieuw voor.

2. **Inbox-vervuiling:** 12 bestanden in `inbox/` waarvan minimaal 7 afgehandelde intakes (Kennispipeline Golf 1-3, Planning Tracking, Storage S2-S3, Vectorstore Weaviate). Sprint-prep scant al deze documenten en presenteert ze als kandidaten.

3. **Overbrede scope bij sprint-start:** De sprint-skill en sprint-prep-skill laden standaard alle BORIS-node context via `adapter.get_report()`, `adapter.read_claude_md()`, `adapter.read_overdracht()`, `adapter.read_cowork_brief()`. Voor DevHub-eigen sprints (Kennispipeline, Governance, Mentor) is dit 100% overbodig — kost tokens en vertraagt.

4. **Fase-gebonden tracker:** FASE3_TRACKER.md is hardcoded op Fase 3. Bij fase-overgang wordt dit document historisch en moet een nieuw bestand aangemaakt worden. Claude Code moet dan weten welk tracker-bestand actief is → zelfde overdrachts-probleem als punt 1.

### Fase-context

Fase 3 nadert afsluiting. Als deze problemen niet nu worden opgelost, worden ze meegenomen naar Fase 4 (BORIS-migratie) waar de impact groter is door cross-project complexiteit.

### Root cause analyse

De sprint-close flow (`devhub-sprint` skill, stap 6) bevat:
- ✅ **6E: FASE3_TRACKER bijwerken** — dit werkt
- ❌ **DEVHUB_BRIEF bijwerken** — ontbreekt als stap
- ❌ **TRIAGE_INDEX bijwerken** — ontbreekt als stap
- ❌ **ROADMAP bijwerken** — ontbreekt als stap
- ❌ **Intake archiveren** (inbox → sprints) — ontbreekt als stap
- ❌ **Fase-agnostische tracker** — bestaat niet

Het probleem is dus niet dat de stappen falen, maar dat ze **niet bestaan** in de workflow.

## Onderzoeksvragen (SPIKE scope)

### V1: Single Source of Truth — welke documenten overlappen?

Huidige statusdocumenten en hun overlap:

| Document | Bevat | Bijgewerkt tot |
|----------|-------|----------------|
| FASE3_TRACKER.md | Golfplanning, velocity, cycle time, capaciteit, kritiek pad | Sprint 24 ✅ |
| DEVHUB_BRIEF.md | Actieve sprint, fase-positie, tellingen, kritiek pad, health | Sprint 10 ❌ |
| TRIAGE_INDEX.md | Inbox/backlog/parked overzicht, tellingen, kritiek pad | Sprint 12 ❌ |
| ROADMAP.md | Strategische roadmap, track-status, fase-positie | Sprint 10 ❌ |

**Overlap:** fase-positie (4x), kritiek pad (3x), tellingen (2x), sprint-lijst (3x).

**Onderzoeksvraag:** Kan SPRINT_TRACKER.md (fase-agnostisch) de tracker + brief + tellingen combineren tot één levend document? Wat blijft er over als aparte verantwoordelijkheid voor TRIAGE_INDEX en ROADMAP?

### V2: Inbox-archivering — waar in de flow?

**Onderzoeksvraag:** Moet archivering (inbox → sprints) een verplichte stap worden in sprint-close (stap 6, na akkoord), of een aparte cleanup-actie? Hoe detecteert de skill welke intake bij de afgeronde sprint hoort?

**Richting:** Sprint-doc verwijst naar intake-bestand → bij close verplaatsen. Alternatief: status-marker in intake-bestand (STATUS: DONE) zonder verplaatsing.

### V3: Scope-beperking sprint-start

**Onderzoeksvraag:** Hoe onderscheidt de sprint-skill een DevHub-eigen sprint (geen node-context nodig) van een node-gebonden sprint (wel node-context nodig)?

**Richting:** Parameter `node_id` in sprint-start die optioneel is. Geen node = skip adapter calls. Of: apart "devhub-internal" pad in de skill.

### V4: Fase-agnostische tracker

**Onderzoeksvraag:** Hoe groeit SPRINT_TRACKER.md mee over fases zonder onhandelbaar groot te worden?

**Richting:**
- Actieve fase = uitgebreide sectie (golven, hill charts, capaciteit)
- Vorige fases = samenvatting (start/eind datum, test-delta, aantal sprints)
- Velocity en cycle time = doorlopend (niet per fase resetten)
- Fase-overgang = nieuw golf-blok toevoegen, vorige inklappen

## Deliverables

- [ ] **Analyse-rapport:** welke documenten overlappen, wat kan weg, wat wordt samengevoegd
- [ ] **Voorstel SPRINT_TRACKER.md structuur** — fase-agnostisch, doorlopend
- [ ] **Voorstel sprint-close flow v2** — alle update-stappen expliciet, inclusief archivering
- [ ] **Voorstel sprint-start flow v2** — optionele node-context, DevHub-only pad
- [ ] **Migratiestappen** — hoe komen we van huidige staat naar nieuwe structuur

## Grenzen (wat we NIET doen)

- NIET implementeren in deze SPIKE — alleen analyseren en voorstellen
- NIET de Python-laag wijzigen (adapters, orchestrator)
- NIET BORIS-gerelateerde wijzigingen voorstellen
- NIET het planningssysteem zelf herstructureren (inbox/backlog/sprints/parked blijft)
- NIET de skill-bestanden wijzigen — dat is een aparte FEAT sprint

## Afhankelijkheden

| Type | Beschrijving |
|------|-------------|
| Geblokkeerd door | Geen — SPIKE kan direct starten |
| BORIS impact | Nee — raakt alleen DevHub-interne processen |
| Raakt skills | devhub-sprint (close flow), devhub-sprint-prep (scope), planner agent |
| Raakt documenten | DEVHUB_BRIEF.md, TRIAGE_INDEX.md, ROADMAP.md, FASE3_TRACKER.md |

## Open vragen voor Claude Code

1. Hoe leest de sprint-skill momenteel de FASE3_TRACKER? Hardcoded pad of via config?
2. Zijn er andere plekken in agents/skills die DEVHUB_BRIEF lezen bij sessie-start?
3. Kan `adapter.get_sprint_prep_context()` een optionele `node_id=None` modus krijgen, of is een aparte methode beter?
4. Hoeveel tokens kost een gemiddelde BORIS-context load (CLAUDE.md + OVERDRACHT + COWORK_BRIEF + rapport)?

## Prioriteit

**Hoog** — Dit probleem raakt élke sprint-start en wordt erger naarmate er meer sprints afgerond worden. Bij Fase 4 (cross-project) is de impact kritiek.

## DEV_CONSTITUTION impact

| Artikel | Geraakt | Toelichting |
|---------|---------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Betere overdracht = Niels hoeft minder te corrigeren |
| Art. 2 (Verificatieplicht) | Ja | Single Source of Truth vermindert verouderde claims |
| Art. 4 (Transparantie) | Ja | Alle wijzigingen traceerbaar via één tracker |
| Art. 7 (Impact-zonering) | Nee | SPIKE = GREEN (alleen analyse) |

## Technische richting (Claude Code mag afwijken)

De SPIKE zou het beste werken als een gestructureerde analyse die resulteert in:
1. Een **concept SPRINT_TRACKER.md** met de voorgestelde structuur
2. Een **diff-overzicht** van de sprint-close flow (huidige vs. voorgestelde stappen)
3. Een **decision record** (mini-ADR) voor de keuze "één tracker vs. meerdere documenten"

Verwachte output: 1-2 documenten die als input dienen voor een FEAT-sprint die de daadwerkelijke wijzigingen implementeert.
