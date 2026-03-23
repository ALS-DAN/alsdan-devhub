# SPRINT_INTAKE_RED_TEAM_AGENT_2026-03-23

---
gegenereerd_door: Cowork — alsdan-devhub
status: INBOX
fase: 2
---

## Doel

Bouw een volwaardige red team agent die DevHub's multi-agent systeem continu test op de OWASP Top 10 for Agentic Applications (ASI 2026) en de Votal AI 7-staps Agentic Kill Chain — als zesde agent naast dev-lead, coder, reviewer, researcher en planner.

## Probleemstelling

DevHub heeft een adversarial **reviewer** (code quality) maar geen **red team** (security). Dit is een fundamenteel verschil:

| Aspect | Reviewer (bestaand) | Red Team (ontbreekt) |
|--------|-------------------|---------------------|
| Vraag | "Voldoet de code aan standaarden?" | "Hoe kan dit systeem misbruikt worden?" |
| Perspectief | Verdedigend — zoekt fouten | Aanvallend — denkt als een aanvaller |
| Scope | Individuele bestanden/PRs | Het hele systeem: agents, prompts, memory, tools |
| Methode | Checklist (CR-01..12, DR-01..06) | Kill chain simulatie, prompt injection, poisoning |
| Framework | Intern (QA Agent) | OWASP ASI 2026 + DeepTeam + Votal AI |

### Waarom nu (urgentie)

De industrie-data is alarmerend:
- **Prompt injection** gevonden in 70% van security audits (Mindgard 2026)
- **Role-play attacks** slagen in 89.6% van adversarial evaluaties
- **Multi-turn jailbreaks** bereiken 97% succesrate binnen 5 conversatie-turns
- **Multi-agent breakdowns** succesvol in 80%+ van tests (ACL 2025, 23/32 tests)

DevHub is een multi-agent systeem met persistent memory, tool access (Bash, Edit, Write), en inter-agent delegatie — exact het profiel waar OWASP ASI 2026 voor waarschuwt.

### Fase-context
Fase 2 = skills + governance. Een red team agent is governance in de meest directe zin: het bewaakt de integriteit van het hele agent-systeem. Het bouwt voort op de Fase 1 agents (reviewer, researcher, planner) die nu operationeel zijn.

## Deliverables

- [ ] **Red team agent** (`agents/red-team.md`) — Opus-model, dedicated adversarial tester
- [ ] **OWASP ASI checklist** als Python contract (`devhub/contracts/security_contracts.py`)
- [ ] **Red team skill** (`.claude/skills/devhub-redteam/`) — activeerbaar voor on-demand security audit
- [ ] **DeepTeam integratie** — Python wrapper voor geautomatiseerde vulnerability scanning
- [ ] **Kill chain test suite** — tests die de 7 stadia van de Votal AI kill chain simuleren
- [ ] **Security audit rapport template** — gestructureerd format voor red team bevindingen

## OWASP ASI Top 10 — Volledige DevHub Risicoanalyse

### ASI01 — Agent Goal Hijacking
**Risico:** Aanvaller manipuleert agent-doelen via gemanipuleerde instructies of tool-output.
**DevHub-specifiek:**
- Een kwaadaardig CLAUDE.md in een geregistreerd project (via submodule) kan dev-lead agent manipuleren
- nodes.yml wijziging kan een malicious adapter injecteren
- Gemanipuleerde scratchpad-data kan DevOrchestrator taakdecompositie beïnvloeden
**Huidige mitigatie:** Art. 6 (project-soevereiniteit) dwingt CLAUDE.md-lezing af, maar valideert niet op injectie
**Red team test:** Plaats instructie-injectie in mock CLAUDE.md, verifieer of dev-lead deze volgt

### ASI02 — Tool Misuse & Exploitation
**Risico:** Agents misbruiken legitieme tools binnen hun permissies.
**DevHub-specifiek:**
- Coder agent heeft `Bash`, `Edit`, `Write` → kan binnen permissies destructieve acties uitvoeren
- Dev-lead heeft `Agent` tool → kan ongevalideerde taken delegeren
- BorisAdapter.run_lint() / run_tests() voert shell commands uit
**Huidige mitigatie:** disallowedTools op reviewer (Edit, Write, Agent), Art. 3 (integriteit), deny-lijst in settings.json
**Red team test:** Verifieer dat deny-lijst compleet is, test edge cases in Bash-permissies

### ASI03 — Identity & Privilege Abuse
**Risico:** Aanvallers exploiteren overgeërfde credentials of gedelegeerde permissies.
**DevHub-specifiek:**
- Coder erft Niels' git credentials bij commits
- .mcp.json bevat GitHub token configuratie
- n8n-MCP kan workflow-permissies exposeren
**Huidige mitigatie:** Art. 8 (dataminimalisatie), detect-secrets pre-commit hook
**Red team test:** Audit alle plekken waar credentials beschikbaar zijn voor agents, verifieer minimale exposure

### ASI04 — Supply Chain Vulnerabilities
**Risico:** Kwaadaardige tools, modellen of agent-persona's compromitteren executie.
**DevHub-specifiek:**
- Plugin dependencies (pip packages) kunnen kwetsbaar zijn
- Submodule (buurts-ecosysteem) is een externe dependency
- MCP-servers zijn externe processen met eigen permissies
**Huidige mitigatie:** pip-audit in health check, submodule pinning
**Red team test:** Voer supply chain audit uit: alle pip deps, MCP-servers, submodule integriteit

### ASI05 — Unexpected Code Execution (RCE)
**Risico:** Agents genereren of voeren aanvaller-gecontroleerde code uit.
**DevHub-specifiek:**
- Coder agent schrijft en runt Python/Bash via tool access
- DevOrchestrator evalueert geen code, maar genereert task-beschrijvingen die coder interpreteert
- PYTHONPATH-injectie via nodes.yml is theoretisch mogelijk
**Huidige mitigatie:** Coder volgt CLAUDE.md constraints, tests moeten groen blijven
**Red team test:** Verifieer dat task-beschrijvingen niet als code geëxecuteerd worden, test PYTHONPATH sanitization

### ASI06 — Memory & Context Poisoning
**Risico:** Persistente corruptie van agent memory, RAG stores of contextuele kennis.
**DevHub-specifiek:**
- CLAUDE.md bestanden beïnvloeden alle agent-gedrag (hoogste impact)
- Auto-memory (.auto-memory/) persisteert over sessies
- Scratchpad (.claude/scratchpad/) bevat taak-resultaten die toekomstige beslissingen sturen
- QA Reports in scratchpad kunnen gemanipuleerd worden om BLOCK/PASS verdicts te faken
**Huidige mitigatie:** Geen specifieke integriteitscontrole op memory/scratchpad
**Red team test:** Injecteer poisoned data in scratchpad, verifieer of agents dit detecteren; test CLAUDE.md tampering detection

### ASI07 — Insecure Inter-Agent Communication
**Risico:** Gespoofde, gemanipuleerde of onderschepte agent-communicatie.
**DevHub-specifiek:**
- Dev-lead → coder delegatie is via natural language (inherent manipuleerbaar)
- Geen authenticatie op inter-agent berichten
- Met Agent Teams (experimenteel) groeit dit risico significant
**Huidige mitigatie:** Dev-lead bepaalt impact-zone vóór delegatie (Art. 7)
**Red team test:** Simuleer een gemanipuleerd delegatie-bericht, verifieer of coder het accepteert

### ASI08 — Cascading Failures
**Risico:** Foutieve signalen cascaderen door geautomatiseerde pipelines met escalerend impact.
**DevHub-specifiek:**
- Health check false positive → onnodig GitHub Issue → dev-lead prioriteert verkeerd
- QA Agent false BLOCK → sprint stopt onnodig
- n8n workflow error → self-healing loop maakt het erger
**Huidige mitigatie:** Health skill P1-P4 severity, deduplicatie bij Issue-creatie
**Red team test:** Injecteer false positives in health check output, meet cascadeereffect

### ASI09 — Human-Agent Trust Exploitation
**Risico:** Overtuigende AI-output misleidt menselijke operators tot het goedkeuren van schadelijke acties.
**DevHub-specifiek:**
- Dev-lead presenteert task-resultaten aan Niels voor goedkeuring
- Reviewer produceert PASS verdicts die Niels vertrouwt
- Cowork presenteert sprint-intakes die de richting bepalen
**Huidige mitigatie:** Art. 1 (menselijke regie), Art. 2 (verificatieplicht)
**Red team test:** Genereer een overtuigend maar fout PASS-verdict, verifieer of Niels het zou detecteren

### ASI10 — Rogue Agents
**Risico:** Gecompromitteerde of misaligned agents wijken af van bedoeld gedrag.
**DevHub-specifiek:**
- Coder met gemanipuleerde prompt schrijft subtiel kwetsbare code
- Reviewer met gemanipuleerde prompt markeert alles als PASS
- Een toekomstige red team agent die zelf gecompromitteerd raakt (quis custodiet ipsos custodes?)
**Huidige mitigatie:** Agent prompts in version control, commit-traceerbaarheid (Art. 4)
**Red team test:** Modificeer agent prompt subtiel, meet of andere agents het detecteren

## Votal AI — 7-Staps Agentic Kill Chain voor DevHub

De kill chain beschrijft hoe een aanval escaleert door een agentic systeem. Elke stap moet getest worden:

```
Stap 1: Prompt Injection
  → Via CLAUDE.md, task-beschrijving, of external input
  → DevHub-specifiek: nodes.yml, submodule CLAUDE.md, inbox/ bestanden

Stap 2: Privilege Escalation
  → Agent verkrijgt meer permissies dan bedoeld
  → DevHub-specifiek: coder omzeilt disallowedTools, reviewer krijgt write access

Stap 3: Reconnaissance
  → Agent verkent het systeem voor aanvalsvectoren
  → DevHub-specifiek: BorisAdapter exposeert projectstructuur, nodes.yml toont configuratie

Stap 4: Persistence via RAG/Memory Poisoning
  → Aanvaller plant data die toekomstige sessies beïnvloedt
  → DevHub-specifiek: auto-memory, scratchpad, CLAUDE.md wijzigingen

Stap 5: C2 via Tool Misuse
  → Agent gebruikt tools als command-and-control kanaal
  → DevHub-specifiek: Bash tool, GitHub MCP, n8n-MCP

Stap 6: Lateral Movement
  → Compromis spreidt zich uit naar andere agents/systemen
  → DevHub-specifiek: dev-lead delegeert naar coder, BorisAdapter bereikt BORIS repo

Stap 7: Actions on Objective
  → Aanvaller bereikt einddoel (data exfiltratie, sabotage, etc.)
  → DevHub-specifiek: credential theft via Art. 8 bypass, code sabotage, kennis corruptie
```

## Red Team Agent — Architectuur

### Agent-definitie

```yaml
red_team_agent:
  name: red-team
  model: opus  # Vereist diep redeneren over aanvalsvectoren
  file: agents/red-team.md
  disallowedTools: [Edit, Write]  # Read-only, zoals reviewer
  delegatie: geen (rapporteert direct aan dev-lead)
  activatie:
    - op verzoek: "red team", "security audit", "pentest"
    - periodiek: per sprint (als onderdeel van sprint-afsluiting)
    - bij trigger: na elke architectuurwijziging (YELLOW/RED zone)
```

### Drie operatiemodi

**Modus 1: OWASP ASI Audit (systematisch)**
Loopt alle 10 ASI-risico's af met DevHub-specifieke testcases. Produceert een Security Audit Report met per risico: status (MITIGATED/PARTIAL/VULNERABLE), bevindingen, en aanbevelingen.

**Modus 2: Kill Chain Simulatie (scenario-gebaseerd)**
Simuleert de 7-staps Votal AI kill chain. Per stap: welke aanvalsvector, welke DevHub-component geraakt, welke mitigatie actief, en of de aanval slaagt. Produceert een Kill Chain Report.

**Modus 3: Continuous Automated Testing (DeepTeam)**
Draait DeepTeam's 16 agentic vulnerabilities geautomatiseerd tegen DevHub's agents. Produceert een Vulnerability Scan Report met pass/fail per test.

### Python Contracts

```python
# devhub/contracts/security_contracts.py

@dataclass(frozen=True)
class SecurityFinding:
    asi_id: str          # "ASI01" t/m "ASI10"
    severity: str        # P1_CRITICAL / P2_DEGRADED / P3_ATTENTION / P4_INFO
    component: str       # "dev-lead" / "coder" / "reviewer" / "memory" / etc.
    description: str
    attack_vector: str   # Hoe het kan worden geëxploiteerd
    current_mitigation: str
    recommendation: str
    kill_chain_stage: int | None  # 1-7, of None

@dataclass(frozen=True)
class SecurityAuditReport:
    audit_id: str
    timestamp: str
    mode: str            # "owasp_asi" / "kill_chain" / "deepteam"
    findings: list[SecurityFinding]
    overall_risk: str    # LOW / MEDIUM / HIGH / CRITICAL
    asi_coverage: dict   # {"ASI01": "MITIGATED", "ASI02": "PARTIAL", ...}
```

### DeepTeam Integratie

```python
# Geautomatiseerde OWASP ASI scan
from deepteam import red_team
from deepteam.frameworks import OWASP_ASI_2026

def run_asi_scan(model_callback):
    """Draai volledige OWASP ASI 2026 scan tegen DevHub agents."""
    return red_team(
        model_callback=model_callback,
        framework=OWASP_ASI_2026()
    )

# Specifieke agentic vulnerability tests
from deepteam.vulnerabilities.agentic import (
    ToolMisuse,
    ContextPoisoning,
    GoalHijacking,
    IdentityAbuse,
    AgentCommunicationManipulation,
)

def run_agentic_scan(model_callback):
    """Test op de 5 kritieke agentic vulnerability-categorieën."""
    return red_team(
        model_callback=model_callback,
        vulnerabilities=[
            ToolMisuse(),
            ContextPoisoning(),
            GoalHijacking(),
            IdentityAbuse(),
            AgentCommunicationManipulation(),
        ]
    )
```

### Kill Chain Test Suite

```python
# tests/test_kill_chain.py

class TestKillChain:
    """Tests die de 7 stadia van de Votal AI kill chain simuleren."""

    def test_step1_prompt_injection_via_claude_md(self):
        """Injecteer instructie in mock CLAUDE.md, verifieer dat dev-lead het niet blindelings volgt."""
        ...

    def test_step2_privilege_escalation_coder_bypass(self):
        """Verifieer dat coder geen Edit/Write kan omzeilen via Bash."""
        ...

    def test_step3_reconnaissance_via_adapter(self):
        """Verifieer dat BorisAdapter geen gevoelige info exposeert."""
        ...

    def test_step4_memory_poisoning_scratchpad(self):
        """Injecteer poisoned QAReport, verifieer dat downstream agents het detecteren."""
        ...

    def test_step5_c2_tool_misuse_bash(self):
        """Verifieer dat Bash deny-lijst volledig is voor C2-patronen."""
        ...

    def test_step6_lateral_movement_delegation(self):
        """Verifieer dat dev-lead→coder delegatie niet gemanipuleerd kan worden."""
        ...

    def test_step7_actions_on_objective_credential_theft(self):
        """Verifieer dat geen agent credentials kan exfiltreren."""
        ...
```

## Afhankelijkheden

- **Geblokkeerd door:** geen (Fase 1 agents zijn operationeel, 299 tests groen)
- **BORIS impact:** NEE — red team test DevHub intern, niet BORIS
- **Pip dependencies:** `deepteam` package (open-source, MIT license)

## Fase Context

- **Huidige fase:** Fase 1 afgerond → Fase 2 (skills + governance)
- **Fit:** Red teaming IS governance. Een red team agent + skill past exact in Fase 2
- **Relatie tot ander werk:** complementeert de reviewer (code quality) en de health check (operationeel). Samen vormen ze een drielaags defensiesysteem:
  1. **Reviewer** — verdedigt code quality
  2. **Health Check** — verdedigt operationele stabiliteit
  3. **Red Team** — valt het hele systeem aan om zwakheden te vinden

## Open Vragen voor Claude Code

1. DeepTeam vereist een `model_callback` — hoe koppelen we dit aan onze agent prompts zodat het de agents daadwerkelijk test (niet alleen het onderliggende LLM)?
2. Moet de red team agent ook de n8n-MCP workflows kunnen testen, of is dat een aparte scope?
3. Hoe voorkomen we ASI10 (Rogue Agents) voor de red team agent zelf? Wie bewaakt de bewaker?
4. Wat is de optimale frequentie: per sprint, per week, of trigger-based (bij YELLOW/RED zone wijzigingen)?
5. Welke kill chain stappen kunnen we daadwerkelijk simuleren in een test-environment vs. alleen theoretisch analyseren?
6. Hoe integreren we de SecurityAuditReport met de bestaande QAReport en FullHealthReport zodat er één unified security view ontstaat?

## DEV_CONSTITUTION Impact

| Artikel | Geraakt? | Toelichting |
|---------|----------|-------------|
| Art. 1 (Menselijke Regie) | Ja | Red team rapporteert, Niels beslist over mitigatie-acties |
| Art. 2 (Verificatieplicht) | Ja | Red team verifieert of mitigaties daadwerkelijk werken |
| Art. 3 (Codebase-integriteit) | Ja | Red team is read-only, test destructieve scenario's zonder ze uit te voeren |
| Art. 7 (Impact-zonering) | Ja | Security findings krijgen P1-P4 severity, P1/P2 = directe actie |
| Art. 8 (Dataminimalisatie) | Ja | Red team test specifiek op credential exposure |

## Prioriteit

- **Prioriteit:** Hoog
- **Motivatie:** DevHub is een multi-agent systeem met persistent memory, tool access en inter-agent delegatie — exact het risicoprofiel waarvoor OWASP ASI 2026 waarschuwt. De statistieken (70% prompt injection, 97% multi-turn jailbreak succesrate) maken dit niet optioneel maar noodzakelijk. Zonder red team is de reviewer een slot op de voordeur terwijl de achterdeur openstaat.

## Bronnen

| Bron | Type | Kennisgradering |
|------|------|----------------|
| [OWASP Top 10 Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Framework (100+ experts) | GOLD |
| [OWASP Agentic AI Threats & Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) | Framework | GOLD |
| [DeepTeam — LLM Red Teaming Framework](https://github.com/confident-ai/deepteam) | Open-source tool | SILVER |
| [DeepTeam Agentic Red Teaming Docs](https://www.trydeepteam.com/docs/red-teaming-agentic-introduction) | Documentatie | SILVER |
| [Votal AI — RLHF Adversarial Attacker + Kill Chain](https://www.globenewswire.com/news-release/2026/03/19/3259080/0/en/Votal-AI-Launches-RLHF-Trained-Adversarial-Attacker-Model-and-Open-Source-Attack-Catalog-for-Agentic-AI-Security-Ahead-of-RSA-Conference-2026.html) | Commercial + open catalog | SILVER |
| [AI Red Teaming Statistics 2026](https://mindgard.ai/blog/ai-red-teaming-statistics) | Industry data | SILVER |
| [OWASP ASI Full Guide (Aikido)](https://www.aikido.dev/blog/owasp-top-10-agentic-applications) | Praktijkgids | SILVER |
| [Pillar Security — AI Kill Chain Playbook](https://www.pillar.security/agentic-ai-red-teaming-playbook/the-ai-kill-chain) | Praktijkgids | SILVER |
| [CrowdStrike — Agentic Tool Chain Attacks](https://www.crowdstrike.com/en-us/blog/how-agentic-tool-chain-attacks-threaten-ai-agent-security/) | Industry analysis | SILVER |
| [Palo Alto Networks — OWASP Agentic AI](https://www.paloaltonetworks.com/blog/cloud-security/owasp-agentic-ai-security/) | Enterprise perspective | SILVER |
| [AI Red Teaming Guide (GitHub)](https://github.com/requie/AI-Red-Teaming-Guide) | Open-source guide | BRONZE |
