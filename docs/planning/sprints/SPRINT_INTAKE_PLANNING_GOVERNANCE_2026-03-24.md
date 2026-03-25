# Sprint Intake: Planning Governance & Backlog-laag

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: BACKLOG
fase: 2
prioriteit: P1
sprint_type: CHORE
---

## Doel

DevHub's planningssysteem krijgt een backlog-laag, reinigingsprotocol en triage-index zodat de inbox beheersbaar blijft en items traceerbaar door de pipeline stromen.

## Probleemstelling

De inbox groeide naar 21+ items zonder structuur. Er is geen tussenstap tussen "ruw idee" en "actieve sprint". Items verouderen onzichtbaar. Duplicaten worden niet gedetecteerd. Dit is geen schaalbaar proces — zeker niet als DevHub meer projecten gaat bedienen.

## Deliverables

- [x] `docs/planning/backlog/` directory aangemaakt
- [x] `docs/planning/parked/` directory aangemaakt
- [x] `docs/planning/REINIGINGSPROTOCOL.md` geschreven
- [x] `docs/planning/TRIAGE_INDEX.md` initiële triage uitgevoerd
- [x] `docs/planning/ROADMAP.md` geconsolideerde roadmap
- [ ] Duplicaat-IDEAs verplaatsen naar `parked/` (n8n health, governance, PR gate IDEAs)
- [ ] Geparkeerde items fysiek verplaatsen naar `parked/`
- [ ] sprint-prep skill updaten: scant nu backlog/ in plaats van alleen inbox/
- [ ] planner agent updaten: kent backlog-promotie als taak
- [ ] DEVHUB_BRIEF.md updaten met nieuwe planningsstructuur

## Afhankelijkheden

- Geblokkeerd door: geen
- BORIS impact: nee

## Fase-context

Fase 2 (afronding). Dit is housekeeping die nodig is voordat Fase 3 start. Zonder dit groeit de chaos mee.

## Open vragen voor Claude Code

1. Moet sprint-prep skill de TRIAGE_INDEX.md automatisch bijwerken bij elke run?
2. Moet de planner agent een "triage-modus" krijgen als apart commando?
3. Willen we een pre-commit hook die waarschuwt als inbox/ >15 items bevat?

## DEV_CONSTITUTION impact

- Art. 4 (Traceerbaarheid): TRIAGE_INDEX.md borgt zichtbaarheid van alle items
- Art. 7 (Impact-zonering): GROEN — geen code-impact, alleen planning-documenten
