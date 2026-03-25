# IDEA: n8n Wekelijkse Knowledge Decay Scan

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | Cowork — alsdan-devhub |
| **Status** | INBOX |
| **Fase** | 2 (Skills + Governance) |
| **Datum** | 2026-03-24 |

---

## Kernidee

Een n8n-workflow (lokaal, Docker) die wekelijks (zaterdag 10:00 — start weekendsessie) de kennisbestanden in DevHub's `knowledge/` en `docs/` directories scant op veroudering. De workflow bepaalt veroudering via `git log` (laatste commit-datum per bestand) en matcht die tegen configureerbare drempels per EVIDENCE-grade. Bij significante veroudering genereert de workflow automatisch een `RESEARCH_VOORSTEL_*.md` in de inbox, zodat de researcher-agent de kennis kan vernieuwen. De workflow doet alleen voorstellen — hij past zelf geen graderingen aan (Art. 1: menselijke regie).

**Context**: Niels werkt solo, voornamelijk avonduren en weekenden. Zaterdag 10:00 is het ideale moment: aan het begin van het weekend kan Niels de voorstellen reviewen en besluiten of er research-werk in de weekendsessie past.

**Frontmatter-vereiste**: deze workflow veronderstelt dat kennisbestanden een YAML-frontmatter blok hebben met minimaal `evidence_grade` en `domain`. Voorbeeld:

```yaml
---
evidence_grade: GOLD
domain: AI-engineering
last_validated: 2025-09-15
---
```

Als deze metadata ontbreekt, is een voorbereidende migratie-sprint nodig (zie open punten).

## Motivatie

Kennis veroudert — vooral in AI-engineering waar frameworks, best practices en API's snel evolueren. DevHub's EVIDENCE-methodiek gradeert kennis (GOLD → SILVER → BRONZE → SPECULATIVE), maar er is geen mechanisme dat actief bewaakt of die graderingen nog kloppen. Een GOLD-bron van 6 maanden geleden kan inmiddels achterhaald zijn.

Dit sluit aan bij:
- **Art. 5 (Kennisintegriteit)**: actieve bewaking van kennisgradering
- **Feedback Loop 3** (uit RESEARCH_VOORSTEL_ZELFVERBETEREND_SYSTEEM): Knowledge Decay & Refresh
- **researcher-agent**: krijgt gestructureerde input over wat onderzocht moet worden

## Impact

| Dimensie | Effect |
|----------|--------|
| **Op** | knowledge/, docs/, researcher-agent, EVIDENCE-methodiek |
| **Grootte** | Middel — nieuwe n8n-workflow + conventie voor metadata in kennisbestanden |
| **Risico** | GREEN (read-only scan, schrijft alleen naar inbox/) |

## n8n Workflow Specificatie

### Architectuur

```
scheduleTrigger (zaterdag 10:00, wekelijks — start weekendsessie)
    │
    ▼
executeCommand: Scan knowledge/ en docs/ bestanden
    │ → cd $DEVHUB_REPO_PATH
    │ → git log --format="%H %ai" -1 -- {bestand}
    │ → parse EVIDENCE-grading uit YAML frontmatter
    │
    ▼
code: Bereken leeftijd per bestand + pas decay-regels toe
    │
    │  Decay-drempels:
    │  ├── GOLD:   >6 maanden → degradeer naar SILVER-kandidaat
    │  ├── SILVER: >4 maanden → degradeer naar BRONZE-kandidaat
    │  ├── BRONZE: >3 maanden → markeer als REVIEW-nodig
    │  └── SPECULATIVE: >2 maanden → markeer als VERWIJDER-kandidaat
    │
    ▼
filter: Alleen bestanden die drempel overschrijden
    │
    ▼
if: Bestaat er al een RESEARCH_VOORSTEL voor dit onderwerp in inbox/?
    │
    ├─→ [ja] Skip (voorkom duplicaten)
    └─→ [nee]
          │
          ├─→ code: Genereer RESEARCH_VOORSTEL markdown
          └─→ github: Commit bestand naar docs/planning/inbox/
                      (of: executeCommand: schrijf lokaal)
```

### n8n Nodes (geverifieerd via n8n MCP)

| Stap | Node | Type | Configuratie |
|------|------|------|-------------|
| **1. Trigger** | `n8n-nodes-base.scheduleTrigger` (v1.3) | Trigger | `rule.interval[0].triggerAtDay: 6` (zaterdag), `triggerAtHour: 10` |
| **2. Scan** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "cd $DEVHUB_REPO_PATH && find knowledge/ docs/ -name '*.md' -exec git log ..."` |
| **3. Parse** | `n8n-nodes-base.code` | Transform | JS: parse git dates + frontmatter EVIDENCE-gradering |
| **4. Decay** | `n8n-nodes-base.code` | Transform | JS: bereken leeftijd, pas drempels toe, genereer decay-rapport |
| **5. Filter** | `n8n-nodes-base.filter` | Transform | Alleen items waar `decayDetected === true` |
| **6. Duplicaat-check** | `n8n-nodes-base.executeCommand` (v1) | Transform | `command: "ls docs/planning/inbox/RESEARCH_VOORSTEL_*"` |
| **7a. Genereer voorstel** | `n8n-nodes-base.code` | Transform | JS: bouw RESEARCH_VOORSTEL markdown volgens template |
| **7b. Commit** | `n8n-nodes-base.github` (v1.1) | Input | `resource: file, operation: create, path: docs/planning/inbox/RESEARCH_VOORSTEL_DECAY_{onderwerp}_{datum}.md` (PAT auth) |

### Decay-logica (Code node)

```javascript
// Decay-drempels in dagen
const THRESHOLDS = {
  GOLD: 180,        // 6 maanden
  SILVER: 120,      // 4 maanden
  BRONZE: 90,       // 3 maanden
  SPECULATIVE: 60   // 2 maanden
};

const today = new Date();
const results = files.map(file => {
  const lastModified = new Date(file.gitDate);
  const ageDays = Math.floor((today - lastModified) / (1000 * 60 * 60 * 24));
  const threshold = THRESHOLDS[file.evidenceGrade] || 90;
  const decayDetected = ageDays > threshold;
  const urgency = ageDays > (threshold * 1.5) ? 'HOOG' : 'MIDDEL';

  return {
    ...file,
    ageDays,
    threshold,
    decayDetected,
    urgency,
    suggestedAction: decayDetected
      ? `Hervalideer ${file.evidenceGrade}-bron (${ageDays} dagen oud, drempel: ${threshold})`
      : null
  };
});
```

### Gegenereerd RESEARCH_VOORSTEL Template

```markdown
# RESEARCH_VOORSTEL: Knowledge Decay — {onderwerp}

| Veld | Waarde |
|------|--------|
| **Gegenereerd door** | n8n Knowledge Decay Scan (automated) |
| **Status** | INBOX |
| **Datum** | {datum} |

## Kennislacune

| Aspect | Detail |
|--------|--------|
| **Domein** | {domein uit bestand} |
| **Gat** | Bron "{bestandsnaam}" is {X} dagen niet bijgewerkt (drempel: {Y} dagen) |
| **Huidige grading** | {GOLD/SILVER/BRONZE/SPECULATIVE} |
| **Voorgestelde actie** | Hervalideer of degradeer naar {lagere grade} |

## Onderzoeksvraag

{Automatisch afgeleid uit bestandsnaam en inhoud}

## Bronnen

- [ ] Semantic Scholar
- [ ] ArXiv
- [ ] Anthropic docs
- [ ] CNCF
- [ ] Web

## Evidence doel

| Aspect | Detail |
|--------|--------|
| **Grade** | Herbevestig {huidige grade} of degradeer |
| **Vereist** | Recente peer-reviewed/framework-docs/trusted bronnen |

## Prioriteit

| Aspect | Detail |
|--------|--------|
| **Fase** | 2-3 |
| **Kritiek pad** | {ja als GOLD-bron, nee als BRONZE/SPECULATIVE} |
| **Urgentie** | {HOOG/MIDDEL} |
```

## Relatie bestaand

- **researcher-agent**: ontvangt de gegenereerde RESEARCH_VOORSTEL's als input
- **EVIDENCE-methodiek**: deze workflow automatiseert de "decay"-component
- **devhub-health skill**: complementair — health checkt code, decay checkt kennis
- **Feedback Loop 3** (zelfverbeterend systeem): directe implementatie

## BORIS-impact

**Nee** — scant alleen DevHub's eigen `knowledge/` en `docs/`. BORIS' kennisbestanden vallen onder BORIS' eigen governance (Art. 6 project-soevereiniteit).

## Beslissingen (vastgelegd 2026-03-24)

| Punt | Beslissing |
|------|-----------|
| n8n hosting | Lokaal, Docker op Niels' Mac |
| GitHub auth | Personal Access Token (PAT) via n8n credentials |
| Paden | Environment variables (`$DEVHUB_REPO_PATH`) |
| Trigger-tijd | Zaterdag 10:00 (start weekendsessie — solo developer) |
| Datum-bron | `git log` (betrouwbaarder dan filesystem mtime) |
| Degradatie | Workflow doet alleen voorstellen, past zelf geen graderingen aan (Art. 1) |

| Email SMTP | Gmail met App Password |

## Open punten (resterend — Claude Code scope)

1. **Frontmatter-migratie**: Claude Code inventariseert welke kennisbestanden al EVIDENCE-grading in frontmatter hebben. Ontbrekende frontmatter wordt aangevuld als voorbereidende taak.
2. **Scope**: aanbeveling: alles onder `knowledge/` + `docs/` behalve `docs/planning/` (dat is transient). Claude Code stelt definitieve scope vast.
3. **Threshold-configuratie**: implementeer als `config/decay_thresholds.yml` zodat drempels aanpasbaar zijn zonder de n8n-workflow te wijzigen.
