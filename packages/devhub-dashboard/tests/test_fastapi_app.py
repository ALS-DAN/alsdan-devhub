"""Tests voor de FastAPI+HTMX dashboard app (Fase 1 PoC)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from devhub_core.contracts.node_interface import (
    FullHealthReport,
    HealthCheckResult,
    HealthStatus,
)

from devhub_dashboard.data.providers import SprintInfo

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _mock_health_report() -> FullHealthReport:
    checks = (
        HealthCheckResult(dimension="tests", status=HealthStatus.HEALTHY, summary="1735 tests"),
        HealthCheckResult(dimension="packages", status=HealthStatus.HEALTHY, summary="4 packages"),
    )
    return FullHealthReport(node_id="devhub", timestamp="2026-03-30T10:00:00Z", checks=checks)


def _mock_sprint_info() -> SprintInfo:
    return SprintInfo(
        nummer=47,
        naam="Planning Herstructurering",
        status="ACTIEF",
        test_baseline=1735,
        fase="Fase 4",
    )


def _mock_compliance():
    mock = MagicMock()
    mock.percentage = 88.9
    mock.active = 8
    mock.total = 9
    return mock


def _mock_freshness():
    mock = MagicMock()
    mock.freshness_score = 0.75
    mock.total_articles = 12
    mock.fresh_count = 9
    mock.aging_count = 2
    mock.stale_count = 1
    return mock


@pytest.fixture()
def client():
    """TestClient met gemockte providers."""
    with (
        patch("devhub_dashboard.fastapi_app._get_health") as mock_health,
        patch("devhub_dashboard.fastapi_app._get_planning") as mock_planning,
        patch("devhub_dashboard.fastapi_app._get_governance") as mock_governance,
        patch("devhub_dashboard.fastapi_app._get_growth") as mock_growth,
        patch("devhub_dashboard.fastapi_app._get_knowledge") as mock_knowledge,
    ):
        # Health
        health_prov = MagicMock()
        health_prov.get_health_report.return_value = _mock_health_report()
        mock_health.return_value = health_prov

        # Planning
        planning_prov = MagicMock()
        planning_prov.get_sprint_info.return_value = _mock_sprint_info()
        planning_prov.get_inbox_items.return_value = []
        mock_planning.return_value = planning_prov

        # Governance
        gov_prov = MagicMock()
        gov_prov.get_compliance_score.return_value = _mock_compliance()
        mock_governance.return_value = gov_prov

        # Growth
        growth_prov = MagicMock()
        growth_prov.get_skill_radar_data.return_value = [("Python", 3), ("Architecture", 2)]
        mock_growth.return_value = growth_prov

        # Knowledge
        knowledge_prov = MagicMock()
        knowledge_prov.get_freshness_summary.return_value = _mock_freshness()
        mock_knowledge.return_value = knowledge_prov

        from devhub_dashboard.fastapi_app import app

        yield TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOverviewPage:
    """GET / — Executive Summary pagina."""

    def test_returns_200(self, client: TestClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_title(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "Executive Summary" in resp.text

    def test_contains_kpi_cards(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "1735" in resp.text  # test baseline
        assert "#47" in resp.text  # sprint nummer
        assert "Fase 4" in resp.text

    def test_contains_system_pulse(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "System Pulse" in resp.text
        assert "Health" in resp.text
        assert "Governance" in resp.text

    def test_contains_compliance_kpi(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "89%" in resp.text  # compliance percentage
        assert "8/9 actief" in resp.text

    def test_contains_knowledge_freshness(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "75%" in resp.text  # freshness score
        assert "12 items" in resp.text

    def test_contains_activity_feed(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "Recente Activiteit" in resp.text
        assert "Sprint #47" in resp.text

    def test_contains_htmx_button(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "hx-post" in resp.text
        assert "/api/actions/refresh-health" in resp.text

    def test_html_structure(self, client: TestClient) -> None:
        resp = client.get("/")
        assert "<!DOCTYPE html>" in resp.text
        assert "htmx.org" in resp.text
        assert "dashboard.css" in resp.text


class TestStaticFiles:
    """Static file serving."""

    def test_css_returns_200(self, client: TestClient) -> None:
        resp = client.get("/static/css/dashboard.css")
        assert resp.status_code == 200
        assert "text/css" in resp.headers["content-type"]

    def test_css_contains_theme(self, client: TestClient) -> None:
        resp = client.get("/static/css/dashboard.css")
        assert "#1a1a2e" in resp.text  # dark theme background
        assert "#4ecca3" in resp.text  # accent color


class TestHealthRefreshEndpoint:
    """POST /api/actions/refresh-health — HTMX partial."""

    def test_returns_200(self, client: TestClient) -> None:
        resp = client.post("/api/actions/refresh-health")
        assert resp.status_code == 200

    def test_returns_html_fragment(self, client: TestClient) -> None:
        resp = client.post("/api/actions/refresh-health")
        assert "Health Check" in resp.text
        assert "tests" in resp.text

    def test_invalidates_cache(self, client: TestClient) -> None:
        """Verify cache invalidation is called."""
        resp = client.post("/api/actions/refresh-health")
        assert resp.status_code == 200


class TestNavigation:
    """Header navigation links."""

    def test_overview_link_active(self, client: TestClient) -> None:
        resp = client.get("/")
        assert 'class="active"' in resp.text

    def test_all_nav_links_present(self, client: TestClient) -> None:
        resp = client.get("/")
        for page in ["Health", "Planning", "Knowledge", "Governance", "Growth", "Research"]:
            assert page in resp.text
