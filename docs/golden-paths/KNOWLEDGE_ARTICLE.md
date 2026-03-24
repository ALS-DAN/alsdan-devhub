# Golden Path: Knowledge Article

_Template voor gestructureerde kennisartikelen in de knowledge base._

---

## Wanneer gebruiken

- Nieuw onderzoek documenteren na `/devhub-research-loop`
- Sprint-lessen vastleggen
- Externe kennis internaliseren
- Impact-zone: GREEN (alleen schrijft naar `knowledge/`)

---

## Kennisdomeinen

| Domein | Pad | Inhoud |
|--------|-----|--------|
| Shape Up | `knowledge/shape-up/` | Methodiek, best practices, anti-patronen |
| Evidence Framework | `knowledge/evidence-framework/` | Bewijsvoering, validatiemodellen |
| AI Governance | `knowledge/ai-governance/` | AI-ethiek, constituties, HITL |
| Development Patterns | `knowledge/development-patterns/` | Code-patronen, architectuurkeuzes |
| Retrospectives | `knowledge/retrospectives/` | Geleerde lessen uit sprints |

---

## Article Template

```markdown
---
title: <titel>
domain: <domein uit tabel hierboven>
grade: <GOLD|SILVER|BRONZE|SPECULATIVE>
sources:
  - <bron 1 URL of referentie>
  - <bron 2>
date: <YYYY-MM-DD>
author: <researcher-agent | naam>
verification: <percentage claims Geverifieerd>
---

# <titel>

## Samenvatting
<2-3 zinnen kernboodschap>

## Inhoud
<gestructureerde analyse>

Per substantiele claim, label:
- [Geverifieerd] — bevestigd door ≥2 bronnen of primaire bron
- [Aangenomen] — eén betrouwbare bron, geen tegenspraak
- [Onbekend] — niet verifieerbaar

## Bronnen
<volledige bronvermelding met URLs waar mogelijk>

## Toepassing
<hoe dit relevant is voor DevHub en managed projecten>

## Open vragen
<wat nog onderzocht moet worden>
```

---

## Graderingsregels (Art. 5 DEV_CONSTITUTION)

| Graad | Criterium | Degradatie |
|-------|-----------|------------|
| **GOLD** | Bewezen in ≥3 sprints OF peer-reviewed | → SILVER na 6 maanden zonder hervalidatie |
| **SILVER** | Gevalideerd in 1 sprint OF expert-bron | → BRONZE na 6 maanden |
| **BRONZE** | Ervaring-gebaseerd, niet formeel gevalideerd | Blijft BRONZE |
| **SPECULATIVE** | Hypothese, nog te testen | Mag NOOIT als feit gepresenteerd |

**Regel:** Bij twijfel, kies de lagere graad.

---

## Verificatie checklist

- [ ] Frontmatter compleet (title, domain, grade, sources, date, author)
- [ ] Samenvatting aanwezig (2-3 zinnen)
- [ ] Claims gelabeld (Art. 2 — Verificatieplicht)
- [ ] Bronvermelding aanwezig (Art. 5 — minimaal 1 bron)
- [ ] Gradering correct toegekend
- [ ] Geschreven naar juiste `knowledge/{domein}/` directory
- [ ] Geen PII of secrets in artikel (Art. 8)
