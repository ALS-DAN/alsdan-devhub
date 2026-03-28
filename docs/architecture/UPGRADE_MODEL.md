# Upgrade-model: DevHub verbetert projecten

---
laatst_bijgewerkt: 2026-03-27
status: ACTIEF
vervangt: docs/MIGRATION_PLAN.md (gearchiveerd)
---

## Principe

DevHub **upgradet** projecten. Het sloopt niets, het vervangt niets. Het bekijkt bestaande code met een SOTA-bril en verbetert waar mogelijk — zonder de essentie te verliezen.

De "ziel" van BORIS-agents (VERA, LUMEN, CLAIR, SCOUT, HERALD, CURATOR, ATLAS, SCRIPTOR) blijft bewaard. Deze Gems zijn ontstaan vanuit een visie en hebben een eigen identiteit. DevHub respecteert die identiteit en versterkt ze.

## Hoe upgraden werkt

```
1. DevHub analyseert     →  NodeInterface leest project-status
2. DevHub identificeert  →  Verbeterkansen op basis van SOTA-kennis
3. DevHub stelt voor     →  Upgrade-voorstel aan Niels
4. Niels keurt goed      →  DEV_CONSTITUTION Art. 1
5. DevHub implementeert  →  Code upgraden met behoud van essentie
6. DevHub verifieert     →  Tests, review, health check
```

## Wat DevHub kan upgraden

### Project-skills

BORIS heeft eigen skills die DevHub heeft geschreven of kan verbeteren:

| BORIS skill | Functie | Upgrade-potentieel |
|-------------|---------|-------------------|
| buurts-sprint | Sprint lifecycle | Workflow verfijnen, betere context-loading |
| buurts-health | 10-staps diagnostic | Uitbreiden met DevHub health-patronen |
| buurts-review | Code review | Al gedeeltelijk geüpgraded via QA Agent checks |
| boris-sprint-prep | Sprint voorbereiding | Integratie met DevHub sprint-prep patronen |
| mentor-dev | O-B-B developer coaching | Uitbreiden met Skill Radar, Challenge Engine |

**Belangrijk:** Deze skills worden geüpgraded, niet vervangen. Ze blijven in BORIS leven.

### Project-code

BORIS runtime agents kunnen geüpgraded worden:

| Agent | Gem-identiteit | Upgrade-aanpak |
|-------|---------------|----------------|
| VERA | Analyse + safety | Code-kwaliteit, test coverage verbeteren |
| LUMEN | Monitoring + rapportage | DevReport format uitbreiden |
| CLAIR | Kennisverwerking | Integratie met devhub-vectorstore patronen |
| SCOUT | Document discovery | Verbeteren met storage-patronen |
| HERALD | Publicatie + sync | Workflow optimalisatie |
| CURATOR | Kennisbeheer | Kwaliteitschecks versterken |
| ATLAS | Navigatie | Architectuur-inzichten toevoegen |
| SCRIPTOR | Document generatie | Diátaxis-principes toepassen |

### BorisAdapter uitbreidingen

De adapter kan groeien om meer project-context beschikbaar te maken:

| Capability | Status | Nodig voor |
|-----------|--------|------------|
| LUMEN DevReport lezen | Done | Health, analyse |
| MkDocs navigatie scannen | Done | Docs audit |
| Pytest uitvoeren | Done | Quality check |
| Health status bepalen | Done | Health skill |
| Sprint-docs lezen | TODO | Sprint context |
| OVERDRACHT.md lezen | TODO | Sessie-continuïteit |
| Inbox lezen | TODO | Sprint planning |

## Feedback loop

Kennis stroomt in twee richtingen:

**DevHub → Project:** DevHub schrijft en upgradet skills en code voor projecten.

**Project → DevHub:** Als een project-innovatie een beter patroon oplevert dan wat DevHub zelf gebruikt, detecteert DevHub dat en stelt voor om zichzelf te verbeteren.

Voorbeeld: Als BORIS' HERALD-publicatiepatroon effectiever blijkt dan DevHub's eigen sprint-afsluiting, kan DevHub dat patroon overnemen.

## Volgorde

Er is geen vaste migratie-volgorde. DevHub upgradet op basis van:

1. **Behoefte** — Wat heeft het project nu nodig?
2. **Impact** — Waar levert verbetering het meeste op?
3. **Readiness** — Wat kan DevHub al goed genoeg om te upgraden?
4. **Niels' prioriteit** — Wat wil Niels als eerste aanpakken?

## Wat dit NIET is

- **Geen migratie** — Code verhuist niet van BORIS naar DevHub
- **Geen vervanging** — BORIS skills worden niet gesloopt
- **Geen overname** — BORIS behoudt eigen identiteit en governance
- **Geen one-size-fits-all** — Elke upgrade is maatwerk per project
