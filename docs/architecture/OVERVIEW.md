# DevHub Architectuur — Overzicht

---
laatst_bijgewerkt: 2026-03-27
status: ACTIEF
---

## DevHub is de ontwikkelaar

DevHub is geen tool, geen framework, geen library. DevHub is de **ontwikkelaar**. Het denkt na over architectuur, schrijft code, reviewt kwaliteit, plant sprints, en leert van wat het bouwt.

Projecten zijn wat DevHub maakt en onderhoudt. Het eerste project is BORIS (Buurts Ecosysteem) — een zorgdomein RAG-systeem dat ontstaan is uit Gemini Gems (VERA, LUMEN, CLAIR) en vibe coding. BORIS heeft een eigen identiteit en ziel die bewaard blijft.

## Het hybride model

```
DevHub monorepo (alsdan-devhub/)
├── packages/               Python runtime (contracts, adapters, agents)
├── agents/                 Plugin agents (dev-lead, coder, reviewer, ...)
├── skills/                 Plugin skills (devhub-sprint, devhub-health, ...)
├── config/nodes.yml        Registry: welke projecten kent DevHub
├── docs/ + knowledge/      Second Brain (governance, kennis, beslissingen)
└── projects/
    └── buurts-ecosysteem/  Git submodule → private BORIS repo

BORIS eigen repo (buurts-ecosysteem/)
├── src/boris/              Eigen runtime code
├── .claude/skills/         Eigen skills (buurts-sprint, buurts-health, ...)
├── .claude/agents/         Eigen runtime agents (VERA, LUMEN, CLAIR, ...)
├── .claude/hooks/          Eigen validators
└── devhub_integration/     BorisAdapter (NodeInterface implementatie)
```

**Kernprincipes:**

1. **Projecten leven in hun eigen repo.** BORIS is privaat, DevHub linkt via git submodule.
2. **Pull-based communicatie.** DevHub leest van projecten via NodeInterface. Projecten weten niet dat DevHub bestaat.
3. **Project-soevereiniteit (Art. 6).** Wanneer je in een project werkt, gelden de regels van dat project. DevHub overschrijft nooit project-regels.

## Drie lagen

### Laag 1: Python runtime (`packages/`)

De denkkracht. Analyseert, decomponeert, checkt kwaliteit.

| Package | Functie |
|---------|---------|
| devhub-core | NodeInterface ABC, contracts, adapters, agents, registry |
| devhub-storage | Bestandsopslag (Local, Google Drive, SharePoint) |
| devhub-vectorstore | Vector DB (ChromaDB, Weaviate, embeddings) |

**NodeInterface** is het communicatiecontract. Elk project implementeert dit via een adapter. De adapter is read-only — DevHub leest, maar schrijft nooit naar projecten.

### Laag 2: Claude Code plugin (`agents/`, `skills/`)

De interface. Agents en skills die Claude Code gebruikers toegang geven tot DevHub.

- **Plugin agents** (`agents/`): dev-lead, coder, reviewer, researcher, planner, red-team
- **Plugin skills** (`skills/devhub-*/`): sprint, health, mentor, sprint-prep, review, research-loop, governance-check, redteam

Deze zijn node-agnostisch — ze werken voor elk geregistreerd project.

### Laag 3: Second Brain (`docs/`, `knowledge/`)

Het geheugen. Governance, kennis, beslissingen, retrospectives.

- **Governance:** DEV_CONSTITUTION (8 artikelen), ADRs
- **Kennis:** Retrospectives, research, golden paths
- **Planning:** Sprint tracker, roadmap, triage index

## Skills-model

DevHub schrijft skills. Er zijn twee soorten:

### DevHub-skills (node-agnostisch)

Leven in `skills/devhub-*/`. Werken voor elk project via de NodeInterface adapter. Voorbeelden: `/devhub-health` draait een health check op welk project dan ook.

### Project-skills (project-specifiek)

Leven in het project zelf (bijv. `.claude/skills/buurts-*/`). Zijn geschreven door DevHub, maar leven bij het project. Ze kennen de project-context, de domeinlogica, de specifieke agents.

**DevHub maakt beide.** Als BORIS een research hub nodig heeft, schrijft DevHub die als project-skill. Als dat ontwerp beter blijkt dan wat DevHub zelf gebruikt, detecteert DevHub dat en stelt zelfverbetering voor.

## Upgrade-model (niet migratie)

DevHub vervangt geen project-code. DevHub **upgradet** projecten:

1. DevHub bekijkt bestaande code met SOTA-bril
2. Identificeert verbetermogelijkheden
3. Upgradet zonder de essentie te verliezen
4. De "ziel" van Gems (VERA, LUMEN, CLAIR) blijft bewaard

Dit is fundamenteel anders dan migratie. Er wordt niets gesloopt. Er wordt verbeterd.

## Feedback loop

Kennis stroomt in twee richtingen:

```
DevHub → Project    DevHub schrijft/upgradet skills en code
Project → DevHub    Project-innovaties verbeteren DevHub zelf
```

Als een project-skill een beter patroon gebruikt dan DevHub's eigen implementatie, detecteert DevHub dat en stelt voor om zichzelf te verbeteren. Het systeem leert van wat het bouwt.

## Project-registratie

Projecten worden geregistreerd in `config/nodes.yml`:

```yaml
nodes:
  - node_id: boris-buurts
    name: "BORIS — Buurts Ecosysteem"
    path: "/Users/nielspostma/buurts-ecosysteem"
    adapter: "devhub_integration.boris_node.BorisAdapter"
    enabled: true
```

De NodeRegistry laadt adapters lazy en ondersteunt meerdere nodes.

## Samenvatting

| Vraag | Antwoord |
|-------|----------|
| Waar leeft project-code? | In de eigen repo van het project |
| Wie schrijft skills? | DevHub |
| Waar leven project-skills? | In het project |
| Waar leven DevHub-skills? | In DevHub |
| Vervangt DevHub project-skills? | Nee, het upgradet ze |
| Kan DevHub van projecten leren? | Ja, via de feedback loop |
| Overschrijft DevHub project-regels? | Nooit (Art. 6) |
