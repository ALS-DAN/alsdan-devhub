"""Tests voor NodeRegistry."""

import pytest

from devhub_core.registry import NodeConfig, NodeRegistry
from devhub_core.contracts.node_interface import (
    NodeHealth,
    NodeDocStatus,
    NodeInterface,
    NodeReport,
    TestResult,
)


# ---------------------------------------------------------------------------
# NodeConfig
# ---------------------------------------------------------------------------


class TestNodeConfig:
    def test_valid(self):
        cfg = NodeConfig(
            node_id="boris-buurts",
            name="BORIS",
            path="/tmp/boris",
            adapter="devhub_core.adapters.boris_adapter.BorisAdapter",
        )
        assert cfg.enabled is True
        assert cfg.devagents_enabled is False

    def test_empty_node_id(self):
        with pytest.raises(ValueError, match="node_id"):
            NodeConfig(node_id="", name="X", path="/tmp", adapter="x.Y")

    def test_empty_path(self):
        with pytest.raises(ValueError, match="path"):
            NodeConfig(node_id="x", name="X", path="", adapter="x.Y")


# ---------------------------------------------------------------------------
# Fake adapter for testing
# ---------------------------------------------------------------------------


class FakeAdapter(NodeInterface):
    """Test adapter die geen extern systeem nodig heeft."""

    def __init__(self, path: str) -> None:
        self.path = path

    def get_report(self) -> NodeReport:
        return NodeReport(
            node_id="fake",
            timestamp="2026-03-23T00:00:00Z",
            health=NodeHealth(
                status="UP", components={}, test_count=0, test_pass_rate=0.0, coverage_pct=0.0
            ),
            doc_status=NodeDocStatus(total_pages=0, stale_pages=0, diataxis_coverage={}),
        )

    def get_health(self) -> NodeHealth:
        return NodeHealth(
            status="UP", components={}, test_count=0, test_pass_rate=0.0, coverage_pct=0.0
        )

    def list_docs(self):
        return []

    def run_tests(self):
        return TestResult(total=0, passed=0, failed=0, errors=0, duration_seconds=0.0)


# ---------------------------------------------------------------------------
# NodeRegistry
# ---------------------------------------------------------------------------


class TestNodeRegistry:
    def test_register_and_retrieve(self):
        registry = NodeRegistry()
        cfg = NodeConfig(
            node_id="test", name="Test", path="/tmp", adapter="tests.test_registry.FakeAdapter"
        )
        registry.register(cfg)

        assert registry.get_config("test") == cfg
        assert len(registry.list_nodes()) == 1

    def test_unregister(self):
        registry = NodeRegistry()
        cfg = NodeConfig(node_id="test", name="Test", path="/tmp", adapter="x.Y")
        registry.register(cfg)
        registry.unregister("test")
        assert registry.get_config("test") is None
        assert len(registry.list_nodes()) == 0

    def test_list_enabled(self):
        registry = NodeRegistry()
        cfg1 = NodeConfig(node_id="a", name="A", path="/tmp", adapter="x.Y", enabled=True)
        cfg2 = NodeConfig(node_id="b", name="B", path="/tmp", adapter="x.Y", enabled=False)
        registry.register(cfg1)
        registry.register(cfg2)
        assert len(registry.list_enabled()) == 1

    def test_get_adapter_unknown_node(self):
        registry = NodeRegistry()
        with pytest.raises(KeyError, match="not registered"):
            registry.get_adapter("nonexistent")

    def test_get_adapter_lazy_instantiation(self):
        registry = NodeRegistry()
        cfg = NodeConfig(
            node_id="test",
            name="Test",
            path="/tmp",
            adapter="tests.test_registry.FakeAdapter",
        )
        registry.register(cfg)
        adapter = registry.get_adapter("test")
        assert isinstance(adapter, FakeAdapter)
        # Second call should return cached instance
        adapter2 = registry.get_adapter("test")
        assert adapter is adapter2

    def test_get_report_via_registry(self):
        registry = NodeRegistry()
        cfg = NodeConfig(
            node_id="test",
            name="Test",
            path="/tmp",
            adapter="tests.test_registry.FakeAdapter",
        )
        registry.register(cfg)
        report = registry.get_report("test")
        assert report.node_id == "fake"

    def test_load_from_yaml(self, tmp_path):
        config_file = tmp_path / "nodes.yml"
        config_file.write_text("""
nodes:
  - node_id: yaml-test
    name: YAML Test
    path: /tmp/test
    adapter: tests.test_registry.FakeAdapter
    enabled: true
    tags:
      - test
""")
        registry = NodeRegistry(config_path=config_file)
        assert len(registry.list_nodes()) == 1
        assert registry.get_config("yaml-test") is not None

    def test_to_dict(self):
        registry = NodeRegistry()
        cfg = NodeConfig(node_id="test", name="Test", path="/tmp", adapter="x.Y", tags=["tag1"])
        registry.register(cfg)
        d = registry.to_dict()
        assert "test" in d
        assert d["test"]["tags"] == ["tag1"]

    def test_get_report_unknown_node_raises_key_error(self):
        """get_report() should propagate KeyError for non-existent node IDs."""
        registry = NodeRegistry()
        with pytest.raises(KeyError, match="nonexistent-node"):
            registry.get_report("nonexistent-node")

    def test_invalid_adapter_import(self):
        registry = NodeRegistry()
        cfg = NodeConfig(node_id="bad", name="Bad", path="/tmp", adapter="nonexistent.module.Class")
        registry.register(cfg)
        with pytest.raises(ImportError, match="Cannot load adapter"):
            registry.get_adapter("bad")
