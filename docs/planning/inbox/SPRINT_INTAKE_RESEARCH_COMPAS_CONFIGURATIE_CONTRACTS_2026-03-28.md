# SPRINT INTAKE: Research Compas — Configuratie & Contracts

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 3
---

## Doel

Breid de kennisinfrastructuur uit van 4 platte domeinen naar een drie-ringen domeinstructuur met RQ-tags en graph-ready velden op alle contracts — zonder runtime-wijzigingen.

## Probleemstelling

### Waarom nu

De huidige kennisinfrastructuur (`KnowledgeDomain` enum met 4 waarden, `knowledge.yml` als platte lijst) is te smal voor kennisbewuste agents. De planner heeft kennis nodig over estimation (past niet in "development_methodology"), de reviewer over anti-patronen (past niet in "python_architecture"), de red-team agent over OWASP (geen domein). Agents kunnen niet uitdrukken welke kennis ze nodig hebben, laat staan lacunes detecteren.

Daarnaast is de datastructuur niet voorbereid op cross-domein relaties — cruciaal voor BORIS met 10+ zorgdomeinen waar interventies over domeingrenzen heen werken. SOTA-onderzoek (GraphRAG, Graphiti, LazyGraphRAG) bevestigt dat graph-ready datastructuren nu voorbereid moeten worden, ook als de graph-engine later komt.

### Fase-context

Fase 3 (Knowledge & Memory) — dit is de configuratie-laag die de kennispipeline (Golf 1-3, operationeel) verrijkt met structuur en metadata. Geen nieuwe runtime-functionaliteit, alleen uitbreiding van het datamodel.

## Deliverables

- [ ] `config/knowledge.yml` — uitgebreid met drie-ringen structuur, RQ-focus per domein, `related_domains` veld, bootstrap-prioriteiten
- [ ] `KnowledgeDomain` enum — uitgebreid van 4 naar 16 domeinen (5 kern + 8 agent-specifiek + 3 project-specifiek) met ring-metadata
- [ ] `ResearchRequest` contract — nieuw veld `rq_tags: tuple[str, ...]` (welke RQ's raakt dit request)
- [ ] `KnowledgeArticle` contract — nieuwe velden: `rq_tags: tuple[str, ...]`, `entity_refs: tuple[str, ...]` (graph-ready), `domain_ring: Literal["core", "agent", "project"]`
- [ ] `config/agent_knowledge.yml` — nieuw configuratiebestand met knowledge profiles per agent (required_domains, min_grade, rq_focus, pre_task_check, auto_research flags)
- [ ] Bestaande tests groen (geen breaking changes — alle nieuwe velden hebben defaults)
- [ ] Nieuwe tests voor uitgebreide enums, nieuwe velden, configuratie-parsing

## Afhankelijkheden

- **Geblokkeerd door:** geen — bouwt voort op bestaande Golf 1-3 contracts
- **BORIS-impact:** nee — DevHub-intern. Ring 3 project-domeinen zijn configuratie-placeholders, geen actieve BORIS-koppeling

## Fase-context

**Fase 3** — Knowledge & Memory. Past volledig binnen de huidige fase. De drie-ringen structuur en graph-ready velden zijn voorbereidend voor Fase 4/5 maar vereisen geen Fase 4-goedkeuring (het zijn DevHub-interne datamodel-uitbreidingen).

## Open vragen voor Claude Code

1. `KnowledgeDomain` is nu een Python enum. Met 16 waarden + ring-metadata: blijft een enum het juiste patroon, of is een registry-class met YAML-backing beter? (Overweeg: Weaviate collections gebruiken de enum-waarden als filter)
2. `agent_knowledge.yml` als nieuw bestand vs. uitbreiding van bestaande agent `.md` files met YAML frontmatter — wat past beter bij het plugin-systeem?
3. `related_domains` in knowledge.yml: simpele lijst van strings, of een gewogen relatie `{domain: str, weight: float, relation_type: str}`? (Graph-readiness vs. complexiteit nu)
4. Backward compatibility: `to_dict()` en `to_document_chunk()` methoden moeten de nieuwe velden meenemen naar Weaviate. Hoe omgaan met bestaande data in de vectorstore die deze velden niet heeft?

## Prioriteit

**Hoog** — Dit is de fundatie waarop Sprint 2 (runtime + bootstrap) bouwt. Zonder deze contract-uitbreidingen kunnen agents geen knowledge profiles gebruiken.

## Technische richting (suggestie — Claude Code mag afwijken)

- Alle nieuwe velden op frozen dataclasses krijgen defaults (backward compatible)
- `KnowledgeDomain` uitbreiden met `ring` property of migreren naar registry-pattern
- `knowledge.yml` parser uitbreiden (bestaande health-audit drempels behouden)
- Tests: parametrized tests voor alle 16 domeinen, edge cases voor nieuwe velden

## DEV_CONSTITUTION impact

- **Art. 3 (codebase-integriteit):** alle wijzigingen backward compatible — GREEN zone
- **Art. 5 (kennisintegriteit):** deze sprint implementeert de structuur voor volledige Art. 5 compliance (RQ-dekking, grading per domein)
- **Art. 9 (planning-integriteit):** SPRINT_TRACKER.md bijwerken na afronding

## SOTA-onderbouwing

| Concept | Bron | Gradering |
|---------|------|-----------|
| Drie-ringen domeinstructuur | Ontology-Enhanced Decision-Making (arXiv 2405.17691) | SILVER |
| Graph-ready datamodellen | Graphiti (arXiv 2501.13956, Zep/Neo4j 2025) | SILVER |
| LazyGraphRAG kostenmodel | Microsoft Research (2025) | SILVER |
| Agent knowledge profiles | KnowAgent (NAACL 2025) | SILVER |
| RQ-gestructureerde kennisorganisatie | BORIS ADR-037 (MEC-methode) | Geverifieerd |
| Hybrid RAG architectuur (vector+graph) | Neo4j benchmark, Lettria/AWS 2024 | SILVER |
