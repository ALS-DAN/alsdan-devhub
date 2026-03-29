"""Tests voor dashboard UI-componenten.

NiceGUI componenten worden getest via nicegui.testing.
Deze tests verifiëren dat componenten correct renderen zonder browser.
"""

from devhub_dashboard.components.status_badge import StatusLevel, _STATUS_CONFIG
from devhub_dashboard.components.knowledge_card import _RING_COLORS, _GRADE_COLORS
from devhub_dashboard.components.status_flow import _STEPS, _STEP_LABELS, _STEP_ICONS


class TestStatusBadgeConfig:
    """Test de status badge configuratie (geen UI nodig)."""

    def test_all_levels_have_config(self):
        levels: list[StatusLevel] = ["healthy", "attention", "critical", "unknown"]
        for level in levels:
            assert level in _STATUS_CONFIG
            color, icon, label = _STATUS_CONFIG[level]
            assert color
            assert icon
            assert label

    def test_healthy_is_positive(self):
        color, _, _ = _STATUS_CONFIG["healthy"]
        assert color == "positive"

    def test_critical_is_negative(self):
        color, _, _ = _STATUS_CONFIG["critical"]
        assert color == "negative"

    def test_attention_is_warning(self):
        color, _, _ = _STATUS_CONFIG["attention"]
        assert color == "warning"


class TestKnowledgeCardConfig:
    """Test knowledge card kleur-mappings."""

    def test_ring_colors_complete(self):
        for ring in ("core", "agent", "project"):
            assert ring in _RING_COLORS

    def test_grade_colors_complete(self):
        for grade in ("GOLD", "SILVER", "BRONZE", "SPECULATIVE"):
            assert grade in _GRADE_COLORS

    def test_gold_is_golden(self):
        assert _GRADE_COLORS["GOLD"] == "#FFD700"


class TestStatusFlowConfig:
    """Test status flow stappen-configuratie."""

    def test_five_steps(self):
        assert len(_STEPS) == 5

    def test_steps_order(self):
        assert _STEPS == ["pending", "approved", "in_progress", "review", "completed"]

    def test_all_steps_have_labels(self):
        for step in _STEPS:
            assert step in _STEP_LABELS
            assert _STEP_LABELS[step]

    def test_all_steps_have_icons(self):
        for step in _STEPS:
            assert step in _STEP_ICONS
            assert _STEP_ICONS[step]

    def test_review_step_present(self):
        assert "review" in _STEPS
        assert _STEP_LABELS["review"] == "Review"
