"""Tests voor DevOrchestrator."""

import json

from devhub_core.agents.orchestrator import DevOrchestrator, DIATAXIS_CATEGORIES
from devhub_core.contracts.node_interface import (
    NodeDocStatus,
    NodeHealth,
    NodeInterface,
    NodeReport,
    TestResult,
)
from devhub_core.registry import NodeConfig, NodeRegistry


# ---------------------------------------------------------------------------
# Fake adapter voor tests
# ---------------------------------------------------------------------------


class FakeAdapter(NodeInterface):
    def __init__(self, path: str) -> None:
        self.path = path

    def get_report(self) -> NodeReport:
        return NodeReport(
            node_id="fake-node",
            timestamp="2026-03-23T12:00:00Z",
            health=NodeHealth(
                status="UP", components={}, test_count=100, test_pass_rate=1.0, coverage_pct=75.0
            ),
            doc_status=NodeDocStatus(total_pages=10, stale_pages=1, diataxis_coverage={}),
        )

    def get_health(self) -> NodeHealth:
        return NodeHealth(
            status="UP", components={}, test_count=100, test_pass_rate=1.0, coverage_pct=75.0
        )

    def list_docs(self) -> list[str]:
        return ["index.md", "setup.md"]

    def run_tests(self) -> TestResult:
        return TestResult(total=100, passed=100, failed=0, errors=0, duration_seconds=5.0)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_registry_with_fake(tmp_path) -> NodeRegistry:
    registry = NodeRegistry()
    cfg = NodeConfig(
        node_id="fake-node",
        name="Fake",
        path=str(tmp_path),
        adapter="tests.test_orchestrator.FakeAdapter",
    )
    registry.register(cfg)
    return registry


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDevOrchestrator:
    def test_create_task(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        task = orch.create_task(
            description="Add LUMEN export",
            node_id="fake-node",
            scope_files=["agents/lumen_agent.py"],
            constraints=["geen main.py wijzigingen"],
        )

        assert task.task_id.startswith("TASK-")
        assert task.description == "Add LUMEN export"
        assert task.node_id == "fake-node"
        assert "agents/lumen_agent.py" in task.scope_files

    def test_task_written_to_scratchpad(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        orch.create_task(description="Test", node_id="fake-node")

        task_file = scratchpad / "current_task.json"
        assert task_file.exists()
        data = json.loads(task_file.read_text())
        assert data["description"] == "Test"

    def test_get_current_task(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        orch.create_task(description="Read back", node_id="fake-node")
        task = orch.get_current_task()

        assert task is not None
        assert task.description == "Read back"

    def test_get_current_task_empty(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        assert orch.get_current_task() is None

    def test_get_node_context(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        orch = DevOrchestrator(registry, scratchpad_path=tmp_path / "scratchpad")

        report = orch.get_node_context("fake-node")
        assert report.node_id == "fake-node"
        assert report.health.status == "UP"

    def test_decompose_for_docs(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        task = orch.create_task(
            description="New feature",
            node_id="fake-node",
            scope_files=["src/feature.py"],
        )
        doc_req = orch.decompose_for_docs(
            task,
            diataxis_category="reference",
            audience="developer",
            target_files=["docs/reference/feature.md"],
        )

        assert doc_req.task_id == task.task_id
        assert doc_req.diataxis_category == "reference"
        assert doc_req.audience == "developer"

    def test_doc_queue_persistence(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        task = orch.create_task(description="Test queue", node_id="fake-node")
        orch.decompose_for_docs(task, diataxis_category="tutorial", target_files=["docs/t1.md"])
        orch.decompose_for_docs(task, diataxis_category="howto", target_files=["docs/h1.md"])

        queue = orch.get_doc_queue()
        assert len(queue) == 2
        assert queue[0].diataxis_category == "tutorial"
        assert queue[1].diataxis_category == "howto"

    def test_record_task_result(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        result = orch.record_task_result(
            task_id="TASK-001",
            files_changed=["a.py", "b.py"],
            tests_added=5,
            lint_clean=True,
        )

        assert result.task_id == "TASK-001"
        assert result.tests_added == 5
        result_file = scratchpad / "results" / "TASK-001.json"
        assert result_file.exists()

    def test_clear_task(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        orch.create_task(description="To clear", node_id="fake-node")
        assert orch.get_current_task() is not None

        orch.clear_task()
        assert orch.get_current_task() is None

    def test_clear_doc_queue(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        task = orch.create_task(description="Test", node_id="fake-node")
        orch.decompose_for_docs(task, diataxis_category="reference", target_files=["docs/r.md"])

        orch.clear_doc_queue()
        assert orch.get_doc_queue() == []

    def test_diataxis_categories_defined(self):
        assert "tutorial" in DIATAXIS_CATEGORIES
        assert "howto" in DIATAXIS_CATEGORIES
        assert "reference" in DIATAXIS_CATEGORIES
        assert "explanation" in DIATAXIS_CATEGORIES

    def test_corrupt_scratchpad_graceful(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        scratchpad.mkdir(parents=True)
        (scratchpad / "current_task.json").write_text("not valid json{{{")
        (scratchpad / "doc_queue.json").write_text("also bad")

        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)
        assert orch.get_current_task() is None
        assert orch.get_doc_queue() == []

    # --- Golf 3: Analyse-taken ---

    def test_create_analysis_task_returns_analyse_task_type(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        orch = DevOrchestrator(registry, scratchpad_path=tmp_path / "scratchpad")

        task = orch.create_analysis_task(
            question="Wat is de stand van zaken rond embeddings?",
            title="Embeddings SOTA",
        )

        assert task.task_id.startswith("ANALYSE-")
        assert task.task_type == "analyse"

    def test_create_analysis_task_writes_to_scratchpad(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        scratchpad = tmp_path / "scratchpad"
        orch = DevOrchestrator(registry, scratchpad_path=scratchpad)

        orch.create_analysis_task(
            question="Trade-offs tussen ChromaDB en Weaviate?",
            title="Vector DB Vergelijking",
            analysis_type="comparative",
        )

        queue_file = scratchpad / "analysis_queue.json"
        assert queue_file.exists()
        import json

        data = json.loads(queue_file.read_text())
        assert len(data) == 1
        assert data[0]["analysis_type"] == "comparative"

    def test_get_analysis_queue_empty_initially(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        orch = DevOrchestrator(registry, scratchpad_path=tmp_path / "scratchpad")

        assert orch.get_analysis_queue() == []

    def test_analysis_queue_roundtrip(self, tmp_path):
        registry = _make_registry_with_fake(tmp_path)
        orch = DevOrchestrator(registry, scratchpad_path=tmp_path / "scratchpad")

        orch.create_analysis_task(
            question="Hoe past Weaviate in DevHub?",
            title="Weaviate Toepassingsanalyse",
            analysis_type="application",
            domains=["ai_engineering"],
        )

        queue = orch.get_analysis_queue()
        assert len(queue) == 1
        assert queue[0].title == "Weaviate Toepassingsanalyse"
        assert queue[0].question == "Hoe past Weaviate in DevHub?"
