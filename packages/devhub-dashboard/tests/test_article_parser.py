"""Tests voor KnowledgeArticleParser — fuzzy frontmatter parsing."""

from pathlib import Path

from devhub_dashboard.data.article_parser import KnowledgeArticleParser, ParsedArticle


def _make_parser() -> KnowledgeArticleParser:
    return KnowledgeArticleParser()


class TestStandardFrontmatter:
    """Formaat B: standaard YAML frontmatter bovenaan."""

    def test_parse_standard_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text(
            "---\n"
            "title: Test Article\n"
            "grade: SILVER\n"
            "date: 2026-03-28\n"
            "author: devhub-sprint\n"
            "domain: retrospectives\n"
            "sprint: Dashboard NiceGUI\n"
            "---\n\n"
            "# Test Article\n\n"
            "Dit is de samenvatting van het artikel. Met meerdere zinnen.\n"
        )
        parser = _make_parser()
        result = parser.parse(f, knowledge_root=tmp_path)

        assert result is not None
        assert result.title == "Test Article"
        assert result.grade == "SILVER"
        assert result.date == "2026-03-28"
        assert result.author == "devhub-sprint"
        assert result.domain == "retrospectives"
        assert result.sprint == "Dashboard NiceGUI"

    def test_summary_extraction(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text(
            "---\ntitle: Test\ngrade: GOLD\n---\n\n"
            "# Header\n\n"
            "Eerste zin. Tweede zin. Derde zin. Vierde zin.\n"
        )
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert "Eerste zin." in result.summary
        assert "Tweede zin." in result.summary

    def test_freshness_calculation(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: Fresh\ndate: 2026-03-29\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.freshness_days >= 0

    def test_freshness_no_date(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: Old\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.freshness_days == 9999

    def test_quoted_values(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: \"Quoted Title\"\ngrade: 'GOLD'\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.title == "Quoted Title"
        assert result.grade == "GOLD"


class TestHeaderFrontmatter:
    """Formaat A: # Title boven --- yaml ---."""

    def test_parse_header_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "research.md"
        f.write_text(
            "# Research: Agent Teams SPIKE\n"
            "---\n"
            "sprint: 38\n"
            "type: SPIKE\n"
            "kennisgradering: SILVER\n"
            "datum: 2026-03-28\n"
            "bron: SPRINT_INTAKE_AGENT_TEAMS\n"
            "verdict: GEPARKEERD\n"
            "---\n\n"
            "## Samenvatting\n\n"
            "Dit is de samenvatting.\n"
        )
        parser = _make_parser()
        result = parser.parse(f, knowledge_root=tmp_path)

        assert result is not None
        assert result.title == "Research: Agent Teams SPIKE"
        assert result.grade == "SILVER"
        assert result.date == "2026-03-28"
        assert result.sprint == "38"
        assert "SPRINT_INTAKE_AGENT_TEAMS" in result.sources

    def test_normalize_kennisgradering_to_grade(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("# Test\n---\nkennisgradering: BRONZE\ndatum: 2026-01-01\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.grade == "BRONZE"

    def test_normalize_datum_to_date(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("# Test\n---\ndatum: 2026-03-15\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.date == "2026-03-15"


class TestDomainInference:
    """Domein afleiden uit directorystructuur."""

    def test_subdirectory_becomes_domain(self, tmp_path: Path) -> None:
        sub = tmp_path / "retrospectives"
        sub.mkdir()
        f = sub / "retro.md"
        f.write_text("---\ntitle: Retro\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.domain == "retrospectives"

    def test_root_file_gets_general_domain(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: Root\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.domain == "general"

    def test_explicit_domain_overrides_inference(self, tmp_path: Path) -> None:
        sub = tmp_path / "retrospectives"
        sub.mkdir()
        f = sub / "article.md"
        f.write_text("---\ntitle: Test\ndomain: custom_domain\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.domain == "custom_domain"


class TestArticleId:
    """Article ID = relatief pad zonder .md extensie."""

    def test_root_file_id(self, tmp_path: Path) -> None:
        f = tmp_path / "RESEARCH_TEST.md"
        f.write_text("---\ntitle: Test\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.article_id == "RESEARCH_TEST"

    def test_subdirectory_file_id(self, tmp_path: Path) -> None:
        sub = tmp_path / "retrospectives"
        sub.mkdir()
        f = sub / "RETRO_TEST.md"
        f.write_text("---\ntitle: Test\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.article_id == "retrospectives/RETRO_TEST"


class TestRingClassification:
    """Ring classificatie op basis van domein."""

    def test_core_domains(self) -> None:
        article = ParsedArticle(
            file_path="test",
            title="",
            domain="testing_qa",
            grade="SILVER",
            date="",
            author="",
            summary="",
            freshness_days=0,
            sprint="",
        )
        assert article.ring == "core"

    def test_agent_domains(self) -> None:
        article = ParsedArticle(
            file_path="test",
            title="",
            domain="coaching_learning",
            grade="SILVER",
            date="",
            author="",
            summary="",
            freshness_days=0,
            sprint="",
        )
        assert article.ring == "agent"

    def test_unknown_domain_is_project(self) -> None:
        article = ParsedArticle(
            file_path="test",
            title="",
            domain="retrospectives",
            grade="SILVER",
            date="",
            author="",
            summary="",
            freshness_days=0,
            sprint="",
        )
        assert article.ring == "project"


class TestEdgeCases:
    """Edge cases en foutafhandeling."""

    def test_nonexistent_file_returns_none(self, tmp_path: Path) -> None:
        result = _make_parser().parse(tmp_path / "nonexistent.md")
        assert result is None

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.md"
        f.write_text("")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.title == "empty"
        assert result.grade == "SPECULATIVE"

    def test_no_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "plain.md"
        f.write_text("# Just a Title\n\nSome content here.")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.title == "Just a Title"
        assert result.grade == "SPECULATIVE"

    def test_invalid_date_format(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: Test\ndate: not-a-date\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.freshness_days == 9999

    def test_grade_case_insensitive(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: Test\ngrade: gold\n---\nContent")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.grade == "GOLD"

    def test_grade_inferred_from_content(self, tmp_path: Path) -> None:
        f = tmp_path / "article.md"
        f.write_text("---\ntitle: Test\n---\n\nGrading: BRONZE\n\nMore content.")
        result = _make_parser().parse(f, knowledge_root=tmp_path)
        assert result is not None
        assert result.grade == "BRONZE"

    def test_freshness_color_fresh(self) -> None:
        a = ParsedArticle(
            file_path="t",
            title="",
            domain="",
            grade="",
            date="",
            author="",
            summary="",
            freshness_days=5,
            sprint="",
        )
        assert a.freshness_color == "positive"

    def test_freshness_color_aging(self) -> None:
        a = ParsedArticle(
            file_path="t",
            title="",
            domain="",
            grade="",
            date="",
            author="",
            summary="",
            freshness_days=45,
            sprint="",
        )
        assert a.freshness_color == "warning"

    def test_freshness_color_stale(self) -> None:
        a = ParsedArticle(
            file_path="t",
            title="",
            domain="",
            grade="",
            date="",
            author="",
            summary="",
            freshness_days=100,
            sprint="",
        )
        assert a.freshness_color == "negative"
