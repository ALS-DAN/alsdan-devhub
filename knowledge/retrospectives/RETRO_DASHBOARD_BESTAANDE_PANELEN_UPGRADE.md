# Retrospective: Sprint 44 — Dashboard Bestaande Panelen Upgrade

**Datum:** 2026-03-29
**Type:** FEAT
**Size:** S (1 sprint)
**Node:** devhub
**Fase:** 4

## Resultaat

5 bestaande dashboard-panelen volledig upgraded van placeholder/statische data naar echte DevHub-systeem integratie.

| Metric | Waarde |
|--------|--------|
| Tests toegevoegd | +110 |
| Test baseline | 1489 → 1599 |
| Ruff errors | 0 |
| Geschatte grootte | S |
| Werkelijke grootte | S |

## Wat is opgeleverd

### Nieuwe componenten
- **SprintTrackerParser** — dedicated parser voor SPRINT_TRACKER.md (500+ regels), extraheert frontmatter, sprint history, velocity, cycle times, fase progress
- **CachedProvider mixin** — TTL-based caching (30s) met `_get_cached(key, loader)` voor filesystem-scanning providers
- **GovernanceProvider** — per-artikel DEV_CONSTITUTION verificatie via lambda checkers, compliance score, OWASP ASI coverage
- **GrowthProvider** — dynamische skill radar uit YAML/JSON, challenge engine, T-shape profiel
- **Multi-trend chart component** — Plotly multi-line wrapper
- **Kanban board component** — herbruikbaar met KanbanColumn/KanbanItem dataclasses

### Upgraded panelen
1. **Overview** — Smart KPI strip (7 cards incl. Compliance %), System Pulse 3x2 grid, Activity Feed
2. **Health** — 7-dimensie cards (was 2), multi-metric trend chart, snapshot history tabel
3. **Planning** — KPI strip met derived metrics, Fase pipeline, Sprint Analytics tabs (Velocity + Cycle Time), Kanban board
4. **Governance** — CSS conic-gradient compliance gauge, interactieve artikel-cards, OWASP ASI bars, Impact zone distributie
5. **Growth** — Dynamische Plotly radar met target overlay, domain detail cards, T-shape profiel, Challenge engine, Learning recommendations

### Backward compatibility
- HealthSnapshot uitgebreid met 4 nieuwe velden (`knowledge_items`, `knowledge_freshness`, `dependency_issues`, `sprint_hygiene_score`), allemaal met `= 0` defaults
- `from_dict` filtert onbekende keys — oude JSON snapshots laden zonder errors

## Wat ging goed

- **Scope split beslissing**: Mid-planning kwamen er 3 cross-cutting features bij (Quick Actions, Activity Stream, Projects page) via tech spec + mockup. Door direct te splitsen in Sprint 44 (panelen) en Sprint 45 (cross-cutting) bleef de sprint beheersbaar.
- **CachedProvider patroon**: Eenmalig geschreven, door meerdere providers hergebruikt. Voorkomt herhaalde filesystem scans.
- **SprintTrackerParser**: Door SPRINT_TRACKER.md parsing te isoleren in een dedicated parser met eigen tests (21 stuks) is het Planning-paneel robuust en testbaar.
- **Cowork-synchronisatie**: Cowork had parallel Sprint 43 afgesloten in SPRINT_TRACKER.md en pyproject.toml bijgewerkt. Geen conflicten — onze nieuwe bestanden (untracked) en Cowork's updates (tracked) raakten elkaar niet.

## Wat kan beter

- **Pre-existing test failures**: 2 tests (port 8080 vs 8765) bestonden al sinds Sprint 43. Eerder opmerken en fixen voorkomt verwarring bij sprint-afsluiting.
- **Mockup HTML formaat**: De HTML mockup was te groot om in één keer te lezen. Chunked reading werkte maar is traag. Overweeg voor toekomstige mockups een compacter formaat of een aparte design-spec.

## Scope voor Sprint 45

De volgende items zijn expliciet buiten scope gehouden voor Sprint 45:
- Quick Actions paneel (taak-shortcuts vanuit dashboard)
- Activity Stream (EventBus-driven activiteitenfeed)
- Projects pagina (node-overzicht met status)
