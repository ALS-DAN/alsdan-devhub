"""Tests voor TemplateLoader."""

import pytest

from devhub_core.analysis.template_loader import TemplateLoader
from devhub_core.contracts.analysis_contracts import AnalysisType


def test_load_sota_template():
    loader = TemplateLoader()
    template = loader.load(AnalysisType.SOTA)
    assert template["analysis_type"] == "sota"
    assert "sections" in template
    assert len(template["sections"]) > 0


def test_load_all_four_templates():
    loader = TemplateLoader()
    for analysis_type in AnalysisType:
        template = loader.load(analysis_type)
        assert isinstance(template, dict)


def test_template_has_required_sections():
    loader = TemplateLoader()
    for analysis_type in AnalysisType:
        template = loader.load(analysis_type)
        assert "sections" in template, f"{analysis_type.value} mist 'sections'"
        assert len(template["sections"]) >= 2, f"{analysis_type.value} heeft te weinig secties"
        for section in template["sections"]:
            assert "id" in section
            assert "heading" in section


def test_load_unknown_type_raises():
    # Simuleer een type dat geen template-bestand heeft door custom dir te gebruiken
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        empty_loader = TemplateLoader(template_dir=Path(tmpdir))
        with pytest.raises(ValueError, match="niet gevonden"):
            empty_loader.load(AnalysisType.FREE)
