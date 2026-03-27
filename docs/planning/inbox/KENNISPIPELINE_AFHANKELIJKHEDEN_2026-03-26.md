# Kennispipeline — Afhankelijkheden & Volgorde

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
type: afhankelijkheidsdocument
doel: Claude Code gebruikt dit om de juiste volgorde en parallellisatie te bepalen
---

## Overzicht

De kennispipeline bestaat uit 5 sprint intakes verdeeld over 3 golven. Dit document beschrijft de afhankelijkheden zodat Claude Code automatisch de volgende ongeblokkeerde intake kan oppakken.

## Afhankelijkheidsgrafiek

```
GOLF 1 (parallel — geen blokkades)
├── Golf 1A: Research Contracts         → geen blokkade
├── Golf 1B: DocumentInterface + ODF    → geen blokkade
└── Track B S2: Google Drive adapter    → geen blokkade (bestaande intake)

        ↓ (Golf 1A + Track C S3-S5 moeten af)

GOLF 2 (sequentieel)
├── Golf 2A: Researcher + Curator       → geblokkeerd door: Golf 1A + Track C S3 + C5
└── Golf 2B: KWP DEV Bootstrap          → geblokkeerd door: Golf 2A

        ↓ (Golf 2B + Golf 1B + Track B S2 moeten af)

GOLF 3
└── Golf 3: Analyse Pipeline            → geblokkeerd door: Golf 2A, 2B, 1B, Track B S2
```

## Beslislogica voor Claude Code

Bij elke sessie-start, check:

1. **Is er een kennispipeline-intake ongeblokkeerd?**
   - Lees `geblokkeerd_door` veld in elke intake
   - Een intake is ongeblokkeerd als alle genoemde blokkades afgerond zijn
   - Afgerond = sprint-doc bestaat in `docs/planning/sprints/` OF tests groen

2. **Zijn er Golf 1 intakes die parallel kunnen?**
   - Golf 1A, 1B en Track B S2 hebben geen onderlinge afhankelijkheden
   - Combineer ze in één sprint als scope past, of pak ze sequentieel op

3. **Is Track C S3-S5 af?**
   - Zonder werkende Weaviate + embeddings kan Golf 2 NIET starten
   - Check: `packages/devhub-vectorstore/` bevat Weaviate adapter + embedding provider tests groen

4. **Is Golf 2A af?**
   - Zonder researcher + curator kan Golf 2B (bootstrap) niet starten
   - Check: `agents/knowledge-curator.md` bestaat + curator tests groen

5. **Zijn alle Golf 1 + Golf 2 af?**
   - Pas dan kan Golf 3 (analyse pipeline) starten

## Parallellisatie-regels

| Situatie | Actie |
|----------|-------|
| Golf 1 intakes ongeblokkeerd | Combineer maximaal 2 in één sprint |
| Track C S3-S5 nog bezig | Werk aan Golf 1 intakes |
| Golf 1 af, Track C af | Start Golf 2A |
| Golf 2A af | Start Golf 2B |
| Alles af behalve Track B S2 | Golf 3 kan starten met lokale opslag, Drive-opslag volgt |

## Architectuurbeslissingen (bindend)

Deze beslissingen zijn door Niels goedgekeurd tijdens de shaping-sessie van 2026-03-26:

1. **Weaviate als enige store** — geen SQLite. Observations, kennis, research requests: alles in Weaviate collections
2. **ODF als primair documentformaat** — vendor-agnostic (ISO/IEC 26300). Library: odfpy
3. **KnowledgeCurator als aparte agent** — niet als uitbreiding van QA Agent
4. **Demand-driven research** — agents kunnen ResearchRequests genereren
5. **BORIS-patronen hergebruiken** — curator audit-dimensies, observation types, health score. Maar als DevHub-implementatie, niet als BORIS-dependency
6. **DevHub bouwt tooling, projecten zijn standalone** — KWP DEV is DevHub's eigen kennisbank. BORIS heeft eigen KWP's, los van DevHub

## Relatie tot bestaande roadmap

Deze intakes voegen een nieuwe track toe aan Fase 3:

| Track | Status | Relatie kennispipeline |
|-------|--------|----------------------|
| Track A (uv workspace) | ✅ af | — |
| Track B (Storage) | S1 ✅, S2 📋 | S2 (Google Drive) = Golf 1 parallel |
| Track C (Vectorstore) | S1+S2 ✅, S3-S5 📋 | S3-S5 = fundament voor Golf 2 |
| Track M (Mentor) | 📋 | onafhankelijk |
| Track G (Governance) | 📋 | onafhankelijk |
| **Track K (Kennispipeline)** | **nieuw** | Golf 1 → 2 → 3 |
