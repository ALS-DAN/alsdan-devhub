"""
NodeRegistry — Beheer van managed project nodes.

Registreert nodes met hun configuratie en adapter-klasse.
Ondersteunt meerdere nodes (BORIS, toekomstige projecten).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from devhub_core.contracts.node_interface import NodeInterface, NodeReport

logger = logging.getLogger(__name__)


@dataclass
class NodeConfig:
    """Configuratie voor één managed node."""

    node_id: str
    name: str
    path: str  # Absoluut pad naar project root
    adapter: str  # Fully qualified adapter class name
    enabled: bool = True
    devagents_enabled: bool = False
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        if not self.path:
            raise ValueError("path is required")


class NodeRegistry:
    """Registry voor managed project nodes.

    Laadt node-configuraties uit een YAML bestand en instantieert
    adapters on-demand.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self._nodes: dict[str, NodeConfig] = {}
        self._adapters: dict[str, NodeInterface] = {}
        if config_path and config_path.exists():
            self._load_config(config_path)

    def _load_config(self, path: Path) -> None:
        """Laad node-configuraties uit YAML."""
        data = yaml.safe_load(path.read_text())
        if not data or "nodes" not in data:
            return
        for node_data in data["nodes"]:
            config = NodeConfig(**node_data)
            self._nodes[config.node_id] = config

    def register(self, config: NodeConfig) -> None:
        """Registreer een node programmatisch."""
        self._nodes[config.node_id] = config
        # Clear cached adapter als er een was
        self._adapters.pop(config.node_id, None)

    def unregister(self, node_id: str) -> None:
        """Verwijder een node uit de registry."""
        self._nodes.pop(node_id, None)
        self._adapters.pop(node_id, None)

    def get_config(self, node_id: str) -> NodeConfig | None:
        """Haal node-configuratie op."""
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[NodeConfig]:
        """Lijst alle geregistreerde nodes."""
        return list(self._nodes.values())

    def list_enabled(self) -> list[NodeConfig]:
        """Lijst alleen ingeschakelde nodes."""
        return [n for n in self._nodes.values() if n.enabled]

    def get_adapter(self, node_id: str) -> NodeInterface:
        """Haal de adapter-instantie op voor een node.

        Lazy-instantiatie: adapter wordt pas aangemaakt bij eerste gebruik.
        """
        if node_id in self._adapters:
            return self._adapters[node_id]

        config = self._nodes.get(node_id)
        if config is None:
            raise KeyError(f"Node '{node_id}' not registered")

        adapter = self._instantiate_adapter(config)
        self._adapters[node_id] = adapter
        return adapter

    def get_report(self, node_id: str) -> NodeReport:
        """Convenience: haal NodeReport op via de adapter."""
        adapter = self.get_adapter(node_id)
        return adapter.get_report()

    def _instantiate_adapter(self, config: NodeConfig) -> NodeInterface:
        """Instantieer een adapter op basis van de fully qualified class name."""
        module_path, class_name = config.adapter.rsplit(".", 1)
        try:
            import importlib

            module = importlib.import_module(module_path)
            adapter_class: type[NodeInterface] = getattr(module, class_name)
            return adapter_class(config.path)
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Cannot load adapter '{config.adapter}' for node '{config.node_id}': {e}"
            ) from e

    def to_dict(self) -> dict[str, dict]:
        """Exporteer registry als dict (voor serialisatie)."""
        return {
            node_id: {
                "node_id": cfg.node_id,
                "name": cfg.name,
                "path": cfg.path,
                "adapter": cfg.adapter,
                "enabled": cfg.enabled,
                "devagents_enabled": cfg.devagents_enabled,
                "tags": cfg.tags,
            }
            for node_id, cfg in self._nodes.items()
        }
