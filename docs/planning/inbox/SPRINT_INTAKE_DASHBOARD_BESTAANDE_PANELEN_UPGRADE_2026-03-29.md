---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
node: devhub
sprint_type: FEAT
fase: 4
---

# Sprint Intake: Dashboard Bestaande Panelen Upgrade — Overview, Health, Planning, Governance, Growth

## Doel

Upgrade de vijf bestaande dashboard-pagina's (Overview, Health, Planning, Governance, Growth) van basale statusweergaven naar informatierijke, interactieve panelen met analytics, audit trails, en actionable insights.

## Probleemstelling

De vijf pagina's uit Sprint 43 zijn functioneel maar oppervlakkig. Ze tonen basisgegevens zonder context, historie, of interactie.

**1. Overview = statisch.** Zes KPI-cards en zes domein-kaarten, maar geen activity feed, geen sparklines, geen "system pulse". Je moet doorklikken naar elke pagina om iets te weten.

**2. Health = te weinig dimensies.** Twee checks (tests, packages). DevHub heeft 7 health-dimensies beschikbaar (tests, packages, dependencies, architecture, knowledge health, security, sprint hygiene) — vijf worden niet getoond. De trend-chart toont alleen test-bestanden.

**3. Planning = geen analytics.** Een inbox-tabel en fase-voortgang. De SPRINT_TRACKER bevat 43 sprints met velocity data, cycle time, test-deltas, en hill chart informatie — niets daarvan wordt gevisualiseerd. Geen Kanban-weergave van de planning-pipeline.

**4. Governance = statisch.** Een lijst van 9 artikelen zonder verificatiestatus, audit trail, of compliance-scores. De SecurityAuditReport en OWASP ASI contracts bestaan maar worden niet benut. Geen inzicht in welke sprints welke artikelen raken.

**5. Growth = hardcoded.** Dreyfus levels zijn hardcoded in de pagina-code. `growth_contracts.py` biedt SkillRadarProfile, DevelopmentChallenge, LearningRecommendation, en GrowthReport — allemaal onbenut. Geen challenge-tracking, geen learning recommendations, geen growth velocity.

**Waarom nu:** Deze pagina's vormen samen met de Kennisbibliotheek + Research upgrade (aparte intake) het complete dashboard. Door beide intakes samen te plannen wordt het dashboard in één keer naar productieniveau gebracht.

**Fase-context:** Fase 4 — Verbindingen. De data voor deze upgrades bestaat al in het systeem (SPRINT_TRACKER, contracts, Event Bus). Het dashboard moet die data ontsluiten.

## SOTA-onderbouwing

### Sprint Analytics & Velocity
- **DORA Metrics** (dora.dev): Deployment Frequency, Lead Time, Change Failure Rate, Time to Restore. DevHub's equivalent: Sprint Frequency, Cycle Time (inbox → done), Estimation Accuracy, Sprint Velocity.
- **SPACE Framework** (LinearB 2025): Satisfaction, Performance, Activity, Communication, Efficiency — meerdere dimensies naast pure velocity.
- **Axify 2025**: 17 Agile metrics waaronder velocity trend, sprint burndown, cycle time distribution, throughput.

### Governance & Compliance Dashboards
- **MetricStream 2025**: Real-time compliance dashboards met circulaire gauges, heatmaps, audit trails. 78% van compliance professionals rapporteert betere risicomitigatie met real-time dashboards.
- **GRC best practices** (V-Comply): Compliance scoring, policy tracking, audit trail met wie/wanneer/wat, color-coded status (groen/geel/rood).
- **Apptega**: Compliance frameworks als visual scorecards, gap-analyse per policy.

### Developer Growth & Learning Analytics
- **Dreyfus Model** (Kaizenko, LeadingSapiens): Vijf stadia met duidelijke drijfveren en behoeften per niveau. Bereiken van "proficient" vereist vele uren deliberate practice.
- **Cognota 2025**: L&D metrics dashboard framework: business outcome → vragen → KPIs. Stages: completions → engagement → capability mapping → AI forecasting → productivity correlation.
- **D2L Corporate Learning Analytics 2026**: Vijf volwassenheidsstadia van learning analytics, van compliance tracking tot AI-driven insights.

## Deliverables

### A. Overview Upgrade

- [ ] **Smart KPI Strip** — 7 KPI-cards met sparkline mini-charts
  - Tests (sparkline: groei over laatste 10 sprints)
  - Sprint # (met velocity indicator: "100% on-time")
  - Packages (met versie-indicators)
  - Knowledge (met freshness breakdown: N fresh / N aging / N stale)
  - Research (met pending-count badge)
  - Health (overall status dot)
  - Fase (met progress dots 0-5)
  - Data: gecombineerd uit HealthProvider, PlanningProvider, KnowledgeProvider, ResearchQueueManager

- [ ] **System Pulse / Activity Feed** — laatste 5-10 systeem-events
  - Chronologisch: sprint afgerond, kennis toegevoegd, research ingediend, health alert, etc.
  - Data: Event Bus events of fallback naar filesystem timestamps
  - Compact formaat: icoon + beschrijving + timestamp

- [ ] **Domein Status grid verbeterd** — per domein meer context
  - Health: dimensies gecontroleerd + alerts count
  - Planning: actieve sprint + inbox count + velocity badge
  - Knowledge: artikelen + freshness score + dekkingspercentage
  - Governance: compliance % (artikelen actief/totaal)
  - Research: pending/active/completed counts
  - Growth: gemiddeld Dreyfus level + primary gap
  - Per kaart: quick-link "→ Details" naar detail-pagina

### B. Health Upgrade

- [ ] **7 Health Dimensies** — uitbreiden van 2 naar 7 checks
  - Tests: test-bestanden tellen (bestaand)
  - Packages: workspace packages tellen (bestaand)
  - Dependencies: pyproject.toml scannen op outdated/pinning issues
  - Architecture: NodeInterface compliance check (adapter pattern intact)
  - Knowledge Health: freshness score + grading verdeling (hergebruik KnowledgeProvider)
  - Security: laatste SecurityAuditReport ophalen indien beschikbaar
  - Sprint Hygiene: velocity accuracy + stale inbox items + actieve sprint check

- [ ] **Multi-metric Trend Chart** — 3 lijnen op één grafiek
  - Test count (groen), Package count (blauw), Knowledge items (paars)
  - Data: HistoryStore uitbreiden met extra metrics per snapshot
  - NiceGUI: Plotly line chart (bestaand patroon via trend_chart component)

- [ ] **HealthSnapshot uitbreiden** met extra velden
  ```python
  # Toevoegen aan HealthSnapshot:
  knowledge_items: int = 0
  knowledge_freshness: float = 0.0  # 0.0-1.0
  dependency_issues: int = 0
  sprint_hygiene_score: float = 1.0  # 0.0-1.0
  ```
  Backwards-compatible: bestaande JSON-bestanden werken met defaults.

- [ ] **Health History tabel** — snapshots met sorteerbare kolommen

### C. Planning Upgrade

- [ ] **Sprint Analytics tabs**

  **Tab 1: Velocity & Cycle Time**
  - Bar chart: test-delta per sprint (laatste 15-20 sprints)
  - Line chart: cycle time trend (inbox → done)
  - Metric cards: Avg cycle time, Avg test delta, Estimation accuracy
  - Data: parse SPRINT_TRACKER.md velocity tracking + cycle time tabellen

  **Tab 2: Sprint Historie**
  - Sorteerbare tabel: #, Sprint naam, Type (FEAT/SPIKE/CHORE/BUG), Size (XS/S/M), Tests Δ, Cycle Time, Fase
  - Color-coded type badges
  - Filterable op type en fase
  - Data: parse SPRINT_TRACKER.md sprint log

- [ ] **PlanningProvider uitbreiden** met sprint-historie
  ```python
  @dataclass(frozen=True)
  class SprintHistoryItem:
      nummer: int
      naam: str
      sprint_type: str  # FEAT | SPIKE | CHORE | BUG | RESEARCH
      size: str  # XS | S | M
      tests_delta: int
      cycle_time: str  # "<1 dag" | "1 dag" | "2 dagen" etc.
      fase: str
      status: str  # DONE | ACTIEF

  # Nieuwe methode:
  def get_sprint_history(self) -> list[SprintHistoryItem]: ...
  def get_velocity_data(self) -> tuple[list[str], list[int]]: ...
  def get_cycle_time_data(self) -> tuple[list[str], list[float]]: ...
  ```

- [ ] **Planning Pipeline Kanban** — visuele kolommen
  - INBOX: sprint intakes met status INBOX
  - KLAAR: items met status READY/SHAPED (toekomstig)
  - ACTIEF: huidige actieve sprint
  - DONE: laatste 3-5 afgeronde sprints
  - PARKED: count badge (items in `parked/`)
  - NiceGUI: `ui.card()` per kolom met `ui.row()` layout

- [ ] **Fase Voortgang verbeterd** — verbonden cirkels met labels
  - Fase 0-5 als horizontale pipeline (vergelijkbaar met status_flow component)
  - ✅ voor afgerond, 🔄 voor actief, ○ voor toekomstig
  - Per fase: korte omschrijving + sprint-count

### D. Governance Upgrade

- [ ] **Compliance Score** — circulaire gauge
  - "9/9 artikelen actief" = 100%
  - Berekend uit daadwerkelijke checks per artikel
  - NiceGUI: Plotly gauge chart of CSS-based circular progress

- [ ] **DEV_CONSTITUTION Interactive View** — per artikel uitklapbaar
  - Artikel-badge + titel + korte beschrijving (bestaand)
  - Compliance status: ✅ Actief / ⚠️ Aandacht / ❌ Overtreding
  - Verificatiemethode: hoe wordt compliance gecontroleerd
  - Gerelateerde sprints: welke sprints dit artikel raakten
  - Audit trail entries: laatste wijzigingen
  - Data: combinatie van filesystem checks + SPRINT_TRACKER parsing

  Per artikel concrete verificatie:
  | Artikel | Verificatiemethode |
  |---------|-------------------|
  | Art. 1 (Identiteit) | CLAUDE.md + plugin.json bestaan |
  | Art. 2 (Autonomie) | Niels-goedkeuringen in sprint intakes |
  | Art. 3 (Codebase) | Test count > 0 + alle tests groen |
  | Art. 4 (Transparantie) | Sprint count + SPRINT_TRACKER.md bestaat |
  | Art. 5 (Kennisintegriteit) | Knowledge items met grading > 0 |
  | Art. 6 (Soevereiniteit) | nodes.yml + project-specifieke CLAUDE.md's bestaan |
  | Art. 7 (Impact-zonering) | Golden paths bestaan in docs/golden-paths/ |
  | Art. 8 (Security) | Geen secrets in git (check) + audit rapport bestaat |
  | Art. 9 (Planning) | SPRINT_TRACKER.md bestaat + is bijgewerkt |

- [ ] **GovernanceProvider** — nieuwe data provider
  ```python
  class GovernanceProvider:
      def get_compliance_score(self) -> ComplianceScore: ...
      def get_article_status(self) -> list[ArticleComplianceStatus]: ...
      def get_security_summary(self) -> SecuritySummary | None: ...
      def get_audit_trail(self, limit: int = 10) -> list[AuditEntry]: ...
  ```

- [ ] **OWASP ASI Coverage** — horizontale bars per checkpoint
  - 10 ASI checkpoints met mitigatie-status (mitigated/partial/open)
  - Data: SecurityAuditReport.asi_coverage uit security_contracts
  - Fallback: toon "Geen audit data — draai /devhub-redteam"

- [ ] **Impact Zone Distribution** — pie chart of stacked bar
  - GREEN/YELLOW/RED verdeling van sprints
  - Data: parse sprint intakes op impact-zonering markers

### E. Growth Upgrade

- [ ] **Dynamische Skill Radar** — vervang hardcoded data
  - Lees `knowledge/skill_radar/SKILL_RADAR_PROFILE_2026-03-26.yaml` als bron
  - Fallback naar defaults als bestand niet bestaat
  - Twee overlays op Plotly radar: huidig (solid) + target (dashed, +1 per ZPD-domein)
  - Hover: subdomeinen en evidence per domein

- [ ] **GrowthProvider** — nieuwe data provider
  ```python
  class GrowthProvider:
      def get_skill_radar(self) -> SkillRadarProfile | None: ...
      def get_challenges(self) -> list[DevelopmentChallenge]: ...
      def get_recommendations(self) -> list[LearningRecommendation]: ...
      def get_growth_report(self) -> GrowthReport | None: ...
  ```
  Data-bronnen:
  - Skill radar: `knowledge/skill_radar/*.yaml`
  - Challenges: `data/challenges/*.json` (nieuw)
  - Recommendations: gegenereerd door mentor agent → `data/recommendations/*.json`

- [ ] **Domain Detail Cards** — per domein uitklapbaar
  - Dreyfus level badge (1-5 met label)
  - Progress bar naar volgend niveau
  - Evidence: welke sprints/werk dit niveau aantonen
  - ZPD tasks: voorgestelde uitdagingen
  - Growth velocity: pijl omhoog/vlak/omlaag

- [ ] **T-Shape Profiel verbeterd** — visuele T
  - Horizontale balk: domeinen op level 2+ als verbonden blokken
  - Verticale balk: specialisatiedomeinen met diepte-indicators
  - Dynamisch op basis van skill radar data

- [ ] **Challenge Engine paneel**
  - Actieve challenges: lijst (status ACCEPTED)
  - Voorgestelde challenges: kaarten met type badge, domein, beschrijving, scaffolding level
  - Afgeronde challenges: historie met feedback
  - "Start Challenge" / "Skip" / "Complete" acties
  - Data: `DevelopmentChallenge` dataclass + file-based storage

- [ ] **Learning Recommendations**
  - 3-5 aanbevelingskaarten
  - Per kaart: titel, resource type badge (paper/docs/tutorial/video), domein, geschatte tijd, ZPD alignment, prioriteit
  - Data: `LearningRecommendation` dataclass + file-based storage

## Afhankelijkheden

| Afhankelijkheid | Impact | Status |
|-----------------|--------|--------|
| SPRINT_TRACKER.md | Planning analytics parsed alle sprint-data hieruit | ✅ Beschikbaar (505 regels) |
| HealthProvider + HistoryStore | Health upgrade bouwt voort op bestaande providers | ✅ Beschikbaar |
| growth_contracts.py | Growth upgrade gebruikt SkillRadarProfile, Challenge, etc. | ✅ Beschikbaar |
| security_contracts.py | Governance upgrade leest SecurityAuditReport | ✅ Beschikbaar |
| event_contracts.py | Overview activity feed leest Event Bus events | ✅ Beschikbaar |
| SKILL_RADAR_PROFILE_*.yaml | Growth dynamisch laden van skill data | ✅ 1 bestand aanwezig |
| KnowledgeProvider (uit andere intake) | Overview + Health gebruiken freshness data | Depends on Kennisbibliotheek sprint |
| BORIS-impact | Geen — pure DevHub-dashboard code | n.v.t. |

## Fase-context

Fase 4 — Verbindingen. Deze sprint verbindt bestaande data-bronnen (SPRINT_TRACKER, contracts, Event Bus, knowledge/, skill_radar/) met het dashboard. Alle data bestaat al — het dashboard moet het ontsluiten.

## DEV_CONSTITUTION impact

| Artikel | Impact |
|---------|--------|
| Art. 4 (Transparantie) | Governance-paneel maakt compliance-verificatie transparant |
| Art. 5 (Kennisintegriteit) | Health-paneel toont knowledge freshness |
| Art. 7 (Impact-zonering) | GREEN: dashboard-only wijzigingen |
| Art. 9 (Planning) | Planning-paneel visualiseert SPRINT_TRACKER data (read-only) |

## Open vragen voor Claude Code

1. **SPRINT_TRACKER parsing**: Het bestand is 505 regels met tabellen en regex-parseerbare structuur. Hoe robuust moet de parser zijn? Suggestie: dedicated `SprintTrackerParser` class met fallbacks.
2. **HealthProvider dimensies**: De huidige provider doet 2 checks. Uitbreiden naar 7 vereist meer filesystem-scans. Performance-impact bij elke page load? Suggestie: caching met 30s TTL.
3. **Growth data persistentie**: Challenges en recommendations moeten ergens opgeslagen worden. `data/challenges/` en `data/recommendations/` als JSON-bestanden? Of in de vectorstore?
4. **Governance audit trail**: Waar worden governance-events opgeslagen? Event Bus is in-memory. Suggestie: file-based audit log in `data/governance/audit_log.json`.
5. **Plotly dependencies**: Growth en Planning gebruiken Plotly intensief. Is de huidige `ui.plotly()` performance voldoende bij 5+ charts per pagina?
6. **SPRINT_TRACKER als API**: Veel data wordt geparsed uit markdown-tabellen. Is het waard om een `sprint_tracker.json` cache te genereren bij elke sprint-afsluiting?

## Prioriteit

**Hoog** — Deze vijf pagina's + de Kennisbibliotheek/Research intake vormen samen het complete dashboard. Door ze samen te plannen wordt het dashboard in één keer naar productieniveau gebracht. De data is er, het dashboard moet het alleen ontsluiten.

## Relatie met andere intakes

| Intake | Relatie |
|--------|---------|
| Dashboard Kennisbibliotheek & Research Upgrade | Complementair — die intake doet Knowledge + Research pagina's, deze doet de rest |
| Kennisketen End-to-End | KnowledgeProvider data wordt rijker na kennisketen sprint |
| Event Bus Lifecycle Hooks (Sprint 42) | ✅ DONE — events beschikbaar voor activity feed |
