# DevHub Roadmap — Digitaal Development Team
_Gegenereerd door: Cowork — alsdan-devhub_
_Status: INBOX_
_Datum: 2026-03-23_

---

## Kernidee

alsdan-devhub wordt een volledig digitaal development team: een project-agnostisch systeem dat development-kennis, governance en werkwijze borgt. Het team bestaat uit AI-agents die samenwerken via een Python-runtime, aangestuurd door een Claude Code plugin, met een Second Brain als geheugen.

**Visie:** Eén dev-systeem dat elk project kan bedienen via een gestandaardiseerd NodeInterface contract — BORIS is de eerste klant, niet de laatste.

---

## Huidige positie (geverifieerd)

| Onderdeel | Status |
|-----------|--------|
| Fase 0 — Fundament | ✅ Afgerond |
| Fase 1 — Kernagents + Infra | ✅ Afgerond (FASE1_BOOTSTRAP sprint) |
| Tests | 299 groen (218 Python + 81 plugin-laag) |
| Agents | 5 operationeel (dev-lead, coder, reviewer, researcher, planner) |
| Skills | 5 gevalideerd (sprint, health, mentor, sprint-prep, review) |
| Governance | DEV_CONSTITUTION v1.0 (8 artikelen), ADR-001 |
| Projecten | 1 geregistreerd: boris-buurts (git submodule) |

---

## Fase 2 — Skills + Governance

**Doel:** Het team leert consistent en betrouwbaar werken. Van "het kan" naar "het doet het goed, elke keer."

### Deliverables

| # | Deliverable | Cynefin | Sprint-type | Risico |
|---|-------------|---------|-------------|--------|
| 2.1 | Research-loop skill | Complex | SPIKE | YELLOW — nieuwe capability, onvoorspelbare scope |
| 2.2 | Golden Path templates | Complicated | FEAT | GREEN — patronen vastleggen, geen architectuurimpact |
| 2.3 | Governance-check skill | Complicated | FEAT | YELLOW — raakt DEV_CONSTITUTION handhaving |

### 2.1 Research-loop skill

**Probleem:** De researcher-agent kan informatie ophalen, maar heeft geen gestructureerde workflow voor het graden van kennis volgens EVIDENCE-methodiek (Art. 5 — Kennisintegriteit).

**Oplossing:** Een skill die de researcher-agent een loop geeft: detecteer kennislacune → formuleer zoekvraag → doorzoek bronnen (Semantic Scholar, ArXiv, Anthropic docs, CNCF) → gradeer resultaat (GOLD/SILVER/BRONZE/SPECULATIVE) → sla op in knowledge base.

**Acceptatiecriteria:**
- [ ] Skill voert minimaal 3 bronnen door per onderzoeksvraag
- [ ] Resultaten krijgen automatische EVIDENCE-gradering
- [ ] Output is een gestructureerd kennisdocument met bronvermelding
- [ ] Integreert met bestaande researcher-agent memory
- [ ] Tests geschreven en groen

**Cynefin-classificatie:** Complex — we weten niet precies hoe de research-loop zich in de praktijk gedraagt. SPIKE vereist: eerst een probe bouwen, evalueren, dan pas formaliseren.

**Afhankelijkheden:** Geen blokkerend. EVIDENCE-methodiek (bron = BORIS) moet als kopie beschikbaar zijn in DevHub.

**Tijdsinschatting:** 1 SPIKE sprint (verkenning) + 1 FEAT sprint (formalisatie)

**DEV_CONSTITUTION impact:** Art. 5 (Kennisintegriteit) — dit is de implementatie van kennisgradering.

---

### 2.2 Golden Path templates

**Probleem:** De coder-agent produceert code zonder gestandaardiseerde patronen. Elke sprint heruitvinden leidt tot inconsistentie en onnodige review-rondes.

**Oplossing:** Een set templates voor veelvoorkomende development-taken: nieuwe agent toevoegen, skill schrijven, adapter bouwen, test-suite opzetten, ADR schrijven. Golden Paths = "de gevalideerde manier om X te doen."

**Acceptatiecriteria:**
- [ ] Minimaal 5 Golden Path templates gedefinieerd
- [ ] Templates bevatten: structuur, naamconventies, verplichte secties, voorbeeldcode
- [ ] Coder-agent kan templates als startpunt gebruiken
- [ ] Templates gevalideerd tegen bestaande agents/skills (retrospectief)
- [ ] Kennisgradering: SILVER (gebaseerd op Fase 0+1 ervaring)

**Cynefin-classificatie:** Complicated — we weten wat er nodig is, het vereist expertise om het goed te structureren.

**Afhankelijkheden:** Geen blokkerend.

**Tijdsinschatting:** 1 FEAT sprint

**DEV_CONSTITUTION impact:** Art. 4 (Transparantie) — templates standaardiseren beslissingspatronen.

---

### 2.3 Governance-check skill

**Probleem:** De DEV_CONSTITUTION (8 artikelen) wordt nu handmatig getoetst. Er is geen automatische check of een sprint-plan, code review of deployment aan alle artikelen voldoet.

**Oplossing:** Een skill die gegeven een sprint-intake, code diff of deployment-plan automatisch toetst tegen alle 8 DEV_CONSTITUTION artikelen en een compliance-rapport genereert.

**Acceptatiecriteria:**
- [ ] Toetst tegen alle 8 artikelen van DEV_CONSTITUTION v1.0
- [ ] Input: sprint-intake, code diff of deployment-plan
- [ ] Output: compliance-rapport met per artikel PASS/WARN/FAIL
- [ ] Integreert met dev-lead agent (pre-sprint check)
- [ ] Integreert met reviewer agent (pre-merge check)
- [ ] Tests geschreven en groen

**Cynefin-classificatie:** Complicated — de regels zijn helder, de implementatie vereist zorgvuldig ontwerp.

**Afhankelijkheden:** DEV_CONSTITUTION v1.0 (✅ bestaat).

**Tijdsinschatting:** 1 FEAT sprint

**DEV_CONSTITUTION impact:** Raakt alle 8 artikelen — dit IS de handhavingslaag.

---

### Fase 2 — Volgorde en kritiek pad

```
[2.1 SPIKE: Research-loop verkenning]
        ↓
[2.2 FEAT: Golden Path templates]  ←  parallel mogelijk
[2.3 FEAT: Governance-check]       ←  parallel mogelijk
        ↓
[2.1b FEAT: Research-loop formalisatie]
```

**Kritiek pad:** 2.1 (research-loop SPIKE) — dit ontsluit kennisopbouw voor alle latere fases.

**Totale doorlooptijd Fase 2:** 3-4 sprints (afhankelijk van parallellisatie)

---

## Fase 3 — Knowledge + Memory

**Doel:** Het team krijgt een geheugen. Kennis uit sprints wordt opgeslagen, gegradeerd en herbruikbaar.

### Deliverables

| # | Deliverable | Cynefin | Sprint-type | Risico |
|---|-------------|---------|-------------|--------|
| 3.1 | KWP DEV setup | Complex | SPIKE | YELLOW — nieuw kennisdomein, structuur onbekend |
| 3.2 | EVIDENCE-kopie | Simpel | CHORE | GREEN — kopieer + pas aan, geen architectuurimpact |
| 3.3 | Retrospective learnings | Complicated | FEAT | GREEN — pattern vastleggen |

### 3.1 KWP DEV (9e kennisdomein)

**Probleem:** Development-kennis (AI-engineering, multi-agent patronen, governance) is verspreid over agent memories en ad-hoc notities. Er is geen gestructureerd kennisdomein.

**Oplossing:** KWP DEV als 9e kennisdomein — een vector store met development-specifieke kennis, doorzoekbaar door de researcher-agent, gegradeerd via EVIDENCE-methodiek.

**Acceptatiecriteria:**
- [ ] KWP DEV structuur gedefinieerd (categorieën, metadata-schema)
- [ ] Minimaal 10 kennisdocumenten geïngest uit Fase 0+1 ervaringen
- [ ] Researcher-agent kan KWP DEV doorzoeken
- [ ] Kennisdocumenten hebben EVIDENCE-gradering
- [ ] Integratie met research-loop skill (Fase 2.1)

**Cynefin:** Complex — we weten niet precies welke structuur optimaal is. SPIKE eerst.

**Afhankelijkheden:** Research-loop skill (2.1) moet operationeel zijn voor gradering.

**Tijdsinschatting:** 1 SPIKE + 1 FEAT sprint

---

### 3.2 EVIDENCE-kopie

**Probleem:** De EVIDENCE-methodiek (kennisgradering) leeft in BORIS. DevHub heeft een eigen kopie nodig om onafhankelijk te kunnen graden.

**Oplossing:** Kopieer de EVIDENCE-methodiek naar DevHub, pas aan voor development-context.

**Acceptatiecriteria:**
- [ ] EVIDENCE-methodiek beschikbaar in `knowledge/` of `docs/`
- [ ] Aangepast voor development-specifieke bronnen (geen zorg-bronnen)
- [ ] Geïntegreerd met research-loop skill

**Cynefin:** Simpel — kopieer, pas aan, valideer.

**Afhankelijkheden:** Geen (BORIS-bron is read-only beschikbaar via submodule).

**Tijdsinschatting:** 1 CHORE sprint (of onderdeel van een FEAT sprint)

---

### 3.3 Retrospective learnings

**Probleem:** Na elke sprint gaat kennis verloren. Er is geen gestructureerd proces om lessen te extraheren en op te slaan.

**Oplossing:** Een retrospective-workflow in de sprint-skill die na afsluiting automatisch leerpunten extraheert, gradeert en opslaat in KWP DEV.

**Acceptatiecriteria:**
- [ ] Sprint-afsluiting bevat retrospective-stap
- [ ] Leerpunten worden automatisch geëxtraheerd uit sprint-docs
- [ ] Leerpunten krijgen EVIDENCE-gradering (initieel BRONZE)
- [ ] Opslag in KWP DEV met metadata (sprint, datum, categorie)

**Cynefin:** Complicated — het patroon is bekend, implementatie vereist zorgvuldig ontwerp.

**Afhankelijkheden:** KWP DEV (3.1) moet bestaan. Sprint-skill (bestaand) moet uitgebreid worden.

**Tijdsinschatting:** 1 FEAT sprint

---

### Fase 3 — Volgorde

```
[3.2 CHORE: EVIDENCE-kopie]  ←  kan parallel met Fase 2
        ↓
[3.1 SPIKE: KWP DEV verkenning]
        ↓
[3.1b FEAT: KWP DEV implementatie]
        ↓
[3.3 FEAT: Retrospective learnings]
```

**Totale doorlooptijd Fase 3:** 3-4 sprints

---

## Fase 4 — BORIS-migratie (APART TRAJECT)

**Doel:** DevHub neemt de development-orchestratie van BORIS over. BORIS wordt een puur zorgproduct.

> **⚠️ GATE:** Fase 4 start NOOIT zonder expliciete Niels-goedkeuring (project-instructies + DEV_CONSTITUTION Art. 1).

### Deliverables

| # | Deliverable | Cynefin | Sprint-type | Risico |
|---|-------------|---------|-------------|--------|
| 4.1 | BorisAdapter uitbreidingen | Complicated | FEAT | YELLOW — raakt BORIS interface |
| 4.2 | devhub-sprint migratie (F3) | Complex | SPIKE→FEAT | RED — vervangt kernworkflow |
| 4.3 | devhub-health migratie (F4) | Complicated | FEAT | YELLOW — diagnostiek |
| 4.4 | devhub-mentor migratie (F5) | Complicated | FEAT | GREEN — coaching, geen runtime |
| 4.5 | devhub-sprint-prep migratie (F6) | Simpel | CHORE | GREEN — scheduled task |
| 4.6 | Sloop BORIS dev-skills | Simpel | CHORE | RED — destructief, Art. 3 |

### Migratieprotocol (per skill)

Zoals gedocumenteerd in MIGRATION_PLAN.md:
1. DevHub skill geschreven + getest
2. Eén sprint uitgevoerd met DevHub skill (validatie)
3. BORIS skill verwijderd: `git rm .claude/skills/{skill}/`
4. CLAUDE.md bijgewerkt
5. HERALD sync

**Volgorde:** sprint (4.2) → health (4.3) → mentor (4.4) → sprint-prep (4.5) → sloop (4.6)

**BorisAdapter uitbreidingen nodig (geverifieerd via MIGRATION_PLAN.md):**
- Sprint-docs lezen
- OVERDRACHT.md lezen
- CLAUDE.md lezen
- Inbox lezen
- HERALD triggeren
- Ruff uitvoeren
- pip-audit uitvoeren

**Totale doorlooptijd Fase 4:** 5-7 sprints (inclusief validatiesprints)

---

## Fase 5 — Uitbreiding

**Doel:** DevHub bewijst dat het project-agnostisch werkt en schaalt naar meerdere projecten.

### Deliverables

| # | Deliverable | Cynefin | Sprint-type | Risico |
|---|-------------|---------|-------------|--------|
| 5.1 | Agent Teams | Complex | SPIKE→FEAT | YELLOW — nieuw concept |
| 5.2 | Plugin marketplace-ready | Complicated | FEAT | YELLOW — distributie |
| 5.3 | 2e project proof-of-concept | Complex | SPIKE | YELLOW — validatie |

### 5.1 Agent Teams

**Probleem:** Agents werken nu solo. Complexe taken vereisen coördinatie tussen meerdere agents (bijv. coder + reviewer + docs in parallelle flow).

**Oplossing:** Een Agent Teams framework waarin de dev-lead meerdere agents kan orchestreren voor één taak.

**Tijdsinschatting:** 2-3 sprints

---

### 5.2 Plugin marketplace-ready

**Probleem:** DevHub is nu een lokale plugin. Om waardevol te zijn voor anderen moet het installeerbaar en configureerbaar zijn.

**Oplossing:** Plugin packaging, documentatie, configuratie-wizard, onboarding flow.

**Tijdsinschatting:** 1-2 sprints

---

### 5.3 Tweede project proof-of-concept

**Probleem:** DevHub claimt project-agnostisch te zijn, maar heeft alleen BORIS als klant.

**Oplossing:** Een tweede project registreren, een nieuwe adapter schrijven, en bewijzen dat DevHub's skills en agents werken zonder BORIS-aannames.

**Tijdsinschatting:** 1 SPIKE sprint

---

## Totaaloverzicht

```
FASE 0 ✅  Fundament                           [afgerond]
FASE 1 ✅  Kernagents + Infra                   [afgerond]
─────────────────────────────────────────────────────────
FASE 2 🔲  Skills + Governance                  [3-4 sprints]
  ├─ 2.1  Research-loop skill (SPIKE→FEAT)
  ├─ 2.2  Golden Path templates (FEAT)
  └─ 2.3  Governance-check skill (FEAT)

FASE 3 🔲  Knowledge + Memory                   [3-4 sprints]
  ├─ 3.1  KWP DEV (SPIKE→FEAT)
  ├─ 3.2  EVIDENCE-kopie (CHORE)
  └─ 3.3  Retrospective learnings (FEAT)

FASE 4 🔲  BORIS-migratie (GATE: Niels)         [5-7 sprints]
  ├─ 4.1  BorisAdapter uitbreidingen (FEAT)
  ├─ 4.2  Sprint-migratie (SPIKE→FEAT)
  ├─ 4.3  Health-migratie (FEAT)
  ├─ 4.4  Mentor-migratie (FEAT)
  ├─ 4.5  Sprint-prep migratie (CHORE)
  └─ 4.6  Sloop BORIS dev-skills (CHORE)

FASE 5 🔲  Uitbreiding                          [4-6 sprints]
  ├─ 5.1  Agent Teams (SPIKE→FEAT)
  ├─ 5.2  Plugin marketplace-ready (FEAT)
  └─ 5.3  2e project PoC (SPIKE)
```

**Totaal geschatte doorlooptijd:** 15-21 sprints (Fase 2 t/m 5)

---

## Risicomatrix

| Risico | Impact | Kans | Mitigatie |
|--------|--------|------|-----------|
| Research-loop scope-explosie | Hoog | Middel | SPIKE eerst, appetite begrenzen |
| KWP DEV structuur past niet | Middel | Middel | Iteratief opbouwen, niet big-bang |
| BORIS-migratie breekt workflows | Hoog | Laag | Validatiesprint per skill, sloop-protocol |
| Agent Teams te complex | Hoog | Middel | PoC met 2 agents, niet alle 5 |
| 2e project niet representatief | Middel | Laag | Kies bewust ander domein dan zorg |
| Tech debt uit snelle Fase 0+1 | Middel | Middel | Golden Paths + governance-check als vangnet |

---

## Tech Debt Bewustzijn (Fowler-classificatie)

| Type | Waar | Actie |
|------|------|-------|
| Bewust-prudent | Fase 0+1 snelheid boven perfectie | Documenteer in Golden Paths (2.2) |
| Onbewust-prudent | Patronen uit Fase 0 die beter kunnen | Ontdek via retrospective (3.3) |
| Bewust-roekeloos | — | Niet gedetecteerd |
| Onbewust-roekeloos | — | Governance-check (2.3) moet dit vangen |

---

## Beslissingen Niels (2026-03-23)

1. **Fase 2 start:** Direct beginnen met research-loop SPIKE — sprint intake in volgende sessie.
2. **Parallellisatie:** 2.2 (Golden Paths) en 2.3 (governance-check) mogen parallel lopen indien mogelijk.
3. **Fase 4 horizon:** Pas na bewezen Fase 0-3. Geen eerder startmoment.
4. **2e project (5.3):** Niet prioritair — DevHub zelf + BORIS vormen al twee projecten als validatie.
