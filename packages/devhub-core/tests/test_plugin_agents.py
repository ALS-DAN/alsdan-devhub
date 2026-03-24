"""E2e tests voor plugin-laag: agent-definities.

Valideert dat alle agent .md bestanden correct zijn gestructureerd
en voldoen aan de Fase 0 plugin-specificatie.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

REQUIRED_AGENTS = ["dev-lead", "coder", "reviewer", "researcher", "planner", "red-team"]
VALID_MODELS = {"opus", "sonnet", "haiku"}


def _parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse YAML frontmatter van een agent .md bestand."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Handle multi-line description
            if not value:
                continue
            result[key] = value
    return result


class TestAgentDefinitions:
    """Valideer dat alle agent-definities correct zijn."""

    def test_all_required_agents_exist(self):
        """Alle 5 vereiste agents moeten bestaan."""
        for agent in REQUIRED_AGENTS:
            agent_file = AGENTS_DIR / f"{agent}.md"
            assert agent_file.exists(), f"Agent {agent} ontbreekt: {agent_file}"

    @pytest.mark.parametrize("agent_name", REQUIRED_AGENTS)
    def test_agent_has_frontmatter(self, agent_name: str):
        """Elke agent moet YAML frontmatter hebben."""
        agent_file = AGENTS_DIR / f"{agent_name}.md"
        text = agent_file.read_text(encoding="utf-8")
        assert text.startswith("---"), f"{agent_name} mist frontmatter"
        assert text.count("---") >= 2, f"{agent_name} heeft onvolledige frontmatter"

    @pytest.mark.parametrize("agent_name", REQUIRED_AGENTS)
    def test_agent_has_name_field(self, agent_name: str):
        """Elke agent frontmatter moet een 'name' veld hebben."""
        fm = _parse_frontmatter(AGENTS_DIR / f"{agent_name}.md")
        assert "name" in fm, f"{agent_name} mist 'name' in frontmatter"
        assert fm["name"] == agent_name, f"{agent_name} name mismatch: {fm['name']}"

    @pytest.mark.parametrize("agent_name", REQUIRED_AGENTS)
    def test_agent_has_description(self, agent_name: str):
        """Elke agent frontmatter moet een 'description' veld hebben."""
        fm = _parse_frontmatter(AGENTS_DIR / f"{agent_name}.md")
        assert "description" in fm, f"{agent_name} mist 'description' in frontmatter"

    @pytest.mark.parametrize("agent_name", REQUIRED_AGENTS)
    def test_agent_has_valid_model(self, agent_name: str):
        """Elke agent moet een geldig model specificeren."""
        fm = _parse_frontmatter(AGENTS_DIR / f"{agent_name}.md")
        assert "model" in fm, f"{agent_name} mist 'model' in frontmatter"
        assert fm["model"] in VALID_MODELS, f"{agent_name} ongeldig model: {fm['model']}"

    @pytest.mark.parametrize("agent_name", REQUIRED_AGENTS)
    def test_agent_has_governance_section(self, agent_name: str):
        """Elke agent moet naar DEV_CONSTITUTION verwijzen."""
        text = (AGENTS_DIR / f"{agent_name}.md").read_text(encoding="utf-8")
        assert "DEV_CONSTITUTION" in text, f"{agent_name} mist DEV_CONSTITUTION verwijzing"

    def test_no_unexpected_agents(self):
        """Alleen de 5 verwachte agents mogen in agents/ staan."""
        agent_files = [f.stem for f in AGENTS_DIR.glob("*.md")]
        for agent in agent_files:
            assert agent in REQUIRED_AGENTS, f"Onverwachte agent: {agent}"

    def test_read_only_agents_have_disallowed_tools(self):
        """Read-only agents (reviewer, planner) mogen niet schrijven."""
        for agent_name in ["reviewer", "planner", "red-team"]:
            fm = _parse_frontmatter(AGENTS_DIR / f"{agent_name}.md")
            assert "disallowedTools" in fm, f"{agent_name} mist disallowedTools"
            disallowed = fm["disallowedTools"]
            assert "Edit" in disallowed, f"{agent_name} mist Edit in disallowedTools"
            assert "Write" in disallowed, f"{agent_name} mist Write in disallowedTools"

    def test_coder_cannot_delegate(self):
        """Coder mag niet delegeren (disallowedTools: Agent)."""
        fm = _parse_frontmatter(AGENTS_DIR / "coder.md")
        assert "disallowedTools" in fm
        assert "Agent" in fm["disallowedTools"]
