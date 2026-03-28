---
title: Retrospective — Documentatie-productie Pipeline & BORIS-blauwdruk (Sprint 34)
domain: retrospectives
grade: SILVER
date: 2026-03-28
author: devhub-sprint
sprint: Doc Pipeline & BORIS-blauwdruk
---

# Retrospective — Documentatie-productie Pipeline & BORIS-blauwdruk

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | 34 |
| Type | FEAT |
| Duur | 2026-03-28 → 2026-03-28 |
| Tests start | 743 |
| Tests eind | 814 |
| Tests delta | +71 |
| Deliverables | 6/6 afgerond |
| Lint | 0 errors |

## Wat ging goed

- **Drie packages verbonden zonder wijzigingen aan die packages**: devhub-vectorstore, devhub-documents en devhub-storage ongewijzigd — alleen orkestratie-laag erboven
- **Graceful degradation werkt**: DocumentService functioneert zonder storage (lokaal-only) en zonder vectorstore (template-only), met fatsoenlijke fallbacks
- **FolderRouter als apart component**: herbruikbaar buiten DocumentService, node-specifieke taxonomie is configuratie in YAML
- **Checksum-dedup eerste keer goed**: SHA256 vergelijking voorkomt onnodige re-uploads naar storage
- **BORIS-blauwdruk via configuratie**: boris-buurts hoeft alleen taxonomy + drive_root in documents.yml — geen code
- **Hoog test-delta (+71)**: E2E tests valideren de volledige keten inclusief idempotentie

## Wat kan beter

- **Documenten zijn template-only**: zonder vectorstore-content bevatten de gegenereerde documenten alleen sectie-koppen en placeholder-tekst. Echte content vereist gevulde vectorstore
- **Google Drive nog niet getest**: OAuth2 flow niet doorlopen (geen credentials in CI). CredentialResolver is gebouwd maar Drive-publicatie is ongevalideerd
- **DocsAgent en DocumentService nog parallel**: twee systemen voor document-generatie. DocsAgent genereert markdown via string-templates, DocumentService via DocumentRequest + adapters. Toekomstige integratie gewenst

## Actiepunten

1. **Google Drive validatie** — handmatig testen met echte credentials wanneer beschikbaar
2. **Vectorstore-content vullen** — Research Compas Runtime sprint (intake C) bootstrap Ring 1 domeinen, daarna documenten met echte kennis genereren
3. **DocsAgent integratie** — overweeg DocsAgent te laten delegeren naar DocumentService voor gestructureerde output

## Kenniswinst

- Het **orchestrator-patroon met dependency injection** (storage=None, vectorstore=None) is een krachtig middel voor testbaarheid en stapsgewijze uitrol
- **Node-specifieke configuratie in YAML** schaalt beter dan code: boris-buurts toevoegen kostte 6 regels YAML, nul Python
- **Checksum-based dedup** is eenvoudiger en betrouwbaarder dan versienummer-vergelijking
