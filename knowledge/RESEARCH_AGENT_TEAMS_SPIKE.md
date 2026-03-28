# Research: Agent Teams Activatie SPIKE

---
sprint: 38
type: SPIKE
kennisgradering: SILVER
datum: 2026-03-28
bron: SPRINT_INTAKE_AGENT_TEAMS_ACTIVATIE_2026-03-28
vorige_research: RESEARCH_CLAUDE_OPTIMALISATIE_CONCLUSIE (Sprint 31)
verdict: GEPARKEERD (herbevestigd met actuele onderbouwing)
---

## Samenvatting

Deze SPIKE onderzocht of Claude Code Agent Teams DevHub's bestaande 7 agents kan upgraden van solo-workers naar een gecoordineerd team. **Conclusie: GEPARKEERD.** Twee fundamentele blokkades verhinderen adoptie:

1. **Custom agents niet als teammates** — Agent Teams spawnt alleen generieke agents. DevHub's gespecialiseerde agents (tool-restricties, modellen, permissions) kunnen niet als teammates draaien.
2. **Nog steeds experimenteel** — Feature vereist `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, geen stabiele release, bekende beperkingen onveranderd.

De Sprint 31 conclusie (GEPARKEERD, P4) wordt herbevestigd met sterkere onderbouwing.

---

## Fact-Finding Resultaten

### Bevinding 1: Experimentele status onveranderd

| Aspect | Bevinding | Verificatie |
|--------|-----------|-------------|
| Feature flag | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` nog steeds vereist | Geverifieerd (Anthropic docs) |
| Minimale versie | Claude Code v2.1.32+ | Geverifieerd (Anthropic docs) |
| Release-status | Research Preview (6 feb 2026), geen GA-aankondiging | Geverifieerd (Anthropic docs) |
| Session resumption | Niet beschikbaar — teammates verdwijnen na `/resume` | Geverifieerd (Anthropic docs) |
| Nested teams | Niet mogelijk — teammates kunnen geen eigen teams spawnen | Geverifieerd (Anthropic docs) |
| Teams per sessie | Maximaal 1 team per lead-sessie | Geverifieerd (Anthropic docs) |

**Kennisgradering:** GOLD — primaire bron (Anthropic officiele documentatie).

**Bron:** [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)

### Bevinding 2: Custom agents als teammates — NIET MOGELIJK

Dit is de fundamentele blokkade voor DevHub.

**Hoe Agent Teams werkt:**
- Lead spawnt teammates via natuurlijke taal prompt
- Alle teammates starten als **generieke Claude Code instanties**
- Specialisatie alleen via prompt-instructies (niet deterministisch afdwingbaar)
- Alle teammates erven de lead's permission-modus — geen per-teammate configuratie bij spawn

**Wat DevHub nodig heeft maar niet kan krijgen:**

| DevHub-vereiste | Agent Teams status | Impact |
|-----------------|-------------------|--------|
| `coder` zonder Agent tool (`disallowedTools: Agent`) | Niet mogelijk — teammates krijgen alle tools | Coder kan ongewenst agents spawnen |
| `reviewer` read-only (geen Edit/Write) | Niet afdwingbaar — alleen via prompt | Reviewer kan ongewenst bestanden wijzigen |
| Verschillende modellen per agent (reviewer=opus, coder=sonnet) | Niet per-teammate instelbaar bij spawn | Alle teammates draaien op lead's model |
| Persistent memory per agent | Niet beschikbaar — teammates starten vers | Geen opgebouwde kennis per agent-rol |
| Lifecycle hooks per agent | Niet beschikbaar | Geen per-agent quality gates |

**Community-bevestiging:** GitHub Issue [anthropics/claude-code#24316](https://github.com/anthropics/claude-code/issues/24316) — "Allow custom `.claude/agents/` definitions as agent team teammates" (26 upvotes, 27 comments, OPEN, geen Anthropic-reactie per 18 mrt 2026).

**Kernargument uit de issue:**
> "Natural language prompts can be ignored, misinterpreted, or overridden by the model. Tool restrictions and hooks are deterministic enforcement mechanisms — a teammate with `tools: Read, Grep, Glob` physically cannot write files."

**Kennisgradering:** GOLD — primaire bronnen (Anthropic docs + GitHub issue).

### Bevinding 3: 90.2% claim niet verifieerbaar

| Aspect | Bevinding | Verificatie |
|--------|-----------|-------------|
| Bronvermelding in intake | codewithseb.com multi-agent guide | Onbekend (HTTP 403, bron ontoegankelijk) |
| Context | Claim gaat over multi-agent systemen generiek, niet Agent Teams specifiek | Aangenomen (afgeleid uit andere bronnen die dezelfde benchmark citeren) |
| Relevantie voor DevHub | DevHub heeft al multi-agent via subagent-delegatie — de vergelijking single-agent vs multi-agent is al opgelost | Geverifieerd (eigen systeem) |

**Kennisgradering:** BRONZE — bron ontoegankelijk, claim niet verifieerbaar, context suggereert irrelevantie.

### Bevinding 4: Roadmap-positie klopt

| Document | Positie Agent Teams | Onderbouwing |
|----------|---------------------|-------------|
| ROADMAP.md | Fase 5D (na heel Fase 4, vereist 5B) | Dependency-analyse in afhankelijkheidsdiagram |
| Sprint 31 Research | P4 (laagste prioriteit) | Experimenteel, token-overhead, governance-risico's |
| SPIKE Intake | Fase 4 Golf 1 (eerste sprint) | Geen — intake gaf geen reden voor afwijking van roadmap |

**Conclusie:** ROADMAP.md positie (5D) is correct. De intake's claim van "Fase 4 Golf 1" was gebaseerd op een optimistische inschatting die niet door feiten wordt ondersteund.

**Kennisgradering:** SILVER — gevalideerd tegen eigen documentatie en huidige feiten.

---

## Antwoorden op Open Vragen

### OV1: Werkt TeammateTool vanuit plugin-agents?

**Antwoord: Niet relevant.** TeammateTool is beschikbaar in Claude Code sessies met de feature flag. Maar het probleem is niet of je het kunt *aanroepen* — het probleem is dat je geen custom agent-definities kunt meegeven aan teammates. DevHub's `agents/dev-lead.md` kan theoretisch een team spawnen, maar de teammates zijn generieke agents, niet de gespecialiseerde coder/reviewer.

### OV2: Kunnen teammates elkaars agent-memory lezen?

**Antwoord: Nee.** Elke teammate heeft een eigen context window. Ze laden wel dezelfde CLAUDE.md en MCP servers, maar conversation history wordt niet gedeeld. Agent-memory (`.claude/agent-memory/`) is per-sessie.

**Verificatie:** Geverifieerd (Anthropic docs: "The lead's conversation history does not carry over").

### OV3: Shared task list vs. SPRINT_TRACKER.md?

**Antwoord: Geen interactie.** Agent Teams' shared task list (`~/.claude/tasks/{team-name}/`) is een in-sessie coordinatie-mechanisme. SPRINT_TRACKER.md is een persistent planning-document. Ze opereren op verschillende niveaus en kennen elkaar niet.

### OV4: Teammate-resultaten loggen voor kennispipeline?

**Antwoord: Deels.** Teammates schrijven naar het filesystem — als ze Markdown naar `knowledge/` schrijven, is dat persistent. Maar er is geen automatische brug naar de kennispipeline. Dit zou handmatig of via hooks moeten.

### OV5: Kunnen teammates skills aanroepen?

**Antwoord: Ja, waarschijnlijk.** Teammates laden CLAUDE.md en skills automatisch. Maar zonder tool-restricties kan een teammate onbedoeld destructieve skills aanroepen. Dit is een governance-risico (Art. 7).

---

## Vergelijking: Subagent-delegatie vs. Agent Teams

| Criterium | Subagent-delegatie (huidig) | Agent Teams | Voordeel |
|-----------|----------------------------|-------------|----------|
| Specialisatie | Custom agents met tool-restricties | Alleen generieke agents | Subagents |
| Parallellisme | Beperkt (via Explore/Plan agents) | Volledig parallel met communicatie | Agent Teams |
| Governance (Art. 1) | Dev-lead controleert volledig | Lead controleert, maar teammates zijn autonomer | Subagents |
| Traceerbaarheid (Art. 4) | Volledige transcript in hoofdsessie | Verspreid over meerdere context windows | Subagents |
| Token-kosten | Lager (resultaten samengevat) | Significant hoger (elk teammate = eigen context) | Subagents |
| Inter-agent communicatie | Niet mogelijk (alleen rapportage aan parent) | Mailbox + shared task list | Agent Teams |
| Session resumption | Werkt (subagent results in hoofdsessie) | Niet beschikbaar | Subagents |

**Score: 5-2 voor subagent-delegatie** in DevHub's huidige context.

---

## Aanbeveling

### Verdict: GEPARKEERD (herbevestigd)

Agent Teams is een krachtig concept maar **niet compatibel met DevHub's architectuur** zolang custom agent-definities niet als teammates kunnen draaien. De twee systemen (subagents met specialisatie vs. teams met collaboratie) zijn gescheiden werelden.

### Herevaluatie-criteria

Heropen deze SPIKE wanneer **alle drie** deze condities waar zijn:

1. **Custom agents als teammates** — GitHub Issue #24316 is opgelost: `.claude/agents/` definities werken als teammate-configuratie (tool-restricties, modellen, hooks)
2. **Stabiele release** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` flag is verwijderd of Agent Teams is GA
3. **Session resumption** — Teams overleven `/resume` en `/rewind`

### Alternatieve verbeteringen (huidige subagent-flow)

In plaats van Agent Teams, overweeg deze verbeteringen aan DevHub's bestaande architectuur:

| Verbetering | Impact | Effort | Afhankelijkheid |
|-------------|--------|--------|-----------------|
| Parallelle subagent-spawning (dev-lead spawnt coder + reviewer tegelijk) | Snelheid | XS | Geen — al mogelijk met Agent tool |
| Hooks voor quality gates (PostToolUse na code-wijzigingen) | Governance | XS | Geen |
| Event Bus voor agent-communicatie (Sprint 2 intake) | Coordinatie | S | Geen |
| Path-scoped rules voor modulaire context-laden | Efficiency | XS | Geen |

---

## Bronverantwoording

| Bron | Type | Kennisgradering | Verificatie |
|------|------|-----------------|-------------|
| [Anthropic Agent Teams docs](https://code.claude.com/docs/en/agent-teams) | Primaire bron | GOLD | Geverifieerd |
| [GitHub #24316](https://github.com/anthropics/claude-code/issues/24316) | Community feature request | GOLD | Geverifieerd |
| [Sean Kim — March 2026 Update](https://blog.imseankim.com/claude-code-team-mode-multi-agent-orchestration-march-2026/) | Externe analyse | SILVER | Geverifieerd |
| [Addy Osmani — Claude Code Swarms](https://addyosmani.com/blog/claude-code-agent-teams/) | Externe analyse | SILVER | Geverifieerd |
| [Kieran Klaassen — Swarm Skill](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea) | Referentie-implementatie | SILVER | Geverifieerd |
| codewithseb.com multi-agent guide | Externe bron (90.2% claim) | BRONZE | Onbekend (HTTP 403) |
| DevHub codebase + Sprint 31 research | Eigen systeem | GOLD | Geverifieerd |
| ROADMAP.md afhankelijkheidsdiagram | Eigen planning | GOLD | Geverifieerd |

---

## Conclusie

Agent Teams is GEPARKEERD met sterkere onderbouwing dan Sprint 31. De kernblokkade (custom agents niet als teammates) is nu concreet gedocumenteerd met primaire bronnen. De roadmap-positie (Fase 5D) is correct — Agent Teams hoort na de subagent-architectuur volwassen is en Anthropic custom-agent-support heeft toegevoegd.

DevHub's subagent-delegatie is voor de huidige use cases (governance-workflows, audit trails, gespecialiseerde agents) de betere keuze. De alternatieve verbeteringen (parallelle spawning, hooks, event bus) bieden meer waarde op kortere termijn.
