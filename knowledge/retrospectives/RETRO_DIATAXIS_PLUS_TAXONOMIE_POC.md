---
title: Retrospective — Diátaxis+ Taxonomie & PoC (Sprint 32)
domain: retrospectives
grade: SILVER
date: 2026-03-28
author: devhub-sprint
sprint: Diátaxis+ Taxonomie & PoC
---

# Retrospective — Diátaxis+ Taxonomie & PoC

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | 32 |
| Type | FEAT |
| Duur | 2026-03-28 → 2026-03-28 |
| Tests start | 673 |
| Tests eind | 743 |
| Tests delta | +70 |
| Deliverables | 6/6 afgerond |
| Lint | 0 errors |

## Wat ging goed

- **Bestaande patronen hergebruikt**: DocumentCategory enum volgt exact het DocumentFormat patroon — geen nieuwe architectuur nodig
- **Backward compatible**: `category: str | None = None` breekt geen enkele bestaande test
- **Twee disconnected systemen (DocsAgent + devhub-documents) onafhankelijk uitgebreid**: geen grote refactor nodig
- **PoC valideert de pipeline end-to-end**: van DocumentRequest → MarkdownAdapter → bestand met frontmatter incl. category
- **Test-delta hoog (+70)**: goede dekking van alle 12 categorieën

## Wat kan beter

- **ODF adapter niet getest** (odfpy niet geïnstalleerd in de dev environment) — ODF-generatie overgeslagen
- **DocsAgent en devhub-documents nog disconnected**: DocsAgent gebruikt inline string templates, devhub-documents gebruikt gestructureerde DocumentRequest. Toekomstige sprint kan ze verbinden
- **Detectie in _detect_category() is keyword-based**: kan false positives geven (bijv. "context" matcht "explanation" maar kan in elke doc voorkomen)

## Actiepunten

1. odfpy installeren en ODF-output valideren (eventueel als chore)
2. Sprint 2 (Documentatie Pipeline) kan nu starten — intake is klaar
3. Overweeg DocsAgent → devhub-documents integratie in een toekomstige sprint

## Metrics

| Metric | Waarde |
|--------|--------|
| Bestanden gewijzigd | 8 |
| Bestanden nieuw | 4 (2 scripts, 1 testbestand, 1 retro) |
| DocumentCategory members | 12 |
| DIATAXIS_TEMPLATES entries | 12 |
| Gegenereerde documenten | 2 (explanation + reference) |
