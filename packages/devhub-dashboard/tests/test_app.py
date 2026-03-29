"""Tests voor de dashboard app module."""

from devhub_dashboard.app import _get_config, _get_health_provider, _get_planning_provider
from devhub_dashboard.config import DashboardConfig
from devhub_dashboard.data.providers import HealthProvider, PlanningProvider

import devhub_dashboard.app as app_module


class TestAppProviders:
    def setup_method(self):
        """Reset global state voor elke test."""
        app_module._config = None
        app_module._health_provider = None
        app_module._planning_provider = None

    def test_get_config_returns_default(self):
        config = _get_config()
        assert isinstance(config, DashboardConfig)
        assert config.port == 8765

    def test_get_config_is_cached(self):
        c1 = _get_config()
        c2 = _get_config()
        assert c1 is c2

    def test_get_health_provider(self):
        provider = _get_health_provider()
        assert isinstance(provider, HealthProvider)

    def test_get_health_provider_is_cached(self):
        p1 = _get_health_provider()
        p2 = _get_health_provider()
        assert p1 is p2

    def test_get_planning_provider(self):
        provider = _get_planning_provider()
        assert isinstance(provider, PlanningProvider)

    def test_get_planning_provider_is_cached(self):
        p1 = _get_planning_provider()
        p2 = _get_planning_provider()
        assert p1 is p2
