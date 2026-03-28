"""Knowledge Config — Drie-ringen domeinstructuur uit knowledge.yml en agent_knowledge.yml.

Frozen dataclasses voor configuratie-parsing. Consistent met het contract-patroon.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from devhub_core.contracts.curator_contracts import KnowledgeDomain


@dataclass(frozen=True)
class RingConfig:
    """Configuratie voor een ring (core/agent/project)."""

    name: str
    description: str = ""
    auto_bootstrap: bool = False


@dataclass(frozen=True)
class DomainConfig:
    """Configuratie voor een kennisdomein."""

    name: str
    ring: Literal["core", "agent", "project"]
    freshness_months: int = 12
    rq_focus: tuple[str, ...] = ()
    related_domains: tuple[str, ...] = ()
    bootstrap_priority: int = 0
    description: str = ""
    node_scope: str = ""
    monitored_sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if self.ring not in ("core", "agent", "project"):
            raise ValueError(f"ring must be core/agent/project, got {self.ring}")
        if self.freshness_months < 1:
            raise ValueError(f"freshness_months must be >= 1, got {self.freshness_months}")

    @property
    def knowledge_domain(self) -> KnowledgeDomain:
        """Map naar de KnowledgeDomain enum."""
        return KnowledgeDomain(self.name)


@dataclass(frozen=True)
class AgentKnowledgeProfile:
    """Kennisprofiel voor een agent."""

    agent_name: str
    domains: tuple[tuple[str, str], ...] = ()  # ((domain, grade), ...)
    pre_task_check: bool = False
    auto_research: bool = False

    def __post_init__(self) -> None:
        if not self.agent_name:
            raise ValueError("agent_name is required")


@dataclass(frozen=True)
class KnowledgeConfig:
    """Volledige kennisconfiguratie uit knowledge.yml + agent_knowledge.yml."""

    rings: tuple[RingConfig, ...] = ()
    domains: tuple[DomainConfig, ...] = ()
    agent_profiles: tuple[AgentKnowledgeProfile, ...] = ()
    health_max_speculative_pct: float = 60.0
    health_max_stale_pct: float = 20.0
    health_max_single_source_pct: float = 70.0
    grading_gold_min_verification_pct: float = 80.0
    grading_silver_min_verification_pct: float = 50.0

    def get_domain(self, name: str) -> DomainConfig | None:
        """Zoek een domein op naam."""
        for d in self.domains:
            if d.name == name:
                return d
        return None

    def domains_by_ring(self, ring: str) -> list[DomainConfig]:
        """Retourneer alle domeinen in een ring."""
        return [d for d in self.domains if d.ring == ring]

    def get_agent_profile(self, agent_name: str) -> AgentKnowledgeProfile | None:
        """Zoek een agent-profiel op naam."""
        for p in self.agent_profiles:
            if p.agent_name == agent_name:
                return p
        return None

    def bootstrap_domains(self) -> list[DomainConfig]:
        """Retourneer domeinen die auto-bootstrap vereisen, gesorteerd op prioriteit."""
        auto_rings = {r.name for r in self.rings if r.auto_bootstrap}
        return sorted(
            [d for d in self.domains if d.ring in auto_rings and d.bootstrap_priority > 0],
            key=lambda d: d.bootstrap_priority,
        )


def load_knowledge_config(
    knowledge_path: Path,
    agent_knowledge_path: Path | None = None,
) -> KnowledgeConfig:
    """Laad KnowledgeConfig uit YAML-bestanden."""
    raw = yaml.safe_load(knowledge_path.read_text(encoding="utf-8")) or {}
    k = raw.get("knowledge", {})

    # Rings
    rings_raw = k.get("rings", {})
    rings = tuple(
        RingConfig(
            name=name,
            description=cfg.get("description", ""),
            auto_bootstrap=cfg.get("auto_bootstrap", False),
        )
        for name, cfg in rings_raw.items()
    )

    # Domains
    domains_raw = k.get("domains", {})
    domains = tuple(
        DomainConfig(
            name=name,
            ring=cfg.get("ring", "core"),
            freshness_months=cfg.get("freshness_months", 12),
            rq_focus=tuple(cfg.get("rq_focus", [])),
            related_domains=tuple(cfg.get("related_domains", [])),
            bootstrap_priority=cfg.get("bootstrap_priority", 0),
            description=cfg.get("description", ""),
            node_scope=cfg.get("node_scope", ""),
            monitored_sources=tuple(cfg.get("monitored_sources", [])),
        )
        for name, cfg in domains_raw.items()
    )

    # Health & grading
    health = k.get("health", {})
    grading = k.get("grading", {})

    # Agent profiles
    agent_profiles: tuple[AgentKnowledgeProfile, ...] = ()
    if agent_knowledge_path and agent_knowledge_path.exists():
        agent_raw = yaml.safe_load(agent_knowledge_path.read_text(encoding="utf-8")) or {}
        profiles_raw = agent_raw.get("agent_profiles", {})
        agent_profiles = tuple(
            AgentKnowledgeProfile(
                agent_name=name,
                domains=tuple((d, g) for d, g in cfg.get("domains", {}).items()),
                pre_task_check=cfg.get("pre_task_check", False),
                auto_research=cfg.get("auto_research", False),
            )
            for name, cfg in profiles_raw.items()
        )

    return KnowledgeConfig(
        rings=rings,
        domains=domains,
        agent_profiles=agent_profiles,
        health_max_speculative_pct=health.get("max_speculative_pct", 60.0),
        health_max_stale_pct=health.get("max_stale_pct", 20.0),
        health_max_single_source_pct=health.get("max_single_source_pct", 70.0),
        grading_gold_min_verification_pct=grading.get("gold_min_verification_pct", 80.0),
        grading_silver_min_verification_pct=grading.get("silver_min_verification_pct", 50.0),
    )
