"""E2e tests voor plugin-laag: skill-definities.

Valideert dat alle SKILL.md bestanden correct zijn gestructureerd
en de vereiste secties bevatten voor Claude Code invocatie.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"

REQUIRED_SKILLS = [
    "devhub-sprint",
    "devhub-health",
    "devhub-mentor",
    "devhub-review",
    "devhub-sprint-prep",
    "devhub-research-loop",
    "devhub-governance-check",
    "devhub-redteam",
    "devhub-analyse",
]

# Secties die elke skill moet bevatten (minimaal één per groep)
REQUIRED_SECTION_GROUPS = [
    ["Doel", "doel"],  # Doelomschrijving
    ["Workflow", "workflow"],  # Werkwijze
    ["Stap", "stap", "### 0", "### 1"],  # Stappen (genummerd of met prefix)
]


class TestSkillDefinitions:
    """Valideer dat alle skill-definities correct zijn."""

    def test_all_required_skills_exist(self):
        """Alle 5 vereiste skills moeten bestaan."""
        for skill in REQUIRED_SKILLS:
            skill_dir = SKILLS_DIR / skill
            assert skill_dir.exists(), f"Skill directory {skill} ontbreekt"
            skill_file = skill_dir / "SKILL.md"
            assert skill_file.exists(), f"SKILL.md ontbreekt voor {skill}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_not_empty(self, skill_name: str):
        """Elke SKILL.md moet inhoud hebben."""
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        assert len(content) > 100, f"{skill_name} SKILL.md is te kort ({len(content)} chars)"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_has_required_sections(self, skill_name: str):
        """Elke skill moet de vereiste secties bevatten (minimaal één variant per groep)."""
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        for group in REQUIRED_SECTION_GROUPS:
            found = any(variant in content for variant in group)
            assert found, f"{skill_name} mist sectie uit groep {group}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_references_governance(self, skill_name: str):
        """Elke skill moet governance-verwijzingen bevatten."""
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        # Moet naar DEV_CONSTITUTION of governance verwijzen
        has_governance = (
            "DEV_CONSTITUTION" in content
            or "governance" in content.lower()
            or "Developer beslist" in content
            or "Regels" in content
            or "Art." in content
            or "compliance" in content.lower()
            or "kwaliteit" in content.lower()
        )
        assert has_governance, f"{skill_name} mist governance-verwijzing"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_has_python_integration(self, skill_name: str):
        """Elke skill moet Python-laag integratie tonen (BorisAdapter of devhub imports)."""
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        has_python = (
            "PYTHONPATH" in content
            or "devhub_core." in content
            or "BorisAdapter" in content
            or "NodeRegistry" in content
        )
        assert has_python, f"{skill_name} mist Python-laag integratie"

    def test_no_unexpected_skills(self):
        """Alleen de 7 verwachte skills mogen bestaan."""
        skill_dirs = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        for skill in skill_dirs:
            assert skill in REQUIRED_SKILLS, f"Onverwachte skill: {skill}"
