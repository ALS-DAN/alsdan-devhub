"""Tests voor machine-leesbare systeembestanden (Art. 4.6, Sprint 46).

Valideert dat governance-documenten, ADRs en agent-definities
machine-leesbare YAML-blokken en gestandaardiseerde frontmatter bevatten.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEV_CONSTITUTION = REPO_ROOT / "docs" / "compliance" / "DEV_CONSTITUTION.md"
ADR_DIR = REPO_ROOT / "docs" / "adr"
MACHINE_READABILITY_STANDARD = REPO_ROOT / "docs" / "compliance" / "MACHINE_READABILITY_STANDARD.md"


class TestDevConstitutionYamlBlocks:
    """Valideer YAML-blokken in DEV_CONSTITUTION."""

    def _get_yaml_blocks(self) -> list[dict]:
        """Extract alle YAML-blokken met # MACHINE-LEESBAAR BLOK marker."""
        text = DEV_CONSTITUTION.read_text(encoding="utf-8")
        raw_blocks = re.findall(
            r"```yaml\n# MACHINE-LEESBAAR BLOK\n(.*?)```",
            text,
            re.DOTALL,
        )
        blocks = []
        for raw in raw_blocks:
            parsed = yaml.safe_load(raw)
            if parsed:
                blocks.append(parsed)
        return blocks

    def test_constitution_exists(self):
        """DEV_CONSTITUTION.md moet bestaan."""
        assert DEV_CONSTITUTION.exists()

    def test_nine_yaml_blocks_present(self):
        """Er moeten 9 YAML-blokken zijn (1 per artikel)."""
        blocks = self._get_yaml_blocks()
        assert len(blocks) == 9, f"Verwacht 9 blokken, gevonden: {len(blocks)}"

    def test_all_articles_represented(self):
        """Elk artikel (1-9) moet een YAML-blok hebben."""
        blocks = self._get_yaml_blocks()
        article_numbers = {b["artikel"] for b in blocks}
        expected = set(range(1, 10))
        assert article_numbers == expected, f"Ontbrekende artikelen: {expected - article_numbers}"

    @pytest.mark.parametrize("article_num", range(1, 10))
    def test_article_block_has_required_fields(self, article_num: int):
        """Elk YAML-blok moet artikel, titel, regels en handhaving bevatten."""
        blocks = self._get_yaml_blocks()
        block = next((b for b in blocks if b["artikel"] == article_num), None)
        assert block is not None, f"Art. {article_num} blok niet gevonden"
        assert "titel" in block, f"Art. {article_num} mist 'titel'"
        assert "regels" in block, f"Art. {article_num} mist 'regels'"
        assert "handhaving" in block, f"Art. {article_num} mist 'handhaving'"

    @pytest.mark.parametrize("article_num", range(1, 10))
    def test_rules_have_required_fields(self, article_num: int):
        """Elke regel moet id, tekst en type hebben."""
        blocks = self._get_yaml_blocks()
        block = next((b for b in blocks if b["artikel"] == article_num), None)
        assert block is not None
        for rule in block["regels"]:
            assert "id" in rule, f"Art. {article_num} regel mist 'id'"
            assert "tekst" in rule, f"Art. {article_num} regel mist 'tekst'"
            assert "type" in rule, f"Art. {article_num} regel mist 'type'"

    def test_article_7_has_zones(self):
        """Art. 7 moet een zones-structuur hebben met GREEN, YELLOW, RED."""
        blocks = self._get_yaml_blocks()
        block = next(b for b in blocks if b["artikel"] == 7)
        assert "zones" in block, "Art. 7 mist 'zones'"
        for zone in ["GREEN", "YELLOW", "RED"]:
            assert zone in block["zones"], f"Art. 7 mist zone: {zone}"
            zone_data = block["zones"][zone]
            assert "criteria" in zone_data, f"Zone {zone} mist 'criteria'"
            assert "vereiste" in zone_data, f"Zone {zone} mist 'vereiste'"
            assert "automation_allowed" in zone_data, f"Zone {zone} mist 'automation_allowed'"

    def test_article_4_6_exists(self):
        """Art. 4.6 (machine-leesbaarheidsverplichting) moet bestaan in de tekst."""
        text = DEV_CONSTITUTION.read_text(encoding="utf-8")
        assert "4.6." in text, "Art. 4.6 ontbreekt in DEV_CONSTITUTION"
        assert "machine-leesbare blokken" in text.lower() or "machine-leesbaar" in text.lower()

    def test_prose_not_modified(self):
        """Bestaande artikelkoppen moeten ongewijzigd zijn."""
        text = DEV_CONSTITUTION.read_text(encoding="utf-8")
        expected_headings = [
            "## Artikel 1 — Menselijke Regie",
            "## Artikel 2 — Verificatieplicht",
            "## Artikel 3 — Codebase-integriteit",
            "## Artikel 4 — Transparantie & Traceerbaarheid",
            "## Artikel 5 — Kennisintegriteit",
            "## Artikel 6 — Project-soevereiniteit",
            "## Artikel 7 — Impact-zonering",
            "## Artikel 8 — Dataminimalisatie",
            "## Artikel 9 — Architecturele Continuïteit",
        ]
        for heading in expected_headings:
            assert heading in text, f"Artikelkop ontbreekt of gewijzigd: {heading}"


class TestAdrStandard:
    """Valideer ADR frontmatter standaard."""

    REQUIRED_FIELDS = ["Status", "Datum", "Context", "Impact-zone"]

    def _get_adr_files(self) -> list[Path]:
        return sorted(ADR_DIR.glob("ADR-*.md"))

    def test_adrs_exist(self):
        """Er moeten ADR bestanden zijn."""
        adrs = self._get_adr_files()
        assert len(adrs) > 0, "Geen ADRs gevonden"

    @pytest.mark.parametrize(
        "adr_file",
        sorted(
            (Path(__file__).resolve().parent.parent.parent.parent / "docs" / "adr").glob("ADR-*.md")
        ),
        ids=lambda p: p.stem,
    )
    def test_adr_has_required_table_fields(self, adr_file: Path):
        """Elke ADR moet een tabel hebben met Status, Datum, Context, Impact-zone."""
        text = adr_file.read_text(encoding="utf-8")
        for field in self.REQUIRED_FIELDS:
            assert f"| {field} |" in text, f"{adr_file.stem} mist '{field}' in tabel"


class TestMachineReadabilityStandard:
    """Valideer dat het standaard-document bestaat en compleet is."""

    def test_standard_exists(self):
        """MACHINE_READABILITY_STANDARD.md moet bestaan."""
        assert MACHINE_READABILITY_STANDARD.exists()

    def test_standard_references_art_4_6(self):
        """Standaard moet verwijzen naar Art. 4.6."""
        text = MACHINE_READABILITY_STANDARD.read_text(encoding="utf-8")
        assert "Art. 4.6" in text or "4.6" in text


class TestMermaidDiagrams:
    """Valideer dat Mermaid-diagrammen aanwezig zijn in sleutelbestanden."""

    def test_constitution_has_mermaid(self):
        """DEV_CONSTITUTION moet minimaal 1 Mermaid-diagram bevatten."""
        text = DEV_CONSTITUTION.read_text(encoding="utf-8")
        mermaid_count = text.count("```mermaid")
        assert mermaid_count >= 1, f"Verwacht >=1 Mermaid-diagram, gevonden: {mermaid_count}"

    def test_dev_lead_has_mermaid(self):
        """Dev-lead agent moet een delegatie-diagram bevatten."""
        dev_lead = REPO_ROOT / "agents" / "dev-lead.md"
        text = dev_lead.read_text(encoding="utf-8")
        assert "```mermaid" in text, "dev-lead.md mist Mermaid-diagram"
