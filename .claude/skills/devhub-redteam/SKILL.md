# devhub-redteam — Node-Agnostische Security Audit Skill

## Trigger
Activeer bij: "red team", "security audit", "pentest", "owasp", "security check", "kwetsbaarheidsanalyse", "beveiligingsaudit".

## Doel
On-demand security audit van het DevHub multi-agent systeem op basis van de OWASP Top 10 for Agentic Applications (ASI 2026). Produceert een SecurityAuditReport met bevindingen per ASI-risico, kill chain mapping en mitigatie-aanbevelingen. Node-agnostisch via NodeRegistry.

De kracht: (1) systematische 10-punts OWASP ASI audit — niets wordt overgeslagen, (2) kill chain mapping die aanvalsketens zichtbaar maakt, (3) gestructureerde SecurityFindings die direct naar de backlog kunnen.

---

## Setup

```python
from devhub_core.registry import NodeRegistry
from devhub_core.contracts.security_contracts import SecurityFinding, SecurityAuditReport
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")
```

---

## Workflow

### Stap 0: Modus bepalen

Vraag de developer of leid af uit context:

| Modus | Wanneer | Output |
|-------|---------|--------|
| **OWASP ASI Audit** | Standaard, per sprint of op verzoek | SecurityAuditReport met 10-punts ASI coverage |
| **Kill Chain Analyse** | Bij architectuurwijziging of incident | SecurityAuditReport met kill chain stage mapping |

### Stap 1: Systeem-context laden

Lees alle relevante configuratie en agent-definities:

```python
# Node context
report = adapter.get_report()
claude_md = adapter.read_claude_md()
overdracht = adapter.read_overdracht()
```

Lees daarnaast direct:
- `agents/*.md` — alle agent-definities (rol, model, disallowedTools)
- `config/nodes.yml` — node-registratie en adapter-paden
- `.mcp.json` — MCP server configuraties
- `.claude/settings.json` of `.claude/settings.local.json` — permissie-instellingen
- `devhub/contracts/*.py` — contract-definities
- `devhub/adapters/*.py` — adapter-implementaties (shell commands)

### Stap 2: OWASP ASI Audit (10 checks)

Loop elk ASI-risico af. Per risico:
1. **Identificeer DevHub-vectoren** — welke componenten zijn geraakt?
2. **Analyseer huidige mitigatie** — welke DEV_CONSTITUTION artikelen / technische maatregelen bestaan?
3. **Beoordeel effectiviteit** — is de mitigatie volledig, gedeeltelijk of afwezig?
4. **Produceer SecurityFinding** bij PARTIAL of VULNERABLE status

#### ASI01 — Agent Goal Hijacking
- Scan: CLAUDE.md bestanden, nodes.yml, scratchpad content
- Check: Content validation op instructie-bronnen

#### ASI02 — Tool Misuse & Exploitation
- Scan: disallowedTools per agent in `agents/*.md`
- Check: Bash deny-lijst volledigheid, BorisAdapter shell commands

#### ASI03 — Identity & Privilege Abuse
- Scan: .mcp.json, git config, environment variables
- Check: Credential exposure minimaal (Art. 8)

#### ASI04 — Supply Chain Vulnerabilities
- Scan: pip dependencies, submodule integriteit, MCP-servers
- Check: `pip-audit` resultaat, submodule pinning

#### ASI05 — Unexpected Code Execution (RCE)
- Scan: Coder agent tool-gebruik, PYTHONPATH configuratie
- Check: Task descriptions niet als code geëxecuteerd

#### ASI06 — Memory & Context Poisoning
- Scan: auto-memory, scratchpad, CLAUDE.md bestanden
- Check: Integriteitscontroles op persistent state

#### ASI07 — Insecure Inter-Agent Communication
- Scan: Delegatie-patronen in dev-lead.md
- Check: Authenticatie/validatie op inter-agent berichten

#### ASI08 — Cascading Failures
- Scan: Health check → Issue pipeline, QA Agent → sprint stop
- Check: False positive handling, deduplicatie

#### ASI09 — Human-Agent Trust Exploitation
- Scan: Agent-output formatting, PASS verdicts
- Check: Art. 1/Art. 2 naleving in agent-instructies

#### ASI10 — Rogue Agents
- Scan: Agent prompts in version control
- Check: Commit-traceerbaarheid, cross-agent detectie

### Stap 3: Kill Chain Mapping (optioneel)

Als modus = kill_chain, analyseer per stap:

| Stap | Check |
|------|-------|
| 1. Prompt Injection | Welke bronnen beïnvloeden agent-instructies? |
| 2. Privilege Escalation | Kan een agent meer permissies verkrijgen? |
| 3. Reconnaissance | Welke systeeminformatie is beschikbaar? |
| 4. Persistence | Kan data worden geplant die toekomstige sessies beïnvloedt? |
| 5. C2 via Tool Misuse | Welke tools kunnen als C2 kanaal dienen? |
| 6. Lateral Movement | Hoe kan een compromis zich verspreiden? |
| 7. Actions on Objective | Wat is het worst-case scenario? |

Koppel elke finding aan het relevante kill_chain_stage (1-7).

### Stap 4: Rapport genereren

```python
from datetime import datetime, timezone

report = SecurityAuditReport(
    audit_id=f"audit-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}",
    timestamp=datetime.now(timezone.utc).isoformat(),
    mode="owasp_asi",  # of "kill_chain"
    findings=findings,  # list[SecurityFinding]
    asi_coverage={
        "ASI01": "MITIGATED",  # of "PARTIAL" / "VULNERABLE" / "NOT_ASSESSED"
        # ... voor alle 10 ASI's
    },
)
```

### Stap 5: Presentatie aan developer

Toon gestructureerd rapport:

```
## Security Audit Report — {audit_id}

**Modus:** {mode}
**Overall Risk:** {overall_risk}
**Timestamp:** {timestamp}

### ASI Coverage
| ASI | Status | Bevindingen |
|-----|--------|------------|
| ASI01 | MITIGATED | 0 |
| ASI02 | PARTIAL | 2 |
| ... | ... | ... |

### Bevindingen ({total_findings})

#### P1 — Critical ({len})
[SecurityFindings met P1]

#### P2 — Degraded ({len})
[SecurityFindings met P2]

...

### Aanbevelingen (geprioriteerd)
1. [Hoogste impact mitigatie]
2. ...
```

> WACHT OP DEVELOPER REACTIE voordat actie wordt ondernomen op bevindingen.

---

## Regels (altijd van toepassing)
- Read-only: analyseer en rapporteer, exploiteer niet
- Alle 10 ASI-risico's worden getoetst — geen overgeslagen
- Bevindingen altijd met concrete evidence (bestandspaden, regelnummers)
- Severity niet naar beneden bijstellen bij twijfel
- Developer beslist over mitigatie-acties (Art. 1)
