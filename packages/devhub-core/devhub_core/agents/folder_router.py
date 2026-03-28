"""
FolderRouter — Routeert documenten naar de juiste storage-map.

Leest node-specifieke configuratie uit documents.yml en lost paden op
op basis van DocumentCategory en node_id.

Pad-opbouw: {drive_root}/{layer_folder}/{category.value}/{filename}
Voorbeeld: DevHub/knowledge/methodology/shape-up-in-devhub.md
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from devhub_documents.contracts import DocumentCategory

logger = logging.getLogger(__name__)


class FolderRouter:
    """Routeert documenten naar storage-paden op basis van categorie en node."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self._config: dict = {}
        if config_path:
            path = Path(config_path)
            if path.exists():
                raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                self._config = raw.get("nodes", {})

    @property
    def nodes(self) -> dict:
        """Alle geconfigureerde nodes."""
        return self._config

    def resolve_path(
        self,
        category: DocumentCategory,
        filename: str,
        node_id: str = "devhub",
    ) -> str:
        """Los het volledige storage-pad op voor een document.

        Args:
            category: De Diátaxis+ categorie van het document.
            filename: De bestandsnaam (bijv. 'shape-up-in-devhub.md').
            node_id: De target node (default: 'devhub').

        Returns:
            Pad zoals 'DevHub/knowledge/methodology/shape-up-in-devhub.md'.

        Raises:
            KeyError: Als node_id niet geconfigureerd is.
            ValueError: Als category niet toegestaan is voor de node.
        """
        node_config = self._get_node_config(node_id)

        if not self.is_category_allowed(category, node_id):
            raise ValueError(f"Category '{category.value}' is not allowed for node '{node_id}'")

        drive_root = node_config.get("drive_root", node_id)
        layer = category.layer()
        folder_map = node_config.get("folder_map", {})
        layer_folder = folder_map.get(layer, layer)

        return f"{drive_root}/{layer_folder}/{category.value}/{filename}"

    def get_node_taxonomy(self, node_id: str) -> list[DocumentCategory]:
        """Geef de toegestane categorieën voor een node.

        Args:
            node_id: De node identifier.

        Returns:
            Lijst van DocumentCategory enums.

        Raises:
            KeyError: Als node_id niet geconfigureerd is.
        """
        node_config = self._get_node_config(node_id)
        taxonomy_strings = node_config.get("taxonomy", [])
        return [DocumentCategory.from_string(s) for s in taxonomy_strings]

    def is_category_allowed(self, category: DocumentCategory, node_id: str) -> bool:
        """Controleer of een categorie toegestaan is voor een node.

        Args:
            category: De DocumentCategory om te controleren.
            node_id: De node identifier.

        Returns:
            True als de categorie in de node-taxonomie staat.

        Raises:
            KeyError: Als node_id niet geconfigureerd is.
        """
        allowed = self.get_node_taxonomy(node_id)
        return category in allowed

    def _get_node_config(self, node_id: str) -> dict:
        """Haal node-configuratie op, raises KeyError als niet gevonden."""
        if node_id not in self._config:
            raise KeyError(
                f"Node '{node_id}' not found in documents.yml. "
                f"Available nodes: {list(self._config.keys())}"
            )
        return self._config[node_id]
