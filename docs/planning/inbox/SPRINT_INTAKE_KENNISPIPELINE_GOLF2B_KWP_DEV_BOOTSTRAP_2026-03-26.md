# Sprint Intake: Kennispipeline Golf 2B — KWP DEV Bootstrap

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
prioriteit: P1 (eerste echte vulling van KWP DEV)
sprint_type: CHORE
cynefin: simpel (researcher + curator staan klaar, dit is uitvoering)
impact_zone: GROEN (schrijft alleen naar vectorstore en knowledge/)
kennispipeline_golf: 2
parallel_met: geen
geblokkeerd_door: KENNISPIPELINE_GOLF2A_RESEARCHER_CURATOR
volgende_stap: KENNISPIPELINE_GOLF3_ANALYSE_PIPELINE
---

## Doel

Eerste gerichte vulling van KWP DEV. Laat de researcher draaien op een vooraf gedefinieerde set onderzoeksvragen voor de 4 kerndomeinen. Curator valideert en ingesteert in Weaviate. Na deze sprint is KWP DEV doorzoekbaar en bruikbaar.

## Probleemstelling

Na Golf 2A staan researcher en curator klaar, maar KWP DEV is leeg. Zonder content is de hele pipeline nutteloos. Een gestructureerde bootstrap met gerichte onderzoeksvragen vult de kennisbank met een solide basis.

## Deliverables

### Bootstrap onderzoeksvragen per domein

- [ ] **KB-01** — Domein: AI-engineering (8-10 research requests)
  - Prompt engineering SOTA en anti-patronen
  - Multi-agent architectuur patronen (orchestrator, blackboard, event-driven)
  - RAG-patronen: chunking strategieën, hybrid search, reranking
  - Tool use patterns en best practices
  - Context window management en optimalisatie
  - Agent memory: korte termijn vs. lange termijn, persistentie-patronen

- [ ] **KB-02** — Domein: Claude-specifiek (6-8 research requests)
  - Claude model capabilities en beperkingen (actueel)
  - Claude Code best practices en patronen
  - MCP-protocol: architectuur, security, best practices
  - Plugin-architectuur: structuur, distributie, versioning
  - System prompt design en optimalisatie

- [ ] **KB-03** — Domein: Python/software-architectuur (6-8 research requests)
  - ABC + frozen dataclass patroon: wanneer wel/niet, alternatieven
  - uv als package manager: workspace patterns, monorepo
  - Modern Python testing: pytest patterns, fixture design, property-based testing
  - Pydantic v2 vs. frozen dataclasses: trade-offs
  - Factory pattern varianten in Python

- [ ] **KB-04** — Domein: Development-methodiek (4-6 research requests)
  - Shape Up: verdieping appetite, betting table, hill charts
  - Cynefin: toepassing in software development, probe-sense-respond
  - DORA metrics: implementatie in solo/klein team context
  - Trunk-based development vs. feature branches bij solo development

### Uitvoering

- [ ] **KB-05** — Alle requests via ResearchQueue indienen
  - Diepte: STANDARD (5-10 bronnen per vraag)
  - Prioriteit: kerndomeinen eerst (AI-engineering, Claude)

- [ ] **KB-06** — Curator draait ingest-validatie op alle output
  - Verificatie dat gradering onderbouwd is
  - Deduplicatie-check
  - Art. 5 compliance

- [ ] **KB-07** — Kwaliteitsrapport na bootstrap
  - Health audit draaien
  - Gradering-distributie (verwacht: overwegend SILVER, sommige GOLD)
  - Dekking per domein
  - Openstaande kennislacunes identificeren

### Content doelen

- [ ] Minimum 25 kennisartikelen na bootstrap
- [ ] Elk kerndomein minimaal 5 artikelen
- [ ] Gemiddelde gradering minimaal SILVER
- [ ] Verificatiepercentage gemiddeld >60%

## Afhankelijkheden

- **Geblokkeerd door:** Golf 2A (researcher + curator moeten operationeel zijn)
- **BORIS impact:** nee
- **Extern:** WebSearch beschikbaarheid voor researcher

## Fase-context

Fase 3 (Knowledge & Memory). Dit is het moment dat KWP DEV van leeg naar bruikbaar gaat. Na deze sprint kan de analyse pipeline (Golf 3) kennis ophalen.

## Open vragen voor Claude Code

1. Moeten de research requests handmatig gedefinieerd worden of kan de researcher zelf sub-vragen genereren?
2. Wat is een realistisch aantal artikelen per sessie (token-budget)?
3. Moet de bootstrap in één sprint of gefaseerd (eerst 2 domeinen, dan 2)?

## DEV_CONSTITUTION impact

- **Art. 2 (Verificatieplicht):** elke claim in elk artikel wordt gelabeld
- **Art. 5 (Kennisintegriteit):** gradering is verplicht, curator valideert
- **Art. 7 (Impact-zonering):** GROEN — schrijft alleen naar vectorstore/knowledge
