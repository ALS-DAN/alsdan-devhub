---
title: Retrospective — Dual-Format Machine-Leesbare Systeembestanden (Sprint 46)
domain: retrospectives
grade: SILVER
date: 2026-03-29
author: devhub-sprint
sprint: Dual-Format Machine-Leesbare Systeembestanden
---

# Retrospective — Dual-Format Machine-Leesbare Systeembestanden

## Sprint Samenvatting

| Aspect | Waarde |
|--------|--------|
| Sprint | 46 |
| Type | FEAT |
| Duur | 2026-03-29 → 2026-03-29 |
| Tests start | 1682 |
| Tests eind | 1735 |
| Tests delta | +53 |
| Deliverables | 7/7 afgerond |
| Lint | 0 errors |
| Impact-zone | YELLOW (governance-document wijziging) |

## Wat ging goed

- **Bestaande proza ongewijzigd**: Alle 9 DEV_CONSTITUTION artikelen behielden hun originele tekst — YAML-blokken zijn puur additief. Geen enkel bestaand test is gebroken.
- **YAML parseerbaarheid direct gevalideerd**: `yaml.safe_load` op alle 9 blokken succesvol — geen handmatige verificatie nodig.
- **Agent frontmatter uitbreiding veilig**: De bestaande regex-parser in `test_plugin_agents.py` bleef werken voor de originele velden. Nieuwe `yaml.safe_load`-based parser toegevoegd voor uitgebreide velden — beide parsers co-existeren.
- **ADR standaardisatie minimaal**: Slechts 1 ADR (ADR-001-node-architecture) miste het tabel-formaat. De andere 3 hadden het al.
- **Mermaid-diagrammen dogfooding**: Zone-classificatie flowchart in Art. 7 is direct bruikbaar als referentie door agents.
- **53 nieuwe tests**: Dekking voor YAML-blokken, agent frontmatter, ADR formaat, Mermaid aanwezigheid en standaard-document.

## Wat kan beter

- **Geen runtime-consumptie**: De YAML-blokken zijn gevalideerd op parseerbaarheid maar worden nog door geen runtime-code geconsumeerd. Governance-check skill en DevOrchestrator parsen de DEV_CONSTITUTION nog steeds niet programmatisch.
- **Agent frontmatter niet in productie**: `_parse_yaml_frontmatter()` bestaat alleen in tests. DevHub-core heeft geen code die agent capabilities opvraagt voor delegatie-beslissingen.
- **Mermaid rendering onzeker lokaal**: GitHub rendert Mermaid native, maar VS Code en lokale tools mogelijk niet. Geen CI-validatie van Mermaid syntax.
- **Geen JSON Schema validatie**: YAML-blokken zijn vrij-formaat. Een schema zou afdwingen dat regels altijd id/tekst/type hebben.

## Geleerde lessen

1. **Dual-format werkt als additieve strategie**: Door YAML-blokken toe te voegen in plaats van proza te herschrijven, is het risico op regressie minimaal. Dit patroon is herhaalbaar voor andere documenten.
2. **yaml.safe_load is de juiste parser**: De bestaande regex-parser faalt op YAML arrays. Voor uitgebreide frontmatter is `yaml.safe_load` noodzakelijk.
3. **Documentatie-sprints zijn sneller dan verwacht**: 7 deliverables in 1 sprint is haalbaar wanneer het vooral additief werk is zonder complexe code-afhankelijkheden.

## Aanbevelingen voor volgende sprints

- **Runtime-consumptie bouwen**: Een `ConstitutionParser` class die YAML-blokken uit DEV_CONSTITUTION extraheert en beschikbaar maakt voor governance-check en DevOrchestrator.
- **Agent capability registry**: Dev-lead kan bij delegatie formeel checken welke agent welke capabilities heeft op basis van parsed frontmatter.
- **JSON Schema voor YAML-blokken**: Optioneel SPIKE om schema-validatie te introduceren.
