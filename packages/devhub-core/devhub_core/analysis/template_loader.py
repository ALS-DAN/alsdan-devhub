"""
TemplateLoader — Laadt analyse-templates uit YAML-bestanden.

Templates definiëren de structuur van een analyse: welke secties,
in welke volgorde, met welke prompt-hints voor de synthese-stap.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from devhub_core.contracts.analysis_contracts import AnalysisType

# Standaard locatie van de templates (relatief aan dit bestand)
_DEFAULT_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "analysis"


class TemplateLoader:
    """Laadt analyse-templates uit YAML-bestanden.

    Elke template beschrijft de sectie-structuur voor één AnalysisType.
    """

    def __init__(self, template_dir: Path | None = None) -> None:
        self._template_dir = template_dir or _DEFAULT_TEMPLATE_DIR

    def load(self, analysis_type: AnalysisType) -> dict:
        """Laad de template voor het gegeven analysis type.

        Args:
            analysis_type: Het type analyse waarvoor de template geladen wordt.

        Returns:
            Dict met template-configuratie (sections, title_prefix, etc.).

        Raises:
            ValueError: Als de template niet bestaat.
        """
        template_file = self._template_dir / f"{analysis_type.value}.yml"
        if not template_file.exists():
            raise ValueError(
                f"Template voor '{analysis_type.value}' niet gevonden: {template_file}"
            )
        with template_file.open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    def list_templates(self) -> list[AnalysisType]:
        """Geef een lijst van beschikbare template types.

        Returns:
            Lijst van AnalysisType waarden waarvoor een template beschikbaar is.
        """
        available = []
        for analysis_type in AnalysisType:
            template_file = self._template_dir / f"{analysis_type.value}.yml"
            if template_file.exists():
                available.append(analysis_type)
        return available
