"""Tests voor ReviewContext dataclass en NodeInterface default."""

from dataclasses import FrozenInstanceError

import pytest

from devhub_core.contracts.node_interface import ReviewContext


class TestReviewContext:
    """Test ReviewContext frozen dataclass."""

    def test_valid_construction(self):
        ctx = ReviewContext(
            recent_commits=("fix: bug", "feat: new feature"),
            staged_files=("src/main.py",),
            diff_content="+ new line",
            governance_files=("CLAUDE.md",),
        )
        assert ctx.recent_commits == ("fix: bug", "feat: new feature")
        assert ctx.staged_files == ("src/main.py",)
        assert ctx.diff_content == "+ new line"
        assert ctx.governance_files == ("CLAUDE.md",)

    def test_empty_default(self):
        ctx = ReviewContext()
        assert ctx.recent_commits == ()
        assert ctx.staged_files == ()
        assert ctx.diff_content == ""
        assert ctx.governance_files == ()

    def test_frozen(self):
        ctx = ReviewContext()
        with pytest.raises(FrozenInstanceError):
            ctx.diff_content = "modified"

    def test_partial_construction(self):
        ctx = ReviewContext(
            recent_commits=("commit 1",),
        )
        assert ctx.recent_commits == ("commit 1",)
        assert ctx.staged_files == ()
        assert ctx.diff_content == ""

    def test_with_governance_files(self):
        ctx = ReviewContext(
            governance_files=("CLAUDE.md", ".claude/settings.json"),
        )
        assert len(ctx.governance_files) == 2


class TestNodeInterfaceDefaultReviewContext:
    """Test that NodeInterface provides a default get_review_context()."""

    def test_default_returns_empty_review_context(self):
        """NodeInterface.get_review_context() returns empty ReviewContext."""
        from devhub_core.contracts.node_interface import (
            NodeHealth,
            NodeInterface,
            NodeReport,
            TestResult,
            NodeDocStatus,
        )

        class MinimalAdapter(NodeInterface):
            def get_report(self) -> NodeReport:
                return NodeReport(
                    node_id="test",
                    timestamp="2026-01-01",
                    health=NodeHealth(
                        status="UP",
                        components={},
                        test_count=0,
                        test_pass_rate=1.0,
                        coverage_pct=0.0,
                    ),
                    doc_status=NodeDocStatus(
                        total_pages=0,
                        stale_pages=0,
                        diataxis_coverage={},
                    ),
                )

            def get_health(self) -> NodeHealth:
                return NodeHealth(
                    status="UP",
                    components={},
                    test_count=0,
                    test_pass_rate=1.0,
                    coverage_pct=0.0,
                )

            def list_docs(self) -> list[str]:
                return []

            def run_tests(self) -> TestResult:
                return TestResult(
                    total=0,
                    passed=0,
                    failed=0,
                    errors=0,
                    duration_seconds=0.0,
                )

        adapter = MinimalAdapter()
        ctx = adapter.get_review_context()
        assert isinstance(ctx, ReviewContext)
        assert ctx.recent_commits == ()
        assert ctx.staged_files == ()
        assert ctx.diff_content == ""
        assert ctx.governance_files == ()
