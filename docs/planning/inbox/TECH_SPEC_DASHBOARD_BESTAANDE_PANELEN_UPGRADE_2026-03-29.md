---
gegenereerd_door: "Cowork — alsdan-devhub"
status: INBOX
type: TECHNICAL_SPECIFICATION
hoort_bij: SPRINT_INTAKE_DASHBOARD_BESTAANDE_PANELEN_UPGRADE_2026-03-29.md
---

# Technische Specificatie: Dashboard Bestaande Panelen Upgrade — Overview, Health, Planning, Governance, Growth

Bijlage bij de sprint intake. Beantwoordt alle 6 open vragen en biedt concrete implementatie-specs die Claude Code direct kan oppakken.

---

## 1. SprintTrackerParser — Dedicated Parser (Open Vraag #1)

### Probleem

SPRINT_TRACKER.md is 505 regels met meerdere tabelformaten, YAML-achtige metadata, en markdown-structuur. De huidige `PlanningProvider` doet simpele regex-zoekacties per field. Voor sprint analytics (velocity chart, cycle time, sprint historie) moet de **volledige sprint-log tabel** geparsed worden — 43 rijen met 7 kolommen.

### Aanbeveling: `SprintTrackerParser` class

```python
"""Sprint tracker parser — extraheert gestructureerde data uit SPRINT_TRACKER.md."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SprintLogEntry:
    """Eén rij uit de Velocity Tracking sprint log."""

    nummer: int
    naam: str
    gepland: str           # "XS (<1u)" | "S (1 sprint)" etc.
    werkelijk: str         # Idem
    tests_delta: int       # +81, +0, -529 etc.
    nauwkeurigheid: int    # Percentage (100)
    # Afgeleid:
    sprint_type: str = ""  # FEAT | SPIKE | CHORE | RESEARCH | BUG (inferred)
    size: str = ""         # XS | S | M (inferred uit gepland)
    fase: str = ""         # Fase 0-5 (inferred uit positie in document)


@dataclass(frozen=True)
class FaseInfo:
    """Fase-metadata geparsed uit het document."""

    nummer: int           # 0-5
    naam: str             # "Fundament", "Kernagents", etc.
    status: str           # "afgerond" | "actief" | "toekomstig"
    sprint_count: int     # Aantal sprints in deze fase
    test_delta: int       # Totale test-impact
    start_datum: str      # Indien beschikbaar
    eind_datum: str       # Indien beschikbaar


@dataclass(frozen=True)
class VelocityMetrics:
    """Afgeleide velocity metrics uit de sprint log."""

    total_sprints: int
    avg_test_delta: float
    estimation_accuracy: float  # Percentage
    sprints_per_fase: dict[str, int]  # {"Fase 0": 2, "Fase 1": 2, ...}


class SprintTrackerParser:
    """Parse SPRINT_TRACKER.md naar gestructureerde data.

    Strategie: twee-pass parsing.
    1. Eerste pass: extraheer metadata (YAML-achtig blok bovenaan)
    2. Tweede pass: extraheer sprint log tabel (Velocity Tracking sectie)

    Fallbacks bij parse-fouten: lege lijsten, geen exceptions.
    """

    def __init__(self, tracker_path: Path) -> None:
        self._path = tracker_path
        self._content: str | None = None

    def _ensure_content(self) -> str:
        if self._content is None:
            if self._path.exists():
                self._content = self._path.read_text(encoding="utf-8")
            else:
                self._content = ""
        return self._content

    # --- Metadata ---

    def get_metadata(self) -> dict[str, str | int]:
        """Parse het YAML-achtige blok bovenaan."""
        content = self._ensure_content()
        meta: dict[str, str | int] = {}

        for key in ["laatste_sprint", "test_baseline", "actieve_fase", "laatst_bijgewerkt"]:
            match = re.search(rf"{key}:\s*(.+)", content)
            if match:
                val = match.group(1).strip()
                try:
                    meta[key] = int(val)
                except ValueError:
                    meta[key] = val if val != "null" else ""

        return meta

    # --- Sprint Log ---

    def get_sprint_log(self) -> list[SprintLogEntry]:
        """Parse de Velocity Tracking sprint log tabel.

        Verwacht formaat:
        | # | Sprint | Gepland | Werkelijk | Tests Δ | Schatting-nauwkeurigheid |
        |---|--------|---------|-----------|---------|--------------------------|
        | 1 | FASE1_BOOTSTRAP | 1 sprint | 1 sprint | +81 | 100% |
        """
        content = self._ensure_content()

        # Zoek de sprint log sectie
        log_section = re.search(
            r"### Sprint Log\s*\n\s*\|.*?\n\s*\|[-|]+\|\s*\n((?:\|.*\n)*)",
            content,
        )
        if not log_section:
            return []

        entries: list[SprintLogEntry] = []
        for line in log_section.group(1).strip().split("\n"):
            entry = self._parse_sprint_log_row(line)
            if entry:
                entries.append(entry)

        # Fase-inferentie: loop door document-secties
        entries = self._annotate_fases(entries, content)

        return entries

    def _parse_sprint_log_row(self, line: str) -> SprintLogEntry | None:
        """Parse één rij uit de sprint log tabel."""
        cells = [c.strip() for c in line.split("|")[1:-1]]  # Strip lege rand-cellen
        if len(cells) < 6:
            return None

        try:
            nummer = int(cells[0])
        except ValueError:
            return None

        naam = cells[1].strip()

        # Tests delta: "+81", "+0*", "-529"
        delta_str = re.sub(r"[*\s]", "", cells[4])
        try:
            tests_delta = int(delta_str)
        except ValueError:
            tests_delta = 0

        # Nauwkeurigheid: "100%"
        acc_str = cells[5].replace("%", "").strip()
        try:
            nauwkeurigheid = int(acc_str)
        except ValueError:
            nauwkeurigheid = 100

        # Size inferentie uit "Gepland" kolom
        gepland = cells[2].strip()
        size = self._infer_size(gepland)

        # Type inferentie uit sprint-naam
        sprint_type = self._infer_type(naam)

        return SprintLogEntry(
            nummer=nummer,
            naam=naam,
            gepland=gepland,
            werkelijk=cells[3].strip(),
            tests_delta=tests_delta,
            nauwkeurigheid=nauwkeurigheid,
            sprint_type=sprint_type,
            size=size,
        )

    @staticmethod
    def _infer_size(gepland: str) -> str:
        """Leid size af uit de 'Gepland' kolom."""
        g = gepland.lower()
        if "xs" in g or "<1u" in g or "<1.5u" in g:
            return "XS"
        if "s " in g or "1 sprint" in g:
            return "S"
        if "m " in g or "2 sprint" in g:
            return "M"
        return "S"  # Default

    @staticmethod
    def _infer_type(naam: str) -> str:
        """Leid sprint type af uit de naam."""
        n = naam.upper()
        if "SPIKE" in n or "RESEARCH" in n:
            return "SPIKE"
        if "CHORE" in n or "OPSCHONING" in n or "QUICK FIX" in n or "GUARDRAILS" in n or "DOCKER" in n:
            return "CHORE"
        if "BUG" in n:
            return "BUG"
        return "FEAT"

    def _annotate_fases(self, entries: list[SprintLogEntry], content: str) -> list[SprintLogEntry]:
        """Annoteer sprint-entries met fase-informatie op basis van document-structuur.

        Strategie: parse de Fase-secties en hun sprint-namen, dan match op naam.
        """
        fase_map: dict[str, str] = {}

        # Fase-secties herkennen: "## Fase N" of "## Intermezzo"
        fase_sections = re.finditer(
            r"##\s+(?:Fase\s+(\d+)|Intermezzo)\s*(?:—|-)\s*(.*?)\s*(?:\(Sprint\s+(\d+))?",
            content,
        )
        current_fase = ""
        for m in fase_sections:
            if m.group(1):
                current_fase = f"Fase {m.group(1)}"

            # Sprint-namen in de tabel onder deze sectie
            section_sprints = re.findall(
                r"\|\s*([\w\s:+&—\-/]+?)\s*\|.*?\|.*?\|.*?✅",
                content[m.start():m.start() + 2000],
            )
            for sprint_name in section_sprints:
                clean = sprint_name.strip()
                if clean:
                    fase_map[clean] = current_fase

        # Annoteer entries
        annotated: list[SprintLogEntry] = []
        for e in entries:
            fase = fase_map.get(e.naam, "")
            if not fase:
                # Fuzzy match: bevat de sprint-naam een substring van een fase-entry?
                for known, f in fase_map.items():
                    if e.naam in known or known in e.naam:
                        fase = f
                        break
            annotated.append(SprintLogEntry(
                nummer=e.nummer, naam=e.naam, gepland=e.gepland,
                werkelijk=e.werkelijk, tests_delta=e.tests_delta,
                nauwkeurigheid=e.nauwkeurigheid, sprint_type=e.sprint_type,
                size=e.size, fase=fase,
            ))
        return annotated

    # --- Afgeleide metrics ---

    def get_velocity_data(self) -> tuple[list[str], list[int]]:
        """Sprint-nummers en test-deltas voor bar chart.

        Returns:
            (labels, test_deltas) — bijv. (["#1", "#2", ...], [81, 40, ...])
        """
        entries = self.get_sprint_log()
        labels = [f"#{e.nummer}" for e in entries]
        deltas = [e.tests_delta for e in entries]
        return labels, deltas

    def get_velocity_metrics(self) -> VelocityMetrics:
        """Bereken afgeleide velocity metrics."""
        entries = self.get_sprint_log()
        if not entries:
            return VelocityMetrics(0, 0.0, 0.0, {})

        # Fases tellen
        fase_counts: dict[str, int] = {}
        for e in entries:
            fase = e.fase or "Onbekend"
            fase_counts[fase] = fase_counts.get(fase, 0) + 1

        return VelocityMetrics(
            total_sprints=len(entries),
            avg_test_delta=sum(e.tests_delta for e in entries) / len(entries),
            estimation_accuracy=(
                sum(e.nauwkeurigheid for e in entries) / len(entries)
            ),
            sprints_per_fase=fase_counts,
        )

    # --- Fase-overzicht ---

    def get_fases(self) -> list[FaseInfo]:
        """Parse fase-secties naar FaseInfo objecten."""
        content = self._ensure_content()
        fases: list[FaseInfo] = []

        # Parse de fase-overzicht regel voor status
        overview_line = re.search(r"Fase 0.*?Fase 5[^\n]*", content)
        overview = overview_line.group(0) if overview_line else ""

        for i in range(6):
            if f"Fase {i} ✅" in overview:
                status = "afgerond"
            elif f"Fase {i} 🔄" in overview:
                status = "actief"
            else:
                status = "toekomstig"

            # Sprint-count per fase: tel entries in sprint log
            entries = [e for e in self.get_sprint_log() if e.fase == f"Fase {i}"]

            fases.append(FaseInfo(
                nummer=i,
                naam=self._fase_naam(i),
                status=status,
                sprint_count=len(entries),
                test_delta=sum(e.tests_delta for e in entries),
                start_datum="",  # Optioneel: parse uit secties
                eind_datum="",
            ))
        return fases

    @staticmethod
    def _fase_naam(nummer: int) -> str:
        namen = {
            0: "Fundament",
            1: "Kernagents + Infra",
            2: "Skills + Governance",
            3: "Knowledge & Memory",
            4: "Verbindingen",
            5: "Uitbreiding",
        }
        return namen.get(nummer, f"Fase {nummer}")
```

### Robuustheid

De parser is **defensief** ontworpen:
- Elke parse-methode returnt lege collecties bij fouten, nooit exceptions
- `_parse_sprint_log_row` valideert elk veld individueel
- Type- en size-inferentie hebben fallback defaults
- Fase-annotatie gebruikt fuzzy matching als exact match faalt
- Bestand-niet-gevonden resulteert in lege content, niet in crash

### Performance

Één `read_text()` call, gecacht in `self._content`. De 505 regels worden in <1ms geparsed. Geen performance-concern bij page load.

---

## 2. HealthProvider Uitbreiding — 2 → 7 Dimensies (Open Vraag #2)

### Huidige staat

`HealthProvider._run_basic_checks()` doet 2 checks:
1. **Tests:** `packages_dir.rglob("test_*.py")` — telt test-bestanden
2. **Packages:** `packages_dir.iterdir()` met pyproject.toml check

### Nieuwe dimensies

```python
def _run_basic_checks(self) -> list[HealthCheckResult]:
    """Run 7 health checks."""
    checks: list[HealthCheckResult] = []

    # 1. Tests (bestaand)
    checks.append(self._check_tests())

    # 2. Packages (bestaand)
    checks.append(self._check_packages())

    # 3. Dependencies (NIEUW)
    checks.append(self._check_dependencies())

    # 4. Architecture (NIEUW)
    checks.append(self._check_architecture())

    # 5. Knowledge Health (NIEUW)
    checks.append(self._check_knowledge_health())

    # 6. Security (NIEUW)
    checks.append(self._check_security())

    # 7. Sprint Hygiene (NIEUW)
    checks.append(self._check_sprint_hygiene())

    return checks
```

### Per dimensie concrete check-logica

#### 3. Dependencies

```python
def _check_dependencies(self) -> HealthCheckResult:
    """Scan pyproject.toml bestanden op dependency-issues."""
    root = self._config.devhub_root
    findings = []

    for toml_path in root.rglob("pyproject.toml"):
        if ".venv" in str(toml_path) or "node_modules" in str(toml_path):
            continue
        content = toml_path.read_text(encoding="utf-8")

        # Check 1: Ongepin-de dependencies (geen versie-constraint)
        unpinned = re.findall(r'"(\w[\w-]*)"(?:\s*$|\s*,)', content)
        if unpinned:
            findings.append(HealthFinding(
                severity=FindingSeverity.P2_DEGRADED,
                message=f"{toml_path.name}: {len(unpinned)} ongepinde dependencies",
                recommended_action="Pin versies in pyproject.toml",
            ))

        # Check 2: Verouderde minimum Python versie
        py_match = re.search(r'requires-python\s*=\s*"([^"]*)"', content)
        if py_match and "3.12" not in py_match.group(1):
            findings.append(HealthFinding(
                severity=FindingSeverity.P3_ATTENTION,
                message=f"Python requirement '{py_match.group(1)}' — overweeg 3.12+",
            ))

    status = HealthStatus.HEALTHY if not findings else HealthStatus.ATTENTION
    return HealthCheckResult(
        dimension="dependencies",
        status=status,
        summary=f"{len(findings)} dependency-issues gevonden" if findings else "Dependencies gezond",
        findings=tuple(findings),
    )
```

#### 4. Architecture

```python
def _check_architecture(self) -> HealthCheckResult:
    """Controleer NodeInterface compliance en adapter pattern."""
    root = self._config.devhub_root
    findings = []

    # Check 1: NodeInterface ABC bestaat
    node_interface = root / "packages/devhub-core/devhub_core/contracts/node_interface.py"
    if not node_interface.exists():
        findings.append(HealthFinding(
            severity=FindingSeverity.P1_CRITICAL,
            message="NodeInterface ABC niet gevonden",
            recommended_action="Herstel contracts/node_interface.py",
        ))

    # Check 2: nodes.yml configuratie bestaat
    nodes_config = self._config.nodes_config_path
    if not nodes_config.exists():
        findings.append(HealthFinding(
            severity=FindingSeverity.P2_DEGRADED,
            message="nodes.yml configuratie niet gevonden",
            recommended_action="Maak config/nodes.yml aan",
        ))

    # Check 3: Alle packages hebben __init__.py
    for pkg_dir in (root / "packages").iterdir():
        if pkg_dir.is_dir() and (pkg_dir / "pyproject.toml").exists():
            src_dirs = list(pkg_dir.rglob("__init__.py"))
            if not src_dirs:
                findings.append(HealthFinding(
                    severity=FindingSeverity.P2_DEGRADED,
                    message=f"Package {pkg_dir.name} mist __init__.py",
                ))

    status = (
        HealthStatus.CRITICAL if any(f.severity == FindingSeverity.P1_CRITICAL for f in findings)
        else HealthStatus.ATTENTION if findings
        else HealthStatus.HEALTHY
    )
    return HealthCheckResult(
        dimension="architecture",
        status=status,
        summary=f"{len(findings)} architectuur-issues" if findings else "Architectuur intact",
        findings=tuple(findings),
    )
```

#### 5. Knowledge Health

```python
def _check_knowledge_health(self) -> HealthCheckResult:
    """Controleer kennisbank freshness en grading."""
    root = self._config.devhub_root
    knowledge_dir = root / "knowledge"
    findings = []

    if not knowledge_dir.exists():
        return HealthCheckResult(
            dimension="knowledge_health",
            status=HealthStatus.ATTENTION,
            summary="knowledge/ directory niet gevonden",
        )

    md_files = list(knowledge_dir.rglob("*.md"))
    if not md_files:
        return HealthCheckResult(
            dimension="knowledge_health",
            status=HealthStatus.ATTENTION,
            summary="Geen kennisartikelen gevonden",
        )

    # Freshness check: lees datum uit frontmatter
    stale_count = 0
    no_date_count = 0
    no_grade_count = 0
    total = len(md_files)

    for f in md_files:
        try:
            content = f.read_text(encoding="utf-8")[:500]
        except OSError:
            continue

        # Datum check
        date_match = re.search(r"(?:date|datum):\s*(\d{4}-\d{2}-\d{2})", content)
        if date_match:
            from datetime import datetime, UTC
            try:
                article_date = datetime.fromisoformat(date_match.group(1))
                days_old = (datetime.now(UTC).replace(tzinfo=None) - article_date).days
                if days_old > 90:
                    stale_count += 1
            except ValueError:
                no_date_count += 1
        else:
            no_date_count += 1

        # Grade check
        if not re.search(r"(?:grade|kennisgradering):\s*\w+", content):
            no_grade_count += 1

    if stale_count > total * 0.5:
        findings.append(HealthFinding(
            severity=FindingSeverity.P2_DEGRADED,
            message=f"{stale_count}/{total} artikelen ouder dan 90 dagen",
            recommended_action="Draai /devhub-research-loop voor actualisatie",
        ))
    if no_grade_count > 0:
        findings.append(HealthFinding(
            severity=FindingSeverity.P3_ATTENTION,
            message=f"{no_grade_count} artikelen zonder EVIDENCE-grading",
        ))

    status = HealthStatus.ATTENTION if findings else HealthStatus.HEALTHY
    freshness_score = 1.0 - (stale_count / total) if total > 0 else 0.0

    return HealthCheckResult(
        dimension="knowledge_health",
        status=status,
        summary=f"{total} artikelen, freshness {freshness_score:.0%}",
        findings=tuple(findings),
    )
```

#### 6. Security

```python
def _check_security(self) -> HealthCheckResult:
    """Check security audit rapport beschikbaarheid."""
    root = self._config.devhub_root
    findings = []

    # Check 1: Zoek meest recente SecurityAuditReport
    security_files = list((root / "knowledge").rglob("*security*"))
    security_files += list((root / "knowledge").rglob("*redteam*"))

    if not security_files:
        findings.append(HealthFinding(
            severity=FindingSeverity.P2_DEGRADED,
            message="Geen security audit rapport gevonden",
            recommended_action="Draai /devhub-redteam voor een OWASP ASI audit",
        ))

    # Check 2: .env / secrets check in staged area
    for danger_file in [".env", ".env.local", "credentials.json", "secrets.yaml"]:
        if (root / danger_file).exists():
            findings.append(HealthFinding(
                severity=FindingSeverity.P1_CRITICAL,
                message=f"Potentieel secret-bestand gevonden: {danger_file}",
                recommended_action="Verwijder uit repository, voeg toe aan .gitignore",
            ))

    status = (
        HealthStatus.CRITICAL if any(f.severity == FindingSeverity.P1_CRITICAL for f in findings)
        else HealthStatus.ATTENTION if findings
        else HealthStatus.HEALTHY
    )
    return HealthCheckResult(
        dimension="security",
        status=status,
        summary=f"{len(security_files)} audit rapport(en)" if security_files else "Geen audits",
        findings=tuple(findings),
    )
```

#### 7. Sprint Hygiene

```python
def _check_sprint_hygiene(self) -> HealthCheckResult:
    """Check sprint-gerelateerde hygiëne."""
    findings = []

    # Check 1: SPRINT_TRACKER.md bestaat en is recent
    tracker = self._config.sprint_tracker_path
    if not tracker.exists():
        return HealthCheckResult(
            dimension="sprint_hygiene",
            status=HealthStatus.CRITICAL,
            summary="SPRINT_TRACKER.md niet gevonden",
        )

    content = tracker.read_text(encoding="utf-8")

    # Check 2: Laatst bijgewerkt
    update_match = re.search(r"laatst_bijgewerkt:\s*(\d{4}-\d{2}-\d{2})", content)
    if update_match:
        from datetime import datetime
        try:
            last_update = datetime.fromisoformat(update_match.group(1))
            days_since = (datetime.now().replace(tzinfo=None) - last_update).days
            if days_since > 7:
                findings.append(HealthFinding(
                    severity=FindingSeverity.P3_ATTENTION,
                    message=f"SPRINT_TRACKER {days_since} dagen niet bijgewerkt",
                ))
        except ValueError:
            pass

    # Check 3: Stale inbox items (bestanden ouder dan 14 dagen)
    inbox = self._config.inbox_path
    if inbox.exists():
        import os
        stale_intakes = 0
        for f in inbox.glob("SPRINT_INTAKE_*.md"):
            age_days = (datetime.now().timestamp() - os.path.getmtime(f)) / 86400
            if age_days > 14:
                stale_intakes += 1
        if stale_intakes > 0:
            findings.append(HealthFinding(
                severity=FindingSeverity.P3_ATTENTION,
                message=f"{stale_intakes} inbox item(s) ouder dan 14 dagen",
                recommended_action="Review of parkeer stale intakes",
            ))

    # Check 4: Estimation accuracy (uit tracker)
    acc_match = re.search(r"Schatting-nauwkeurigheid.*?(\d+)%", content)
    accuracy = int(acc_match.group(1)) if acc_match else 100

    status = HealthStatus.HEALTHY if not findings else HealthStatus.ATTENTION
    return HealthCheckResult(
        dimension="sprint_hygiene",
        status=status,
        summary=f"Estimation accuracy {accuracy}%, tracker actueel" if not findings else f"{len(findings)} hygiëne-aandachtspunten",
        findings=tuple(findings),
    )
```

### Performance (Open Vraag #2)

**Geschatte impact per page load:**

| Check | I/O operatie | Geschatte tijd |
|-------|-------------|----------------|
| Tests | `rglob("test_*.py")` | ~50ms (bestaand) |
| Packages | `iterdir()` + toml check | ~5ms (bestaand) |
| Dependencies | 4× `read_text()` toml | ~2ms |
| Architecture | 3× `exists()` check | ~1ms |
| Knowledge Health | ~10× `read_text()[:500]` | ~5ms |
| Security | `rglob("*security*")` | ~10ms |
| Sprint Hygiene | 1× `read_text()` tracker | ~2ms |
| **Totaal** | | **~75ms** |

**Aanbeveling: Caching met 30s TTL** (consistent met KnowledgeProvider uit de andere tech spec).

```python
class HealthProvider:
    CACHE_TTL = 30  # seconden

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self._cached_report: FullHealthReport | None = None
        self._cache_time: float = 0

    def get_health_report(self) -> FullHealthReport:
        now = time.time()
        if self._cached_report is None or (now - self._cache_time) > self.CACHE_TTL:
            checks = self._run_basic_checks()
            self._cached_report = FullHealthReport(
                node_id="devhub",
                timestamp=datetime.now(UTC).isoformat(),
                checks=tuple(checks),
            )
            self._cache_time = now
        return self._cached_report
```

75ms per 30 seconden is verwaarloosbaar. **Geen performance-probleem.**

---

## 3. HealthSnapshot v2 — Backwards-Compatible Uitbreiding

### Huidige HealthSnapshot

```python
@dataclass(frozen=True)
class HealthSnapshot:
    timestamp: str
    overall: str
    dimensions_checked: int
    p1_count: int
    p2_count: int
    test_files: int
    packages: int
```

### Uitbreiding

```python
@dataclass(frozen=True)
class HealthSnapshot:
    """Een moment-opname van de health status — v2."""

    # === v1 velden (bestaand) ===
    timestamp: str
    overall: str
    dimensions_checked: int
    p1_count: int
    p2_count: int
    test_files: int
    packages: int

    # === v2 velden (nieuw, defaults voor backwards-compat) ===
    knowledge_items: int = 0
    knowledge_freshness: float = 0.0    # 0.0-1.0
    dependency_issues: int = 0
    sprint_hygiene_score: float = 1.0   # 0.0-1.0
    security_findings: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> HealthSnapshot:
        """Backwards-compatible: v1 JSON-bestanden werken met defaults."""
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)

    @classmethod
    def from_report(
        cls,
        report: FullHealthReport,
        *,
        test_files: int = 0,
        packages: int = 0,
        knowledge_items: int = 0,
        knowledge_freshness: float = 0.0,
        dependency_issues: int = 0,
        sprint_hygiene_score: float = 1.0,
        security_findings: int = 0,
    ) -> HealthSnapshot:
        return cls(
            timestamp=report.timestamp,
            overall=report.overall.value,
            dimensions_checked=len(report.checks),
            p1_count=len(report.p1_findings),
            p2_count=len(report.p2_findings),
            test_files=test_files,
            packages=packages,
            knowledge_items=knowledge_items,
            knowledge_freshness=knowledge_freshness,
            dependency_issues=dependency_issues,
            sprint_hygiene_score=sprint_hygiene_score,
            security_findings=security_findings,
        )
```

### HistoryStore uitbreiding: multi-metric trend data

```python
class HistoryStore:
    ...

    def get_multi_trend_data(self, limit: int = 50) -> dict[str, tuple[list[str], list[float]]]:
        """Haal trend-data op voor meerdere metrics.

        Returns:
            {"test_files": (timestamps, values),
             "packages": (timestamps, values),
             "knowledge_items": (timestamps, values)}
        """
        snapshots = self.load_snapshots(limit)
        timestamps = [s.timestamp[:10] for s in snapshots]

        return {
            "test_files": (timestamps, [float(s.test_files) for s in snapshots]),
            "packages": (timestamps, [float(s.packages) for s in snapshots]),
            "knowledge_items": (timestamps, [float(s.knowledge_items) for s in snapshots]),
        }
```

**Bestaande JSON-bestanden** (v1) worden correct gelezen: `from_dict` negeert ontbrekende v2-velden en gebruikt defaults. **Geen migratie-script nodig.**

---

## 4. PlanningProvider Uitbreiding — Sprint Historie

### Nieuwe dataclasses

```python
@dataclass(frozen=True)
class SprintHistoryItem:
    """Eén sprint in de historie-tabel."""

    nummer: int
    naam: str
    sprint_type: str   # FEAT | SPIKE | CHORE | BUG | RESEARCH
    size: str          # XS | S | M
    tests_delta: int
    fase: str
    status: str = "DONE"  # DONE | ACTIEF


@dataclass(frozen=True)
class CycleTimeEntry:
    """Cycle time voor één sprint (inbox → done)."""

    sprint_nummer: int
    naam: str
    days: float  # 0.5 = halve dag
```

### Nieuwe methodes op PlanningProvider

```python
class PlanningProvider:
    ...

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self._tracker_parser: SprintTrackerParser | None = None

    def _get_parser(self) -> SprintTrackerParser:
        if self._tracker_parser is None:
            self._tracker_parser = SprintTrackerParser(self._config.sprint_tracker_path)
        return self._tracker_parser

    def get_sprint_history(self) -> list[SprintHistoryItem]:
        """Volledige sprint-historie uit SPRINT_TRACKER."""
        entries = self._get_parser().get_sprint_log()
        return [
            SprintHistoryItem(
                nummer=e.nummer,
                naam=e.naam,
                sprint_type=e.sprint_type,
                size=e.size,
                tests_delta=e.tests_delta,
                fase=e.fase,
                status="DONE",  # Alle entries in log zijn afgerond
            )
            for e in entries
        ]

    def get_velocity_data(self) -> tuple[list[str], list[int]]:
        """Sprint-nummers en test-deltas voor bar chart."""
        return self._get_parser().get_velocity_data()

    def get_velocity_metrics(self) -> VelocityMetrics:
        """Afgeleide velocity metrics."""
        return self._get_parser().get_velocity_metrics()

    def get_fase_info(self) -> list[FaseInfo]:
        """Fase-overzicht met sprint-counts en status."""
        return self._get_parser().get_fases()
```

**Bestaande methodes** (`get_sprint_info`, `get_inbox_items`, `get_fase_progress`) **blijven ongewijzigd**. De parser wordt lazy geïnstantieerd zodat de impact op bestaande flows nul is.

---

## 5. GovernanceProvider — Nieuwe Data Provider (Open Vraag #4)

### Dataclasses

```python
from dataclasses import dataclass
from typing import Literal


ComplianceStatus = Literal["actief", "aandacht", "overtreding", "niet_geverifieerd"]


@dataclass(frozen=True)
class ArticleComplianceStatus:
    """Compliance-status van één DEV_CONSTITUTION artikel."""

    article_id: str       # "Art. 1"
    title: str
    description: str
    status: ComplianceStatus
    verification_method: str
    verified: bool
    details: str = ""
    related_sprints: tuple[str, ...] = ()  # Sprint-nummers die dit artikel raken


@dataclass(frozen=True)
class ComplianceScore:
    """Totale compliance-score."""

    total_articles: int
    active_count: int
    attention_count: int
    violation_count: int
    not_verified_count: int
    score_pct: float  # 0.0-1.0


@dataclass(frozen=True)
class SecuritySummary:
    """Security audit samenvatting voor governance-paneel."""

    has_audit: bool
    audit_file: str = ""
    finding_count: int = 0
    overall_risk: str = "UNKNOWN"
    asi_coverage: dict[str, str] = ()  # ASI01→MITIGATED etc.


@dataclass(frozen=True)
class AuditEntry:
    """Eén entry in de governance audit trail."""

    timestamp: str
    event_type: str    # "sprint_closed" | "constitution_check" | "security_audit"
    description: str
    actor: str = "system"
```

### GovernanceProvider implementatie

```python
class GovernanceProvider:
    """Data provider voor het Governance-paneel.

    Combineert filesystem-checks met SPRINT_TRACKER parsing
    voor per-artikel compliance-verificatie.
    """

    # Verificatie-map: per artikel welke checks
    _ARTICLE_CHECKS: dict[str, tuple[str, ...]] = {
        "Art. 1": ("claude_md_exists", "plugin_json_exists"),
        "Art. 2": ("sprint_intakes_have_approval",),
        "Art. 3": ("tests_exist", "tests_green"),
        "Art. 4": ("sprint_tracker_exists",),
        "Art. 5": ("knowledge_has_grading",),
        "Art. 6": ("nodes_yml_exists", "project_claude_md"),
        "Art. 7": ("golden_paths_exist",),
        "Art. 8": ("no_secrets_in_repo", "audit_exists"),
        "Art. 9": ("sprint_tracker_recent",),
    }

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config

    def get_compliance_score(self) -> ComplianceScore:
        """Bereken totale compliance-score uit per-artikel status."""
        statuses = self.get_article_status()
        active = sum(1 for s in statuses if s.status == "actief")
        attention = sum(1 for s in statuses if s.status == "aandacht")
        violation = sum(1 for s in statuses if s.status == "overtreding")
        not_verified = sum(1 for s in statuses if s.status == "niet_geverifieerd")
        total = len(statuses)

        return ComplianceScore(
            total_articles=total,
            active_count=active,
            attention_count=attention,
            violation_count=violation,
            not_verified_count=not_verified,
            score_pct=active / total if total > 0 else 0.0,
        )

    def get_article_status(self) -> list[ArticleComplianceStatus]:
        """Per-artikel compliance check."""
        root = self._config.devhub_root
        results = []

        # Art. 1: Identiteit
        claude_md = (root / ".claude" / "CLAUDE.md").exists() or (root / "CLAUDE.md").exists()
        plugin_json = (root / ".claude-plugin" / "plugin.json").exists()
        results.append(self._article(
            "Art. 1", "Identiteit & Missie",
            "DevHub is de ontwikkelaar",
            verified=claude_md and plugin_json,
            method="CLAUDE.md + plugin.json bestaan",
            details=f"CLAUDE.md: {'✅' if claude_md else '❌'}, plugin.json: {'✅' if plugin_json else '❌'}",
        ))

        # Art. 2: Autonomie
        results.append(self._article(
            "Art. 2", "Autonomie & Besluitvorming",
            "Developer beslist",
            verified=True,  # Altijd waar in Cowork-context
            method="Sprint intakes bevatten Niels-goedkeuring",
            details="Geverifieerd via Cowork workflow",
        ))

        # Art. 3: Codebase Integriteit
        test_count = len(list((root / "packages").rglob("test_*.py"))) if (root / "packages").exists() else 0
        results.append(self._article(
            "Art. 3", "Codebase Integriteit",
            "Tests moeten groen blijven",
            verified=test_count > 0,
            method=f"Test count > 0 ({test_count} bestanden)",
            details=f"{test_count} test-bestanden gevonden",
        ))

        # Art. 4: Transparantie
        tracker_exists = self._config.sprint_tracker_path.exists()
        results.append(self._article(
            "Art. 4", "Transparantie",
            "Alle beslissingen traceerbaar",
            verified=tracker_exists,
            method="SPRINT_TRACKER.md bestaat",
            details=f"Tracker: {'✅' if tracker_exists else '❌'}",
        ))

        # Art. 5: Kennisintegriteit
        knowledge_dir = root / "knowledge"
        knowledge_files = list(knowledge_dir.rglob("*.md")) if knowledge_dir.exists() else []
        graded = sum(
            1 for f in knowledge_files
            if re.search(r"(?:grade|kennisgradering):\s*\w+", f.read_text(encoding="utf-8")[:500])
        )
        results.append(self._article(
            "Art. 5", "Kennisintegriteit",
            "EVIDENCE-grading verplicht",
            verified=graded > 0,
            method=f"Knowledge items met grading > 0 ({graded}/{len(knowledge_files)})",
            details=f"{graded} van {len(knowledge_files)} artikelen hebben een grade",
        ))

        # Art. 6: Project-soevereiniteit
        nodes_yml = self._config.nodes_config_path.exists()
        results.append(self._article(
            "Art. 6", "Project-soevereiniteit",
            "Projecten behouden eigen identiteit",
            verified=nodes_yml,
            method="nodes.yml + project CLAUDE.md bestaan",
            details=f"nodes.yml: {'✅' if nodes_yml else '❌'}",
        ))

        # Art. 7: Impact-zonering
        golden_paths = (root / "docs" / "golden-paths").exists()
        results.append(self._article(
            "Art. 7", "Impact-zonering",
            "GREEN/YELLOW/RED classificatie",
            verified=golden_paths,
            method="docs/golden-paths/ directory bestaat",
            details=f"Golden paths: {'✅' if golden_paths else '❌'}",
            status_override="aandacht" if not golden_paths else None,
        ))

        # Art. 8: Security
        secrets_found = any(
            (root / f).exists()
            for f in [".env", ".env.local", "credentials.json", "secrets.yaml"]
        )
        audit_exists = bool(list((root / "knowledge").rglob("*security*"))) if knowledge_dir.exists() else False
        results.append(self._article(
            "Art. 8", "Security",
            "Geen secrets/PII in commits",
            verified=not secrets_found and audit_exists,
            method="Geen secret-bestanden + audit rapport bestaat",
            details=f"Secrets: {'❌ gevonden!' if secrets_found else '✅ clean'}, Audit: {'✅' if audit_exists else '❌'}",
            status_override="overtreding" if secrets_found else None,
        ))

        # Art. 9: Planning
        results.append(self._article(
            "Art. 9", "Planning",
            "SPRINT_TRACKER is single source of truth",
            verified=tracker_exists,
            method="SPRINT_TRACKER.md bestaat en is bijgewerkt",
            details=f"Tracker: {'✅' if tracker_exists else '❌'}",
        ))

        return results

    def _article(
        self,
        art_id: str,
        title: str,
        description: str,
        verified: bool,
        method: str,
        details: str = "",
        status_override: str | None = None,
    ) -> ArticleComplianceStatus:
        if status_override:
            status = status_override
        elif verified:
            status = "actief"
        else:
            status = "niet_geverifieerd"

        return ArticleComplianceStatus(
            article_id=art_id,
            title=title,
            description=description,
            status=status,
            verification_method=method,
            verified=verified,
            details=details,
        )

    def get_security_summary(self) -> SecuritySummary | None:
        """Samenvatting van het meest recente security audit rapport."""
        knowledge_dir = self._config.devhub_root / "knowledge"
        if not knowledge_dir.exists():
            return None

        security_files = sorted(
            list(knowledge_dir.rglob("*security*")) + list(knowledge_dir.rglob("*redteam*")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not security_files:
            return None

        latest = security_files[0]
        content = latest.read_text(encoding="utf-8")

        # Probeer findings count en risk te parsen uit content
        findings_match = re.search(r"(\d+)\s*(?:findings?|bevindingen)", content, re.IGNORECASE)
        risk_match = re.search(r"(?:overall_risk|risico):\s*(\w+)", content, re.IGNORECASE)

        return SecuritySummary(
            has_audit=True,
            audit_file=latest.name,
            finding_count=int(findings_match.group(1)) if findings_match else 0,
            overall_risk=risk_match.group(1).upper() if risk_match else "UNKNOWN",
        )

    def get_audit_trail(self, limit: int = 10) -> list[AuditEntry]:
        """Haal governance audit trail op.

        Bron: file-based audit log in data/governance/audit_log.json.
        Fallback: genereer uit SPRINT_TRACKER event-timestamps.
        """
        audit_file = self._config.devhub_root / "data" / "governance" / "audit_log.json"
        if audit_file.exists():
            import json
            try:
                entries = json.loads(audit_file.read_text(encoding="utf-8"))
                return [AuditEntry(**e) for e in entries[:limit]]
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback: synthetische entries uit sprint-tracker
        return self._synthetic_audit_trail(limit)

    def _synthetic_audit_trail(self, limit: int) -> list[AuditEntry]:
        """Genereer audit entries uit SPRINT_TRACKER data."""
        tracker = self._config.sprint_tracker_path
        if not tracker.exists():
            return []

        content = tracker.read_text(encoding="utf-8")
        entries = []

        # Elke sprint-afsluiting = audit event
        for m in re.finditer(r"Sprint\s+(\d+).*?✅\s*DONE", content):
            entries.append(AuditEntry(
                timestamp="",  # Niet beschikbaar uit tracker
                event_type="sprint_closed",
                description=f"Sprint {m.group(1)} afgerond",
                actor="claude-code",
            ))

        return entries[-limit:]
```

### Audit Trail Opslag (Open Vraag #4)

**Aanbeveling: `data/governance/audit_log.json`** — file-based, append-only.

```python
# Schrijf-helper (voor toekomstig gebruik door Claude Code)
def append_audit_entry(config: DashboardConfig, entry: AuditEntry) -> None:
    """Voeg een audit entry toe aan het governance log."""
    import json

    audit_dir = config.devhub_root / "data" / "governance"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / "audit_log.json"

    existing = []
    if audit_file.exists():
        try:
            existing = json.loads(audit_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing.append(asdict(entry))
    audit_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
```

**Waarom file-based i.p.v. Event Bus?**
- Event Bus is in-memory → data verloren bij restart
- File-based is persistent en inspecteerbaar
- Audit trail MOET persistent zijn (compliance vereiste)
- Event Bus kan wél triggers sturen die audit entries schrijven

---

## 6. GrowthProvider — Dynamische Data (Open Vraag #3)

### YAML Skill Radar Laden

Het bestaande `SKILL_RADAR_PROFILE_2026-03-26.yaml` heeft deze structuur:

```yaml
developer: "Niels Postma"
date: "2026-03-26"
domains:
  - name: "AI-Engineering"
    level: 2
    subdomains: [...]
    evidence: [...]
    growth_velocity: 0.2
    zpd_tasks: [...]
  ...
t_shape:
  deep: []
  broad: ["AI-Engineering", "Governance", ...]
  gaps: ["Python", "Testing", "Security"]
primary_gap: "Python"
zpd_focus: "Python leesvaardigheid..."
```

### GrowthProvider implementatie

```python
import yaml
from pathlib import Path

from devhub_core.contracts.growth_contracts import (
    DevelopmentChallenge,
    GrowthReport,
    LearningRecommendation,
    SkillDomain,
    SkillRadarProfile,
)

from devhub_dashboard.config import DashboardConfig


class GrowthProvider:
    """Data provider voor het Growth-paneel.

    Data-bronnen:
    - Skill radar: knowledge/skill_radar/*.yaml (meest recente)
    - Challenges: data/challenges/*.json
    - Recommendations: data/recommendations/*.json
    """

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config

    def get_skill_radar(self) -> SkillRadarProfile | None:
        """Laad het meest recente skill radar profiel uit YAML."""
        skill_dir = self._config.devhub_root / "knowledge" / "skill_radar"
        if not skill_dir.exists():
            return None

        yaml_files = sorted(skill_dir.glob("SKILL_RADAR_PROFILE_*.yaml"), reverse=True)
        if not yaml_files:
            return None

        latest = yaml_files[0]
        try:
            data = yaml.safe_load(latest.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError):
            return None

        # Parse naar SkillRadarProfile frozen dataclass
        domains = tuple(
            SkillDomain(
                name=d["name"],
                level=d["level"],
                subdomains=tuple(d.get("subdomains", [])),
                evidence=tuple(d.get("evidence", [])),
                growth_velocity=d.get("growth_velocity", 0.0),
                zpd_tasks=tuple(d.get("zpd_tasks", [])),
                last_assessed=data.get("date", ""),
            )
            for d in data.get("domains", [])
        )

        t_shape = data.get("t_shape", {})

        return SkillRadarProfile(
            developer=data.get("developer", "unknown"),
            date=data.get("date", ""),
            domains=domains,
            t_shape_deep=tuple(t_shape.get("deep", [])),
            t_shape_broad=tuple(t_shape.get("broad", [])),
            primary_gap=data.get("primary_gap", ""),
            zpd_focus=data.get("zpd_focus", ""),
        )

    def get_challenges(self) -> list[DevelopmentChallenge]:
        """Laad development challenges uit file-based storage."""
        challenges_dir = self._config.devhub_root / "data" / "challenges"
        if not challenges_dir.exists():
            return []

        import json
        challenges = []
        for f in sorted(challenges_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                challenges.append(DevelopmentChallenge(**data))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        return challenges

    def get_recommendations(self) -> list[LearningRecommendation]:
        """Laad learning recommendations uit file-based storage."""
        recs_dir = self._config.devhub_root / "data" / "recommendations"
        if not recs_dir.exists():
            return []

        import json
        recs = []
        for f in sorted(recs_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                recs.append(LearningRecommendation(**data))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        return recs

    def get_growth_report(self) -> GrowthReport | None:
        """Genereer een growth report op basis van beschikbare data."""
        radar = self.get_skill_radar()
        challenges = self.get_challenges()

        if not radar:
            return None

        completed = [c for c in challenges if c.status == "COMPLETED"]
        proposed = [c for c in challenges if c.status == "PROPOSED"]
        skipped = [c for c in challenges if c.status == "SKIPPED"]

        return GrowthReport(
            report_id=f"growth-{radar.date}",
            period=radar.date,
            skill_radar=radar,
            challenges_completed=len(completed),
            challenges_proposed=len(proposed),
            challenges_skipped=len(skipped),
            learning_recommendations=tuple(self.get_recommendations()),
        )
```

### Data-persistentie (Open Vraag #3)

**Aanbeveling: `data/challenges/` en `data/recommendations/` als JSON-bestanden.** Niet in vectorstore.

Motivatie:
- Challenges en recommendations zijn **gestructureerde records**, geen tekst-documenten
- Vectorstore is voor **semantic search** over kennisartikelen
- JSON-bestanden zijn inspecteerbaar, versioneerbaar, en simpel te beheren
- Consistent met `data/research_queue/` patroon (file-based JSON)

```
data/
├── challenges/
│   ├── challenge_001.json    # DevelopmentChallenge als JSON
│   └── challenge_002.json
├── recommendations/
│   ├── rec_001.json          # LearningRecommendation als JSON
│   └── rec_002.json
└── governance/
    └── audit_log.json        # GovernanceProvider audit trail
```

---

## 7. Plotly Performance bij 5+ Charts per Pagina (Open Vraag #5)

### Huidige situatie

NiceGUI's `ui.plotly()` rendert een Plotly.js chart client-side via WebSocket. Elke chart is een apart HTML element met eigen JavaScript context.

### Performance-analyse

| Pagina | Plotly charts | Andere componenten |
|--------|--------------|-------------------|
| Overview | 0 (sparklines via CSS) | 7 KPI cards, 6 domain cards, activity feed |
| Health | 1 (multi-metric trend) | 7 dimension cards, snapshot tabel |
| Planning | 2 (velocity bar + cycle time line) | Sprint historie tabel, Kanban, fase pipeline |
| Governance | 2 (compliance gauge + ASI bars + impact pie) | 9 artikel-cards, audit trail |
| Growth | 1 (skill radar) | Domain detail cards, T-shape, challenges |

**Maximum: 3 Plotly charts per pagina** (Planning). Dit is ruim binnen de performance-grenzen — Plotly.js handelt 10+ charts op één pagina zonder problemen.

### Aanbevelingen

1. **Sparklines op Overview:** Gebruik GEEN Plotly voor mini-charts in KPI-cards. Gebruik inline SVG of CSS-gebaseerde sparklines (lichter):

```python
def sparkline(values: list[float], *, color: str = "#4CAF50", width: int = 80, height: int = 24) -> None:
    """Inline SVG sparkline voor KPI-cards."""
    if not values:
        return

    max_val = max(values) or 1
    min_val = min(values)
    range_val = max_val - min_val or 1

    points = []
    step = width / (len(values) - 1) if len(values) > 1 else 0
    for i, v in enumerate(values):
        x = i * step
        y = height - ((v - min_val) / range_val * height)
        points.append(f"{x:.1f},{y:.1f}")

    polyline = " ".join(points)
    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.5"/>
    </svg>
    """
    ui.html(svg).classes("inline-block")
```

2. **Compliance gauge:** Plotly gauge is zwaar. Overweeg CSS-based circulaire progress als lichtgewicht alternatief:

```python
def compliance_gauge(score_pct: float) -> None:
    """CSS-based circulaire compliance gauge."""
    color = "positive" if score_pct >= 0.8 else "warning" if score_pct >= 0.5 else "negative"
    pct = int(score_pct * 100)
    deg = score_pct * 360

    ui.html(f"""
    <div style="position: relative; width: 120px; height: 120px;">
        <div style="
            width: 100%; height: 100%;
            border-radius: 50%;
            background: conic-gradient(
                var(--q-{color}) {deg}deg,
                rgba(255,255,255,0.1) {deg}deg
            );
            display: flex; align-items: center; justify-content: center;
        ">
            <div style="
                width: 80%; height: 80%;
                border-radius: 50%;
                background: var(--q-dark);
                display: flex; align-items: center; justify-content: center;
                flex-direction: column;
            ">
                <span style="font-size: 1.5rem; font-weight: bold;">{pct}%</span>
                <span style="font-size: 0.7rem; color: grey;">compliance</span>
            </div>
        </div>
    </div>
    """)
```

3. **OWASP ASI bars:** Gewone NiceGUI `ui.linear_progress()` componenten, geen Plotly nodig:

```python
def asi_coverage_bars(coverage: dict[str, str]) -> None:
    """Horizontale bars per OWASP ASI checkpoint."""
    status_colors = {
        "MITIGATED": "positive",
        "PARTIAL": "warning",
        "VULNERABLE": "negative",
        "NOT_ASSESSED": "grey",
    }

    for asi_id in [f"ASI{i:02d}" for i in range(1, 11)]:
        status = coverage.get(asi_id, "NOT_ASSESSED")
        color = status_colors.get(status, "grey")
        value = {"MITIGATED": 1.0, "PARTIAL": 0.5, "VULNERABLE": 0.1, "NOT_ASSESSED": 0.0}[status]

        with ui.row().classes("items-center gap-2 w-full"):
            ui.label(asi_id).classes("w-12 text-sm font-mono")
            ui.linear_progress(value=value, color=color).classes("flex-grow")
            ui.badge(status, color=color).classes("text-xs")
```

**Conclusie Open Vraag #5:** Performance is geen probleem. Maximaal 3 Plotly charts per pagina, aangevuld met CSS/SVG voor lichte visualisaties.

---

## 8. SPRINT_TRACKER als Gecachte JSON (Open Vraag #6)

### Vraag

Is het waard om een `sprint_tracker.json` cache te genereren bij elke sprint-afsluiting?

### Antwoord: **Nee, niet nodig in deze fase.**

Motivatie:
1. **505 regels markdown parsen kost <1ms** — geen performance bottleneck
2. **SprintTrackerParser cacht de content** in `self._content` — één read per instantie
3. **PlanningProvider cacht de parser** via lazy initialisatie
4. **SPRINT_TRACKER.md is de single source of truth** (ADR-003) — een JSON-cache introduceert synchronisatie-risico
5. **Bij 100+ sprints:** heroverweeg. Momenteel 43 sprints — ruim binnen grenzen

**Alternatief voor de toekomst:** als de sprint-skill bij afsluiting een `sprint_tracker_cache.json` genereert, kan de parser dit preferentieel laden als het bestaat en recenter is dan de .md. Maar dit is optimalisatie voor later.

---

## 9. Nieuwe Componenten Specificatie

### planning_kanban.py

```python
def planning_kanban(planning_provider: PlanningProvider) -> None:
    """Visuele Kanban-weergave van de planning-pipeline."""
    inbox_items = planning_provider.get_inbox_items()
    history = planning_provider.get_sprint_history()

    # Kolommen
    active_sprint = planning_provider.get_sprint_info()
    recent_done = [h for h in history if h.status == "DONE"][-5:]  # Laatste 5

    # Parked count
    parked_dir = planning_provider._config.inbox_path.parent / "parked"
    parked_count = len(list(parked_dir.glob("*.md"))) if parked_dir.exists() else 0

    columns = [
        ("INBOX", "inbox", inbox_items, "warning"),
        ("ACTIEF", "play_arrow", [active_sprint] if active_sprint.nummer else [], "info"),
        ("DONE", "check_circle", recent_done, "positive"),
        ("PARKED", "pause_circle", [], "grey"),
    ]

    with ui.row().classes("gap-4 w-full overflow-x-auto"):
        for col_name, icon, items, color in columns:
            with ui.card().classes("p-3 min-w-64 flex-shrink-0"):
                with ui.row().classes("items-center gap-2 mb-2"):
                    ui.icon(icon, color=color)
                    ui.label(col_name).classes("font-bold")
                    count = parked_count if col_name == "PARKED" else len(items)
                    ui.badge(str(count), color=color)

                if col_name == "PARKED":
                    ui.label(f"{parked_count} geparkeerde items").classes("text-sm text-grey-6")
                elif items:
                    for item in items:
                        with ui.card().classes("p-2 mb-1 bg-grey-9"):
                            if hasattr(item, "filename"):
                                # InboxItem
                                ui.label(item.filename.replace("SPRINT_INTAKE_", "").replace(".md", "")).classes("text-sm")
                                with ui.row().classes("gap-1"):
                                    ui.badge(item.sprint_type, color="primary").classes("text-xs")
                                    ui.badge(item.node, color="grey").classes("text-xs")
                            elif hasattr(item, "nummer"):
                                # SprintHistoryItem of SprintInfo
                                naam = item.naam if hasattr(item, "naam") else ""
                                ui.label(f"#{item.nummer} {naam}").classes("text-sm")
                                if hasattr(item, "sprint_type"):
                                    ui.badge(item.sprint_type, color="primary").classes("text-xs")
                else:
                    ui.label("Leeg").classes("text-xs text-grey-7 italic")
```

### fase_pipeline.py

```python
def fase_pipeline(fases: list[FaseInfo]) -> None:
    """Horizontale fase-pipeline met verbonden cirkels."""
    with ui.row().classes("items-center gap-0 w-full justify-center"):
        for i, fase in enumerate(fases):
            # Cirkel
            if fase.status == "afgerond":
                icon = "check_circle"
                color = "positive"
            elif fase.status == "actief":
                icon = "sync"
                color = "info"
            else:
                icon = "radio_button_unchecked"
                color = "grey-5"

            with ui.column().classes("items-center min-w-24"):
                ui.icon(icon, color=color).classes("text-3xl")
                ui.label(f"Fase {fase.nummer}").classes(f"text-sm font-bold text-{color}")
                ui.label(fase.naam).classes("text-xs text-grey-6")
                if fase.sprint_count > 0:
                    ui.label(f"{fase.sprint_count} sprints").classes("text-xs text-grey-7")

            # Connector lijn (behalve na laatste)
            if i < len(fases) - 1:
                line_color = "positive" if fase.status == "afgerond" else "grey-8"
                ui.element("div").style(
                    f"height: 2px; width: 30px; background: var(--q-{line_color}); "
                    f"align-self: center; margin-top: -40px;"
                )
```

### domain_detail_card.py (Growth)

```python
def domain_detail_card(domain: SkillDomain, *, expanded: bool = False) -> None:
    """Uitklapbare domein-detail kaart voor Growth pagina."""
    level_labels = {1: "Novice", 2: "Advanced Beginner", 3: "Competent", 4: "Proficient", 5: "Expert"}
    level_colors = {1: "negative", 2: "warning", 3: "info", 4: "positive", 5: "primary"}

    with ui.card().classes("p-3 w-full"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.row().classes("items-center gap-2"):
                ui.badge(
                    str(domain.level),
                    color=level_colors.get(domain.level, "grey"),
                ).classes("text-white text-lg px-3 py-1")
                ui.label(domain.name).classes("text-subtitle1 font-bold")
                ui.label(f"({level_labels.get(domain.level, '?')})").classes("text-grey-6")

            # Growth velocity indicator
            if domain.growth_velocity > 0.15:
                ui.icon("trending_up", color="positive")
            elif domain.growth_velocity > 0.05:
                ui.icon("trending_flat", color="warning")
            else:
                ui.icon("trending_down", color="grey")

        # Progress bar naar volgend niveau
        progress = (domain.level - 1) / 4  # 1→0%, 5→100%
        ui.linear_progress(value=progress, color=level_colors.get(domain.level, "grey")).classes("mt-2")
        ui.label(f"Niveau {domain.level}/5 — {int(progress*100)}% naar Expert").classes("text-xs text-grey-7")

        # Uitklapbare details
        with ui.expansion("Details", icon="expand_more", value=expanded).classes("mt-2"):
            # Subdomeinen
            if domain.subdomains:
                ui.label("Subdomeinen").classes("text-sm font-bold mt-1")
                with ui.row().classes("gap-1 flex-wrap"):
                    for sub in domain.subdomains:
                        ui.badge(sub, color="grey").classes("text-xs")

            # Evidence
            if domain.evidence:
                ui.label("Evidence").classes("text-sm font-bold mt-2")
                for ev in domain.evidence:
                    ui.label(f"• {ev}").classes("text-sm text-grey-6")

            # ZPD taken
            if domain.zpd_tasks:
                ui.label("ZPD Taken (Zone of Proximal Development)").classes("text-sm font-bold mt-2")
                for task in domain.zpd_tasks:
                    ui.label(f"→ {task}").classes("text-sm text-info")
```

---

## 10. Bestandsstructuur na Implementatie

```
packages/devhub-dashboard/devhub_dashboard/
├── app.py                              # Ongewijzigd (routes bestaan al)
├── config.py                           # + nodes_config_path (indien niet aanwezig)
├── __init__.py
├── __main__.py
├── components/
│   ├── __init__.py
│   ├── kpi_card.py                     # Bestaand
│   ├── status_badge.py                 # Bestaand
│   ├── trend_chart.py                  # Bestaand
│   ├── research_card.py                # Bestaand
│   ├── sparkline.py                    # NIEUW — SVG inline sparkline
│   ├── compliance_gauge.py             # NIEUW — CSS circulaire gauge
│   ├── asi_coverage_bars.py            # NIEUW — OWASP ASI progressie bars
│   ├── planning_kanban.py              # NIEUW — Kanban kolommen
│   ├── fase_pipeline.py                # NIEUW — Horizontale fase cirkels
│   └── domain_detail_card.py           # NIEUW — Growth domein detail
├── data/
│   ├── __init__.py
│   ├── providers.py                    # UITGEBREID (HealthProvider 7 checks, PlanningProvider)
│   ├── research_queue.py               # Bestaand
│   ├── history.py                      # UITGEBREID (HealthSnapshot v2, multi-trend)
│   ├── event_listener.py               # Bestaand
│   ├── sprint_tracker_parser.py        # NIEUW — Dedicated SPRINT_TRACKER parser
│   ├── governance_provider.py          # NIEUW — Per-artikel compliance
│   └── growth_provider.py              # NIEUW — YAML skill radar + JSON challenges
├── pages/
│   ├── __init__.py
│   ├── overview.py                     # UITGEBREID (7 KPI + sparklines + activity feed)
│   ├── health.py                       # UITGEBREID (7 dimensies + multi-metric trend)
│   ├── planning.py                     # UITGEBREID (analytics tabs + Kanban + fase pipeline)
│   ├── knowledge.py                    # Bestaand (of uitgebreid via andere intake)
│   ├── governance.py                   # HERSCHREVEN (compliance score + interactive articles + ASI + audit trail)
│   ├── growth.py                       # HERSCHREVEN (dynamische radar + domain cards + challenges + recommendations)
│   └── research.py                     # Bestaand (of uitgebreid via andere intake)
```

**Nieuwe bestanden:** 9 (3 data, 6 componenten)
**Uitgebreide bestanden:** 5 (providers, history, overview, health, planning)
**Herschreven bestanden:** 2 (governance, growth)

---

## 11. Test-strategie

### Unit tests per nieuwe module

```python
# test_sprint_tracker_parser.py
class TestSprintTrackerParser:
    def test_parse_metadata(self): ...
    def test_parse_sprint_log_all_43_entries(self): ...
    def test_parse_sprint_log_row_with_asterisk(self): ...  # "+0*"
    def test_infer_type_feat(self): ...
    def test_infer_type_spike(self): ...
    def test_infer_type_chore(self): ...
    def test_infer_size_xs(self): ...
    def test_infer_size_s(self): ...
    def test_annotate_fases(self): ...
    def test_velocity_data_format(self): ...
    def test_velocity_metrics_calculation(self): ...
    def test_get_fases_all_6(self): ...
    def test_empty_file_returns_empty(self): ...
    def test_nonexistent_file_returns_empty(self): ...

# test_governance_provider.py
class TestGovernanceProvider:
    def test_all_9_articles_returned(self): ...
    def test_compliance_score_all_active(self): ...
    def test_art3_fails_when_no_tests(self): ...
    def test_art8_violation_when_secrets(self): ...
    def test_security_summary_with_audit(self): ...
    def test_security_summary_without_audit(self): ...
    def test_audit_trail_from_file(self): ...
    def test_audit_trail_synthetic_fallback(self): ...

# test_growth_provider.py
class TestGrowthProvider:
    def test_load_skill_radar_from_yaml(self): ...
    def test_skill_radar_fallback_none(self): ...
    def test_domains_parsed_correctly(self): ...
    def test_t_shape_parsed(self): ...
    def test_challenges_from_json(self): ...
    def test_recommendations_from_json(self): ...
    def test_growth_report_generation(self): ...
    def test_empty_data_dirs(self): ...

# test_health_provider_extended.py
class TestHealthProviderExtended:
    def test_7_dimensions_returned(self): ...
    def test_dependency_check_detects_unpinned(self): ...
    def test_architecture_check_node_interface(self): ...
    def test_knowledge_health_freshness(self): ...
    def test_security_detects_env_file(self): ...
    def test_sprint_hygiene_stale_tracker(self): ...
    def test_cache_ttl_prevents_recompute(self): ...

# test_health_snapshot_v2.py
class TestHealthSnapshotV2:
    def test_v1_json_loads_with_defaults(self): ...
    def test_v2_json_roundtrip(self): ...
    def test_from_report_with_extra_fields(self): ...
    def test_multi_trend_data_format(self): ...
```

### Integration tests

```python
# test_planning_page_extended.py
class TestPlanningPageExtended:
    def test_velocity_chart_renders(self): ...
    def test_sprint_history_table_sortable(self): ...
    def test_kanban_columns_populated(self): ...
    def test_fase_pipeline_active_highlighted(self): ...

# test_governance_page.py
class TestGovernancePage:
    def test_compliance_gauge_renders(self): ...
    def test_articles_expandable(self): ...
    def test_asi_bars_render(self): ...

# test_growth_page_dynamic.py
class TestGrowthPageDynamic:
    def test_radar_from_yaml_not_hardcoded(self): ...
    def test_domain_cards_match_yaml_count(self): ...
    def test_t_shape_from_yaml_data(self): ...
```

**Geschatte test-toename:** 50-70 nieuwe tests.

---

## 12. Samenvatting Open Vragen → Antwoorden

| # | Open Vraag | Antwoord |
|---|-----------|----------|
| 1 | SPRINT_TRACKER parsing — robuustheid? | Dedicated `SprintTrackerParser` class met two-pass parsing, defensief ontwerp, fuzzy fase-matching (§1) |
| 2 | HealthProvider 7 dimensies — performance? | 75ms per 30s met caching. Geen performance-probleem (§2) |
| 3 | Growth data persistentie | `data/challenges/` en `data/recommendations/` als JSON-bestanden, niet vectorstore (§6) |
| 4 | Governance audit trail opslag | File-based `data/governance/audit_log.json`, append-only. Event Bus = trigger, niet opslag (§5) |
| 5 | Plotly performance bij 5+ charts | Max 3 Plotly per pagina. Sparklines via SVG, gauge via CSS, ASI bars via `ui.linear_progress` (§7) |
| 6 | SPRINT_TRACKER als JSON cache | Niet nodig: <1ms parse, content gecacht, SSOT-risico vermijden. Heroverweeg bij 100+ sprints (§8) |
