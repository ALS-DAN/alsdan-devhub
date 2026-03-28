"""Tests voor FolderRouter — categorie-naar-storage-pad routing."""

from pathlib import Path

import pytest

from devhub_documents.contracts import DocumentCategory
from devhub_core.agents.folder_router import FolderRouter

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "documents.yml"


@pytest.fixture
def router() -> FolderRouter:
    """FolderRouter met de echte documents.yml configuratie."""
    return FolderRouter(config_path=CONFIG_PATH)


# ---------------------------------------------------------------------------
# resolve_path
# ---------------------------------------------------------------------------


class TestResolvePath:
    def test_pattern_devhub(self, router: FolderRouter):
        path = router.resolve_path(DocumentCategory.PATTERN, "abc-adapter.md")
        assert path == "DevHub/process/pattern/abc-adapter.md"

    def test_methodology_devhub(self, router: FolderRouter):
        path = router.resolve_path(DocumentCategory.METHODOLOGY, "shape-up.md")
        assert path == "DevHub/knowledge/methodology/shape-up.md"

    def test_tutorial_devhub(self, router: FolderRouter):
        path = router.resolve_path(DocumentCategory.TUTORIAL, "sprint-intake.md")
        assert path == "DevHub/product/tutorial/sprint-intake.md"

    def test_tutorial_boris(self, router: FolderRouter):
        path = router.resolve_path(
            DocumentCategory.TUTORIAL, "eerste-stappen.md", node_id="boris-buurts"
        )
        assert path == "BORIS/product/tutorial/eerste-stappen.md"

    def test_decision_boris(self, router: FolderRouter):
        path = router.resolve_path(DocumentCategory.DECISION, "adr-001.md", node_id="boris-buurts")
        assert path == "BORIS/process/decision/adr-001.md"

    def test_disallowed_category_raises(self, router: FolderRouter):
        with pytest.raises(ValueError, match="not allowed"):
            router.resolve_path(DocumentCategory.METHODOLOGY, "test.md", node_id="boris-buurts")

    def test_unknown_node_raises(self, router: FolderRouter):
        with pytest.raises(KeyError, match="not found"):
            router.resolve_path(DocumentCategory.TUTORIAL, "test.md", node_id="unknown")


# ---------------------------------------------------------------------------
# get_node_taxonomy
# ---------------------------------------------------------------------------


class TestGetNodeTaxonomy:
    def test_devhub_has_12_categories(self, router: FolderRouter):
        taxonomy = router.get_node_taxonomy("devhub")
        assert len(taxonomy) == 12

    def test_boris_has_6_categories(self, router: FolderRouter):
        taxonomy = router.get_node_taxonomy("boris-buurts")
        assert len(taxonomy) == 6

    def test_devhub_includes_all_layers(self, router: FolderRouter):
        taxonomy = router.get_node_taxonomy("devhub")
        layers = {cat.layer() for cat in taxonomy}
        assert layers == {"product", "process", "knowledge"}

    def test_boris_includes_expected(self, router: FolderRouter):
        taxonomy = router.get_node_taxonomy("boris-buurts")
        values = {cat.value for cat in taxonomy}
        assert values == {"tutorial", "howto", "reference", "explanation", "pattern", "decision"}

    def test_unknown_node_raises(self, router: FolderRouter):
        with pytest.raises(KeyError):
            router.get_node_taxonomy("nonexistent")


# ---------------------------------------------------------------------------
# is_category_allowed
# ---------------------------------------------------------------------------


class TestIsCategoryAllowed:
    def test_methodology_allowed_devhub(self, router: FolderRouter):
        assert router.is_category_allowed(DocumentCategory.METHODOLOGY, "devhub") is True

    def test_methodology_not_allowed_boris(self, router: FolderRouter):
        assert router.is_category_allowed(DocumentCategory.METHODOLOGY, "boris-buurts") is False

    def test_tutorial_allowed_both(self, router: FolderRouter):
        assert router.is_category_allowed(DocumentCategory.TUTORIAL, "devhub") is True
        assert router.is_category_allowed(DocumentCategory.TUTORIAL, "boris-buurts") is True


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_no_config_path(self):
        router = FolderRouter()
        assert router.nodes == {}

    def test_nonexistent_config_path(self):
        router = FolderRouter(config_path="/nonexistent/path.yml")
        assert router.nodes == {}
