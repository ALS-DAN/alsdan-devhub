"""Tests voor DocsAgent."""

from pathlib import Path

from devhub_core.agents.docs_agent import DocsAgent, DIATAXIS_TEMPLATES
from devhub_core.contracts.dev_contracts import DocGenRequest


class TestDocsAgent:
    def test_generate_new_tutorial(self, tmp_path):
        docs_root = tmp_path / "docs"
        agent = DocsAgent(docs_root=docs_root)

        request = DocGenRequest(
            task_id="T1",
            target_files=["tutorials/getting-started.md"],
            diataxis_category="tutorial",
            audience="developer",
        )
        result = agent.process_request(request)

        assert result.status == "generated"
        assert len(result.files_generated) == 1
        generated_file = Path(result.files_generated[0])
        assert generated_file.exists()
        content = generated_file.read_text()
        assert "Tutorial" in content
        assert "developer" in content

    def test_generate_reference_doc(self, tmp_path):
        docs_root = tmp_path / "docs"
        agent = DocsAgent(docs_root=docs_root)

        request = DocGenRequest(
            task_id="T2",
            target_files=["reference/node_interface.md"],
            diataxis_category="reference",
            audience="developer",
            source_code_files=["devhub/contracts/node_interface.py"],
        )
        result = agent.process_request(request)

        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Reference" in content
        assert "Parameter" in content

    def test_generate_howto(self, tmp_path):
        docs_root = tmp_path / "docs"
        agent = DocsAgent(docs_root=docs_root)

        request = DocGenRequest(
            task_id="T3",
            target_files=["howto/add-adapter.md"],
            diataxis_category="howto",
            audience="developer",
        )
        result = agent.process_request(request)

        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Probleem" in content

    def test_generate_explanation(self, tmp_path):
        docs_root = tmp_path / "docs"
        agent = DocsAgent(docs_root=docs_root)

        request = DocGenRequest(
            task_id="T4",
            target_files=["explanation/node-architecture.md"],
            diataxis_category="explanation",
            audience="beleid_staff",
        )
        result = agent.process_request(request)

        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Context" in content
        assert "beleid_staff" in content

    def test_update_existing_doc(self, tmp_path):
        docs_root = tmp_path / "docs"
        existing = docs_root / "existing.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("# Existing Doc\n\nSome content here.\n")

        agent = DocsAgent(docs_root=docs_root)
        request = DocGenRequest(
            task_id="T5",
            target_files=["existing.md"],
            diataxis_category="reference",
            audience="developer",
        )
        result = agent.process_request(request)

        assert result.status == "updated"
        assert len(result.files_updated) == 1
        content = existing.read_text()
        assert "> **Type:**" in content

    def test_update_skips_if_header_exists(self, tmp_path):
        docs_root = tmp_path / "docs"
        existing = docs_root / "existing.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("# Doc\n\n> **Type:** Reference\n\nContent.\n")

        agent = DocsAgent(docs_root=docs_root)
        request = DocGenRequest(
            task_id="T6",
            target_files=["existing.md"],
            diataxis_category="reference",
            audience="developer",
        )
        result = agent.process_request(request)

        # Still counts as updated (file was processed)
        assert result.status == "updated"
        # But content should not have double headers
        content = existing.read_text()
        assert content.count("> **Type:**") == 1

    def test_analyze_coverage_empty(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "nonexistent")
        coverage = agent.analyze_coverage()
        assert all(len(v) == 0 for v in coverage.values())

    def test_analyze_coverage_with_docs(self, tmp_path):
        docs_root = tmp_path / "docs"
        (docs_root / "tutorial").mkdir(parents=True)
        (docs_root / "tutorial" / "start.md").write_text("# Tutorial\n\nLeren door doen")
        (docs_root / "reference").mkdir(parents=True)
        (docs_root / "reference" / "api.md").write_text("# API Reference\n\nEndpoints")

        agent = DocsAgent(docs_root=docs_root)
        coverage = agent.analyze_coverage()

        assert len(coverage["tutorial"]) >= 1
        assert len(coverage["reference"]) >= 1

    def test_suggest_docs(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        suggestions = agent.suggest_docs(
            source_files=["devhub/agents/orchestrator.py", "devhub/registry.py"]
        )

        assert len(suggestions) >= 2
        categories = [s.diataxis_category for s in suggestions]
        assert all(c == "reference" for c in categories)

    def test_multiple_target_files(self, tmp_path):
        docs_root = tmp_path / "docs"
        agent = DocsAgent(docs_root=docs_root)

        request = DocGenRequest(
            task_id="T7",
            target_files=["ref/a.md", "ref/b.md"],
            diataxis_category="reference",
            audience="developer",
        )
        result = agent.process_request(request)

        assert result.status == "generated"
        assert len(result.files_generated) == 2

    def test_all_templates_exist(self):
        all_categories = [
            "tutorial",
            "howto",
            "reference",
            "explanation",
            "pattern",
            "analysis",
            "decision",
            "retrospective",
            "methodology",
            "best_practice",
            "sota_review",
            "playbook",
        ]
        assert len(DIATAXIS_TEMPLATES) == 12
        for cat in all_categories:
            assert cat in DIATAXIS_TEMPLATES
            assert len(DIATAXIS_TEMPLATES[cat]) > 50

    # --- Laag 2: Proces templates ---

    def test_generate_pattern_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="P1",
            target_files=["pattern/abc.md"],
            diataxis_category="pattern",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Pattern" in content
        assert "Probleem" in content

    def test_generate_analysis_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="A1",
            target_files=["analysis/perf.md"],
            diataxis_category="analysis",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Onderzoeksvraag" in content

    def test_generate_decision_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="D1",
            target_files=["decision/adr-001.md"],
            diataxis_category="decision",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Beslissing" in content
        assert "Status" in content

    def test_generate_retrospective_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="R1",
            target_files=["retrospective/sprint-1.md"],
            diataxis_category="retrospective",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Wat ging goed" in content

    # --- Laag 3: Kennisbank templates ---

    def test_generate_methodology_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="M1",
            target_files=["methodology/shape-up.md"],
            diataxis_category="methodology",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Principes" in content

    def test_generate_best_practice_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="B1",
            target_files=["best_practice/frozen-dc.md"],
            diataxis_category="best_practice",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Principe" in content
        assert "Valkuilen" in content

    def test_generate_sota_review_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="S1",
            target_files=["sota_review/llm-agents.md"],
            diataxis_category="sota_review",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Huidige stand" in content

    def test_generate_playbook_doc(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "docs")
        request = DocGenRequest(
            task_id="PB1",
            target_files=["playbook/incident.md"],
            diataxis_category="playbook",
            audience="developer",
        )
        result = agent.process_request(request)
        assert result.status == "generated"
        content = Path(result.files_generated[0]).read_text()
        assert "Escalatiepunten" in content

    # --- Coverage en detectie ---

    def test_analyze_coverage_has_12_categories(self, tmp_path):
        agent = DocsAgent(docs_root=tmp_path / "nonexistent")
        coverage = agent.analyze_coverage()
        assert len(coverage) == 13  # 12 categories + uncategorized

    def test_detect_category_pattern(self, tmp_path):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "abc-patroon.md").write_text("# ABC Patroon\n\nDit patroon beschrijft...")
        agent = DocsAgent(docs_root=docs_root)
        coverage = agent.analyze_coverage()
        assert len(coverage["pattern"]) >= 1

    def test_detect_category_decision(self, tmp_path):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "adr-001.md").write_text("# ADR-001\n\nDeze beslissing betreft...")
        agent = DocsAgent(docs_root=docs_root)
        coverage = agent.analyze_coverage()
        assert len(coverage["decision"]) >= 1
