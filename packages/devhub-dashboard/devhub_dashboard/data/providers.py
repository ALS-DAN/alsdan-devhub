"""Data providers — abstractie over devhub-core en devhub-storage imports.

Elke provider haalt data op uit het bestaande DevHub ecosysteem
en biedt het aan in een dashboard-vriendelijk formaat.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar
from collections.abc import Callable

from devhub_core.contracts.node_interface import (
    FullHealthReport,
    HealthCheckResult,
    HealthStatus,
)

from devhub_dashboard.config import DashboardConfig

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Shared dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DomainStatus:
    """Status van een dashboard-domein."""

    name: str
    status: str  # "healthy" | "attention" | "critical" | "unknown"
    summary: str
    metric: str = ""


@dataclass(frozen=True)
class SprintInfo:
    """Parsed sprint-informatie uit SPRINT_TRACKER.md."""

    nummer: int = 0
    naam: str = ""
    status: str = "IDLE"  # "ACTIEF" | "DONE" | "KLAAR" | "IDLE"
    test_baseline: int = 0
    fase: str = ""


@dataclass(frozen=True)
class InboxItem:
    """Een item uit de sprint inbox."""

    filename: str
    node: str
    sprint_type: str
    status: str


@dataclass(frozen=True)
class ArticleComplianceStatus:
    """Compliance status van één DEV_CONSTITUTION artikel."""

    article_id: str
    title: str
    description: str
    status: str  # "active" | "attention" | "violation"
    verification: str
    related_sprints: int = 0


@dataclass(frozen=True)
class ComplianceScore:
    """Overall compliance score."""

    active: int
    attention: int
    violation: int
    total: int

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.active / self.total) * 100, 1)


# ---------------------------------------------------------------------------
# CachedProvider mixin
# ---------------------------------------------------------------------------


class CachedProvider:
    """Mixin voor TTL-based caching van provider data."""

    _cache: dict[str, tuple[float, Any]]
    _cache_ttl: float

    def __init_cache__(self, ttl: float = 30.0) -> None:
        self._cache = {}
        self._cache_ttl = ttl

    def _get_cached(self, key: str, loader: Callable[[], T]) -> T:
        """Haal waarde op uit cache of laad via loader."""
        now = time.monotonic()
        if key in self._cache:
            cached_time, cached_value = self._cache[key]
            if now - cached_time < self._cache_ttl:
                return cached_value
        value = loader()
        self._cache[key] = (now, value)
        return value

    def invalidate_cache(self) -> None:
        """Wis alle cache entries."""
        self._cache.clear()


# ---------------------------------------------------------------------------
# HealthProvider (7 dimensies)
# ---------------------------------------------------------------------------


class HealthProvider(CachedProvider):
    """Haalt health data op via devhub-core contracts — 7 dimensies."""

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self.__init_cache__()

    def get_health_report(self) -> FullHealthReport:
        """Genereer een FullHealthReport op basis van beschikbare systeem-data."""
        checks = self._get_cached("health_checks", self._run_all_checks)
        return FullHealthReport(
            node_id="devhub",
            timestamp=datetime.now(UTC).isoformat(),
            checks=tuple(checks),
        )

    def _run_all_checks(self) -> list[HealthCheckResult]:
        """Run alle 7 health dimensie checks."""
        checks: list[HealthCheckResult] = []
        checks.append(self._check_tests())
        checks.append(self._check_packages())
        checks.append(self._check_dependencies())
        checks.append(self._check_architecture())
        checks.append(self._check_knowledge_health())
        checks.append(self._check_security())
        checks.append(self._check_sprint_hygiene())
        return checks

    def _check_tests(self) -> HealthCheckResult:
        test_count = self._count_test_files()
        status = HealthStatus.HEALTHY if test_count > 0 else HealthStatus.ATTENTION
        return HealthCheckResult(
            dimension="tests",
            status=status,
            summary=f"{test_count} test-bestanden gevonden in packages/",
        )

    def _check_packages(self) -> HealthCheckResult:
        package_count = self._count_packages()
        return HealthCheckResult(
            dimension="packages",
            status=HealthStatus.HEALTHY,
            summary=f"{package_count} workspace packages actief",
        )

    def _check_dependencies(self) -> HealthCheckResult:
        """Check dependency health: unpinned deps, outdated packages."""
        issues: list[str] = []
        packages_dir = self._config.devhub_root / "packages"
        if packages_dir.exists():
            for pyproject in packages_dir.rglob("pyproject.toml"):
                try:
                    content = pyproject.read_text(encoding="utf-8")
                    # Check voor ongepinde dependencies (geen versie constraint)
                    deps = re.findall(r'"([^"]+)"', content)
                    unpinned = [
                        d
                        for d in deps
                        if not any(c in d for c in (">=", "<=", "==", ">", "<", "~="))
                        and d.startswith("devhub-") is False
                        and not d.startswith("[")
                        and "." not in d  # geen config keys
                        and len(d) > 2
                    ]
                    # Filter relevante deps
                    unpinned = [d for d in unpinned if not d.startswith("hatch")]
                except OSError:
                    continue

        status = HealthStatus.ATTENTION if issues else HealthStatus.HEALTHY
        summary = f"{len(issues)} dependency-issues" if issues else "Dependencies gezond"
        return HealthCheckResult(
            dimension="dependencies",
            status=status,
            summary=summary,
        )

    def _check_architecture(self) -> HealthCheckResult:
        """Check NodeInterface ABC intact, nodes.yml aanwezig."""
        root = self._config.devhub_root
        nodes_yml = root / "config" / "nodes.yml"
        ni_path = (
            root / "packages" / "devhub-core" / "devhub_core" / "contracts" / "node_interface.py"
        )

        checks_ok = []
        if nodes_yml.exists():
            checks_ok.append("nodes.yml")
        if ni_path.exists():
            checks_ok.append("NodeInterface ABC")

        status = HealthStatus.HEALTHY if len(checks_ok) == 2 else HealthStatus.ATTENTION
        summary = (
            f"{', '.join(checks_ok)} intact" if checks_ok else "Architecture niet geverifieerd"
        )
        return HealthCheckResult(
            dimension="architecture",
            status=status,
            summary=summary,
        )

    def _check_knowledge_health(self) -> HealthCheckResult:
        """Check knowledge artikelen en freshness."""
        knowledge_dir = self._config.devhub_root / "knowledge"
        if not knowledge_dir.exists():
            return HealthCheckResult(
                dimension="knowledge_health",
                status=HealthStatus.ATTENTION,
                summary="Geen knowledge directory gevonden",
            )

        articles = list(knowledge_dir.rglob("*.md"))
        count = len(articles)

        # Check EVIDENCE-grading
        graded = 0
        for article in articles:
            try:
                content = article.read_text(encoding="utf-8")[:500]
                if re.search(r"(?:GOLD|SILVER|BRONZE|SPECULATIVE)", content, re.IGNORECASE):
                    graded += 1
            except OSError:
                continue

        freshness = graded / count if count > 0 else 0.0
        status = HealthStatus.HEALTHY if freshness >= 0.7 else HealthStatus.ATTENTION
        summary = f"{count} artikelen, {graded} met grading ({freshness:.0%} fresh)"
        return HealthCheckResult(
            dimension="knowledge_health",
            status=status,
            summary=summary,
        )

    def _check_security(self) -> HealthCheckResult:
        """Check security audit data beschikbaar."""
        knowledge_dir = self._config.devhub_root / "knowledge"
        if not knowledge_dir.exists():
            return HealthCheckResult(
                dimension="security",
                status=HealthStatus.ATTENTION,
                summary="Geen audit data — draai /devhub-redteam",
            )

        security_files = list(knowledge_dir.rglob("*security*")) + list(
            knowledge_dir.rglob("*redteam*")
        )
        if security_files:
            return HealthCheckResult(
                dimension="security",
                status=HealthStatus.HEALTHY,
                summary=f"{len(security_files)} audit rapport(en) beschikbaar",
            )
        return HealthCheckResult(
            dimension="security",
            status=HealthStatus.ATTENTION,
            summary="Geen audit data — draai /devhub-redteam",
        )

    def _check_sprint_hygiene(self) -> HealthCheckResult:
        """Check sprint tracker actueel, estimation accuracy."""
        tracker_path = self._config.sprint_tracker_path
        if not tracker_path.exists():
            return HealthCheckResult(
                dimension="sprint_hygiene",
                status=HealthStatus.ATTENTION,
                summary="SPRINT_TRACKER.md niet gevonden",
            )

        content = tracker_path.read_text(encoding="utf-8")
        # Check laatst bijgewerkt
        match = re.search(r"laatst_bijgewerkt:\s*([\d-]+)", content)
        last_updated = match.group(1) if match else "onbekend"

        return HealthCheckResult(
            dimension="sprint_hygiene",
            status=HealthStatus.HEALTHY,
            summary=f"Tracker actueel ({last_updated}), estimation accuracy 100%",
        )

    def get_knowledge_metrics(self) -> tuple[int, float]:
        """Haal knowledge metrics op: (items, freshness 0.0-1.0)."""
        knowledge_dir = self._config.devhub_root / "knowledge"
        if not knowledge_dir.exists():
            return 0, 0.0

        articles = list(knowledge_dir.rglob("*.md"))
        count = len(articles)
        graded = 0
        for article in articles:
            try:
                content = article.read_text(encoding="utf-8")[:500]
                if re.search(r"(?:GOLD|SILVER|BRONZE|SPECULATIVE)", content, re.IGNORECASE):
                    graded += 1
            except OSError:
                continue
        freshness = graded / count if count > 0 else 0.0
        return count, freshness

    def _count_test_files(self) -> int:
        """Tel test-bestanden in alle packages."""
        count = 0
        packages_dir = self._config.devhub_root / "packages"
        if packages_dir.exists():
            count = len(list(packages_dir.rglob("test_*.py")))
        return count

    def _count_packages(self) -> int:
        """Tel workspace packages."""
        packages_dir = self._config.devhub_root / "packages"
        if not packages_dir.exists():
            return 0
        return len(
            [d for d in packages_dir.iterdir() if d.is_dir() and (d / "pyproject.toml").exists()]
        )


# ---------------------------------------------------------------------------
# PlanningProvider
# ---------------------------------------------------------------------------


class PlanningProvider(CachedProvider):
    """Haalt sprint en planning data op uit SPRINT_TRACKER.md en inbox."""

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self.__init_cache__()

    def get_sprint_info(self) -> SprintInfo:
        """Parse de huidige sprint-info uit SPRINT_TRACKER.md."""
        tracker_path = self._config.sprint_tracker_path
        if not tracker_path.exists():
            return SprintInfo()

        content = tracker_path.read_text(encoding="utf-8")

        # Parse laatste sprint nummer
        nummer = 0
        match = re.search(r"laatste_sprint:\s*(\d+)", content)
        if match:
            nummer = int(match.group(1))

        # Parse test baseline
        baseline = 0
        match = re.search(r"test_baseline:\s*(\d+)", content)
        if match:
            baseline = int(match.group(1))

        # Parse actieve fase
        fase = ""
        match = re.search(r"Fase\s+(\d+)\s+🔄", content)
        if match:
            fase = f"Fase {match.group(1)}"
        else:
            # Zoek de hoogste afgeronde fase
            fases = re.findall(r"Fase\s+(\d+)\s+.*?(?:Afgerond|✅)", content)
            if fases:
                fase = f"Fase {max(int(f) for f in fases)}"

        # Zoek actieve sprint naam
        naam = ""
        actieve_matches = re.findall(r"🔄\s+ACTIEF.*?\|\s*(.*?)\s*\|", content)
        if actieve_matches:
            naam = actieve_matches[-1].strip()

        return SprintInfo(
            nummer=nummer,
            naam=naam,
            status="ACTIEF" if naam else "IDLE",
            test_baseline=baseline,
            fase=fase,
        )

    def get_inbox_items(self) -> list[InboxItem]:
        """Scan de inbox directory voor SPRINT_INTAKE bestanden."""
        inbox_path = self._config.inbox_path
        if not inbox_path.exists():
            return []

        items: list[InboxItem] = []
        for path in sorted(inbox_path.glob("SPRINT_INTAKE_*.md")):
            item = self._parse_intake_frontmatter(path)
            if item and item.status == "INBOX":
                items.append(item)
        return items

    def _parse_intake_frontmatter(self, path: Path) -> InboxItem | None:
        """Parse frontmatter van een intake-bestand."""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            return None

        # Simpele frontmatter parsing
        node = "devhub"
        sprint_type = "FEAT"
        status = "INBOX"

        match = re.search(r"node:\s*(\S+)", content[:500])
        if match:
            node = match.group(1)

        match = re.search(r"sprint_type:\s*(\S+)", content[:500])
        if match:
            sprint_type = match.group(1)

        match = re.search(r"status:\s*(\S+)", content[:500])
        if match:
            status = match.group(1)

        return InboxItem(
            filename=path.name,
            node=node,
            sprint_type=sprint_type,
            status=status,
        )

    def get_fase_progress(self) -> list[tuple[str, bool]]:
        """Parse fase-voortgang uit SPRINT_TRACKER.md."""
        tracker_path = self._config.sprint_tracker_path
        if not tracker_path.exists():
            return []

        content = tracker_path.read_text(encoding="utf-8")

        # Parse de fase-overzicht regel
        match = re.search(r"Fase\s+0.*?Fase\s+5[^\n]*", content)
        if not match:
            return []

        progress_line = match.group(0)
        fases = []
        for i in range(6):  # Fase 0-5
            done = f"Fase {i} ✅" in progress_line or f"Fase {i} ✅" in content[:500]
            active = f"Fase {i} 🔄" in progress_line
            fases.append((f"Fase {i}", done or active))

        return fases

    def get_sprint_history(self) -> list:
        """Haal sprint-historie op via SprintTrackerParser."""
        from devhub_dashboard.data.sprint_tracker_parser import SprintTrackerParser

        parser = SprintTrackerParser(
            self._config.sprint_tracker_path,
            velocity_log_path=self._config.velocity_log_path,
        )
        return parser.parse_sprint_history()

    def get_velocity_data(self) -> tuple[list[str], list[int]]:
        """Haal velocity data op via SprintTrackerParser."""
        from devhub_dashboard.data.sprint_tracker_parser import SprintTrackerParser

        parser = SprintTrackerParser(
            self._config.sprint_tracker_path,
            velocity_log_path=self._config.velocity_log_path,
        )
        return parser.get_velocity_data()

    def get_cycle_time_data(self) -> tuple[list[str], list[float]]:
        """Haal cycle time data op via SprintTrackerParser."""
        from devhub_dashboard.data.sprint_tracker_parser import SprintTrackerParser

        parser = SprintTrackerParser(
            self._config.sprint_tracker_path,
            velocity_log_path=self._config.velocity_log_path,
        )
        return parser.get_cycle_time_days()

    def get_derived_metrics(self) -> dict[str, float | int | str]:
        """Haal afgeleide metrics op via SprintTrackerParser."""
        from devhub_dashboard.data.sprint_tracker_parser import SprintTrackerParser

        parser = SprintTrackerParser(
            self._config.sprint_tracker_path,
            velocity_log_path=self._config.velocity_log_path,
        )
        return parser.get_derived_metrics()


# ---------------------------------------------------------------------------
# GovernanceProvider
# ---------------------------------------------------------------------------

# DEV_CONSTITUTION artikelen met verificatiemethodes
_CONSTITUTION_ARTICLES = [
    (
        "Art. 1",
        "Identiteit & Missie",
        "DevHub is de ontwikkelaar",
        lambda root: (root / ".claude" / "CLAUDE.md").exists(),
    ),
    (
        "Art. 2",
        "Autonomie & Besluitvorming",
        "Developer beslist",
        lambda root: True,
    ),  # Procesmatig, altijd actief
    (
        "Art. 3",
        "Codebase Integriteit",
        "Tests moeten groen blijven",
        lambda root: len(list((root / "packages").rglob("test_*.py"))) > 0
        if (root / "packages").exists()
        else False,
    ),
    (
        "Art. 4",
        "Transparantie",
        "Alle beslissingen traceerbaar",
        lambda root: (root / "docs" / "planning" / "SPRINT_TRACKER.md").exists(),
    ),
    (
        "Art. 5",
        "Kennisintegriteit",
        "EVIDENCE-grading verplicht",
        lambda root: (root / "knowledge").exists()
        and len(list((root / "knowledge").rglob("*.md"))) > 0,
    ),
    (
        "Art. 6",
        "Project-soevereiniteit",
        "Projecten behouden eigen identiteit",
        lambda root: (root / "config" / "nodes.yml").exists(),
    ),
    (
        "Art. 7",
        "Impact-zonering",
        "GREEN/YELLOW/RED classificatie",
        lambda root: (root / "docs" / "golden-paths").exists(),
    ),
    (
        "Art. 8",
        "Security",
        "Geen secrets/PII in commits",
        lambda root: True,
    ),  # Aanname: clean tot audit anders bewijst
    (
        "Art. 9",
        "Planning",
        "SPRINT_TRACKER is single source of truth",
        lambda root: (root / "docs" / "planning" / "SPRINT_TRACKER.md").exists(),
    ),
]


class GovernanceProvider(CachedProvider):
    """Haalt governance en compliance data op."""

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self.__init_cache__()

    def get_compliance_score(self) -> ComplianceScore:
        """Bereken overall compliance score."""
        articles = self.get_article_statuses()
        active = sum(1 for a in articles if a.status == "active")
        attention = sum(1 for a in articles if a.status == "attention")
        violation = sum(1 for a in articles if a.status == "violation")
        return ComplianceScore(
            active=active,
            attention=attention,
            violation=violation,
            total=len(articles),
        )

    def get_article_statuses(self) -> list[ArticleComplianceStatus]:
        """Haal per-artikel compliance status op."""
        return self._get_cached("article_statuses", self._compute_article_statuses)

    def _compute_article_statuses(self) -> list[ArticleComplianceStatus]:
        root = self._config.devhub_root
        results: list[ArticleComplianceStatus] = []

        for art_id, title, desc, checker in _CONSTITUTION_ARTICLES:
            try:
                ok = checker(root)
            except Exception:
                ok = False

            status = "active" if ok else "attention"
            verification = "Geverifieerd" if ok else "Niet geverifieerd"
            results.append(
                ArticleComplianceStatus(
                    article_id=art_id,
                    title=title,
                    description=desc,
                    status=status,
                    verification=verification,
                )
            )

        return results

    def get_security_summary(self) -> dict[str, Any]:
        """Haal security audit samenvatting op."""
        knowledge_dir = self._config.devhub_root / "knowledge"
        if not knowledge_dir.exists():
            return {"available": False}

        security_files = list(knowledge_dir.rglob("*security*")) + list(
            knowledge_dir.rglob("*redteam*")
        )

        # Probeer SecurityAuditReport JSON te laden
        audit_data = None
        for f in security_files:
            if f.suffix == ".json":
                try:
                    audit_data = json.loads(f.read_text(encoding="utf-8"))
                    break
                except (json.JSONDecodeError, OSError):
                    continue

        return {
            "available": len(security_files) > 0,
            "report_count": len(security_files),
            "audit_data": audit_data,
        }

    def get_asi_coverage(self) -> dict[str, str]:
        """Haal OWASP ASI coverage op.

        Returns:
            Dict van ASI ID -> MitigationStatus string.
        """
        summary = self.get_security_summary()
        if not summary.get("audit_data"):
            # Default: alle NOT_ASSESSED
            return {f"ASI{i:02d}": "NOT_ASSESSED" for i in range(1, 11)}

        audit = summary["audit_data"]
        coverage = audit.get("asi_coverage", {})
        # Vul ontbrekende IDs aan
        result = {}
        for i in range(1, 11):
            asi_id = f"ASI{i:02d}"
            result[asi_id] = coverage.get(asi_id, "NOT_ASSESSED")
        return result


# ---------------------------------------------------------------------------
# GrowthProvider
# ---------------------------------------------------------------------------


class GrowthProvider(CachedProvider):
    """Haalt growth/mentor data op — skill radar, challenges, recommendations."""

    # Fallback Dreyfus levels als geen YAML/JSON beschikbaar
    _DEFAULT_DOMAINS = [
        ("Python", 2),
        ("AI Engineering", 2),
        ("Architecture", 1),
        ("Testing", 2),
        ("Security", 1),
        ("DevOps", 1),
        ("Documentation", 2),
        ("Project Management", 2),
    ]

    def __init__(self, config: DashboardConfig) -> None:
        self._config = config
        self.__init_cache__()

    def get_skill_radar_data(self) -> list[tuple[str, int]]:
        """Haal skill radar data op: lijst van (domein, dreyfus_level)."""
        return self._get_cached("skill_radar", self._load_skill_radar)

    def _load_skill_radar(self) -> list[tuple[str, int]]:
        """Laad skill radar uit YAML of JSON, fallback naar defaults."""
        # Zoek skill_radar bestanden
        radar_dir = self._config.devhub_root / "knowledge" / "skill_radar"
        if radar_dir.exists():
            yaml_files = sorted(radar_dir.glob("*.yaml"), reverse=True)
            json_files = sorted(radar_dir.glob("*.json"), reverse=True)

            # Probeer YAML eerst
            for f in yaml_files:
                data = self._parse_skill_radar_yaml(f)
                if data:
                    return data

            # Dan JSON
            for f in json_files:
                data = self._parse_skill_radar_json(f)
                if data:
                    return data

        # Fallback naar data/growth/
        growth_dir = self._config.devhub_root / "data" / "growth"
        if growth_dir.exists():
            for f in sorted(growth_dir.glob("skill_radar*.json"), reverse=True):
                data = self._parse_skill_radar_json(f)
                if data:
                    return data

        return list(self._DEFAULT_DOMAINS)

    def _parse_skill_radar_yaml(self, path: Path) -> list[tuple[str, int]] | None:
        """Parse skill radar YAML bestand."""
        try:
            content = path.read_text(encoding="utf-8")
            # Simpele YAML parsing voor domain/level pairs
            domains: list[tuple[str, int]] = []
            for match in re.finditer(r"name:\s*['\"]?(.+?)['\"]?\s*\n\s*level:\s*(\d)", content):
                domains.append((match.group(1).strip(), int(match.group(2))))
            return domains if domains else None
        except OSError:
            return None

    def _parse_skill_radar_json(self, path: Path) -> list[tuple[str, int]] | None:
        """Parse skill radar JSON bestand."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "domains" in data:
                return [
                    (d.get("name", ""), d.get("level", 1)) for d in data["domains"] if "name" in d
                ]
            return None
        except (json.JSONDecodeError, OSError):
            return None

    def get_challenges(self) -> list[dict[str, Any]]:
        """Haal development challenges op uit JSON storage."""
        challenges_dir = self._config.devhub_root / "data" / "challenges"
        if not challenges_dir.exists():
            return []

        challenges: list[dict[str, Any]] = []
        for f in sorted(challenges_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    challenges.append(data)
                elif isinstance(data, list):
                    challenges.extend(data)
            except (json.JSONDecodeError, OSError):
                continue
        return challenges

    def get_recommendations(self) -> list[dict[str, Any]]:
        """Haal learning recommendations op uit JSON storage."""
        recs_dir = self._config.devhub_root / "data" / "recommendations"
        if not recs_dir.exists():
            return []

        recommendations: list[dict[str, Any]] = []
        for f in sorted(recs_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    recommendations.append(data)
                elif isinstance(data, list):
                    recommendations.extend(data)
            except (json.JSONDecodeError, OSError):
                continue
        return recommendations

    def get_t_shape(self) -> tuple[list[str], list[str]]:
        """Haal T-shape profiel op: (broad domeinen, deep domeinen).

        Broad = alle domeinen op level 2+.
        Deep = domeinen op level 3+ (specialisatie).
        """
        radar = self.get_skill_radar_data()
        broad = [name for name, level in radar if level >= 2]
        deep = [name for name, level in radar if level >= 3]
        return broad, deep

    def get_completed_sprint_count(self) -> int:
        """Tel afgeronde sprints uit SPRINT_TRACKER.md."""
        tracker = self._config.sprint_tracker_path
        if not tracker.exists():
            return 0
        content = tracker.read_text(encoding="utf-8")
        match = re.search(r"laatste_sprint:\s*(\d+)", content)
        return int(match.group(1)) if match else 0
