"""Tests voor Content Builders — pre-built document requests."""

from devhub_documents.contracts import DocumentCategory
from devhub_core.agents.content_builders import (
    SPRINT_33_BUILDERS,
    build_blueprint_boris,
    build_methodology_shape_up,
    build_pattern_abc_adapter,
    build_tutorial_sprint_intake,
)
from devhub_core.contracts.pipeline_contracts import DocumentProductionRequest


class TestContentBuilders:
    def test_pattern_abc_adapter(self):
        req = build_pattern_abc_adapter()
        assert isinstance(req, DocumentProductionRequest)
        assert req.category == DocumentCategory.PATTERN
        assert req.skip_vectorstore is True
        assert "Adapter" in req.topic

    def test_methodology_shape_up(self):
        req = build_methodology_shape_up()
        assert isinstance(req, DocumentProductionRequest)
        assert req.category == DocumentCategory.METHODOLOGY
        assert "Shape Up" in req.topic

    def test_tutorial_sprint_intake(self):
        req = build_tutorial_sprint_intake()
        assert isinstance(req, DocumentProductionRequest)
        assert req.category == DocumentCategory.TUTORIAL
        assert "sprint intake" in req.topic.lower()

    def test_blueprint_boris(self):
        req = build_blueprint_boris()
        assert isinstance(req, DocumentProductionRequest)
        assert req.category == DocumentCategory.METHODOLOGY
        assert "pipeline" in req.topic.lower()

    def test_all_builders_produce_valid_requests(self):
        for builder in SPRINT_33_BUILDERS:
            req = builder()
            assert isinstance(req, DocumentProductionRequest)
            assert req.topic.strip()
            assert req.audience == "developer"

    def test_sprint_33_has_four_builders(self):
        assert len(SPRINT_33_BUILDERS) == 4
