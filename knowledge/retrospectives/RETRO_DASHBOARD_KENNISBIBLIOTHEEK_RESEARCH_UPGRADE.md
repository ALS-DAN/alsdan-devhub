---
title: Retrospective — Dashboard Kennisbibliotheek & Research Upgrade (Sprint 45)
domain: retrospectives
grade: SILVER
date: 2026-03-29
author: devhub-sprint
sprint: Dashboard Kennisbibliotheek & Research Upgrade
---

# Retrospective — Dashboard Kennisbibliotheek & Research Upgrade

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | 45 |
| Type | FEAT |
| Duur | 2026-03-29 → 2026-03-29 |
| Tests start | 1601 |
| Tests eind | 1682 |
| Tests delta | +81 |
| Deliverables | 6/6 fasen afgerond |
| Lint | 0 errors |
| Nieuwe bestanden | 6 modules + 3 test-bestanden |

## Git Analyse

| Metric | Waarde |
|--------|--------|
| Nieuwe bestanden | 9 (6 modules, 3 test-bestanden) |
| Gewijzigde bestanden | 5 (research_queue.py, app.py, knowledge.py, research.py, overview.py) |
| Nieuwe regels code | ~2800 (prod + tests) |

## Wat ging goed

- **CachedProvider hergebruik**: KnowledgeProvider volgt exact hetzelfde mixin-patroon als HealthProvider, PlanningProvider — consistent en voorspelbaar
- **Fuzzy frontmatter parser robuust**: Twee markdown-formaten (standaard YAML frontmatter + header+frontmatter) worden beide correct geparsed. Veldnaam-normalisatie (kennisgradering→grade, datum→date) maakt bestaande kennis-artikelen direct bruikbaar
- **ResearchQueueItem v2 backwards-compatible**: Lazy upgrade bij `from_dict()` — bestaande v1 JSON laadt zonder migratie, None-lijsten worden automatisch lege lijsten. Geen data-verlies
- **Componentenbibliotheek groeit**: knowledge_card en status_flow zijn herbruikbare components die op meerdere pagina's worden ingezet (catalogus, detail, search results)
- **81 tests in 6 fasen**: Goede dekking van article_parser (24), knowledge_provider (29), knowledge_pages (12), research v2 (8), components (8). Alle edge cases afgedekt
- **Overview-pagina verrijkt**: Knowledge freshness KPI en real provider data in System Pulse — was voorheen hardcoded "unknown"

## Wat kan beter

- **Geen UI-tests**: Alleen data-laag en configuratie getest. NiceGUI's `nicegui.testing.User` zou component-level browser tests mogelijk maken, maar is niet gebruikt. Overweeg voor toekomstige dashboard-sprints.
- **Sprint 2 (Discovery Engine) blijft open**: ABC-verbindingen, clustering, globale zoekfunctie en cross-paneel verbindingen zijn expliciet out-of-scope gehouden (geblokkeerd door Kennisketen). Dit is bewust maar verdient opvolging.
- **F-string syntax fout**: `f"Ring {{'core': '1'}.get(...)}"` crashte — dictionary literals in f-strings zijn een bekende Python-valkuil. Sneller herkennen in de toekomst.

## Patronen

### Herhaalde patronen (positief)
- **Provider-pattern werkt consistent**: Vijfde keer dat CachedProvider wordt ingezet (Health, Planning, Governance, Growth, Knowledge) — het patroon schaalt goed
- **Tabs-structuur voor pagina-organisatie**: Zowel Knowledge (Catalogus|Dekking|Versheid) als Research (Nieuw|Agent|Mijn|Auto) gebruiken tabs — bewezen UX-patroon uit Sprint 43
- **Frozen dataclasses voor data-transport**: ParsedArticle, DomainCoverage, FreshnessSummary volgen het bestaande frozen-dataclass patroon

### Herhaalde patronen (aandacht)
- **Pagina-herschrijvingen worden groot**: knowledge.py en research.py zijn volledig herschreven. Bij grotere pagina's overweeg opsplitsing in sub-modules (tabs als aparte bestanden)

## Agent-prestaties

| Agent | Ingezet | Observatie |
|-------|---------|------------|
| dev-lead | nee | Sprint via devhub-sprint skill |
| coder | nee | Directe implementatie |
| reviewer | nee | Inline review tijdens implementatie |
| researcher | nee | SOTA uit intake hergebruikt |
| planner | nee | Plan via plan mode |

## Lessen voor volgende sprint

1. **Dictionary literals niet in f-strings gebruiken** — altijd eerst naar variabele extraheren om SyntaxError te voorkomen
2. **Provider-pattern is bewezen** — voor elke nieuwe databron: maak een CachedProvider subclass met TTL 30s
3. **Backwards-compatibiliteit via defaults** — nieuwe dataclass-velden met `field(default_factory=list)` of `""` default voorkomt migratie-scripts

## Open items

- [ ] Sprint 2: Discovery Engine (ABC-verbindingen, clustering, globale zoekfunctie) — geblokkeerd door Kennisketen
- [ ] UI-tests toevoegen met nicegui.testing.User
- [ ] Knowledge-pagina sub-module opsplitsing overwegen bij verdere groei
