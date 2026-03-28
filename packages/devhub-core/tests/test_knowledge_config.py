"""Tests voor knowledge_config.py — Research Compas configuratie (Sprint 33)."""

from __future__ import annotations

from pathlib import Path

import pytest

from devhub_core.contracts.curator_contracts import KnowledgeDomain
from devhub_core.research.knowledge_config import (
    AgentKnowledgeProfile,
    DomainConfig,
    KnowledgeConfig,
    RingConfig,
    SeedQuestion,
    load_knowledge_config,
)

# --- Paths naar echte config bestanden ---
CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"
KNOWLEDGE_YML = CONFIG_DIR / "knowledge.yml"
AGENT_KNOWLEDGE_YML = CONFIG_DIR / "agent_knowledge.yml"


# --- RingConfig tests ---


class TestRingConfig:
    def test_ring_config_creation(self) -> None:
        ring = RingConfig(name="core", description="Altijd actief", auto_bootstrap=True)
        assert ring.name == "core"
        assert ring.description == "Altijd actief"
        assert ring.auto_bootstrap is True

    def test_ring_config_defaults(self) -> None:
        ring = RingConfig(name="agent")
        assert ring.description == ""
        assert ring.auto_bootstrap is False

    def test_ring_config_frozen(self) -> None:
        ring = RingConfig(name="core")
        with pytest.raises(AttributeError):
            ring.name = "agent"  # type: ignore[misc]


# --- DomainConfig tests ---


class TestDomainConfig:
    def test_domain_config_creation(self) -> None:
        domain = DomainConfig(
            name="ai_engineering",
            ring="core",
            freshness_months=3,
            rq_focus=("RQ1", "RQ4", "RQ5"),
            related_domains=("claude_specific",),
            bootstrap_priority=1,
            description="AI stuff",
        )
        assert domain.name == "ai_engineering"
        assert domain.ring == "core"
        assert domain.freshness_months == 3
        assert domain.rq_focus == ("RQ1", "RQ4", "RQ5")
        assert domain.bootstrap_priority == 1

    def test_domain_config_defaults(self) -> None:
        domain = DomainConfig(name="test_domain", ring="agent")
        assert domain.freshness_months == 12
        assert domain.rq_focus == ()
        assert domain.related_domains == ()
        assert domain.bootstrap_priority == 0
        assert domain.node_scope == ""
        assert domain.monitored_sources == ()

    def test_domain_config_validation_empty_name(self) -> None:
        with pytest.raises(ValueError, match="name is required"):
            DomainConfig(name="", ring="core")

    def test_domain_config_validation_invalid_ring(self) -> None:
        with pytest.raises(ValueError, match="ring must be core/agent/project"):
            DomainConfig(name="test", ring="invalid")  # type: ignore[arg-type]

    def test_domain_config_validation_freshness(self) -> None:
        with pytest.raises(ValueError, match="freshness_months must be >= 1"):
            DomainConfig(name="test", ring="core", freshness_months=0)

    def test_domain_config_knowledge_domain_mapping(self) -> None:
        domain = DomainConfig(name="ai_engineering", ring="core")
        assert domain.knowledge_domain == KnowledgeDomain.AI_ENGINEERING

    def test_domain_config_frozen(self) -> None:
        domain = DomainConfig(name="test", ring="core")
        with pytest.raises(AttributeError):
            domain.name = "changed"  # type: ignore[misc]


# --- AgentKnowledgeProfile tests ---


class TestAgentKnowledgeProfile:
    def test_agent_profile_creation(self) -> None:
        profile = AgentKnowledgeProfile(
            agent_name="dev-lead",
            domains=(("ai_engineering", "SILVER"), ("governance_compliance", "BRONZE")),
            pre_task_check=True,
            auto_research=True,
        )
        assert profile.agent_name == "dev-lead"
        assert len(profile.domains) == 2
        assert profile.domains[0] == ("ai_engineering", "SILVER")
        assert profile.pre_task_check is True

    def test_agent_profile_defaults(self) -> None:
        profile = AgentKnowledgeProfile(agent_name="test-agent")
        assert profile.domains == ()
        assert profile.pre_task_check is False
        assert profile.auto_research is False

    def test_agent_profile_validation_empty_name(self) -> None:
        with pytest.raises(ValueError, match="agent_name is required"):
            AgentKnowledgeProfile(agent_name="")

    def test_agent_profile_frozen(self) -> None:
        profile = AgentKnowledgeProfile(agent_name="test")
        with pytest.raises(AttributeError):
            profile.agent_name = "changed"  # type: ignore[misc]


# --- KnowledgeConfig tests ---


class TestKnowledgeConfig:
    @pytest.fixture()
    def sample_config(self) -> KnowledgeConfig:
        return KnowledgeConfig(
            rings=(
                RingConfig(name="core", auto_bootstrap=True),
                RingConfig(name="agent", auto_bootstrap=False),
            ),
            domains=(
                DomainConfig(name="ai_engineering", ring="core", bootstrap_priority=1),
                DomainConfig(name="sprint_planning", ring="agent", bootstrap_priority=2),
                DomainConfig(name="healthcare_ict", ring="project", bootstrap_priority=0),
            ),
            agent_profiles=(
                AgentKnowledgeProfile(
                    agent_name="dev-lead",
                    domains=(("ai_engineering", "SILVER"),),
                ),
            ),
        )

    def test_get_domain(self, sample_config: KnowledgeConfig) -> None:
        d = sample_config.get_domain("ai_engineering")
        assert d is not None
        assert d.name == "ai_engineering"

    def test_get_domain_not_found(self, sample_config: KnowledgeConfig) -> None:
        assert sample_config.get_domain("nonexistent") is None

    def test_domains_by_ring(self, sample_config: KnowledgeConfig) -> None:
        core = sample_config.domains_by_ring("core")
        assert len(core) == 1
        assert core[0].name == "ai_engineering"

    def test_get_agent_profile(self, sample_config: KnowledgeConfig) -> None:
        p = sample_config.get_agent_profile("dev-lead")
        assert p is not None
        assert p.agent_name == "dev-lead"

    def test_get_agent_profile_not_found(self, sample_config: KnowledgeConfig) -> None:
        assert sample_config.get_agent_profile("nonexistent") is None

    def test_bootstrap_domains(self, sample_config: KnowledgeConfig) -> None:
        bootstrap = sample_config.bootstrap_domains()
        assert len(bootstrap) == 1  # only core ring has auto_bootstrap
        assert bootstrap[0].name == "ai_engineering"

    def test_bootstrap_domains_sorted_by_priority(self) -> None:
        config = KnowledgeConfig(
            rings=(RingConfig(name="core", auto_bootstrap=True),),
            domains=(
                DomainConfig(name="governance_compliance", ring="core", bootstrap_priority=3),
                DomainConfig(name="ai_engineering", ring="core", bootstrap_priority=1),
                DomainConfig(name="python_architecture", ring="core", bootstrap_priority=2),
            ),
        )
        bootstrap = config.bootstrap_domains()
        assert [d.name for d in bootstrap] == [
            "ai_engineering",
            "python_architecture",
            "governance_compliance",
        ]


# --- load_knowledge_config integration tests ---


class TestLoadKnowledgeConfig:
    def test_load_real_knowledge_yml(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        assert len(config.rings) == 3
        assert len(config.domains) == 16
        assert config.health_max_speculative_pct == 60.0
        assert config.grading_gold_min_verification_pct == 80.0

    def test_load_real_knowledge_yml_ring_counts(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        assert len(config.domains_by_ring("core")) == 5
        assert len(config.domains_by_ring("agent")) == 8
        assert len(config.domains_by_ring("project")) == 3

    def test_load_real_knowledge_yml_domain_details(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        ai = config.get_domain("ai_engineering")
        assert ai is not None
        assert ai.ring == "core"
        assert ai.freshness_months == 3
        assert "RQ1" in ai.rq_focus
        assert ai.bootstrap_priority == 1

    def test_load_real_knowledge_yml_with_agent_profiles(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML, AGENT_KNOWLEDGE_YML)
        assert len(config.agent_profiles) == 7
        dev_lead = config.get_agent_profile("dev-lead")
        assert dev_lead is not None
        assert dev_lead.pre_task_check is True
        assert any(d == "ai_engineering" for d, _ in dev_lead.domains)

    def test_load_real_knowledge_yml_bootstrap_domains(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        bootstrap = config.bootstrap_domains()
        assert len(bootstrap) == 5  # only core ring, all with priority > 0
        assert bootstrap[0].bootstrap_priority <= bootstrap[-1].bootstrap_priority

    def test_load_all_domains_map_to_enum(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        for d in config.domains:
            kd = d.knowledge_domain
            assert isinstance(kd, KnowledgeDomain)
            assert kd.ring == d.ring

    def test_load_project_domains_have_node_scope(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        for d in config.domains_by_ring("project"):
            assert d.node_scope != "", f"Project domain {d.name} missing node_scope"

    def test_load_without_agent_knowledge(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        assert config.agent_profiles == ()

    def test_load_agent_profiles_all_domains_valid(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML, AGENT_KNOWLEDGE_YML)
        all_domain_names = {d.name for d in config.domains}
        for profile in config.agent_profiles:
            for domain_name, grade in profile.domains:
                assert (
                    domain_name in all_domain_names
                ), f"Agent {profile.agent_name} references unknown domain {domain_name}"
                assert grade in (
                    "GOLD",
                    "SILVER",
                    "BRONZE",
                    "SPECULATIVE",
                ), f"Agent {profile.agent_name} has invalid grade {grade} for {domain_name}"

    def test_load_monitored_sources(self) -> None:
        config = load_knowledge_config(KNOWLEDGE_YML)
        claude = config.get_domain("claude_specific")
        assert claude is not None
        assert len(claude.monitored_sources) > 0

    def test_load_seed_questions_core_domains(self) -> None:
        """Alle kerndomeinen hebben minstens 6 seed questions."""
        config = load_knowledge_config(KNOWLEDGE_YML)
        for d in config.domains_by_ring("core"):
            assert (
                len(d.seed_questions) >= 6
            ), f"Core domain {d.name} has only {len(d.seed_questions)} seed questions"

    def test_load_seed_questions_rq_tags_valid(self) -> None:
        """Seed question rq_tags moeten in het domein's rq_focus zitten."""
        config = load_knowledge_config(KNOWLEDGE_YML)
        for d in config.domains_by_ring("core"):
            for sq in d.seed_questions:
                assert sq.rq_tag in d.rq_focus, (
                    f"Domain {d.name}: seed question rq_tag {sq.rq_tag} "
                    f"not in rq_focus {d.rq_focus}"
                )

    def test_load_seed_questions_non_core_empty(self) -> None:
        """Non-core domeinen hebben geen seed questions."""
        config = load_knowledge_config(KNOWLEDGE_YML)
        for d in config.domains:
            if d.ring != "core":
                assert (
                    len(d.seed_questions) == 0
                ), f"Non-core domain {d.name} should not have seed questions"


class TestSeedQuestion:
    """Tests voor SeedQuestion dataclass."""

    def test_creation(self) -> None:
        sq = SeedQuestion(question="Test vraag?", rq_tag="RQ1")
        assert sq.question == "Test vraag?"
        assert sq.rq_tag == "RQ1"

    def test_frozen(self) -> None:
        sq = SeedQuestion(question="Test", rq_tag="RQ1")
        with pytest.raises(AttributeError):
            sq.question = "other"  # type: ignore[misc]

    def test_question_required(self) -> None:
        with pytest.raises(ValueError, match="question is required"):
            SeedQuestion(question="", rq_tag="RQ1")

    def test_rq_tag_required(self) -> None:
        with pytest.raises(ValueError, match="rq_tag is required"):
            SeedQuestion(question="Test", rq_tag="")
