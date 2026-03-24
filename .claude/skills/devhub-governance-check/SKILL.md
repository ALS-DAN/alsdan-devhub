# devhub-governance-check — Node-Agnostische Compliance Audit Skill

## Trigger
Activeer bij: "governance check", "compliance audit", "check constitution", "governance audit", "controleer compliance", "DEV_CONSTITUTION check", "pre-merge check".

## Doel
Automatische compliance-audit tegen de DEV_CONSTITUTION vóór sprint-start, merge of release. Controleert alle 8 artikelen en produceert een gestructureerd rapport met verdict (PASS/NEEDS_REVIEW/BLOCK). Node-agnostisch via NodeRegistry.

De kracht: (1) systematische check van alle 8 artikelen — niets wordt overgeslagen, (2) automatische detectie van secrets, destructieve operaties en impact-zonering, (3) verdict-systeem dat escaleert naar de juiste persoon.

---

## Setup

```python
from devhub.registry import NodeRegistry
from devhub.agents.qa_agent import QAAgent
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("boris-buurts")
qa = QAAgent()
```

---

## Workflow

### Stap 1: Scope bepalen

Bepaal wat geaudit wordt:

| Scope | Wanneer | Bron |
|-------|---------|------|
| **Staged changes** | Pre-commit / pre-merge | `git diff --staged` |
| **Sprint deliverables** | Sprint-start / sprint-afsluiting | Sprint-doc + gewijzigde bestanden |
| **Volledige repo** | Periodieke audit | Alle bestanden |

```python
ctx = adapter.get_review_context()
# ctx bevat: diff_staged, diff_unstaged, files_staged, files_unstaged, anti_patterns
```

### Stap 2: Artikel-voor-artikel audit

#### Art. 1 — Menselijke Regie
| Check | Methode |
|-------|---------|
| G-01: Geen autonome destructieve acties | Scan diff op `--force`, `--hard`, `rm -rf`, `DROP TABLE` |
| G-02: Beslissingen traceerbaar naar developer | Check commit messages op autorisatie-context |

#### Art. 2 — Verificatieplicht
| Check | Methode |
|-------|---------|
| G-03: Claims gelabeld | Scan nieuwe docs op "Geverifieerd" / "Aangenomen" / "Onbekend" |
| G-04: Bronvermelding aanwezig | Check `knowledge/` artikelen op `sources:` frontmatter |

#### Art. 3 — Codebase-integriteit
| Check | Methode |
|-------|---------|
| G-05: Geen destructieve git operaties | Scan voor `force push`, `reset --hard`, `--no-verify` |
| G-06: Geen ongeautoriseerde bestandsdeletie | Check git diff op deleted files zonder context |

#### Art. 4 — Transparantie & Traceerbaarheid
| Check | Methode |
|-------|---------|
| G-07: Commit messages bevatten WAT + WAAROM | Analyseer recente commits op structuur |
| G-08: Co-Authored-By aanwezig | Check commit trailer |

#### Art. 5 — Kennisintegriteit
| Check | Methode |
|-------|---------|
| G-09: Kennis correct gegradueerd | Scan `knowledge/` op grade: frontmatter |
| G-10: GOLD niet ouder dan 6 maanden | Check date: vs vandaag |

#### Art. 6 — Project-soevereiniteit
| Check | Methode |
|-------|---------|
| G-11: Geen wijzigingen aan project-governance | Scan diff op `projects/*/CLAUDE.md`, `projects/*/.claude/` |

#### Art. 7 — Impact-zonering
| Check | Methode |
|-------|---------|
| G-12: Impact-zone geclassificeerd | Analyseer scope van wijzigingen |
| G-13: RED-zone heeft expliciete goedkeuring | Check voor developer-akkoord bij destructieve changes |

#### Art. 8 — Dataminimalisatie
| Check | Methode |
|-------|---------|
| G-14: Geen secrets in code | `adapter.run_lint()` + detect-secrets scan |
| G-15: Geen PII in commits | Scan diff op email-patronen, BSN, telefoonnummers |
| G-16: Geen .env bestanden gecommit | Check staged files op `.env*` patronen |

```python
# Lint + secrets check
lint_clean, lint_output = adapter.run_lint()

# Anti-patronen (inclusief secrets)
anti_patterns = ctx.get("anti_patterns", [])
```

### Stap 3: QA Agent integratie

```python
from devhub.contracts.dev_contracts import DevTaskResult

task_result = DevTaskResult(
    task_id="governance-audit",
    files_changed=ctx["files_all"],
    tests_added=0,
    lint_clean=lint_clean,
)

# Code checks (CR-03 = secrets, CR-09 = print in prod, etc.)
code_findings = qa.review_code(task_result, project_root=Path(adapter.boris_path))
```

### Stap 4: Verdict bepalen

| Verdict | Criterium |
|---------|-----------|
| **PASS** | Alle checks groen, geen CRITICAL/ERROR findings |
| **NEEDS_REVIEW** | ≥1 WARNING finding OF impact-zone YELLOW |
| **BLOCK** | ≥1 CRITICAL finding OF secrets gedetecteerd OF RED-zone zonder goedkeuring |

### Stap 5: Rapport genereren

**Output format:**
```
## Governance Audit Rapport — [datum]

### Scope
[Staged changes / Sprint X / Volledige repo]

### Artikel-checks

| # | Artikel | Check | Resultaat |
|---|---------|-------|-----------|
| G-01 | Art. 1 Menselijke Regie | Geen autonome destructieve acties | PASS/FAIL |
| G-02 | Art. 1 Menselijke Regie | Beslissingen traceerbaar | PASS/FAIL |
| G-03 | Art. 2 Verificatieplicht | Claims gelabeld | PASS/FAIL/N.V.T. |
| ... | ... | ... | ... |
| G-16 | Art. 8 Dataminimalisatie | Geen .env bestanden | PASS/FAIL |

### Samenvatting
- Checks: [X/16] PASS
- Findings: [X] CRITICAL, [X] ERROR, [X] WARNING, [X] INFO
- Impact-zone: [GREEN/YELLOW/RED]

### Verdict: PASS / NEEDS_REVIEW / BLOCK

### Bevindingen (indien aanwezig)
| # | Severity | Artikel | Beschrijving | Bestand:regel |
|---|----------|---------|-------------|---------------|
| 1 | CRITICAL | Art. 8 | Secret gedetecteerd | config.py:42 |

### Aanbevelingen
[Concrete acties om BLOCK/NEEDS_REVIEW op te lossen]
```

---

## Regels

- Governance check is **ALTIJD read-only** — rapporteert, fixt nooit
- Bij twijfel over impact-zone: kies de hogere zone (Art. 7)
- CRITICAL findings blokkeren ALTIJD — geen uitzonderingen
- Developer beslist bij NEEDS_REVIEW — DevHub adviseert
- Secrets-detectie is de hardste gate: één secret = automatisch BLOCK
- Art. 6 respecteren: project-eigen governance gaat altijd voor
- Rapporteer altijd alle 16 checks, ook als alles PASS is (transparantie)

## Contract Referentie

| Component | Doel |
|-----------|------|
| `adapter.get_review_context()` | Diff + files + anti-patronen |
| `adapter.run_lint()` | Lint + basis secrets check |
| `QAAgent.review_code()` | CR-01..12 code compliance |
| `QAAgent.produce_report()` | QAReport met verdict |
| `docs/compliance/DEV_CONSTITUTION.md` | Bron van waarheid (8 artikelen) |
