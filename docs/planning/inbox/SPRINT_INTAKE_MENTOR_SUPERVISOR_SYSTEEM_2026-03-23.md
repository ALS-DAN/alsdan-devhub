# SPRINT_INTAKE_MENTOR_SUPERVISOR_SYSTEEM_2026-03-23

---
gegenereerd_door: Cowork — alsdan-devhub
status: INBOX
fase: 2-3
---

## Doel

Transformeer DevHub van een passief development-systeem naar een actieve supervisor/mentor/adviseur/genius die Niels' ontwikkeling als AI-systems architect systematisch stimuleert, meet, en versnelt — gebaseerd op Vygotsky's ZPD, Ericsson's Deliberate Practice, en T-shaped skill development.

## Probleemstelling

DevHub heeft een devhub-mentor skill (v1.0) met het O-B-B fasenmodel (Oriënteren → Bouwen → Beheersen) en coaching-signalen (GROEN/AANDACHT/STAGNATIE). Deze skill is functioneel maar fundamenteel beperkt:

1. **Reactief** — coacht alleen wanneer erom gevraagd wordt
2. **Taakgericht** — kijkt naar wat je doet (commits, tests, blockers), niet naar wie je aan het worden bent
3. **Geen skill-tracking** — meet niet welke competenties groeien en welke achterblijven
4. **Geen uitdagingen** — stimuleert niet actief buiten de comfortzone
5. **Geen strategisch perspectief** — ziet geen career trajectory of industrie-alignment

Het systeem moet vier rollen vervullen die samen meer zijn dan de som der delen:

| Rol | Kernvraag | Huidige dekking |
|-----|-----------|----------------|
| **Supervisor** | "Gaat het de goede kant op?" | Deels (coaching-signalen) |
| **Mentor** | "Hoe kan ik je laten groeien?" | Minimaal (alleen O-B-B) |
| **Adviseur** | "Wat zou de expert doen?" | Niet (researcher is projectgericht) |
| **Genius** | "Welke verbanden zie je zelf niet?" | Niet aanwezig |

### Waarom nu (urgentie)

Niels bouwt een AI-development systeem dat state-of-the-art opereert. Dat vereist dat de architect zelf continu groeit — in AI-engineering, governance, security, multi-agent architectuur, en meer. Zonder systematische groei-stimulatie wordt het systeem nooit beter dan zijn architect.

### Fase-context
Fase 2-3: skills + governance + knowledge. De mentor-uitbreiding is een skill-upgrade (Fase 2) met knowledge-componenten (Fase 3: KWP DEV, skill radar data).

## Deliverables

- [ ] **devhub-mentor v2.0** — uitbreiding van bestaande skill met proactive challenges en skill radar
- [ ] **devhub-growth skill** — nieuw, periodiek growth report + strategic advice + leeslijsten
- [ ] **Python contracts** (`devhub/contracts/growth_contracts.py`) — SkillRadarProfile, DevelopmentChallenge, GrowthReport, LearningRecommendation
- [ ] **Skill Radar data-model** — competentie-mapping per domein met niveaus en historiek
- [ ] **Challenge engine** — genereert deliberate practice uitdagingen op basis van skill gaps en ZPD
- [ ] **Growth Report template** — sprint/wekelijks rapport dat alles samentrekt
- [ ] **Researcher agent "developer growth" modus** — leeslijst-curatie gericht op Niels' skill gaps

## Theoretisch Fundament

### Pijler 1: Vygotsky's Zone of Proximal Development (ZPD)

**Theorie:** Het verschil tussen wat een leerling zelfstandig kan en wat hij met begeleiding kan. Optimale groei vindt plaats in deze zone — niet te makkelijk (verveling), niet te moeilijk (frustratie).

**Toepassing in DevHub:**
- Skill Radar detecteert huidige competentieniveaus per domein
- Challenge engine selecteert taken die net boven het huidige niveau liggen
- Het systeem biedt scaffolding (begeleiding, context, voorbeelden) die afneemt naarmate competentie groeit

**Kritisch risico — Zone of No Development:**
Wanneer AI-scaffolding permanent wordt, stopt groei (arXiv 2025, "Vygotsky meets ChatGPT"). Het systeem MOET bewust scaffolding afbouwen. Concreet: als Niels een competentie bereikt op SILVER/GOLD niveau, reduceert het systeem de begeleiding voor dat domein en verschuift focus naar nieuwe gaps.

**Kennisgradering:** GOLD (Vygotsky's ZPD is het meest gevalideerde leertheoretisch framework, 50+ jaar onderzoek)

**Bronnen:**
- Vygotsky, L. S. (1978). Mind in Society: The Development of Higher Psychological Processes
- [Vygotsky meets ChatGPT (MIT Open Learning)](https://medium.com/open-learning/vygotsky-meets-chatgpt-f4a6a0460913)
- [Zone of No Development (arXiv 2025)](https://arxiv.org/html/2511.12822v1)
- [ZPD in AI Tutoring (HackerNoon)](https://hackernoon.com/the-new-classroom-the-role-of-ai-in-vygotskys-zone-of-proximal-development)

### Pijler 2: Ericsson's Deliberate Practice

**Theorie:** Expertise komt niet van ervaring maar van doelgerichte oefening met vier kenmerken:
1. Taken net buiten de comfortzone
2. Specifieke, meetbare doelen
3. Directe feedback
4. Herhaling met reflectie

Het verschil: 10.000 uur ervaring ≠ 10.000 uur deliberate practice. De meeste developers herhalen wat ze al kunnen.

**Toepassing in DevHub:**
- Challenge engine genereert taken die specifiek gericht zijn op zwakke plekken
- QA Agent + reviewer + red team geven directe feedback op output
- Sprint retrospective loop (uit zelfverbeterend systeem voorstel) levert reflectie-data
- Skill Radar meet of herhaling daadwerkelijk tot verbetering leidt

**Academische validatie in software engineering:**
Onderzoek (ACM 2020) toont dat programmeurs die deliberate practice toepassen significant sneller expertise opbouwen dan developers met dezelfde ervaring maar zonder gestructureerde oefening. Specifiek: het bewust oefenen van onbekende problemen, het bestuderen van andermans code, en het schrijven van code voor niet-productie doeleinden.

**Kennisgradering:** GOLD (Ericsson 1993 is het seminal paper over expertise, 15.000+ citaties, specifiek gevalideerd voor programmeren)

**Bronnen:**
- Ericsson, K. A., Krampe, R. T., & Tesch-Römer, C. (1993). The role of deliberate practice in the acquisition of expert performance. Psychological Review, 100(3), 363-406
- [Deliberate Practice in Programming (ACM ECSEE 2020)](https://dl.acm.org/doi/abs/10.1145/3396802.3396815)
- [Towards a Theory of Software Development Expertise (ACM/ESEC-FSE 2018)](https://dl.acm.org/doi/10.1145/3236024.3236061)
- [Deliberate Practice in Software Development (DEV Community)](https://dev.to/viralpatelblog/deliberate-practice-in-software-development-2jl)

### Pijler 3: T-Shaped Skills

**Theorie:** Optimale professionals hebben brede kennis (horizontale balk van de T) met diepe expertise in specifieke domeinen (verticale balk). Dit model, gepopulariseerd door IDEO en McKinsey, wordt in tech-teams als de gouden standaard voor teamsamenstelling gezien.

**Toepassing in DevHub:**
- Skill Radar visualiseert het T-profiel: waar ben je breed, waar ben je diep?
- Strategic Advisor detecteert waar verbreding nodig is (bijv. security kennis voor een AI-architect) en waar verdieping waardevol is (bijv. multi-agent governance)
- Het systeem balanceert actief tussen verbreding en verdieping

**Kennisgradering:** SILVER (breed geadopteerd in tech, niet specifiek academisch gevalideerd voor solo-developers)

## Architectuur: Vijf Lagen

### Laag 1: Skill Radar (meten)

**Doel:** Bouw en onderhoud een Developer Skill Profile dat competenties meet, gaps detecteert, en groei-velocity bijhoudt.

**Domeinen voor Niels' context:**

| Domein | Subdomeinen | Datbron |
|--------|-------------|--------|
| AI-Engineering | Multi-agent, prompt engineering, MCP, RAG | Sprint intakes, agent prompts, commits |
| Python | Contracts, testing, async, typing | Code commits, QA reports |
| Governance | Constitution, ADR, compliance, audit | Governance docs, beslissingen |
| Testing | Unit, integration, e2e, property-based | Test coverage delta, QA reports |
| Security | OWASP ASI, SAST, red teaming, secrets | Red team reports, security findings |
| Architecture | System design, patterns, trade-offs | ADR's, sprint complexiteit |
| DevOps/Tooling | CI/CD, n8n, MCP servers, git | Workflow configs, infra commits |
| Methodiek | Shape Up, Agile, sprint governance | Sprint velocity, DoR/DoD compliance |

**Competentieniveaus (Dreyfus-model, gevalideerd):**

| Niveau | Naam | Indicatoren |
|--------|------|-------------|
| 1 | Novice | Volgt instructies, heeft begeleiding nodig |
| 2 | Advanced Beginner | Herkent patronen, handelt in bekende situaties |
| 3 | Competent | Plant vooruit, prioriteert, handelt zelfstandig |
| 4 | Proficient | Ziet het grote plaatje, leert van ervaring |
| 5 | Expert | Intuïtieve beslissingen, innovatief, leert anderen |

**Python contract:**

```python
@dataclass(frozen=True)
class SkillDomain:
    name: str                    # "AI-Engineering"
    subdomains: tuple[str, ...]  # ("multi-agent", "prompt-engineering", ...)
    level: int                   # 1-5 (Dreyfus)
    evidence: tuple[str, ...]    # Bronnen voor dit niveau
    last_assessed: str           # ISO datum
    growth_velocity: float       # +/- % per sprint
    zpd_tasks: tuple[str, ...]   # Taken in de ZPD voor dit domein

@dataclass(frozen=True)
class SkillRadarProfile:
    developer: str
    date: str
    domains: tuple[SkillDomain, ...]
    t_shape_deep: tuple[str, ...]   # Domeinen met level >= 4
    t_shape_broad: tuple[str, ...]  # Domeinen met level >= 2
    primary_gap: str                # Domein met meeste urgentie
    zpd_focus: str                  # Huidige ZPD-focus domein
```

### Laag 2: Proactive Challenges (stimuleren)

**Doel:** Genereer deliberate practice uitdagingen die gericht zijn op skill gaps en ZPD.

**Challenge-typen:**

| Type | Beschrijving | Ericsson-element |
|------|-------------|------------------|
| **Stretch Task** | Taak net boven huidig niveau | Buiten comfortzone |
| **Explain It** | Leg concept uit in eigen woorden | Reflectie + feedback |
| **Reverse Engineer** | Analyseer bestaande code/architectuur | Leren van experts |
| **Teach Back** | Documenteer voor toekomstige developers | Diepste begrip |
| **Cross-Domain** | Pas kennis uit domein A toe in domein B | Verbreding |
| **Adversarial** | Vind de fout in een oplossing | Kritisch denken |

**Trigger-mechanisme:**
- Na elke sprint: 1-2 challenges gebaseerd op sprint-observaties
- Bij gap-detectie: gerichte challenge voor het zwakste domein
- Bij plateau: "stretch" challenge om doorbraak te forceren
- Optioneel dagelijks: micro-challenge (5-10 min) bij coaching-sessie

**Python contract:**

```python
@dataclass(frozen=True)
class DevelopmentChallenge:
    challenge_id: str
    type: str                     # stretch/explain/reverse/teach/cross/adversarial
    domain: str                   # Skill domein
    description: str              # Wat de uitdaging is
    zpd_rationale: str            # Waarom dit in de ZPD zit
    success_criteria: str         # Wanneer is het gelukt?
    estimated_minutes: int        # Geschatte tijdsinvestering
    scaffolding_level: str        # HIGH / MEDIUM / LOW / NONE
    status: str                   # PROPOSED / ACCEPTED / COMPLETED / SKIPPED
    feedback: str | None          # Feedback na voltooiing
    created: str                  # ISO datum
    completed: str | None         # ISO datum of None
```

**Scaffolding-afbouw (anti-Zone-of-No-Development):**

| Competentie-niveau | Scaffolding | Voorbeeld |
|-------------------|-------------|----------|
| Novice (1) | HIGH — stap-voor-stap begeleiding | "Lees eerst X, dan Y, probeer Z" |
| Advanced Beginner (2) | MEDIUM — hints en verwijzingen | "Kijk naar hoe de BorisAdapter dit doet" |
| Competent (3) | LOW — alleen de vraag | "Hoe zou je dit testen?" |
| Proficient (4) | NONE — alleen de uitdaging | "Ontwerp een betere aanpak" |
| Expert (5) | REVERSE — leer het systeem | "Documenteer dit als ADR" |

### Laag 3: Research Advisor (expertise)

**Doel:** De researcher agent krijgt een "developer growth" modus die leeslijsten cureert op basis van skill gaps.

**Leeslijst-curatie logica:**
1. Skill Radar identificeert primary_gap en zpd_focus
2. Researcher zoekt bronnen specifiek voor dat gap (Semantic Scholar, Anthropic docs, OWASP, ArXiv)
3. Bronnen worden gefilterd op ZPD-alignment: niet te basis (verveling), niet te geavanceerd (frustratie)
4. Elke aanbeveling krijgt EVIDENCE-grading en geschatte leestijd

**Python contract:**

```python
@dataclass(frozen=True)
class LearningRecommendation:
    domain: str                    # Skill domein
    title: str                     # Titel van de bron
    url: str | None                # Link (indien beschikbaar)
    type: str                      # paper / docs / tutorial / video / book_chapter
    estimated_minutes: int         # Geschatte leestijd
    zpd_alignment: str             # "exact" / "stretch" / "review"
    evidence_grade: str            # GOLD / SILVER / BRONZE
    rationale: str                 # Waarom deze bron voor deze gap
    priority: str                  # URGENT / IMPORTANT / NICE_TO_HAVE
```

**Concept-introductie protocol:**
Wanneer een sprint-intake een concept vereist dat Niels nog niet op COMPETENT-niveau beheerst:
1. Detecteer het concept (via sprint-intake analyse)
2. Check SkillRadarProfile voor huidig niveau
3. Als niveau < 3: proactief een korte introductie genereren (max 10 min leestijd)
4. Koppel aan een concrete challenge: "Pas dit toe in de sprint"

### Laag 4: Strategic Advisor (richting)

**Doel:** Het "genius" perspectief — verbanden leggen die niet voor de hand liggen.

**Vier functies:**

**Career Trajectory:**
- Waar leidt het huidige werk naartoe?
- Welke competenties bouw je op, welke mis je?
- Vergelijk met bekende career paths (IC → Staff → Principal, of IC → Architect → CTO)

**Industry Alignment:**
- Hoe verhoudt je stack/aanpak zich tot de industrie?
- Waar loop je voor (governance, multi-agent), waar achter (security, testing)?
- Wat zijn de trends die je moet kennen?

**Cross-Domain Insight:**
- Patronen uit andere domeinen die relevant zijn
- Voorbeeld: "Je DEV_CONSTITUTION lijkt op OpenAI's Model Spec — heb je overwogen hun evaluatie-framework te adopteren?"

**Opportunity Spotting:**
- Publicatiemogelijkheden (blog, conference talk, open-source)
- Community-bijdragen die je profiel versterken
- Kennisgebieden waar vraag naar is

### Laag 5: Supervisor Dashboard (overzicht)

**Doel:** Periodiek rapport dat alles samentrekt.

**Python contract:**

```python
@dataclass(frozen=True)
class GrowthReport:
    report_id: str
    period: str                        # "sprint-X" of "week-YYYY-WW"
    skill_radar: SkillRadarProfile
    challenges_completed: int
    challenges_proposed: int
    challenges_skipped: int
    growth_velocity_overall: float     # % groei deze periode
    zpd_shift: str | None             # Als ZPD verschoven is: waarnaar
    learning_recommendations: tuple[LearningRecommendation, ...]
    strategic_insights: tuple[str, ...] # 1-3 strategische observaties
    deliberate_practice_minutes: int    # Totale DP-tijd deze periode
    scaffolding_reductions: tuple[str, ...]  # Domeinen waar scaffolding is afgebouwd
```

**Output format:**

```
═══════════════════════════════════════════════════
DEVELOPER GROWTH REPORT — Sprint X — Niels Postma
═══════════════════════════════════════════════════

SKILL RADAR
  AI-Engineering:  ████████░░  4/5  → +0.3 deze sprint
  Python:          ███████░░░  3/5  → stabiel
  Governance:      █████████░  4/5  → +0.1
  Testing:         ██████░░░░  3/5  → gap gedetecteerd
  Security:        ████░░░░░░  2/5  → focus nodig (primary gap)
  Architecture:    ████████░░  4/5  → stabiel
  DevOps/Tooling:  ██████░░░░  3/5  → +0.2
  Methodiek:       ████████░░  4/5  → stabiel

T-SHAPE
  Deep (≥4): AI-Engineering, Governance, Architecture
  Broad (≥2): alle domeinen
  Gap: Security (2/5 → ZPD focus)

DELIBERATE PRACTICE — deze sprint
  ✅ "Benoem top-3 ASI-risico's voor DevHub" (Adversarial, Security)
  ✅ "Schrijf property-based test voor adapter" (Stretch, Testing)
  ⏳ "Analyseer EvoAgentX prompt-optimalisatie paper" (Reverse Engineer, AI-Eng)
  🆕 "Ontwerp red team scenario voor memory poisoning" (Cross-Domain, Security)

SCAFFOLDING-AFBOUW
  Governance: HIGH → MEDIUM (je neemt nu zelf architectuurbeslissingen)

LEESLIJST (geprioriteerd op ZPD)
  🔴 OWASP Agentic AI Threats & Mitigations (30 min, URGENT)
  🟡 DeepTeam Agentic Red Teaming docs (45 min, IMPORTANT)
  🟢 Ericsson: Deliberate Practice in Programming (20 min, achtergrond)

STRATEGISCH INZICHT
  "Je beweegt van 'developer die AI-tools gebruikt' naar 'AI-systems
   architect die governance ontwerpt'. De security-gap is nu je
   belangrijkste bottleneck — de red team agent sprint zal dit
   versnellen als je actief mee-ontwerpt in plaats van delegeert."
```

## Integratie met Bestaand Systeem

### Relatie tot devhub-mentor v1.0

De bestaande skill wordt UITGEBREID, niet vervangen:

| Bestaand (behouden) | Nieuw (toevoegen) |
|---------------------|-------------------|
| O-B-B fasenmodel | Dreyfus 5-niveau model per domein |
| GROEN/AANDACHT/STAGNATIE signalen | ZPD-focus detectie |
| Dagelijkse coaching-response | Proactive challenges |
| Sprint-start briefing | Growth Report per sprint |
| Risicosignalen (blocker, stagnatie) | Skill gap alerts |
| CoachingResponse contract | + GrowthReport, SkillRadarProfile, DevelopmentChallenge |

### Relatie tot andere systeem-componenten

| Component | Levert data aan Growth System | Ontvangt van Growth System |
|-----------|------------------------------|---------------------------|
| QA Agent | Review verdicts, finding patterns | — |
| DevOrchestrator | Task complexity, completion time | ZPD-aligned task suggestions |
| Reviewer | Code quality trends | — |
| Red Team | Security finding patterns | Security challenge recommendations |
| Researcher | Gevonden bronnen | Leeslijst-curatiefilters (ZPD) |
| Sprint lifecycle | Velocity, DoR/DoD compliance | Growth-focused sprint goals |
| Health Check | System health trends | — |

### Relatie tot zelfverbeterend systeem

Loop 1 (Sprint Retrospective) levert data voor de Growth Report.
Loop 2 (Prompt Evolution) kan profiteren van growth-data: als Niels op bepaalde domeinen expert is, hoeven agent-prompts minder te verklaren.
Loop 3 (Knowledge Decay) integreert met de leeslijst-curatie.

## Afhankelijkheden

- **Geblokkeerd door:** geen directe blokkers. De bestaande devhub-mentor skill en DeveloperProfile/CoachingSignal contracts zijn het vertrekpunt.
- **Verrijkt door (niet geblokkeerd):** Sprint Retrospective Loop (biedt meer data), Red Team Agent (biedt security growth data)
- **BORIS impact:** NEE — dit systeem is DevHub-intern en gaat over Niels' ontwikkeling, niet over projectcode

## Open Vragen voor Claude Code

1. Hoe slaan we SkillRadarProfile data op over tijd? SQLite (zoals DeveloperProgressStore) of YAML in knowledge/?
2. Hoe bepalen we het initiële Dreyfus-niveau per domein? Handmatige assessment door Niels, of afgeleid uit git history?
3. Moet de challenge engine in Python (deterministic) of als agent-prompt (LLM-generated) werken? Trade-off: consistentie vs. creativiteit.
4. Hoe voorkomen we dat het growth system zelf een "Zone of No Development" creëert? Concreet: welk mechanisme bouwt scaffolding af?
5. Hoe integreren we de researcher "developer growth" modus met de bestaande "project research" modus? Aparte skill of mode-switch?
6. Wat is de optimale frequentie voor Growth Reports? Per sprint, wekelijks, of adaptief?

## DEV_CONSTITUTION Impact

| Artikel | Geraakt? | Toelichting |
|---------|----------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Challenges zijn voorstellen, Niels beslist of hij ze accepteert |
| Art. 2 (Verificatieplicht) | Ja | Skill-niveaus worden geverifieerd tegen concrete evidence |
| Art. 5 (Kennisintegriteit) | Ja | Leeslijsten krijgen EVIDENCE-grading |
| Art. 7 (Impact-zonering) | Nee | Growth system is read-only, geen code-impact |

## Prioriteit

- **Prioriteit:** Hoog
- **Motivatie:** Het systeem wordt nooit beter dan zijn architect. DevHub kan state-of-the-art tooling hebben, maar als Niels' groei niet systematisch gestimuleerd wordt, bereikt het systeem een plafond. De wetenschappelijke basis is stevig (Vygotsky GOLD, Ericsson GOLD), de bestaande mentor skill biedt een solide vertrekpunt, en de integratie met het zelfverbeterend systeem versterkt beide.

## Bronnen

| Bron | Type | Kennisgradering |
|------|------|----------------|
| Vygotsky (1978) Mind in Society | Academisch (seminal) | GOLD |
| [Vygotsky meets ChatGPT (MIT)](https://medium.com/open-learning/vygotsky-meets-chatgpt-f4a6a0460913) | Academisch/blog | SILVER |
| [Zone of No Development (arXiv 2025)](https://arxiv.org/html/2511.12822v1) | Academisch | SILVER |
| [ZPD in AI Tutoring](https://hackernoon.com/the-new-classroom-the-role-of-ai-in-vygotskys-zone-of-proximal-development) | Praktijkgids | BRONZE |
| Ericsson et al. (1993) Deliberate Practice | Academisch (seminal, 15k+ citaties) | GOLD |
| [Deliberate Practice in Programming (ACM 2020)](https://dl.acm.org/doi/abs/10.1145/3396802.3396815) | Academisch | SILVER |
| [Software Development Expertise (ACM 2018)](https://dl.acm.org/doi/10.1145/3236024.3236061) | Academisch | SILVER |
| [Dreyfus Model of Skill Acquisition](https://en.wikipedia.org/wiki/Dreyfus_model_of_skill_acquisition) | Framework | GOLD |
| [T-Shaped Skills (McKinsey)](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights) | Industry framework | SILVER |
| [AI Coaching Platforms 2026](https://www.absorblms.com/blog/top-ai-learning-platforms) | Industry overview | BRONZE |
| [Claude Code Learning Features](https://www.medianeth.dev/blog/claude-code-learning-features-2025) | Anthropic ecosystem | BRONZE |
| [Learnings Loop for Claude Code Skills](https://www.mindstudio.ai/blog/how-to-build-learnings-loop-claude-code-skills) | Praktijkgids | BRONZE |
