# devhub-research-loop — Node-Agnostische Kennisverrijking Skill

## Trigger
Activeer bij: "research", "onderzoek dit", "investigate", "zoek uit", "kennisverrijking", "literature review", "bronnenonderzoek".

## Doel
Gestructureerde kennisverrijking via de researcher agent en knowledge base. Vertaalt een onderzoeksvraag naar een gegradueerde kennisnotitie met bronvermelding. Node-agnostisch via NodeRegistry — kan kennis ophalen over elk geregistreerd project.

De kracht: (1) Art. 2 verificatieplicht is ingebakken — elke claim wordt gelabeld, (2) Art. 5 kennisgradering garandeert dat kwaliteit expliciet is, (3) output is direct herbruikbaar door andere agents en skills.

---

## Setup

```python
from devhub_core.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")  # Of elk ander geregistreerd project
```

---

## Workflow

### Stap 1: Onderzoeksvraag definiëren

Analyseer de vraag en bepaal:

| Aspect | Opties |
|--------|--------|
| **Domein** | shape-up, evidence-framework, ai-governance, development-patterns, retrospectives |
| **Diepte** | QUICK (1-3 bronnen, 15 min) / STANDARD (5-10 bronnen, 30 min) / DEEP (10+ bronnen, 60 min) |
| **Scope** | Node-specifiek (bijv. BORIS architectuur) of cross-project (bijv. Shape Up methodiek) |

### Stap 2: Bestaande kennis checken

```python
# Check of er al relevante kennis bestaat
from pathlib import Path

knowledge_dir = Path("knowledge")
for domain_dir in knowledge_dir.iterdir():
    if domain_dir.is_dir():
        for article in domain_dir.glob("*.md"):
            # Scan titel en samenvatting op relevantie
            content = article.read_text(encoding="utf-8")
            # Rapporteer bestaande kennis aan developer
```

**Doel:** Voorkom duplicaat-onderzoek. Als er bestaande kennis is:
- GOLD/SILVER: verwijs ernaar, verrijk alleen als nieuw perspectief nodig
- BRONZE/SPECULATIVE: upgrade mogelijkheid — nieuw onderzoek kan gradering verhogen

### Stap 3: Bronnen verzamelen

Gebruik de beschikbare tools in volgorde van betrouwbaarheid:

| Prioriteit | Bron | Tool | Betrouwbaarheid |
|-----------|------|------|----------------|
| 1 | Bestaande knowledge base | Glob + Read | Hoogst (intern gevalideerd) |
| 2 | Project-documentatie | adapter.read_claude_md(), adapter.read_goals() | Hoog (project-context) |
| 3 | Officiële documentatie | WebFetch | Hoog (primaire bron) |
| 4 | Wetenschappelijke publicaties | WebSearch | Hoog (peer-reviewed) |
| 5 | Community bronnen | WebSearch | Medium (verifieer claims) |
| 6 | Buurts kennisbank | buurts_knowledge_search / buurts_knowledge_ask | Hoog (domein-specifiek) |

### Stap 4: Analyse en verificatie

Per gevonden claim:

| Label | Criterium |
|-------|-----------|
| **Geverifieerd** | Bevestigd door ≥2 onafhankelijke bronnen OF primaire bron (officiële docs, paper) |
| **Aangenomen** | Eén betrouwbare bron, geen tegenspraak gevonden |
| **Onbekend** | Niet verifieerbaar met beschikbare bronnen — markeer expliciet |

### Stap 5: Kennisgradering bepalen

| Graad | Criterium | Voorbeeld |
|-------|-----------|-----------|
| **GOLD** | Bewezen in ≥3 sprints OF peer-reviewed publicatie | "Shape Up 6-week cycles werken voor ons team" |
| **SILVER** | Gevalideerd in 1 sprint OF gedocumenteerd door expert | "MCP-servers reduceren context-switching" |
| **BRONZE** | Ervaring-gebaseerd, niet formeel gevalideerd | "Pre-commit hooks vangen 80% van secrets" |
| **SPECULATIVE** | Hypothese, nog te testen | "Agent-memory zou sprint-velocity verhogen" |

**Regel:** Bij twijfel, kies de lagere graad. GOLD degradeert naar SILVER na 6 maanden zonder hervalidatie (Art. 5.4).

### Stap 6: Kennisnotitie schrijven

Output in `knowledge/{domein}/` met het researcher output-formaat:

```markdown
---
title: <titel>
domain: <domein>
grade: <GOLD|SILVER|BRONZE|SPECULATIVE>
sources:
  - <bron 1>
  - <bron 2>
date: <YYYY-MM-DD>
author: researcher-agent
verification: <percentage claims Geverifieerd>
---

# <titel>

## Samenvatting
<2-3 zinnen kernboodschap>

## Inhoud
<gestructureerde analyse met per claim: [Geverifieerd/Aangenomen/Onbekend]>

## Bronnen
<volledige bronvermelding met URLs>

## Toepassing
<hoe dit relevant is voor DevHub en managed projecten>

## Open vragen
<wat nog onderzocht moet worden>
```

### Stap 7: Rapportage

**Output format:**
```
## Research Rapport — [onderwerp]

### Onderzoeksvraag
[De oorspronkelijke vraag]

### Resultaat
- Domein: [domein]
- Gradering: [GOLD/SILVER/BRONZE/SPECULATIVE]
- Bronnen: [aantal] (waarvan [X] primair)
- Verificatie: [X]% claims Geverifieerd

### Samenvatting
[2-3 zinnen kernbevinding]

### Kennisnotitie
Geschreven naar: knowledge/[domein]/[bestandsnaam].md

### Aanbevelingen
[Vervolgonderzoek, gerelateerde vragen, upgrade-mogelijkheden]
```

---

## Regels

- Research is **ALTIJD read-only** voor code — schrijf alleen naar `knowledge/`
- Bronvermelding is VERPLICHT — geen notitie zonder bronnen (Art. 2)
- Kennisgradering is VERPLICHT — geen notitie zonder graad (Art. 5)
- Bij twijfel over gradering: kies de lagere graad
- Verificatie-labels op elke substantiële claim
- Developer beslist of onderzoek wordt toegepast — researcher adviseert alleen
- SPECULATIVE kennis mag NOOIT als feit gepresenteerd worden
- Cross-project kennis respecteert project-soevereiniteit (Art. 6)

## Contract Referentie

| Component | Doel |
|-----------|------|
| `adapter.read_claude_md()` | Project-context ophalen |
| `adapter.read_goals()` | Roadmap en strategische context |
| `adapter.read_overdracht()` | Recente beslissingen en staat |
| `adapter.read_backlog()` | Ideeën en shaping-context |
| `knowledge/{domein}/*.md` | Bestaande kennisnotities |
| `WebSearch` / `WebFetch` | Externe bronnen |
| `buurts_knowledge_search` | Buurts domeinkennis |
