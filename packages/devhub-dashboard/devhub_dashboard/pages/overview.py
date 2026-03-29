"""Executive Summary pagina — smart KPI strip, system pulse, activity feed."""

from __future__ import annotations

from devhub_core.contracts.node_interface import HealthStatus

from nicegui import ui

from devhub_dashboard.components.kpi_card import kpi_card
from devhub_dashboard.components.status_badge import StatusLevel, status_badge
from devhub_dashboard.data.knowledge_provider import KnowledgeProvider
from devhub_dashboard.data.providers import (
    DomainStatus,
    GovernanceProvider,
    GrowthProvider,
    HealthProvider,
    PlanningProvider,
)


def _health_to_badge(status: HealthStatus) -> StatusLevel:
    mapping: dict[HealthStatus, StatusLevel] = {
        HealthStatus.HEALTHY: "healthy",
        HealthStatus.ATTENTION: "attention",
        HealthStatus.CRITICAL: "critical",
    }
    return mapping.get(status, "unknown")


def overview_page(
    health_provider: HealthProvider,
    planning_provider: PlanningProvider,
    governance_provider: GovernanceProvider | None = None,
    growth_provider: GrowthProvider | None = None,
    knowledge_provider: KnowledgeProvider | None = None,
) -> None:
    """Render de Executive Summary pagina."""
    # Data ophalen
    health = health_provider.get_health_report()
    sprint = planning_provider.get_sprint_info()
    inbox_items = planning_provider.get_inbox_items()

    # Governance en Growth data (optioneel)
    compliance = None
    if governance_provider:
        compliance = governance_provider.get_compliance_score()

    growth_data = None
    if growth_provider:
        growth_data = growth_provider.get_skill_radar_data()

    # Header
    ui.label("Executive Summary").classes("text-h4 q-mb-md")

    # Smart KPI Strip (7 cards)
    with ui.row().classes("gap-4 q-mb-lg flex-wrap"):
        kpi_card(
            "Tests",
            sprint.test_baseline,
            icon="science",
            color="positive",
            subtitle="baseline",
        )
        kpi_card(
            "Packages",
            health_provider._count_packages(),
            icon="inventory_2",
            color="primary",
            subtitle="workspace",
        )
        kpi_card(
            "Sprint",
            f"#{sprint.nummer}",
            icon="sprint",
            color="info",
            subtitle=sprint.naam or "idle",
        )
        kpi_card(
            "Inbox",
            len(inbox_items),
            icon="inbox",
            color="warning" if inbox_items else "positive",
            subtitle="intake items",
        )
        kpi_card(
            "Health",
            health.overall.value.capitalize(),
            icon="monitor_heart",
            color="positive" if health.overall == HealthStatus.HEALTHY else "warning",
            subtitle=f"{len(health.checks)}/7 dimensies",
        )
        kpi_card(
            "Fase",
            sprint.fase or "?",
            icon="flag",
            color="info",
            subtitle="actief",
        )
        if compliance:
            kpi_card(
                "Compliance",
                f"{compliance.percentage:.0f}%",
                icon="shield",
                color="positive" if compliance.percentage >= 80 else "warning",
                subtitle=f"{compliance.active}/{compliance.total} actief",
            )

        # Knowledge freshness KPI
        if knowledge_provider:
            freshness = knowledge_provider.get_freshness_summary()
            kpi_card(
                "Kennis Versheid",
                f"{freshness.freshness_score:.0%}",
                icon="library_books",
                color="positive" if freshness.freshness_score >= 0.7 else "warning",
                subtitle=f"{freshness.total_articles} items, {freshness.fresh_count} vers",
            )

    # System Pulse (3x2 domain status grid)
    ui.label("System Pulse").classes("text-h5 q-mb-sm")
    domains = _build_domain_statuses(
        health,
        sprint,
        inbox_items,
        compliance,
        growth_data,
        knowledge_provider=knowledge_provider,
    )
    with ui.grid(columns=3).classes("gap-4 q-mb-lg"):
        for domain in domains:
            _domain_color = {
                "healthy": "positive",
                "attention": "warning",
                "critical": "negative",
                "unknown": "grey-5",
            }.get(domain.status, "grey-5")

            with ui.card().classes("p-3").style(f"border-left: 3px solid var(--q-{_domain_color})"):
                with ui.row().classes("items-center justify-between"):
                    ui.label(domain.name).classes("text-subtitle1 font-bold")
                    status_badge(domain.status, domain.summary)  # type: ignore[arg-type]
                if domain.metric:
                    ui.label(domain.metric).classes("text-xs text-grey-6 mt-1")

    # Recente Activiteit feed (filesystem-based voor nu)
    ui.label("Recente Activiteit").classes("text-h5 q-mb-sm")
    _render_activity_feed(sprint, inbox_items)


def _build_domain_statuses(
    health,
    sprint,
    inbox_items,
    compliance=None,
    growth_data=None,
    knowledge_provider=None,
) -> list[DomainStatus]:
    """Bouw domein-statuslijst met echte data uit alle providers."""
    # Governance status
    gov_status: StatusLevel = "unknown"
    gov_summary = "DEV_CONSTITUTION"
    gov_metric = "details op /governance"
    if compliance:
        if compliance.percentage >= 80:
            gov_status = "healthy"
        elif compliance.percentage >= 50:
            gov_status = "attention"
        else:
            gov_status = "critical"
        gov_summary = f"{compliance.active}/{compliance.total} actief"
        gov_metric = f"compliance {compliance.percentage:.0f}%"

    # Growth status
    growth_status: StatusLevel = "unknown"
    growth_summary = "Developer groei"
    growth_metric = "details op /growth"
    if growth_data:
        avg_level = sum(lv for _, lv in growth_data) / len(growth_data)
        broad_count = sum(1 for _, lv in growth_data if lv >= 2)
        deep_count = sum(1 for _, lv in growth_data if lv >= 3)
        growth_status = "healthy" if avg_level >= 2 else "attention"
        growth_summary = f"Level {avg_level:.1f} avg"
        growth_metric = f"{broad_count} broad, {deep_count} deep"

    return [
        DomainStatus(
            name="Health",
            status=_health_to_badge(health.overall),
            summary=f"{len(health.checks)} dimensies, {len(health.alert_findings)} alerts",
            metric=(
                f"{len(health.p1_findings)} P1, {len(health.p2_findings)} P2"
                if health.alert_findings
                else "geen alerts"
            ),
        ),
        DomainStatus(
            name="Sprint & Planning",
            status="healthy" if sprint.nummer > 0 else "unknown",
            summary=f"Sprint #{sprint.nummer}" if sprint.nummer else "Geen sprint data",
            metric=f"{sprint.fase}, 100% accuracy",
        ),
        DomainStatus(
            name="Knowledge",
            status=_knowledge_status(knowledge_provider),
            summary=_knowledge_summary(knowledge_provider),
            metric=_knowledge_metric(knowledge_provider),
        ),
        DomainStatus(
            name="Governance",
            status=gov_status,
            summary=gov_summary,
            metric=gov_metric,
        ),
        DomainStatus(
            name="Growth",
            status=growth_status,
            summary=growth_summary,
            metric=growth_metric,
        ),
        DomainStatus(
            name="Research",
            status="attention" if inbox_items else "healthy",
            summary=f"{len(inbox_items)} inbox items" if inbox_items else "Inbox leeg",
        ),
    ]


def _knowledge_status(knowledge_provider) -> StatusLevel:
    if not knowledge_provider:
        return "unknown"
    f = knowledge_provider.get_freshness_summary()
    if f.total_articles == 0:
        return "attention"
    if f.freshness_score >= 0.7:
        return "healthy"
    return "attention"


def _knowledge_summary(knowledge_provider) -> str:
    if not knowledge_provider:
        return "Kennisbank"
    f = knowledge_provider.get_freshness_summary()
    return f"{f.total_articles} artikelen, {f.freshness_score:.0%} vers"


def _knowledge_metric(knowledge_provider) -> str:
    if not knowledge_provider:
        return "details op /knowledge"
    f = knowledge_provider.get_freshness_summary()
    return f"{f.fresh_count} vers, {f.aging_count} verouderend, {f.stale_count} verlopen"


def _render_activity_feed(sprint, inbox_items) -> None:
    """Render recente activiteit feed (filesystem-based)."""
    activities = []

    # Sprint info als activiteit
    if sprint.nummer > 0:
        activities.append(
            (
                "positive",
                f"Sprint #{sprint.nummer} — {sprint.naam or 'afgerond'}",
                sprint.fase,
            )
        )

    # Inbox items als activiteit
    for item in inbox_items[:3]:
        name = item.filename.replace("SPRINT_INTAKE_", "").replace(".md", "").replace("_", " ")
        activities.append(
            (
                "warning",
                f"Inbox: {name[:40]}",
                f"{item.sprint_type} · {item.node}",
            )
        )

    if not activities:
        ui.label("Geen recente activiteit.").classes("text-grey-6 italic")
        return

    with ui.card().classes("p-4 w-full"):
        for color, text, detail in activities:
            with (
                ui.row()
                .classes("items-start gap-3 py-2")
                .style("border-bottom: 1px solid rgba(255,255,255,0.05)")
            ):
                ui.icon("circle", color=color).classes("text-xs mt-1")
                with ui.column().classes("gap-0"):
                    ui.label(text).classes("text-sm")
                    ui.label(detail).classes("text-xs text-grey-6")
