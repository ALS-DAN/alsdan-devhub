# Sprint Intake: Operationele Validatie — "Draait het echt?"

---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
fase: 3
prioriteit: P1
sprint_type: SPIKE
cynefin: complex (onbekend of systeem end-to-end werkt)
impact_zone: YELLOW (raakt alle lagen, geen destructieve wijzigingen)
---

## Doel

Valideer dat de drie operationele lagen van DevHub (n8n bewaking, agent-orkestratie, Python runtime) daadwerkelijk end-to-end functioneren vóór we Track B en C starten. Elke gap wordt gedocumenteerd, kritieke paden worden gerepareerd.

## Probleemstelling

DevHub heeft 394 tests, 6 agents, 8 skills, 2 GitHub Actions workflows en een n8n foundation. Maar:

- **Tests bewijzen dat code correct is, niet dat workflows draaien.** Unit tests voor BorisAdapter testen contracts, niet de shell-commands tegen een echt BORIS-project.
- **Agents bestaan als definities, niet als geteste workflows.** Dev-lead → coder delegatie is beschreven maar nooit uitgevoerd. Agent Teams (Claude Code feature sinds feb 2026) zijn niet geactiveerd.
- **Skills beschrijven stappen, maar produceren geen bewezen output.** `/devhub-health` heeft een 6-stappen workflow maar is nooit end-to-end gerund.
- **n8n is geconfigureerd maar niet bewezen operationeel.** Sprint-retrospective N8N_CICD meldt: "Health check workflow niet end-to-end getest in draaiende n8n container."
- **n8n MCP-tools zijn beschikbaar maar niet verbonden.** Workflow management (create/update/test) vereist N8N_API_URL + N8N_API_KEY.

Dit is een risico voor Fase 3: Track B (Storage) en Track C (Vectorstore) bouwen op aannames over werkende infrastructuur.

## Deliverables

### Fase 1: n8n Operationeel (bewakingslus)

- [ ] **D1.1** — n8n Docker container draait stabiel op port 5679
  - Verificatie: `curl http://localhost:5679/healthz` retourneert 200
  - Alle 5 Docker-issues uit N8N_DOCKER_FIX geverifieerd opgelost
- [ ] **D1.2** — Health check workflow (`wf1_devhub_health_check.json`) geïmporteerd en actief
  - Verificatie: workflow is zichtbaar in n8n UI, schedule trigger actief
  - Handmatige trigger produceert JSON output met severity mapping
- [ ] **D1.3** — n8n MCP-verbinding operationeel
  - N8N_API_URL en N8N_API_KEY geconfigureerd in `.mcp.json` of environment
  - Verificatie: `n8n_health_check()` MCP-call retourneert instance info
  - Verificatie: `n8n_list_workflows()` toont wf1
- [ ] **D1.4** — GitHub Trigger workflow (optioneel, YELLOW)
  - n8n kan reageren op push-naar-main events
  - Aanvullende checks die GitHub Actions niet kan (Weaviate connectivity, n8n self-status)
  - _Notitie: dit vereist webhook-configuratie. Als te complex → documenteer als Fase 3 backlog item._

### Fase 2: Python Runtime Validatie

- [ ] **D2.1** — BorisAdapter end-to-end test tegen echt BORIS-project
  - `adapter.get_report()` retourneert valide NodeReport
  - `adapter.read_claude_md()` leest BORIS' actuele CLAUDE.md
  - `adapter.run_tests()` voert BORIS' test-suite uit (of documenteert waarom niet)
  - `adapter.run_lint()` draait ruff op BORIS codebase
  - Bevindingen: welke van de 38 methodes werken, welke niet
- [ ] **D2.2** — DevOrchestrator taak-decompositie test
  - `orch.create_task()` met concrete sprint-scope
  - `orch.decompose_for_docs()` genereert doc-taken
  - Verificatie: scratchpad bevat taak-state
- [ ] **D2.3** — QA Agent review-cyclus test
  - `qa.review_code()` op recente commit diff
  - `qa.review_docs()` op een bestaand golden-path doc
  - `qa.full_review()` produceert QAReport met verdict
  - Verificatie: PASS/NEEDS_WORK/BLOCK verdict is correct en traceerbaar

### Fase 3: Skill Validatie (end-to-end)

- [ ] **D3.1** — `/devhub-health` op boris-buurts node
  - Draai volledige 6-stappen workflow
  - Output: FullHealthReport met 6 dimensies + severity per dimensie
  - HEALTH_STATUS.md wordt geschreven naar project root
  - Alert routing: P1/P2 → GitHub Issue (of documenteer waarom niet)
- [ ] **D3.2** — `/devhub-governance-check` op staged changes
  - Draai 16-punten artikel-audit
  - Output: gestructureerd rapport met PASS/NEEDS_REVIEW/BLOCK
  - QA Agent integratie werkt (CR-03 secrets, CR-09 print)
- [ ] **D3.3** — `/devhub-redteam` OWASP ASI quick-scan
  - Draai ASI01-ASI10 checklist op huidige agent-definities
  - Output: SecurityAuditReport met findings + asi_coverage dict
  - Kill chain mapping op ≥1 finding
- [ ] **D3.4** — `/devhub-sprint` dry-run (sprint-start workflow A, stappen 0-3)
  - Context laden via adapter (rapport, claude_md, overdracht)
  - Inbox + backlog scannen
  - Sprint-plan genereren via DevOrchestrator
  - STOP bij stap 4 (wacht op goedkeuring) — bewijs dat het pad werkt

### Fase 4: Agent Teams Proof-of-Concept

- [ ] **D4.1** — Dev-lead → Coder delegatie test
  - Dev-lead ontvangt concrete microtaak (bijv. "voeg een test toe voor NodeRegistry edge case")
  - Dev-lead analyseert, classificeert (GREEN), delegeert aan coder
  - Coder implementeert in eigen context (worktree als beschikbaar)
  - Verificatie: taak voltooid, test groen, commit atomisch
- [ ] **D4.2** — Reviewer review van coder-output
  - Reviewer ontvangt diff van D4.1
  - QA Agent Python-checks draaien
  - Output: PASS/NEEDS_WORK/BLOCK verdict
  - Verificatie: volledige delegatie-cyclus dev-lead → coder → reviewer werkt
- [ ] **D4.3** — Agent Teams configuratie-advies (SPIKE output)
  - Documenteer hoe DevHub's 6 agents als Agent Team geconfigureerd worden
  - Welke agents zijn teammates vs. tools?
  - File-locking strategie voor concurrent werk
  - Task-claiming patronen voor zelfstandig oppakken

### Fase 5: Gap Rapport + Reparatieplan

- [ ] **D5.1** — Operationeel Gap Rapport
  - Per laag (n8n / Python / Skills / Agents): wat werkt, wat niet, wat deels
  - Severity per gap: BLOKKEREND (moet voor Track B/C) / BELANGRIJK / NICE-TO-HAVE
  - Concrete reparatie-acties per gap met geschatte effort
- [ ] **D5.2** — Bijgewerkte DEVHUB_BRIEF.md
  - Operationele status per component
  - Eerste echte health-check resultaten
  - Agent Teams readiness status
- [ ] **D5.3** — ROADMAP.md update
  - Kritiek pad bijwerken op basis van bevindingen
  - Track B/C start condities verfijnen

## Afhankelijkheden

- **Geblokkeerd door:** CHORE-sprint (planning opschoning) — moet eerst afgerond zijn
- **BORIS impact:** Ja — D2.1 leest uit BORIS project (read-only, Art. 6)
- **n8n impact:** Ja — D1.1-D1.4 vereist draaiende n8n Docker instance
- **Externe tools:** n8n MCP-server, GitHub MCP-server (beide beschikbaar)

## Grenzen (wat NIET in scope)

- Geen nieuwe features bouwen (dit is validatie, geen feature-sprint)
- Geen Storage Interface of Vectorstore werk (dat is Track B/C)
- Geen Agent Teams productie-configuratie (alleen PoC en advies)
- Geen n8n workflow-bouw voor nieuwe use cases (alleen bestaande valideren)
- Geen BORIS-wijzigingen (read-only, Art. 6)

## Appetite

**Medium (M)** — 1-2 sprints afhankelijk van het aantal gaps dat gerepareerd moet worden.

Fase 1-3 zijn validatie (snel als alles werkt, langzamer als reparaties nodig zijn).
Fase 4 is een PoC (afgebakend, 1 microtaak).
Fase 5 is documentatie (altijd snel).

## Open vragen voor Claude Code

1. Kan `BorisAdapter.run_tests()` daadwerkelijk BORIS' pytest draaien vanuit de DevHub context, of zijn er padproblemen?
2. Welke BorisAdapter methodes voeren shell-commands uit vs. welke lezen alleen bestanden?
3. Is de n8n Docker container überhaupt gebouwd na de fix? (`docker compose up -d` succesvol?)
4. Hoe configureer je Agent Teams met de huidige agent-definities? Is `agents/*.md` voldoende of zijn er `settings.json` wijzigingen nodig?
5. Welke van de 394 tests zijn integratie-tests vs. unit tests? Hoeveel testen daadwerkelijk shell-commands?

## DEV_CONSTITUTION impact

| Artikel | Impact |
|---------|--------|
| Art. 1 (Menselijke Regie) | Niels beslist welke gaps gerepareerd worden |
| Art. 2 (Verificatieplicht) | **Kern van deze sprint** — verifieer alle claims |
| Art. 3 (Codebase-integriteit) | Geen destructieve wijzigingen, alleen validatie + documentatie |
| Art. 6 (Project-soevereiniteit) | BORIS wordt read-only benaderd |
| Art. 7 (Impact-zonering) | YELLOW — raakt meerdere lagen, geen code-wijzigingen verwacht |

## Risico's

| Risico | Kans | Impact | Mitigatie |
|--------|------|--------|-----------|
| BorisAdapter methodes werken niet tegen echt project | Hoog | Hoog | Documenteer welke, plan reparaties |
| n8n Docker container start niet | Medium | Medium | Terugvallen op GitHub Actions-only model |
| Agent Teams PoC te complex | Laag | Laag | Beperk tot 1 micro-delegatie, documenteer learnings |
| Meer gaps dan verwacht | Medium | Medium | Prioriteer: n8n → Python → Skills. Agents als stretch. |

## Relatie met Fase 3 tracks

Na deze sprint weten we precies welke componenten betrouwbaar zijn voor Track B en C:

- **Storage Interface** (Track B) bouwt op: NodeRegistry, adapter-pattern, skill-framework → allemaal gevalideerd
- **Vectorstore** (Track C) bouwt op: adapter-pattern, Weaviate connectivity (via health check), skill-framework → allemaal gevalideerd
- **KWP DEV** bouwt op: vectorstore + knowledge grading → EVIDENCE-framework gevalideerd via governance-check

Zonder deze validatie bouwen we op aannames. Met deze validatie bouwen we op bewijs.

---

> **Cynefin:** Complex → SPIKE. We weten niet wat we niet weten totdat we het systeem daadwerkelijk draaien.
> **Shape Up:** Het probleem is helder (onbewezen aannames). De oplossing is afgebakend (draai elke laag één keer). De grens is scherp (geen nieuwe features).
> **INVEST:** Independent ✅ | Negotiable ✅ (fasen zijn optioneel) | Valuable ✅ | Estimable ⚠️ (afhankelijk van gaps) | Small ⚠️ (kan 2 sprints worden) | Testable ✅
