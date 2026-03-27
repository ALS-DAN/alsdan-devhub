---
gegenereerd_door: "Cowork — alsdan-devhub"
status: DONE
fase: 3
---

# IDEA: Provider Pattern — BorisAdapter naar BORIS repo

## Kernidee

De BorisAdapter (`devhub_core/adapters/boris_adapter.py`) verhuist uit de DevHub public repo naar de BORIS private repo. DevHub behoudt alleen het generieke contract (NodeInterface ABC + frozen dataclasses) en het discovery-mechanisme (NodeRegistry + `nodes.yml`). BORIS levert zijn eigen NodeInterface-implementatie — zoals Terraform providers hun eigen repo hebben, los van Terraform core.

Dit volgt het **Provider Pattern** (ook: SPI — Service Provider Interface): het platform definieert het contract, het project levert de implementatie.

## Motivatie

**Public/private scheiding.** DevHub is een publieke repo. De BorisAdapter beschrijft BORIS' interne structuur: mappaden (`docs/planning/inbox/`, `.claude/OVERDRACHT.md`, `.claude/scratchpad/dev_report.json`), tooling (mkdocs.yml, pytest venv-locatie), en interne scripts (HERALD). Dit is een plattegrond van een privaat project in een publieke codebase.

**Architecturele zuiverheid.** Het Provider Pattern (Terraform, Kubernetes Operators, Java SPI) scheidt platform van implementatie. Het platform kent het contract, de provider kent het systeem. DevHub schendt dit nu: de BorisAdapter zit in devhub-core, waardoor DevHub BORIS "kent."

**Project-soevereiniteit (Art. 6).** BORIS moet zijn eigen adapter beheren. Als BORIS van mkdocs naar Sphinx overstapt, of HERALD hernoemt, of zijn mapstructuur wijzigt, moet dat een BORIS-wijziging zijn — niet een DevHub-wijziging.

**Tweede project readiness.** Als DevHub straks een tweede project aanstuurt, moet dat project zijn eigen adapter leveren. Het huidige patroon (adapter in devhub-core) schaalt niet.

## Impact

- **Op:** devhub-core (adapter verwijderen), BORIS repo (adapter toevoegen), config/nodes.yml (pad aanpassen)
- **Grootte:** Klein — het is primair een verplaatsing, geen herschrijving

## Wat verhuist naar BORIS

| Component | Huidig pad (DevHub) | Nieuw pad (BORIS) |
|-----------|--------------------|--------------------|
| BorisAdapter | `packages/devhub-core/devhub_core/adapters/boris_adapter.py` | `devhub_integration/boris_node.py` (of vergelijkbaar) |
| Adapter tests | `packages/devhub-core/tests/test_boris_adapter*.py` | `tests/test_boris_node.py` |

## Wat blijft in DevHub (public)

| Component | Pad | Rol |
|-----------|-----|-----|
| NodeInterface ABC | `packages/devhub-core/devhub_core/contracts/node_interface.py` | Het contract — 13 frozen dataclasses + ABC |
| NodeRegistry | `packages/devhub-core/devhub_core/registry.py` | Discovery — laadt adapters via `importlib` + config |
| `nodes.yml` | `config/nodes.yml` | Config — wijst naar adapter-klasse in project |

## Wat verandert in nodes.yml

```yaml
# NU (adapter in DevHub):
nodes:
  - node_id: boris-buurts
    adapter: "devhub_core.adapters.boris_adapter.BorisAdapter"

# STRAKS (adapter in BORIS):
nodes:
  - node_id: boris-buurts
    adapter: "boris_node.BorisAdapter"  # of via entry_points/sys.path
    path: "projects/buurts-ecosysteem"
```

De registry's `_instantiate_adapter()` gebruikt al `importlib.import_module()` — het enige dat verandert is het import-pad.

## Bijkomende opruiming

- **Docstrings:** BORIS-referenties in devhub-vectorstore en devhub-core opruimen naar generieke taal (bijv. "Voorbeeld: Project X Red → RESTRICTED" wordt "Voorbeeld: RESTRICTED, CONTROLLED, OPEN")
- **Seed articles:** `seed_articles.py` bevat BORIS-specifieke voorbeelden — generiek maken of markeren als DevHub-scope
- **Weaviate adapter docstring:** "BORIS-compatibel: Weaviate 1.27.x" → "Getest met Weaviate 1.27.x"

## Relatie bestaand

- **NodeInterface + NodeRegistry:** Blijven ongewijzigd — het contract is al generiek
- **DevOrchestrator:** Gebruikt adapter via registry abstractie, geen directe import — geen wijziging nodig
- **Sprint skill (devhub-sprint):** De SPIKE_LIFECYCLE_HYGIENE maakt BORIS-context al conditioneel — complementair aan deze IDEA
- **Plugin agents (dev-lead, coder, etc.):** Werken direct op bestanden in workspace, onafhankelijk van adapter

## BORIS-impact

- **Ja** — BORIS krijgt een nieuw bestand (`boris_node.py`) + dependency op `devhub_core.contracts.node_interface`
- BORIS moet `devhub-core` als dependency opnemen (alleen het contracts-package), of NodeInterface wordt een apart micro-package

## SOTA-onderbouwing

| Patroon | Bron | Toepassing |
|---------|------|------------|
| Provider Pattern | [Terraform Provider Design Principles](https://developer.hashicorp.com/terraform/plugin/best-practices/hashicorp-provider-design-principles) | Platform (DevHub) definieert contract, provider (BORIS) levert implementatie in eigen repo |
| Service Provider Interface | [Java SPI](https://www.baeldung.com/java-spi) / [Python entry_points](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/) | Discovery via config/registry, lazy loading via importlib |
| Operator Pattern | [Kubernetes Operators](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) | Operator woont bij de applicatie, niet bij het platform — kent zijn eigen reconciliation-logica |
| Separation of Concerns | Terraform: "A provider should manage a single collection of components based on the underlying API" | BorisAdapter kent alleen BORIS; DevHub kent alleen het contract |

**Kennisgradering:** SILVER — gebaseerd op framework-documentatie en bewezen industriepatronen (Terraform, Kubernetes, Java SPI).

## Open punten

1. **Import-mechanisme:** Hoe vindt DevHub de adapter in het submodule-pad? Opties: sys.path manipulatie, Python entry_points, of simpelweg het submodule-pad toevoegen aan de Python path in nodes.yml config.
2. **Dependency richting:** BORIS moet NodeInterface kennen. Wordt dat een `pip install devhub-core[contracts]` in BORIS, of een apart micro-package `devhub-contracts`?
3. **Timing:** Deze IDEA is complementair aan de SPIKE_LIFECYCLE_HYGIENE FEAT. Kan parallel of sequentieel — geen harde dependency.
4. **Test-migratie:** ~13 BORIS-specifieke testbestanden verhuizen. DevHub verliest die tests uit zijn telling (1082 → ~1070). Acceptabel?
