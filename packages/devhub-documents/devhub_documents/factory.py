"""
DocumentFactory — Creëert de juiste adapter op basis van configuratie.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from devhub_documents.contracts import DocumentFormat
from devhub_documents.interface import DocumentInterface


class DocumentFactory:
    """Factory die DocumentInterface adapters aanmaakt op basis van YAML config."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self._config: dict = {}
        if config_path:
            path = Path(config_path)
            if path.exists():
                self._config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    @property
    def config(self) -> dict:
        """Geef de documents configuratie terug."""
        return self._config.get("documents", {})

    @property
    def default_format(self) -> str:
        """Het standaard output formaat."""
        return self.config.get("default_format", "markdown")

    @property
    def output_dir(self) -> str:
        """De standaard output directory."""
        return self.config.get("output_dir", "")

    def create_adapter(self, fmt: DocumentFormat | str | None = None) -> DocumentInterface:
        """Maak een adapter aan voor het opgegeven formaat.

        Args:
            fmt: DocumentFormat enum, format string, of None voor default.

        Returns:
            Een DocumentInterface implementatie.

        Raises:
            ValueError: Als het formaat niet ondersteund wordt.
            ImportError: Als odfpy niet geinstalleerd is voor ODF formaat.
        """
        if fmt is None:
            fmt = self.default_format

        if isinstance(fmt, DocumentFormat):
            format_str = fmt.value
        else:
            format_str = fmt.lower()

        adapters_config = self.config.get("adapters", {})

        if format_str == "markdown":
            if not adapters_config.get("markdown", {}).get("enabled", True):
                raise ValueError("Markdown adapter is disabled in configuration")
            from devhub_documents.adapters.markdown_adapter import MarkdownAdapter

            return MarkdownAdapter()

        elif format_str == "odf":
            if not adapters_config.get("odf", {}).get("enabled", True):
                raise ValueError("ODF adapter is disabled in configuration")
            from devhub_documents.adapters.odf_adapter import ODFAdapter

            return ODFAdapter()

        else:
            raise ValueError(
                f"Unsupported document format: '{format_str}'. " f"Supported formats: markdown, odf"
            )
