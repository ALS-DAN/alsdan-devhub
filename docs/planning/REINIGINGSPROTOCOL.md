# Reinigingsprotocol — DevHub Planning Governance

---
gegenereerd_door: "Cowork Architect — alsdan-devhub"
status: ACTIEF
datum: 2026-03-24
dev_constitution_impact: "Art. 4 (traceerbaarheid), Art. 7 (impact-zonering)"
---

## Doel

DevHub's planningssysteem moet zichzelf schoon houden. Dit protocol definieert hoe items door de planning-pipeline stromen, wanneer ze verouderen, en hoe opruiming werkt.

## Directory-structuur

```
docs/planning/
├── inbox/          ← ruwe ideeën, ongefilterd (IDEA_*, RESEARCH_*, SPRINT_INTAKE_*)
├── backlog/        ← geshaped, geprioriteerd, klaar voor sprint
├── sprints/        ← actieve en afgeronde sprint-documenten
├── parked/         ← uitgesteld (buiten huidige fase, niet-actueel)
└── SPRINT_INPUT.md ← synthese voor volgende sprint (sprint-prep output)
```

## Item-levenscyclus

```
INBOX → [shaping] → BACKLOG → [sprint-prep] → SPRINT → [closure] → RETRO
  ↓                    ↓
PARKED              PARKED (als 2 sprints niet opgepakt)
  ↓                    ↓
VEROUDERD           VEROUDERD (bij fase-overgang review)
  ↓                    ↓
VERWIJDERD          VERWIJDERD (of terug naar INBOX als weer relevant)
```

## Statussen

| Status | Betekenis | Locatie |
|--------|-----------|---------|
| INBOX | Ruw idee, niet geshaped | `inbox/` |
| BACKLOG | Geshaped, geprioriteerd, wacht op sprint | `backlog/` |
| ACTIEF | Onderdeel van lopende sprint | `sprints/` |
| AFGEROND | Sprint voltooid | `sprints/` |
| GEPARKEERD | Buiten scope huidige fase, bewust uitgesteld | `parked/` |
| VEROUDERD | >30 dagen zonder activiteit, niet meer relevant | verwijderd met notitie |

## Verouderingsregels

| Regel | Trigger | Actie |
|-------|---------|-------|
| **Inbox-veroudering** | Item in inbox/ >30 dagen zonder activiteit | Markeer als STALE in triage-index. Bij volgende triage: parkeren of verwijderen. |
| **Backlog-veroudering** | Item in backlog/ niet opgepakt in 2 opeenvolgende sprints | Demote naar parked/. Noteer reden. |
| **Parkeer-review** | Fase-overgang (bijv. Fase 2→3) | Review alle items in parked/. Relevant? → terug naar inbox/. Niet meer? → verwijderen. |
| **Duplicaat-detectie** | Bij elke triage | Items die overlappen met bestaand werk → mergen of verwijderen. |

## Triage-proces

Triage vindt plaats bij:
1. **Sessie-start** — sprint-prep skill scant inbox/ en backlog/
2. **Sprint-closure** — dev-lead evalueert wat overblijft
3. **Fase-overgang** — volledige review van alle directories

Per item wordt getoetst:
1. Past dit in de huidige fase? → Zo niet: parkeren
2. Is dit een duplicaat? → Zo ja: mergen
3. Is het geshaped (probleem + oplossing + grenzen)? → Zo niet: inbox houden
4. Heeft het een afhankelijkheid die nog niet af is? → Noteer blocker
5. Is het testbaar (INVEST-T)? → Zo niet: terug naar shaping

## Triage-index

Het bestand `docs/planning/TRIAGE_INDEX.md` bevat de actuele status van alle items. Dit wordt bijgewerkt bij elke triage. Format:

```markdown
| Item | Status | Fase | Prioriteit | Afhankelijk van | Notitie |
```

## Automatisering (toekomstig)

Wanneer n8n operationeel is:
- **Dagelijks:** inbox/ scan op items >30 dagen → STALE-label
- **Bij sprint-closure:** backlog/ scan op items niet opgepakt → demote-voorstel
- **Bij fase-overgang:** parked/ review trigger → Niels-notificatie

Tot die tijd: handmatige triage bij sessie-start via sprint-prep skill.

## DEV_CONSTITUTION alignment

- **Art. 4 (Traceerbaarheid):** Elke statuswijziging wordt gelogd in TRIAGE_INDEX.md
- **Art. 7 (Impact-zonering):** Parkeren en verwijderen zijn GROEN (reversibel, geen code-impact)
