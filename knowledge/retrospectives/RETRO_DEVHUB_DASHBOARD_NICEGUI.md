---
title: Retrospective — DevHub Dashboard NiceGUI (Sprint 43)
domain: retrospectives
grade: SILVER
date: 2026-03-28
author: devhub-sprint
sprint: DevHub Dashboard NiceGUI
---

# Retrospective — DevHub Dashboard NiceGUI

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | 43 |
| Type | FEAT |
| Duur | 2026-03-28 → 2026-03-28 |
| Tests start | 1424 |
| Tests eind | 1489 |
| Tests delta | +65 |
| Deliverables | 7/7 panelen afgerond |
| Lint | 0 errors |
| Nieuw package | devhub-dashboard v0.1.0 |

## Wat ging goed

- **Frozen dataclasses hergebruikt**: Alle bestaande contracts (FullHealthReport, SkillRadarProfile, SecurityFinding, ResearchRequest, Event types) direct importeerbaar — geen nieuwe data-types nodig
- **Event Bus integratie soepel**: InMemoryEventBus + KnowledgeGapDetected → ResearchQueueManager werkt end-to-end, 4 event tests bevestigen subscribe/unsubscribe/re-subscribe
- **NiceGUI past goed in de stack**: FastAPI-native, pytest-compatible, Plotly-integratie werkt out-of-the-box
- **BORIS-precedent waardevol**: ADR-059 uit buurts-ecosysteem gaf bewezen patronen (ui.run_with, storage_secret)
- **Research-paneel drie-stromen**: Tabs-patroon werkt goed voor visuele scheiding agent/user/auto stromen
- **65 tests in één sprint**: goede dekking van providers, history, queue, events, config, components

## Wat kan beter

- **Health checks beperkt**: Huidige HealthProvider doet alleen test-file telling en package counting. Volledige 7-dimensie health check vereist integratie met bestaande health-skill logica
- **Historische data nog leeg bij eerste start**: Dashboard moet eerst een paar keer de health-pagina bezoeken voordat trend-grafieken data tonen
- **Knowledge grading scan is keyword-based**: `_scan_grading()` zoekt naar "GOLD"/"SILVER" etc. in bestandsinhoud — kan false positives geven
- **Geen nicegui.testing UI-tests**: Alleen data-laag en configuratie getest, geen browser-level component tests. NiceGUI's testing framework is beschikbaar maar niet gebruikt
- **Growth pagina gebruikt hardcoded Dreyfus levels**: _DEFAULT_DOMAINS is statisch, niet gekoppeld aan SkillRadarProfile data

## Actiepunten

1. **Health-skill integratie**: Koppel HealthProvider aan bestaande health-check logica in devhub-core voor volledige 7-dimensie check
2. **UI-tests toevoegen**: Gebruik nicegui.testing.User voor component-level browser tests
3. **Growth data dynamisch**: Lees SkillRadarProfile uit storage/vectorstore in plaats van hardcoded defaults
4. **Auto-refresh**: Implementeer `ui.timer()` voor periodieke data-refresh zonder handmatig herladen

## Architectuurbeslissingen

- **Nieuw package `devhub-dashboard`** in uv workspace — geen wijzigingen aan bestaande packages
- **Lazy provider initialisatie** via global singletons in app.py — simpelste aanpak voor lokaal single-user dashboard
- **JSON-based persistence** voor HistoryStore en ResearchQueueManager — past bij LocalAdapter patroon, later upgradebaar naar devhub-storage

## Impact

- **GREEN zone**: Volledig nieuw package, nul wijzigingen aan bestaande code
- **5e workspace member**: devhub-dashboard naast core, storage, vectorstore, documents
- **Eerste Fase 4 deliverable**: Visueel verbindt alle Fase 0-3 subsystemen
