---
title: Retrospective — Research Compas Configuratie & Contracts (Sprint 33)
domain: retrospectives
grade: SILVER
date: 2026-03-28
author: devhub-sprint
sprint: Research Compas — Configuratie & Contracts
---

# Retrospective — Research Compas Configuratie & Contracts

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | 33 |
| Type | FEAT |
| Duur | 2026-03-28 → 2026-03-28 |
| Tests start | 743 |
| Tests eind | 799 |
| Tests delta | +56 |
| Deliverables | 7/7 afgerond |
| Lint | 0 errors |

## Wat ging goed

- **Backward compatible by design**: alle nieuwe velden (rq_tags, entity_refs, domain_ring) hebben defaults — 0 bestaande tests gebroken door de nieuwe code zelf
- **Bestaand patroon hergebruikt**: `_DOMAIN_RINGS` dict + `ring` property op enum, consistent met bestaande frozen dataclass patronen
- **KnowledgeConfig als frozen dataclass**: YAML-parsing naar immutable objecten, consistent met het contract-patroon in de hele codebase
- **Seed articles + bootstrap uitgebreid zonder breaking changes**: 8 bestaande seeds kregen rq_tags/domain_ring, 48 bootstrap requests dekken alle 16 domeinen

## Wat kan beter

- **7 bestaande tests faalden na enum-uitbreiding**: tests hadden hardcoded aannames over het aantal domeinen (4). Toekomstige tests moeten robuuster zijn tegen enum-groei (bijv. `len(KnowledgeDomain) >= 4` i.p.v. `== 4`)
- **ruff-format hook greep in bij eerste commit-poging**: 4 bestanden moesten geherformateerd. Lokale formatting-check vóór commit had dit voorkomen

## Beslissingen

| Beslissing | Reden |
|-----------|-------|
| CLAUDE_SPECIFIC niet hernoemen | Backward compat met bestaande vectorstore data |
| related_domains als simpele list[str] | YAGNI — gewogen relaties pas bij bewezen behoefte |
| agent_knowledge.yml als apart bestand | Scheiding config/ (systeem) vs agents/ (plugin) |
| rq_tags als post-filter in search | Vectorstore metadata filtering ondersteunt geen pipe-separated tag matching |

## Deliverables

- [x] KnowledgeDomain enum 4 → 16 waarden met ring metadata
- [x] KnowledgeArticle + ResearchRequest uitgebreid met rq_tags, entity_refs, domain_ring
- [x] config/knowledge.yml drie-ringen structuur
- [x] config/agent_knowledge.yml met 7 agent-profielen
- [x] KnowledgeConfig frozen dataclasses + YAML parser
- [x] KWPBootstrap 24 → 48 requests voor alle 16 domeinen
- [x] KnowledgeStore search uitgebreid met ring/rq_tags filters

## Volgende stap

Sprint 34 (Research Compas Runtime & Bootstrap) kan nu voortbouwen op deze contracts en configuratie voor runtime-integratie.
