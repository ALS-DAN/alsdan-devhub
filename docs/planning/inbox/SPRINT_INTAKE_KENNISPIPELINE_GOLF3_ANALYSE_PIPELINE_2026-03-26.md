# Sprint Intake: Kennispipeline Golf 3 — Analyse Pipeline

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
prioriteit: P2 (sluitstuk van de kennispipeline)
sprint_type: FEAT
cynefin: complex (verbindt meerdere subsystemen, eerste end-to-end keten)
impact_zone: GEEL (nieuwe skill, integreert researcher + curator + documents + storage)
kennispipeline_golf: 3
parallel_met: geen
geblokkeerd_door: [KENNISPIPELINE_GOLF2A, KENNISPIPELINE_GOLF2B, KENNISPIPELINE_GOLF1B, TRACK_B_S2_GOOGLE_DRIVE]
volgende_stap: geen (sluitstuk kennispipeline)
---

## Doel

Bouw de analyse pipeline die de volledige keten verbindt: kennis ophalen uit KWP DEV → analyse draaien → ODF-document genereren → opslaan op Google Drive. Dit is het eindplaatje van de kennispipeline.

## Probleemstelling

Na Golf 1 en 2 bestaan alle bouwblokken apart: ResearchQueue, researcher, curator, KWP DEV (Weaviate), DocumentInterface (ODF), StorageInterface (Google Drive). Maar er is geen orkestratielaag die ze verbindt tot een bruikbare pipeline. De eindgebruiker (Niels) wil: "analyseer X" → document op Drive.

## Deliverables

### Analyse skill

- [ ] **AP-01** — Nieuwe skill: `/devhub-analyse`
  - Trigger: "analyseer", "analyse", "onderzoek en rapporteer", "kennisrapport"
  - Input: onderwerp/vraag + scope (breed/specifiek) + output-voorkeur
  - Orkestreert de volledige keten

- [ ] **AP-02** — Pipeline stappen:
  1. **Kennisretrieval** — zoek relevante artikelen in KWP DEV via semantische search
  2. **Lacune-detectie** — identificeer ontbrekende kennis, genereer ResearchRequests
  3. **Aanvullend onderzoek** — researcher vult lacunes aan (optioneel, configureerbaar)
  4. **Synthese** — combineer opgehaalde kennis tot coherente analyse
  5. **Document-generatie** — maak ODF-document via DocumentInterface
  6. **Opslag** — sla op via StorageInterface (lokaal + Google Drive)

- [ ] **AP-03** — Analyse-templates
  - SOTA-analyse: wat is de huidige stand van zaken rondom [onderwerp]?
  - Vergelijkende analyse: wat zijn de trade-offs tussen [A] en [B]?
  - Toepassingsanalyse: hoe past [technologie/patroon] in DevHub/[project]?
  - Vrije analyse: beantwoord [onderzoeksvraag]

### DevOrchestrator integratie

- [ ] **AP-04** — DevOrchestrator uitbreiden
  - Nieuw taaktype: `ANALYSE` (naast bestaande FEATURE, BUGFIX, etc.)
  - Orkestratie: researcher → curator → document service → storage
  - Status-tracking per stap

### Monitoring

- [ ] **AP-05** — Observaties loggen in Weaviate
  - ANALYSIS_COMPLETED, ANALYSIS_FAILED, KNOWLEDGE_GAP_DETECTED
  - Per analyse: bronnen gebruikt, lacunes gevonden, document gegenereerd

### Tests

- [ ] **AP-06** — Tests
  - Unit tests per pipeline stap
  - Integratietest: volledige keten van vraag tot document
  - Minimum: 30 tests

## Afhankelijkheden

- **Geblokkeerd door:**
  - Golf 2A + 2B: researcher en curator moeten operationeel zijn, KWP DEV moet content bevatten
  - Golf 1B: DocumentInterface moet bestaan voor ODF-output
  - Track B S2: Google Drive adapter moet bestaan voor Drive-opslag
- **BORIS impact:** nee — DevHub tooling
- **Opmerking:** als Track B S2 (Google Drive) later af is, kan de pipeline eerst alleen naar lokale opslag schrijven

## Fase-context

Fase 3 (Knowledge & Memory). Dit is het sluitstuk — de pipeline die alle Fase 3 bouwblokken verbindt tot een bruikbaar geheel. Na deze sprint werkt de volledige keten: vraag → onderzoek → validatie → document → opslag.

## Open vragen voor Claude Code

1. Moet de analyse pipeline synchroon draaien (wacht op researcher) of asynchroon (queue-based)?
2. Hoe lang mag een analyse duren voordat er een timeout is?
3. Moet de pipeline ook bestaande kennis kunnen exporteren zonder nieuwe research?
4. Hoe verhoudt `/devhub-analyse` zich tot de bestaande `/devhub-research-loop` skill?

## Technische richting (Claude Code mag afwijken)

- Analyse pipeline als methode op DevOrchestrator of als aparte AnalysisPipeline klasse
- Skill definitie in `.claude/skills/devhub-analyse/`
- Templates als YAML of Markdown in `config/analysis-templates/`
- Graceful degradation: als Google Drive niet beschikbaar → lokale opslag

## DEV_CONSTITUTION impact

- **Art. 2 (Verificatieplicht):** analyse-output bevat bronvermelding en verificatielabels
- **Art. 5 (Kennisintegriteit):** gradering doorgetrokken naar analyse-document
- **Art. 7 (Impact-zonering):** GEEL — nieuwe skill + orchestratie, raakt meerdere subsystemen
