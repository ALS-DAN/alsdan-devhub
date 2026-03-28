# devhub-review — Node-Agnostische Code Review Skill

**Versie:** 1.0.0
**Basis:** BORIS buurts-review → gemigreerd naar DevHub (QA Agent + BorisAdapter)

## Trigger
Activeer bij: "review", "code review", "PR check", "controleer code", "check deze wijziging", "security audit", "bekijk deze code".

## Doel
Gestructureerde code review die compliance-toetsing (12 code + 6 doc checks) combineert met anti-patroon detectie en diepte-analyse. Produceert QAReports met verdict (PASS/NEEDS_WORK/BLOCK). Node-agnostisch via de BorisAdapter + QA Agent.

De kracht: (1) de QA Agent checklist garandeert dat standaard-checks nooit vergeten worden, (2) de anti-patroon scan detecteert node-specifieke violations, (3) het git diff-gebaseerde workflow zorgt dat alleen relevante wijzigingen gereviewed worden.

---

## Setup

```python
from devhub_core.agents.qa_agent import QAAgent
from devhub_core.contracts.dev_contracts import DevTaskResult

qa = QAAgent()

# Alleen bij node: boris-buurts (of andere managed node)
from devhub_core.registry import NodeRegistry
from pathlib import Path

registry = NodeRegistry(config_path=Path("config/nodes.yml"))
adapter = registry.get_adapter("<node-id>")  # bijv. "boris-buurts"
```

---

## Workflow

### Stap 0: Node bepalen (ALTIJD EERST — vóór alles)

> **HARD GATE**: Laad GEEN context voordat de node bepaald is.

Bepaal de target node:
1. **Developer specificeert node**: gebruik die
2. **Geen specificatie**: VRAAG de developer welke node (devhub of boris-buurts)
3. **Contextclue**: als je in een DevHub-sprint zit → `devhub`, als je in een BORIS-sprint zit → `boris-buurts`

> Lanceer NOOIT parallel agents voor meerdere nodes.

---

### Stap 1: Wijzigingen verzamelen (pad volgt uit stap 0)

#### DevHub-pad (node: devhub)

Verzamel wijzigingen via directe git commands:
- `git diff` — unstaged changes
- `git diff --staged` — staged changes
- `git diff --name-only` + `git diff --staged --name-only` — gewijzigde bestanden

QA Agent werkt direct op het DevHub-project (geen adapter nodig).

#### BORIS-pad (node: boris-buurts)

```python
ctx = adapter.get_review_context()
```

Dit levert:
| Key | Inhoud |
|-----|--------|
| `diff_unstaged` | Git diff van unstaged changes |
| `diff_staged` | Git diff van staged changes |
| `files_unstaged` | Lijst unstaged gewijzigde bestanden |
| `files_staged` | Lijst staged bestanden |
| `files_all` | Gecombineerde unieke lijst |
| `anti_patterns` | Gevonden anti-patronen met severity |

### Stap 2: Code Review Checklist (QA Agent)

De QA Agent checkt automatisch 12 code criteria:

| ID | Check |
|----|-------|
| CR-01 | Nieuwe code heeft tests |
| CR-02 | Geen lint errors |
| CR-03 | Geen hardcoded secrets |
| CR-04 | Foutafhandeling aanwezig |
| CR-05 | Single responsibility |
| CR-06 | Project-naamconventies |
| CR-07 | Geen dead code |
| CR-08 | Type hints op publieke functies |
| CR-09 | Geen print() in productie |
| CR-10 | Frozen dataclasses |
| CR-11 | Docstrings op publieke functies |
| CR-12 | Functies <50 regels |

```python
task_result = DevTaskResult(
    task_id="review-session",
    files_changed=ctx["files_all"],
    tests_added=0,  # Wordt later ingevuld
    lint_clean=adapter.run_lint()[0],
)

code_findings = qa.review_code(task_result, project_root=Path(adapter.boris_path))
```

### Stap 3: Anti-patronen scan

Automatisch al in `ctx["anti_patterns"]` — node-specifieke violations:

| Anti-patroon | Severity |
|-------------|----------|
| Direct ChromaDB aanroep buiten ZonedVectorStore | ERROR |
| RED-zone logica buiten safety/policy.py | CRITICAL |
| EphemeralClient zonder UUID-suffix | WARNING |
| Hardcoded secrets/credentials | CRITICAL |
| print() in productie-code | WARNING |

### Stap 4: Documentatie Review (optioneel)

Als er docs gewijzigd zijn:

```python
from devhub_core.contracts.dev_contracts import DocGenRequest

doc_requests = [DocGenRequest(...)]  # Op basis van gewijzigde docs
doc_findings = qa.review_docs(doc_requests)
```

6 doc criteria: DR-01 t/m DR-06 (Diataxis, audience, completeness, etc.)

### Stap 5: Lint & Test

```python
# Lint
lint_clean, lint_output = adapter.run_lint()

# Tests
test_result = adapter.run_tests()
```

### Stap 6: QA Report genereren

```python
report = qa.produce_report(
    task_id="review-session",
    code_findings=code_findings,
    doc_findings=doc_findings,
)

# Verdict: PASS / NEEDS_WORK / BLOCK
print(f"Verdict: {report.verdict}")
```

### Stap 7: Rapportage

**Output format:**
```
## Review Rapport — [datum/bestand]

### Code Checks: [X/12 OK]
[Per check: ✅/⚠️/❌ met toelichting bij afwijkingen]

### Anti-patronen: [X gevonden]
[Details per gevonden anti-patroon met bestand:regel]

### Bevindingen ([X] items)
| # | Severity | Beschrijving | Bestand:regel |
|---|----------|-------------|---------------|
| 1 | CRITICAL | ... | ... |
| 2 | ERROR | ... | ... |

Severity levels: CRITICAL > ERROR > WARNING > INFO

### Lint: [ruff OK/errors]
### Tests: [X/X passed]

### Verdict: ✅ PASS | ⚠️ NEEDS_WORK | ❌ BLOCK
[Samenvatting + aanbevelingen]
```

---

## Regels

- **Node-keuze eerst** — laad GEEN context voordat de node bepaald is (stap 0)
- **Één node per review** — lanceer nooit parallel agents voor meerdere nodes
- **Respecteer Claude Code modes** — in plan mode: alleen planbestand schrijven, geen memory, geen edits
- **Vraag toestemming voor memory** — schrijf nooit feedback of memories zonder expliciete developer-goedkeuring
- Review is **ALTIJD read-only** — nooit zelf code wijzigen tijdens review
- Bij twijfel: rapporteer, laat de developer beslissen
- Nieuwe code zonder tests = automatisch ⚠️ WARNING
- Rapporteer altijd ≥5 bevindingen (bij uitstekende code: positieve observaties)
- Severity-classificatie is verplicht bij elke bevinding
- CRITICAL findings → automatisch BLOCK verdict
- Anti-patroon scan is aanvullend op QA Agent checks (geen overlap)

## Contract Referentie

| Component | Doel |
|-----------|------|
| `QAAgent.review_code()` | CR-01..12 code checks |
| `QAAgent.review_docs()` | DR-01..06 doc checks |
| `QAAgent.produce_report()` | QAReport met verdict |
| `adapter.get_review_context()` | Diff + files + anti-patronen |
| `adapter.scan_anti_patterns()` | Node-specifieke violation scan |
| `adapter.get_git_diff()` | Raw git diff |
| `adapter.get_changed_files()` | Gewijzigde bestanden |
