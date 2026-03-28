# SPRINT INTAKE: Research Compas — Runtime Integratie & Bootstrap

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
node: devhub
sprint_type: FEAT
fase: 3
---

## Doel

Maak agents kennisbewust door pre-task knowledge scans te implementeren en vul de Ring 1 kerndomeinen via auto-bootstrap — zodat DevHub direct inzetbaar is als instrument in het ontwikkelproces.

## Probleemstelling

### Waarom nu

Na Sprint 1 (Configuratie & Contracts) heeft DevHub de datastructuur voor 16 domeinen, RQ-tags en graph-ready velden. Maar zonder runtime-integratie zijn agents nog steeds "blind": ze checken hun kennis niet vóór een taak, en de kennisbank is nog leeg. DevHub is pas als development-instrument bruikbaar als agents zelf lacunes detecteren EN er een basislevel content in het systeem zit.

### Fase-context

Fase 3 (Knowledge & Memory) — laatste stap om de kennislaag operationeel te maken. Na deze sprint kan DevHub zichzelf voeden: agents detecteren lacunes → genereren ResearchRequests → researcher verwerkt → curator valideert → kennisbank groeit organisch.

## Deliverables

### Pre-task Knowledge Scan

- [ ] `KnowledgeScanner` class — leest agent knowledge profile, queryt vectorstore per domein, vergelijkt met min_grade vereisten
- [ ] Scan-resultaat dataclass: `KnowledgeScanResult` met per-domein status (sufficient/insufficient), ontbrekende RQ-dekking, gegenereerde ResearchRequests
- [ ] Integratie in dev-lead agent: scan als eerste stap bij taak-ontvangst
- [ ] Best-effort semantiek: scan blokkeert de taak NIET, annoteert output met lacunes
- [ ] Gegenereerde ResearchRequests automatisch in ResearchQueue

### Auto-Bootstrap Ring 1

- [ ] Bootstrap-mechanisme: leest seed questions uit `config/knowledge.yml`, genereert ResearchRequests per domein
- [ ] Seed questions voor 5 kerndomeinen (ai_engineering, claude_anthropic, python_architecture, development_methodology, governance_compliance) — elk minimaal 6 vragen (1 per RQ)
- [ ] Bootstrap levert BRONZE-niveau artikelen op (breed maar niet diep)
- [ ] Curator valideert basisvereisten (bronvermelding, scope, RQ-tag)
- [ ] Health audit na bootstrap: alle RQ's gedekt? Minimum artikelen per domein bereikt?
- [ ] Rapport aan gebruiker: "{domein} gebootstrapt: {n} artikelen, dekking RQ1-6: {percentages}"

### Knowledge Health uitbreiding

- [ ] `/devhub-health` skill — nieuwe dimensie "Knowledge Health" met domein-dekking, RQ-dekking, grading-distributie
- [ ] Freshness-check per domein op basis van `freshness_months` uit knowledge.yml

### Tests & verificatie

- [ ] Tests voor KnowledgeScanner: voldoende kennis, lacune-detectie, ResearchRequest-generatie
- [ ] Tests voor bootstrap: seed question parsing, artikel-creatie flow, health audit
- [ ] Bestaande tests groen (geen regressies)

## Afhankelijkheden

- **Geblokkeerd door:** Sprint 1 (Configuratie & Contracts) — vereist uitgebreide knowledge.yml, agent_knowledge.yml, en nieuwe contract-velden
- **BORIS-impact:** nee — DevHub-intern. Bootstrap draait alleen voor Ring 1 (kern) domeinen. Ring 3 (project-specifiek) wordt pas bij Fase 4 geactiveerd.

## Fase-context

**Fase 3** — Knowledge & Memory. Dit is de runtime-activering van wat Sprint 1 configureert. Na deze sprint is de kennislaag compleet: structuur (Sprint 1) + intelligentie + content (Sprint 2).

## Open vragen voor Claude Code

1. Bootstrap-uitvoering: synchrone batch (alle 5 domeinen tegelijk) of async queue-based (researcher verwerkt ze als reguliere requests)? Trade-off: batch is sneller maar zwaarder; queue is geleidelijker maar beter geïntegreerd.
2. KnowledgeScanner locatie: devhub-core (bij contracts) of als apart package? Het raakt zowel contracts als vectorstore.
3. Hoe diepe integratie in agents? Alleen dev-lead (orchestrator) of alle agents met `pre_task_check: true`? Suggestie: start met dev-lead, uitbreiden als het patroon werkt.
4. Health skill uitbreiding: apart commando `/devhub-knowledge-status` of uitbreiding bestaande `/devhub-health`? Visiedocument suggereert uitbreiding.
5. Seed questions: hardcoded in knowledge.yml of apart bestand `config/bootstrap_seeds.yml`? Afweging: overzichtelijkheid vs. scheiding van concerns.

## Prioriteit

**Hoog** — Dit maakt DevHub bruikbaar als development-instrument. Zonder pre-task scan en bootstrap-content zijn de contract-uitbreidingen van Sprint 1 configuratie zonder effect.

## Technische richting (suggestie — Claude Code mag afwijken)

- `KnowledgeScanner` als dunne orchestratie-laag die VectorstoreInterface + agent_knowledge.yml combineert
- Bootstrap als queue-based flow: seed questions → ResearchRequests → researcher → curator → vectorstore (hergebruikt bestaande pipeline)
- Health uitbreiding: voeg `knowledge_health()` methode toe aan bestaande health-check systeem
- Impact-zonering: pre-task scan = GREEN (additief), auto-bootstrap = GREEN (nieuwe content, geen wijziging bestaande), health uitbreiding = YELLOW (skill-wijziging)

## DEV_CONSTITUTION impact

- **Art. 1 (menselijke regie):** bootstrap draait automatisch maar levert alleen BRONZE. GOLD vereist Niels' goedkeuring. Hybride autonomie conform visiedocument.
- **Art. 5 (kennisintegriteit):** deze sprint implementeert demand-driven knowledge acquisition — het hart van Art. 5.
- **Art. 7 (impact-zonering):** pre-task scan en bootstrap = GREEN. Health skill-wijziging = YELLOW.
- **Art. 9 (planning-integriteit):** SPRINT_TRACKER.md bijwerken na afronding.

## SOTA-onderbouwing

| Concept | Bron | Gradering |
|---------|------|-----------|
| Pre-task knowledge assessment | KnowAgent (NAACL 2025) | SILVER |
| Demand-driven knowledge acquisition | Anthropic multi-agent research system (2025) | SILVER |
| Auto-bootstrap ontologie | Stardog LLM-driven bootstrapping (2025) | SILVER |
| Knowledge health monitoring | Enterprise RAG audit trails (NStarX 2026) | SILVER |
| Hybrid autonomie (human-in-the-loop) | LLM-MAS Survey (CoLing 2025) | SILVER |
| Temporele freshness tracking | Graphiti bi-temporal model (arXiv 2501.13956) | SILVER |

## Acceptatiecriteria

1. Dev-lead voert pre-task scan uit bij taak-ontvangst en rapporteert lacunes
2. Ring 1 kerndomeinen bevatten minimaal 6 BRONZE-artikelen elk (1 per RQ) na bootstrap
3. `/devhub-health` toont knowledge health dimensie met domein- en RQ-dekking
4. ResearchRequests gegenereerd door pre-task scan verschijnen in de queue
5. Alle bestaande tests + nieuwe tests groen
