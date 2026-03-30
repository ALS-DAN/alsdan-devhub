"""DevHub Dashboard — FastAPI + Jinja2 + HTMX app."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from devhub_core.contracts.node_interface import HealthStatus

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.history import HealthSnapshot, HistoryStore
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider
from devhub_dashboard.data.providers import (
    GovernanceProvider,
    GrowthProvider,
    HealthProvider,
    PlanningProvider,
)
from devhub_dashboard.data.research_queue import (
    RequestStream,
    ResearchQueueManager,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

_PKG_DIR = Path(__file__).parent

app = FastAPI(title="DevHub Dashboard")
app.mount("/static", StaticFiles(directory=_PKG_DIR / "static"), name="static")
templates = Jinja2Templates(directory=_PKG_DIR / "templates")

# ---------------------------------------------------------------------------
# Lazy provider singletons (same pattern as NiceGUI app)
# ---------------------------------------------------------------------------

_config: DashboardConfig | None = None
_health_provider: HealthProvider | None = None
_planning_provider: PlanningProvider | None = None
_governance_provider: GovernanceProvider | None = None
_growth_provider: GrowthProvider | None = None
_knowledge_provider: KnowledgeProvider | None = None
_history_store: HistoryStore | None = None
_queue_manager: ResearchQueueManager | None = None


def _get_config() -> DashboardConfig:
    global _config
    if _config is None:
        _config = DashboardConfig()
    return _config


def _get_health() -> HealthProvider:
    global _health_provider
    if _health_provider is None:
        _health_provider = HealthProvider(_get_config())
    return _health_provider


def _get_planning() -> PlanningProvider:
    global _planning_provider
    if _planning_provider is None:
        _planning_provider = PlanningProvider(_get_config())
    return _planning_provider


def _get_governance() -> GovernanceProvider:
    global _governance_provider
    if _governance_provider is None:
        _governance_provider = GovernanceProvider(_get_config())
    return _governance_provider


def _get_growth() -> GrowthProvider:
    global _growth_provider
    if _growth_provider is None:
        _growth_provider = GrowthProvider(_get_config())
    return _growth_provider


def _get_knowledge() -> KnowledgeProvider:
    global _knowledge_provider
    if _knowledge_provider is None:
        _knowledge_provider = KnowledgeProvider(_get_config())
    return _knowledge_provider


def _get_history() -> HistoryStore:
    global _history_store
    if _history_store is None:
        _history_store = HistoryStore(_get_config())
    return _history_store


def _get_queue() -> ResearchQueueManager:
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = ResearchQueueManager(_get_config())
    return _queue_manager


# ---------------------------------------------------------------------------
# Helper: health status → badge class
# ---------------------------------------------------------------------------

_STATUS_BADGE: dict[str, tuple[str, str]] = {
    "healthy": ("badge-green", "Healthy"),
    "attention": ("badge-yellow", "Attention"),
    "critical": ("badge-red", "Critical"),
    "unknown": ("badge-grey", "Unknown"),
}

_DREYFUS = {1: "Novice", 2: "Beginner", 3: "Competent", 4: "Proficient", 5: "Expert"}

_DIM_ICONS = {
    "tests": "🧪",
    "packages": "📦",
    "dependencies": "🔗",
    "architecture": "🏗️",
    "knowledge_health": "📚",
    "security": "🔒",
    "sprint_hygiene": "🏃",
}

_ASI_COLORS = {
    "MITIGATED": ("badge-green", "#4ecca3", 100),
    "PARTIAL": ("badge-yellow", "#ffc107", 50),
    "VULNERABLE": ("badge-red", "#f44336", 25),
    "NOT_ASSESSED": ("badge-grey", "#9e9e9e", 0),
}

_COMPLIANCE_STATUS = {
    "active": ("badge-green", "Actief"),
    "attention": ("badge-yellow", "Aandacht"),
    "violation": ("badge-red", "Overtreding"),
}


def _health_to_level(status: HealthStatus) -> str:
    mapping = {
        HealthStatus.HEALTHY: "healthy",
        HealthStatus.ATTENTION: "attention",
        HealthStatus.CRITICAL: "critical",
    }
    return mapping.get(status, "unknown")


# ---------------------------------------------------------------------------
# Helper: build KPI and domain data for overview
# ---------------------------------------------------------------------------


def _build_kpis(health, sprint, inbox_items, compliance, freshness):
    """Build list of KPI dicts for the template."""
    kpis = [
        {
            "label": "Tests",
            "value": sprint.test_baseline,
            "color": "#4ecca3",
            "sub": "baseline",
        },
        {
            "label": "Sprint",
            "value": f"#{sprint.nummer}",
            "color": "#2196f3",
            "sub": sprint.naam or "idle",
        },
        {
            "label": "Inbox",
            "value": len(inbox_items),
            "color": "#ffc107" if inbox_items else "#4ecca3",
            "sub": "intake items",
        },
        {
            "label": "Health",
            "value": health.overall.value.capitalize(),
            "color": "#4ecca3" if health.overall == HealthStatus.HEALTHY else "#ffc107",
            "sub": f"{len(health.checks)}/7 dimensies",
        },
        {
            "label": "Fase",
            "value": sprint.fase or "?",
            "color": "#2196f3",
            "sub": "actief",
        },
    ]
    if compliance:
        kpis.append(
            {
                "label": "Compliance",
                "value": f"{compliance.percentage:.0f}%",
                "color": "#4ecca3" if compliance.percentage >= 80 else "#ffc107",
                "sub": f"{compliance.active}/{compliance.total} actief",
            }
        )
    if freshness:
        kpis.append(
            {
                "label": "Kennis Versheid",
                "value": f"{freshness.freshness_score:.0%}",
                "color": "#4ecca3" if freshness.freshness_score >= 0.7 else "#ffc107",
                "sub": f"{freshness.total_articles} items, {freshness.fresh_count} vers",
            }
        )
    return kpis


def _build_domains(health, sprint, inbox_items, compliance, growth_data, freshness):
    """Build list of DomainStatus dicts for System Pulse grid."""
    # Governance
    gov_status, gov_summary, gov_metric = "unknown", "DEV_CONSTITUTION", ""
    if compliance:
        if compliance.percentage >= 80:
            gov_status = "healthy"
        elif compliance.percentage >= 50:
            gov_status = "attention"
        else:
            gov_status = "critical"
        gov_summary = f"{compliance.active}/{compliance.total} actief"
        gov_metric = f"compliance {compliance.percentage:.0f}%"

    # Growth
    growth_status, growth_summary, growth_metric = "unknown", "Developer groei", ""
    if growth_data:
        avg_level = sum(lv for _, lv in growth_data) / len(growth_data)
        broad_count = sum(1 for _, lv in growth_data if lv >= 2)
        deep_count = sum(1 for _, lv in growth_data if lv >= 3)
        growth_status = "healthy" if avg_level >= 2 else "attention"
        growth_summary = f"Level {avg_level:.1f} avg"
        growth_metric = f"{broad_count} broad, {deep_count} deep"

    # Knowledge
    k_status, k_summary, k_metric = "unknown", "Kennisbank", ""
    if freshness:
        if freshness.total_articles == 0:
            k_status = "attention"
        elif freshness.freshness_score >= 0.7:
            k_status = "healthy"
        else:
            k_status = "attention"
        k_summary = f"{freshness.total_articles} artikelen, {freshness.freshness_score:.0%} vers"
        k_metric = (
            f"{freshness.fresh_count} vers, "
            f"{freshness.aging_count} verouderend, "
            f"{freshness.stale_count} verlopen"
        )

    return [
        {
            "name": "Health",
            "status": _health_to_level(health.overall),
            "summary": f"{len(health.checks)} dimensies, {len(health.alert_findings)} alerts",
            "metric": (
                f"{len(health.p1_findings)} P1, {len(health.p2_findings)} P2"
                if health.alert_findings
                else "geen alerts"
            ),
        },
        {
            "name": "Sprint & Planning",
            "status": "healthy" if sprint.nummer > 0 else "unknown",
            "summary": f"Sprint #{sprint.nummer}" if sprint.nummer else "Geen sprint data",
            "metric": f"{sprint.fase}, 100% accuracy",
        },
        {
            "name": "Knowledge",
            "status": k_status,
            "summary": k_summary,
            "metric": k_metric,
        },
        {
            "name": "Governance",
            "status": gov_status,
            "summary": gov_summary,
            "metric": gov_metric,
        },
        {
            "name": "Growth",
            "status": growth_status,
            "summary": growth_summary,
            "metric": growth_metric,
        },
        {
            "name": "Research",
            "status": "attention" if inbox_items else "healthy",
            "summary": f"{len(inbox_items)} inbox items" if inbox_items else "Inbox leeg",
            "metric": "",
        },
    ]


def _build_activities(sprint, inbox_items):
    """Build activity feed list."""
    activities = []
    if sprint.nummer > 0:
        activities.append(
            {
                "color": "#4ecca3",
                "text": f"Sprint #{sprint.nummer} \u2014 {sprint.naam or 'afgerond'}",
                "detail": sprint.fase,
            }
        )
    for item in inbox_items[:3]:
        name = item.filename.replace("SPRINT_INTAKE_", "").replace(".md", "").replace("_", " ")
        activities.append(
            {
                "color": "#ffc107",
                "text": f"Inbox: {name[:40]}",
                "detail": f"{item.sprint_type} \u00b7 {item.node}",
            }
        )
    return activities


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def overview(request: Request):
    """Executive Summary — landing page."""
    health = _get_health().get_health_report()
    sprint = _get_planning().get_sprint_info()
    inbox_items = _get_planning().get_inbox_items()
    compliance = _get_governance().get_compliance_score()
    growth_data = _get_growth().get_skill_radar_data()
    freshness = _get_knowledge().get_freshness_summary()

    return templates.TemplateResponse(
        request,
        "overview.html",
        {
            "active_page": "overview",
            "kpis": _build_kpis(health, sprint, inbox_items, compliance, freshness),
            "domains": _build_domains(
                health, sprint, inbox_items, compliance, growth_data, freshness
            ),
            "activities": _build_activities(sprint, inbox_items),
            "status_badge": _STATUS_BADGE,
        },
    )


@app.post("/api/actions/refresh-health", response_class=HTMLResponse)
async def refresh_health(request: Request):
    """HTMX endpoint: invalidate health cache and return fresh partial."""
    provider = _get_health()
    provider.invalidate_cache()
    report = provider.get_health_report()

    checks = []
    for check in report.checks:
        level = _health_to_level(check.status)
        badge_cls, badge_label = _STATUS_BADGE.get(level, ("badge-grey", "Unknown"))
        checks.append(
            {
                "dimension": check.dimension,
                "status": level,
                "summary": check.summary,
                "badge_cls": badge_cls,
                "badge_label": badge_label,
            }
        )

    return templates.TemplateResponse(
        request,
        "partials/health_refresh.html",
        {
            "overall": report.overall.value.capitalize(),
            "overall_level": _health_to_level(report.overall),
            "checks": checks,
            "status_badge": _STATUS_BADGE,
        },
    )


# ---------------------------------------------------------------------------
# Health page
# ---------------------------------------------------------------------------


@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    """System Health — 7 dimensies."""
    provider = _get_health()
    report = provider.get_health_report()
    history = _get_history()

    # Save snapshot
    snapshot = HealthSnapshot.from_report(
        report,
        test_files=provider._count_test_files(),
        packages=provider._count_packages(),
    )
    history.save_snapshot(snapshot)
    snapshots = history.load_snapshots()

    # Build checks list
    checks = []
    for check in report.checks:
        level = _health_to_level(check.status)
        badge_cls, badge_label = _STATUS_BADGE.get(level, ("badge-grey", "Unknown"))
        findings = []
        if hasattr(check, "findings") and check.findings:
            for f in check.findings:
                findings.append(
                    {
                        "severity": f.severity.value,
                        "message": f.message,
                        "action": getattr(f, "recommended_action", ""),
                    }
                )
        checks.append(
            {
                "dimension": check.dimension,
                "icon": _DIM_ICONS.get(check.dimension, "📋"),
                "label": check.dimension.replace("_", " ").title(),
                "summary": check.summary,
                "badge_cls": badge_cls,
                "badge_label": badge_label,
                "findings": findings,
            }
        )

    # KPIs
    kpis = [
        {
            "label": "Overall",
            "value": report.overall.value.capitalize(),
            "color": ("#4ecca3" if report.overall == HealthStatus.HEALTHY else "#f44336"),
        },
        {
            "label": "Dimensies",
            "value": len(report.checks),
            "color": "#2196f3",
            "sub": "gecontroleerd",
        },
        {
            "label": "P1 Alerts",
            "value": len(report.p1_findings),
            "color": "#f44336" if report.p1_findings else "#4ecca3",
        },
        {
            "label": "P2 Alerts",
            "value": len(report.p2_findings),
            "color": "#ffc107" if report.p2_findings else "#4ecca3",
        },
    ]

    # Snapshot table
    snapshot_rows = [
        {
            "timestamp": s.timestamp[:10],
            "overall": s.overall.capitalize(),
            "dimensions": s.dimensions_checked,
            "p1": s.p1_count,
            "p2": s.p2_count,
            "tests": s.test_files,
        }
        for s in reversed(snapshots[-10:])
    ]

    # Trend data for Plotly (JSON-encoded for template)
    trend_data = None
    if snapshots:
        trend_data = json.dumps(
            {
                "timestamps": [s.timestamp[:10] for s in snapshots],
                "tests": [s.test_files for s in snapshots],
                "packages": [s.packages for s in snapshots],
                "knowledge": [s.knowledge_items for s in snapshots],
            }
        )

    return templates.TemplateResponse(
        request,
        "health.html",
        {
            "active_page": "health",
            "kpis": kpis,
            "checks": checks,
            "snapshot_rows": snapshot_rows,
            "trend_data": trend_data,
            "status_badge": _STATUS_BADGE,
        },
    )


# ---------------------------------------------------------------------------
# Planning page
# ---------------------------------------------------------------------------


@app.get("/planning", response_class=HTMLResponse)
async def planning_page(request: Request):
    """Sprint & Planning."""
    provider = _get_planning()
    sprint = provider.get_sprint_info()
    inbox_items = provider.get_inbox_items()
    fase_progress = provider.get_fase_progress()
    metrics = provider.get_derived_metrics()
    labels, deltas = provider.get_velocity_data()
    ct_labels, ct_days = provider.get_cycle_time_data()
    history = provider.get_sprint_history()

    kpis = [
        {
            "label": "Sprints",
            "value": metrics.get("sprints_afgerond", sprint.nummer),
            "color": "#64ffda",
            "sub": "afgerond",
        },
        {
            "label": "Accuracy",
            "value": str(metrics.get("estimation_accuracy", "—")),
            "color": "#4ecca3",
            "sub": "schattingen",
        },
        {
            "label": "Avg Test Δ",
            "value": f"+{metrics.get('avg_test_delta', 0)}",
            "color": "#2196f3",
            "sub": "per sprint",
        },
        {
            "label": "Inbox",
            "value": len(inbox_items),
            "color": "#ffc107" if inbox_items else "#4ecca3",
            "sub": "items",
        },
        {
            "label": "Fase",
            "value": sprint.fase or "?",
            "color": "#ce93d8",
            "sub": "actief",
        },
    ]

    # Fase pipeline
    fase_names = {
        0: "Fundament",
        1: "Kernagents",
        2: "Skills",
        3: "Knowledge",
        4: "Verbindingen",
        5: "Uitbreiding",
    }
    pipeline = []
    for i, (name, done) in enumerate(fase_progress):
        prev_done = all(fase_progress[j][1] for j in range(i))
        is_active = not done and prev_done
        pipeline.append(
            {
                "nummer": i,
                "name": fase_names.get(i, name),
                "done": done,
                "active": is_active,
            }
        )

    # Kanban columns
    inbox_kanban = [
        {
            "title": item.filename.replace("SPRINT_INTAKE_", "")
            .replace(".md", "")
            .replace("_", " ")[:40],
            "type": item.sprint_type,
            "node": item.node,
        }
        for item in inbox_items[:5]
    ]
    actief_item = (
        {"title": f"#{sprint.nummer} {sprint.naam}", "type": "ACTIEF"} if sprint.naam else None
    )
    done_items = [
        {
            "title": f"#{h.nummer} {h.naam[:30]}",
            "type": h.sprint_type,
            "delta": (f"+{h.tests_delta}" if h.tests_delta > 0 else ""),
        }
        for h in reversed(history[-3:])
    ]

    # Velocity chart data
    velocity_data = None
    if labels:
        velocity_data = json.dumps({"labels": labels, "deltas": deltas})
    cycle_data = None
    if ct_labels:
        cycle_data = json.dumps({"labels": ct_labels, "days": ct_days})

    # History table
    history_rows = [
        {
            "nr": h.nummer,
            "naam": h.naam,
            "type": h.sprint_type,
            "size": h.size,
            "delta": (f"+{h.tests_delta}" if h.tests_delta > 0 else str(h.tests_delta)),
        }
        for h in history
    ]

    return templates.TemplateResponse(
        request,
        "planning.html",
        {
            "active_page": "planning",
            "kpis": kpis,
            "pipeline": pipeline,
            "inbox_kanban": inbox_kanban,
            "inbox_extra": max(0, len(inbox_items) - 5),
            "actief_item": actief_item,
            "done_items": done_items,
            "done_extra": max(0, len(history) - 3),
            "velocity_data": velocity_data,
            "cycle_data": cycle_data,
            "history_rows": history_rows,
        },
    )


# ---------------------------------------------------------------------------
# Knowledge page
# ---------------------------------------------------------------------------


@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request):
    """Knowledge & Kennisbank."""
    provider = _get_knowledge()
    freshness = provider.get_freshness_summary()
    grading = provider.get_grading_distribution()
    articles = provider.get_articles()
    coverage = provider.get_domain_coverage()

    kpis = [
        {
            "label": "Kennis-items",
            "value": freshness.total_articles,
            "color": "#2196f3",
        },
        {
            "label": "Versheid",
            "value": f"{freshness.freshness_score:.0%}",
            "color": ("#4ecca3" if freshness.freshness_score >= 0.7 else "#ffc107"),
            "sub": (f"{freshness.fresh_count} vers, " f"{freshness.aging_count} verouderend"),
        },
        {
            "label": "GOLD",
            "value": grading.get("GOLD", 0),
            "color": "#FFD700",
        },
        {
            "label": "SILVER",
            "value": grading.get("SILVER", 0),
            "color": "#C0C0C0",
        },
    ]

    article_list = [
        {
            "id": a.article_id,
            "title": a.title,
            "domain": a.domain,
            "grade": a.grade,
            "freshness_days": a.freshness_days,
            "freshness_color": a.freshness_color,
        }
        for a in articles
    ]

    # Coverage grouped by ring
    rings: dict[str, list] = {"core": [], "agent": [], "project": []}
    for c in coverage:
        rings.setdefault(c.ring, []).append(
            {
                "domain": c.domain.replace("_", " ").title(),
                "count": c.article_count,
                "score": c.coverage_score,
                "days": c.avg_freshness_days,
                "grades": {k: v for k, v in c.grade_distribution.items() if v > 0},
            }
        )

    return templates.TemplateResponse(
        request,
        "knowledge.html",
        {
            "active_page": "knowledge",
            "kpis": kpis,
            "articles": article_list,
            "rings": rings,
            "freshness": freshness,
        },
    )


# ---------------------------------------------------------------------------
# Knowledge detail page
# ---------------------------------------------------------------------------

_GRADE_COLORS = {
    "GOLD": "#FFD700",
    "SILVER": "#C0C0C0",
    "BRONZE": "#CD7F32",
    "SPECULATIVE": "#9e9e9e",
}


@app.get("/knowledge/{article_id:path}", response_class=HTMLResponse)
async def knowledge_detail(request: Request, article_id: str):
    """Artikel detail pagina."""
    provider = _get_knowledge()
    article = provider.get_article(article_id)

    if not article:
        return templates.TemplateResponse(
            request,
            "knowledge_detail.html",
            {
                "active_page": "knowledge",
                "article": None,
                "article_id": article_id,
            },
        )

    # Read markdown content
    md_content = ""
    knowledge_root = provider._knowledge_root
    md_path = knowledge_root / f"{article.file_path}.md"
    if md_path.exists():
        md_content = md_path.read_text(encoding="utf-8")

    # Related articles
    related = provider.get_articles(domain=article.domain)
    related = [
        {"id": r.article_id, "title": r.title}
        for r in related
        if r.article_id != article.article_id
    ][:5]

    return templates.TemplateResponse(
        request,
        "knowledge_detail.html",
        {
            "active_page": "knowledge",
            "article": {
                "id": article.article_id,
                "title": article.title,
                "grade": article.grade,
                "grade_color": _GRADE_COLORS.get(article.grade, "#9e9e9e"),
                "domain": article.domain.replace("_", " ").title(),
                "ring": article.ring.title(),
                "author": article.author,
                "date": article.date,
                "sprint": article.sprint,
                "sources": article.sources,
                "rq_tags": article.rq_tags,
                "freshness_days": article.freshness_days,
                "freshness_color": article.freshness_color,
            },
            "content": md_content,
            "related": related,
        },
    )


# ---------------------------------------------------------------------------
# Governance page
# ---------------------------------------------------------------------------


@app.get("/governance", response_class=HTMLResponse)
async def governance_page(request: Request):
    """Governance & Compliance."""
    provider = _get_governance()
    score = provider.get_compliance_score()
    articles = provider.get_article_statuses()
    security = provider.get_security_summary()
    asi_coverage = provider.get_asi_coverage()

    article_list = []
    for a in articles:
        badge_cls, badge_label = _COMPLIANCE_STATUS.get(a.status, ("badge-grey", "Onbekend"))
        article_list.append(
            {
                "id": a.article_id,
                "title": a.title,
                "description": a.description,
                "verification": a.verification,
                "badge_cls": badge_cls,
                "badge_label": badge_label,
            }
        )

    asi_bars = []
    for asi_id, status in sorted(asi_coverage.items()):
        badge_cls, color, width = _ASI_COLORS.get(status, ("badge-grey", "#9e9e9e", 0))
        asi_bars.append(
            {
                "id": asi_id,
                "status": status,
                "badge_cls": badge_cls,
                "color": color,
                "width": width,
            }
        )

    gauge_angle = int(score.percentage * 3.6)

    return templates.TemplateResponse(
        request,
        "governance.html",
        {
            "active_page": "governance",
            "score": score,
            "gauge_angle": gauge_angle,
            "articles": article_list,
            "security": security,
            "asi_bars": asi_bars,
        },
    )


# ---------------------------------------------------------------------------
# Growth page
# ---------------------------------------------------------------------------


@app.get("/growth", response_class=HTMLResponse)
async def growth_page(request: Request):
    """Developer Growth."""
    provider = _get_growth()
    radar_data = provider.get_skill_radar_data()
    broad, deep = provider.get_t_shape()
    challenges = provider.get_challenges()
    recommendations = provider.get_recommendations()
    sprint_count = provider.get_completed_sprint_count()

    avg_level = sum(lv for _, lv in radar_data) / len(radar_data) if radar_data else 0

    kpis = [
        {
            "label": "Fase",
            "value": "BOUWEN",
            "color": "#2196f3",
            "sub": "O-B-B model",
        },
        {
            "label": "Sprints",
            "value": sprint_count,
            "color": "#4ecca3",
            "sub": "afgerond",
        },
        {
            "label": "Avg Level",
            "value": f"{avg_level:.1f}",
            "color": "#2196f3",
            "sub": _DREYFUS.get(round(avg_level), ""),
        },
        {
            "label": "Domeinen",
            "value": len(radar_data),
            "color": "#64ffda",
            "sub": f"{len(broad)} broad, {len(deep)} deep",
        },
    ]

    # Radar chart data for Plotly
    radar_json = None
    if radar_data:
        domains = [d[0] for d in radar_data]
        levels = [d[1] for d in radar_data]
        domains_c = domains + [domains[0]]
        levels_c = levels + [levels[0]]
        target_c = [min(lv + 1, 5) for lv in levels] + [min(levels[0] + 1, 5)]
        radar_json = json.dumps(
            {
                "domains": domains_c,
                "levels": levels_c,
                "target": target_c,
            }
        )

    # Domain cards
    domain_cards = [
        {
            "name": name,
            "level": level,
            "label": _DREYFUS.get(level, "?"),
            "progress": level / 5.0 * 100,
            "next_label": _DREYFUS.get(min(level + 1, 5), "?"),
            "next_level": min(level + 1, 5),
        }
        for name, level in radar_data
    ]

    # Challenges grouped
    active_ch = [c for c in challenges if c.get("status") == "ACCEPTED"]
    proposed_ch = [c for c in challenges if c.get("status") == "PROPOSED"]
    completed_ch = [c for c in challenges if c.get("status") == "COMPLETED"][:3]

    return templates.TemplateResponse(
        request,
        "growth.html",
        {
            "active_page": "growth",
            "kpis": kpis,
            "radar_json": radar_json,
            "domain_cards": domain_cards,
            "broad": broad,
            "deep": deep,
            "active_challenges": active_ch,
            "proposed_challenges": proposed_ch,
            "completed_challenges": completed_ch,
            "recommendations": recommendations[:6],
        },
    )


# ---------------------------------------------------------------------------
# Research page
# ---------------------------------------------------------------------------


@app.get("/research", response_class=HTMLResponse)
async def research_page(request: Request):
    """Research & Kennisverzoeken."""
    qm = _get_queue()
    agent_items = qm.list_items(stream=RequestStream.AGENT.value)
    user_items = qm.list_items(stream=RequestStream.USER.value)
    auto_items = qm.list_items(stream=RequestStream.AUTO.value)

    def _item_dict(item):
        return {
            "id": item.item_id,
            "topic": item.topic,
            "domain": item.domain.replace("_", " ").title(),
            "depth": item.depth,
            "status": item.status,
            "stream": item.stream,
            "priority": item.priority,
            "created": item.created_at[:10] if item.created_at else "",
        }

    return templates.TemplateResponse(
        request,
        "research.html",
        {
            "active_page": "research",
            "agent_items": [_item_dict(i) for i in agent_items],
            "user_items": [_item_dict(i) for i in user_items],
            "auto_items": [_item_dict(i) for i in auto_items],
        },
    )


# ---------------------------------------------------------------------------
# Research detail page
# ---------------------------------------------------------------------------


@app.get("/research/{item_id}", response_class=HTMLResponse)
async def research_detail(request: Request, item_id: str):
    """Research detail pagina."""
    item = _get_queue().get_item(item_id)

    if not item:
        return templates.TemplateResponse(
            request,
            "research_detail.html",
            {
                "active_page": "research",
                "item": None,
                "item_id": item_id,
            },
        )

    return templates.TemplateResponse(
        request,
        "research_detail.html",
        {
            "active_page": "research",
            "item": {
                "id": item.item_id,
                "topic": item.topic,
                "domain": item.domain.replace("_", " ").title(),
                "depth": item.depth,
                "status": item.status.upper(),
                "stream": item.stream.upper(),
                "priority": item.priority,
                "background": item.background,
                "research_questions": item.research_questions,
                "scope_in": item.scope_in,
                "scope_out": item.scope_out,
                "description": item.description,
                "review_notes": item.review_notes,
                "rejection_reason": item.rejection_reason,
                "completed_articles": item.completed_articles,
                "related_articles": item.related_articles,
                "expected_grade": item.expected_grade,
                "document_category": item.document_category,
                "source_agent": item.source_agent,
                "deadline": item.deadline,
                "created_at": (item.created_at[:10] if item.created_at else ""),
                "updated_at": (item.updated_at[:10] if item.updated_at else ""),
                "status_history": list(reversed(item.status_history)),
            },
        },
    )
