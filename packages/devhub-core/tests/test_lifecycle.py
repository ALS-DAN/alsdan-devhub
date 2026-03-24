"""End-to-end lifecycle test: DevOrchestrator → DocsAgent → QA Agent."""


from devhub_core.agents.docs_agent import DocsAgent
from devhub_core.agents.orchestrator import DevOrchestrator
from devhub_core.agents.qa_agent import QAAgent
from devhub_core.contracts.node_interface import (
    NodeDocStatus,
    NodeHealth,
    NodeInterface,
    NodeReport,
    TestResult,
)
from devhub_core.registry import NodeConfig, NodeRegistry


class FakeNode(NodeInterface):
    def __init__(self, path: str) -> None:
        self.path = path

    def get_report(self) -> NodeReport:
        return NodeReport(
            node_id="test-node",
            timestamp="2026-03-23T12:00:00Z",
            health=NodeHealth(
                status="UP",
                components={"db": "UP"},
                test_count=50,
                test_pass_rate=1.0,
                coverage_pct=80.0,
            ),
            doc_status=NodeDocStatus(
                total_pages=5, stale_pages=0, diataxis_coverage={}
            ),
        )

    def get_health(self) -> NodeHealth:
        return self.get_report().health

    def list_docs(self) -> list[str]:
        return ["index.md"]

    def run_tests(self) -> TestResult:
        return TestResult(total=50, passed=50, failed=0, errors=0, duration_seconds=3.0)


class TestFullLifecycle:
    """Simuleert een complete sprint-lifecycle met alle 3 agents."""

    def test_create_task_generate_docs_qa_review(self, tmp_path):
        # --- Setup ---
        registry = NodeRegistry()
        registry.register(NodeConfig(
            node_id="test-node",
            name="Test",
            path=str(tmp_path),
            adapter="tests.test_lifecycle.FakeNode",
        ))

        scratchpad = tmp_path / "scratchpad"
        docs_root = tmp_path / "docs"
        reports_dir = tmp_path / "qa_reports"

        orchestrator = DevOrchestrator(registry, scratchpad_path=scratchpad)
        docs_agent = DocsAgent(docs_root=docs_root)
        qa_agent = QAAgent(reports_path=reports_dir)

        # --- Stap 1: DevOrchestrator maakt taak aan ---
        task = orchestrator.create_task(
            description="Add user authentication",
            node_id="test-node",
            scope_files=["src/auth.py", "src/middleware.py"],
            sprint_ref="SPRINT_AUTH",
        )
        assert task.task_id.startswith("TASK-")

        # --- Stap 2: Orchestrator pollt node context ---
        report = orchestrator.get_node_context("test-node")
        assert report.health.status == "UP"

        # --- Stap 3: Orchestrator decomposeert naar docs ---
        doc_req = orchestrator.decompose_for_docs(
            task,
            diataxis_category="reference",
            audience="developer",
            target_files=["reference/auth.md"],
        )
        assert doc_req.diataxis_category == "reference"

        # --- Stap 4: DocsAgent genereert docs (parallel aan dev) ---
        doc_result = docs_agent.process_request(doc_req)
        assert doc_result.status == "generated"
        assert len(doc_result.files_generated) == 1

        # --- Stap 5: Dev-werk wordt voltooid ---
        task_result = orchestrator.record_task_result(
            task_id=task.task_id,
            files_changed=["src/auth.py", "src/middleware.py"],
            tests_added=8,
            lint_clean=True,
        )
        assert task_result.tests_added == 8

        # --- Stap 6: QA Agent reviewt alles ---
        qa_report = qa_agent.full_review(
            task_id=task.task_id,
            task_result=task_result,
            doc_requests=[doc_req],
            docs_root=docs_root,
        )

        # Verdict should be PASS (clean code + generated docs)
        assert qa_report.task_id == task.task_id
        assert qa_report.verdict in ("PASS", "NEEDS_WORK")
        # Doc findings may include DR-05 (placeholders) but no CRITICAL
        critical = [
            f
            for f in list(qa_report.code_findings) + list(qa_report.doc_findings)
            if f.severity == "CRITICAL"
        ]
        assert len(critical) == 0

        # --- Stap 7: Orchestrator cleanup ---
        orchestrator.clear_task()
        orchestrator.clear_doc_queue()
        assert orchestrator.get_current_task() is None
        assert orchestrator.get_doc_queue() == []

    def test_lifecycle_with_failing_qa(self, tmp_path):
        """Lifecycle waar QA BLOCK geeft door hardcoded secret."""
        registry = NodeRegistry()
        registry.register(NodeConfig(
            node_id="test-node",
            name="Test",
            path=str(tmp_path),
            adapter="tests.test_lifecycle.FakeNode",
        ))

        scratchpad = tmp_path / "scratchpad"
        reports_dir = tmp_path / "qa_reports"

        orchestrator = DevOrchestrator(registry, scratchpad_path=scratchpad)
        qa_agent = QAAgent(reports_path=reports_dir)

        # Maak een bestand met een secret
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        (code_dir / "bad.py").write_text(
            'SECRET_KEY = "sk-abcdefghijklmnopqrstuvwxyz"\n'
        )

        task = orchestrator.create_task(
            description="Bad feature",
            node_id="test-node",
            scope_files=["src/bad.py"],
        )
        task_result = orchestrator.record_task_result(
            task_id=task.task_id,
            files_changed=["src/bad.py"],
            tests_added=0,
            lint_clean=True,
        )

        # QA should BLOCK
        qa_report = qa_agent.full_review(
            task_id=task.task_id,
            task_result=task_result,
            project_root=tmp_path,
        )
        assert qa_report.verdict == "BLOCK"

    def test_docs_coverage_analysis(self, tmp_path):
        """DocsAgent analyseert coverage en QA valideert."""
        docs_root = tmp_path / "docs"
        (docs_root / "tutorial").mkdir(parents=True)
        (docs_root / "tutorial" / "start.md").write_text(
            "# Getting Started\n\n> **Type:** Tutorial\n> **Doelgroep:** dev\n\nLearn.\n"
        )

        docs_agent = DocsAgent(docs_root=docs_root)
        coverage = docs_agent.analyze_coverage()
        assert len(coverage["tutorial"]) >= 1

        # Suggest docs for uncovered files
        suggestions = docs_agent.suggest_docs(["devhub/registry.py"])
        assert len(suggestions) >= 1
        assert suggestions[0].diataxis_category == "reference"
