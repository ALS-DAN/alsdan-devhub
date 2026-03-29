# ADR-001: Node Architecture — Vendor-Free Development Orchestration

| Veld | Waarde |
|------|--------|
| Status | Accepted |
| Datum | 2026-03-23 |
| Context | Initiële architectuur: DevHub als multi-node development systeem |
| Impact-zone | YELLOW (nieuwe architectuur, NodeInterface ABC) |

## Context
Het BORIS-project heeft behoefte aan een ontwikkel-orchestratiesysteem dat:
1. Toezicht houdt op BORIS als "klant/node" zonder BORIS te wijzigen
2. Vendor-free is: andere teams kunnen hun eigen DEV setup aan hun eigen project hangen
3. Parallelle documentatie-generatie mogelijk maakt (Docs-as-Code, Diátaxis)
4. Adversarial QA biedt op zowel code als documentatie

## Decision
We bouwen een separaat DEV systeem (`buurts-devhub`) dat via een gestandaardiseerd `NodeInterface` contract communiceert met managed projecten.

### Kernprincipes
1. **Strikte scheiding**: DEV systeem raakt nooit BORIS runtime agents
2. **NodeInterface ABC**: Vendor-free contract — elk project implementeert dit via een adapter
3. **Pull-based communicatie**: DEV leest van nodes; nodes weten niet dat DEV bestaat
4. **LUMEN als brug**: BORIS-LUMEN exporteert een `DevReport` in vendor-free JSON formaat
5. **Lean start**: 3 agents (DevOrchestrator, DocsAgent, QA Agent), uitbreidbaar

### Architectuur
```
DEV systeem (buurts-devhub)
├── NodeInterface (ABC) — vendor-free contract
├── BorisAdapter — implementeert NodeInterface voor BORIS
├── DevOrchestrator — taakdecompositie en delegatie
├── DocsAgent — parallelle docs-generatie (Diátaxis)
└── QA Agent — adversarial code + docs review
```

### NodeInterface Contract
- `get_report() → NodeReport` — volledig node-rapport
- `get_health() → NodeHealth` — gezondheidsstatus
- `list_docs() → List[str]` — documentatie-pagina's
- `run_tests() → TestResult` — test-uitvoering

## Consequences
- BORIS blijft zelfstandig; geen runtime-impact
- Nieuwe projecten implementeren NodeInterface via adapter → onmiddellijk beheerbaar
- LUMEN export is de enige BORIS-wijziging (~30 regels, read-only)
- DEV systeem is extractable: elk team kan het forken voor eigen gebruik
