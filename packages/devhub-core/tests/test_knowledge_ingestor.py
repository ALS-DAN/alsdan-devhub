"""Tests voor KnowledgeIngestor — knowledge/*.md → vectorstore pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.agents.knowledge_ingestor import (
    IngestionResult,
    IngestionSummary,
    KnowledgeIngestor,
    chunk_by_headings,
    parse_frontmatter,
)
from devhub_core.contracts.event_contracts import KnowledgeIngested
from devhub_core.events.in_memory_bus import InMemoryEventBus
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.contracts.vectorstore_contracts import DataZone
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def embedding_provider():
    return HashEmbeddingProvider()


@pytest.fixture
def vectorstore():
    return ChromaDBZonedStore(zones=[DataZone.OPEN])


@pytest.fixture
def knowledge_store(vectorstore, embedding_provider):
    return KnowledgeStore(vectorstore=vectorstore, embedding_provider=embedding_provider)


@pytest.fixture
def curator():
    return KnowledgeCurator()


@pytest.fixture
def event_bus():
    return InMemoryEventBus()


@pytest.fixture
def knowledge_dir(tmp_path):
    """Maak een knowledge/ directory met een test-artikel."""
    kdir = tmp_path / "knowledge" / "ai_engineering"
    kdir.mkdir(parents=True)
    return tmp_path / "knowledge"


def _write_article(knowledge_dir: Path, domain: str, filename: str, **overrides) -> Path:
    """Helper: schrijf een kennisartikel met valide frontmatter."""
    domain_dir = knowledge_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    path = domain_dir / filename

    defaults = {
        "title": "Test Article",
        "domain": domain,
        "grade": "SILVER",
        "sources": ["https://example.com"],
        "date": "2026-03-29",
        "author": "researcher-agent",
        "verification": 60,
    }
    defaults.update(overrides)

    # Build frontmatter
    lines = ["---"]
    for k, v in defaults.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append("# Test Article")
    lines.append("")
    lines.append("## Samenvatting")
    lines.append("")
    lines.append("Dit is een test-samenvatting met voldoende content om te chunken.")
    lines.append("")
    lines.append("## Inhoud")
    lines.append("")
    lines.append("Dit is de inhoud van het kennisartikel met meer details en uitleg.")
    lines.append("Extra tekst om de chunk voldoende lang te maken voor verwerking.")
    lines.append("")
    lines.append("## Bronnen")
    lines.append("")
    lines.append("- https://example.com")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# parse_frontmatter tests
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        text = "---\ntitle: Test\ngrade: SILVER\n---\n\n# Content"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Test"
        assert meta["grade"] == "SILVER"
        assert "# Content" in body

    def test_no_frontmatter(self):
        text = "# Just content\nNo frontmatter here."
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert body == text

    def test_empty_frontmatter(self):
        text = "---\n---\n\nContent"
        meta, body = parse_frontmatter(text)
        assert meta == {}  # yaml.safe_load returns None for empty

    def test_sources_list(self):
        text = "---\ntitle: T\nsources:\n  - https://a.com\n  - https://b.com\n---\n\nBody"
        meta, body = parse_frontmatter(text)
        assert len(meta["sources"]) == 2


# ---------------------------------------------------------------------------
# chunk_by_headings tests
# ---------------------------------------------------------------------------


class TestChunkByHeadings:
    def test_basic_chunking(self):
        body = (
            "Intro text\n\n## Section 1\n\nContent one is here and long enough."
            "\n\n## Section 2\n\nContent two is also here and long enough."
        )
        chunks = chunk_by_headings(body, min_chunk_len=10)
        assert len(chunks) == 3
        assert chunks[0][0] == "intro"
        assert chunks[1][0] == "Section 1"
        assert chunks[2][0] == "Section 2"

    def test_no_headings(self):
        body = "Just plain text without any headings at all."
        chunks = chunk_by_headings(body)
        assert len(chunks) == 1
        assert chunks[0][0] == "intro"

    def test_empty_body(self):
        chunks = chunk_by_headings("")
        assert chunks == []

    def test_merges_short_chunks(self):
        body = "## A\n\nX\n\n## B\n\nThis is a longer section with enough content to stand alone."
        chunks = chunk_by_headings(body, min_chunk_len=50)
        # "X" is too short, gets merged with next
        assert len(chunks) == 1


# ---------------------------------------------------------------------------
# KnowledgeIngestor tests
# ---------------------------------------------------------------------------


class TestKnowledgeIngestor:
    def test_ingest_single_file(self, knowledge_dir, knowledge_store, curator, event_bus):
        path = _write_article(knowledge_dir, "ai_engineering", "test_article.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator, event_bus)

        result = ingestor.ingest_file(path)

        assert result.status == "ingested"
        assert result.chunk_count > 0
        assert result.article_id != ""

    def test_ingest_publishes_event(self, knowledge_dir, knowledge_store, curator, event_bus):
        path = _write_article(knowledge_dir, "ai_engineering", "event_test.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator, event_bus)

        ingestor.ingest_file(path)

        events = event_bus.history(KnowledgeIngested)
        assert len(events) == 1
        assert events[0].domain == "ai_engineering"
        assert events[0].chunk_count > 0

    def test_ingest_no_event_without_bus(self, knowledge_dir, knowledge_store, curator):
        path = _write_article(knowledge_dir, "ai_engineering", "no_bus.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)

        result = ingestor.ingest_file(path)
        assert result.status == "ingested"

    def test_ingest_all(self, knowledge_dir, knowledge_store, curator):
        _write_article(knowledge_dir, "ai_engineering", "article1.md", title="Article 1")
        _write_article(knowledge_dir, "ai_engineering", "article2.md", title="Article 2")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)

        summary = ingestor.ingest_all()

        assert isinstance(summary, IngestionSummary)
        assert summary.total_files == 2
        assert summary.ingested == 2

    def test_incremental_skip(self, knowledge_dir, knowledge_store, curator):
        _write_article(knowledge_dir, "ai_engineering", "incremental.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)

        result1 = ingestor.ingest_file(knowledge_dir / "ai_engineering" / "incremental.md")
        assert result1.status == "ingested"

        result2 = ingestor.ingest_file(knowledge_dir / "ai_engineering" / "incremental.md")
        assert result2.status == "skipped"

    def test_rejected_by_curator(self, knowledge_dir, knowledge_store, curator):
        """Artikel zonder bronnen wordt afgewezen door curator."""
        path = _write_article(
            knowledge_dir,
            "ai_engineering",
            "no_sources.md",
            sources=[],  # Leeg
            grade="GOLD",
            verification=90,
        )
        # Manually fix the file to have no sources
        content = path.read_text()
        content = content.replace("sources:\n", "sources: []\n")
        path.write_text(content)

        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)
        result = ingestor.ingest_file(path)

        assert result.status == "rejected"

    def test_no_frontmatter_error(self, knowledge_dir, knowledge_store, curator):
        path = knowledge_dir / "ai_engineering" / "bad.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# No frontmatter\n\nJust content.", encoding="utf-8")

        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)
        result = ingestor.ingest_file(path)

        assert result.status == "error"
        assert "frontmatter" in result.message.lower()

    def test_nonexistent_file(self, knowledge_dir, knowledge_store, curator):
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)
        result = ingestor.ingest_file(knowledge_dir / "nonexistent.md")

        assert result.status == "error"

    def test_vectorstore_contains_chunks(
        self, knowledge_dir, knowledge_store, curator, vectorstore
    ):
        _write_article(knowledge_dir, "ai_engineering", "stored.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)

        result = ingestor.ingest_file(knowledge_dir / "ai_engineering" / "stored.md")

        assert result.status == "ingested"
        assert vectorstore.count() > 0

    def test_ingest_different_domains(self, knowledge_dir, knowledge_store, curator):
        _write_article(knowledge_dir, "ai_engineering", "ai.md")
        _write_article(knowledge_dir, "python_architecture", "py.md")
        ingestor = KnowledgeIngestor(knowledge_dir, knowledge_store, curator)

        summary = ingestor.ingest_all()

        assert summary.ingested == 2

    def test_result_dataclass(self):
        r = IngestionResult(file_path="/tmp/test.md", status="ingested", chunk_count=3)
        assert r.file_path == "/tmp/test.md"
        assert r.chunk_count == 3

    def test_summary_dataclass(self):
        s = IngestionSummary(total_files=5, ingested=3, skipped=1, rejected=1)
        assert s.total_files == 5
        assert s.errors == 0
