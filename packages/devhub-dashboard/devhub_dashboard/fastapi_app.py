"""DevHub Dashboard — FastAPI + Jinja2 + HTMX app (Fase 1 PoC)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from devhub_core.contracts.node_interface import HealthStatus

from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider
from devhub_dashboard.data.providers import (
    GovernanceProvider,
    GrowthProvider,
    HealthProvider,
    PlanningProvider,
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


# ---------------------------------------------------------------------------
# Helper: health status → badge class
# ---------------------------------------------------------------------------

_STATUS_BADGE: dict[str, tuple[str, str]] = {
    "healthy": ("badge-green", "Healthy"),
    "attention": ("badge-yellow", "Attention"),
    "critical": ("badge-red", "Critical"),
    "unknown": ("badge-grey", "Unknown"),
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
