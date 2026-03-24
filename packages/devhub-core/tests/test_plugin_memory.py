"""E2e tests voor plugin-laag: agent-memory persistentie.

Valideert dat het memory-systeem correct werkt:
- Alle agents hebben memory-directories
- MEMORY.md bestanden zijn leesbaar en correct gestructureerd
- Write/read cyclus werkt
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MEMORY_DIR = REPO_ROOT / ".claude" / "agent-memory"

ALL_AGENTS = ["dev-lead", "coder", "reviewer", "researcher", "planner"]


class TestMemoryStructure:
    """Valideer memory-directorystructuur."""

    def test_memory_dir_exists(self):
        """De agent-memory directory moet bestaan."""
        assert MEMORY_DIR.exists(), "agent-memory directory ontbreekt"

    @pytest.mark.parametrize("agent_name", ALL_AGENTS)
    def test_agent_has_memory_dir(self, agent_name: str):
        """Elke agent moet een eigen memory-directory hebben."""
        agent_dir = MEMORY_DIR / agent_name
        assert agent_dir.exists(), f"Memory dir voor {agent_name} ontbreekt"
        assert agent_dir.is_dir(), f"{agent_name} memory is geen directory"

    @pytest.mark.parametrize("agent_name", ALL_AGENTS)
    def test_agent_has_memory_md(self, agent_name: str):
        """Elke agent moet een MEMORY.md bestand hebben."""
        memory_file = MEMORY_DIR / agent_name / "MEMORY.md"
        assert memory_file.exists(), f"MEMORY.md ontbreekt voor {agent_name}"

    @pytest.mark.parametrize("agent_name", ALL_AGENTS)
    def test_memory_not_empty(self, agent_name: str):
        """Elke MEMORY.md moet inhoud hebben."""
        memory_file = MEMORY_DIR / agent_name / "MEMORY.md"
        content = memory_file.read_text(encoding="utf-8")
        assert len(content) > 50, f"{agent_name} MEMORY.md is te kort"

    @pytest.mark.parametrize("agent_name", ALL_AGENTS)
    def test_memory_has_heading(self, agent_name: str):
        """Elke MEMORY.md moet beginnen met een heading."""
        content = (MEMORY_DIR / agent_name / "MEMORY.md").read_text(encoding="utf-8")
        assert content.startswith("#"), f"{agent_name} MEMORY.md mist heading"


class TestMemoryPersistence:
    """Valideer write/read cyclus."""

    def test_write_and_read_memory(self, tmp_path: Path):
        """Memory bestanden moeten schrijf- en leesbaar zijn."""
        test_memory = tmp_path / "test-agent" / "MEMORY.md"
        test_memory.parent.mkdir(parents=True)

        content = "# Test Agent Memory\n\n## Context\n- Test entry\n"
        test_memory.write_text(content, encoding="utf-8")

        read_back = test_memory.read_text(encoding="utf-8")
        assert read_back == content

    def test_memory_append(self, tmp_path: Path):
        """Memory kan uitgebreid worden zonder bestaande inhoud te verliezen."""
        test_memory = tmp_path / "test-agent" / "MEMORY.md"
        test_memory.parent.mkdir(parents=True)

        initial = "# Memory\n\n## Sectie 1\n- Item A\n"
        test_memory.write_text(initial, encoding="utf-8")

        # Append
        existing = test_memory.read_text(encoding="utf-8")
        updated = existing + "\n## Sectie 2\n- Item B\n"
        test_memory.write_text(updated, encoding="utf-8")

        final = test_memory.read_text(encoding="utf-8")
        assert "Item A" in final
        assert "Item B" in final
        assert "Sectie 1" in final
        assert "Sectie 2" in final


class TestPluginJson:
    """Valideer plugin.json structuur."""

    def test_plugin_json_exists(self):
        """plugin.json moet bestaan."""
        plugin_file = REPO_ROOT / ".claude-plugin" / "plugin.json"
        assert plugin_file.exists()

    def test_plugin_json_valid(self):
        """plugin.json moet valid JSON zijn met vereiste velden."""
        import json

        plugin_file = REPO_ROOT / ".claude-plugin" / "plugin.json"
        data = json.loads(plugin_file.read_text(encoding="utf-8"))

        assert "name" in data
        assert data["name"] == "alsdan-devhub"
        assert "version" in data
        assert "description" in data
        assert "author" in data

    def test_plugin_version_semver(self):
        """Plugin versie moet semver-achtig zijn."""
        import json
        import re

        plugin_file = REPO_ROOT / ".claude-plugin" / "plugin.json"
        data = json.loads(plugin_file.read_text(encoding="utf-8"))

        version = data["version"]
        assert re.match(r"^\d+\.\d+\.\d+$", version), f"Ongeldige versie: {version}"


class TestCoworkInfrastructure:
    """Valideer Cowork-communicatie infrastructuur."""

    def test_inbox_dir_exists(self):
        """docs/planning/inbox/ moet bestaan."""
        inbox = REPO_ROOT / "docs" / "planning" / "inbox"
        assert inbox.exists(), "docs/planning/inbox/ ontbreekt"

    def test_devhub_brief_exists(self):
        """DEVHUB_BRIEF.md moet bestaan."""
        brief = REPO_ROOT / "DEVHUB_BRIEF.md"
        assert brief.exists(), "DEVHUB_BRIEF.md ontbreekt"

    def test_devhub_brief_has_sections(self):
        """DEVHUB_BRIEF.md moet de vereiste secties bevatten."""
        brief = REPO_ROOT / "DEVHUB_BRIEF.md"
        content = brief.read_text(encoding="utf-8")

        required = ["Actieve sprint", "Agent-status", "Plugin-status", "Skills"]
        for section in required:
            assert section in content, f"DEVHUB_BRIEF.md mist sectie '{section}'"

    def test_sprint_dir_exists(self):
        """docs/planning/sprints/ moet bestaan."""
        sprints = REPO_ROOT / "docs" / "planning" / "sprints"
        assert sprints.exists(), "docs/planning/sprints/ ontbreekt"
