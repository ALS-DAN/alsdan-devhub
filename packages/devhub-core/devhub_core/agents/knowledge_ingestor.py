"""
KnowledgeIngestor — Brug tussen knowledge/*.md bestanden en de vectorstore.

Scant de knowledge/ directory, parst YAML frontmatter, chunked content op
heading-structuur, valideert via KnowledgeCurator, en slaat goedgekeurde
artikelen op in de vectorstore via KnowledgeStore.

Incrementeel: alleen nieuwe of gewijzigde bestanden worden verwerkt.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.contracts.curator_contracts import (
    KnowledgeArticle,
    KnowledgeDomain,
)
from devhub_core.contracts.event_contracts import (
    EventBusInterface,
    KnowledgeIngested,
)
from devhub_core.research.knowledge_store import KnowledgeStore


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IngestionResult:
    """Resultaat van het ingest van een enkel bestand."""

    file_path: str
    article_id: str = ""
    chunk_count: int = 0
    status: str = "skipped"  # ingested, skipped, rejected, error
    message: str = ""


@dataclass(frozen=True)
class IngestionSummary:
    """Samenvatting van een volledige ingest-run."""

    total_files: int = 0
    ingested: int = 0
    skipped: int = 0
    rejected: int = 0
    errors: int = 0
    results: tuple[IngestionResult, ...] = ()


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter uit markdown. Retourneert (metadata, body)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw_yaml = match.group(1)
    body = text[match.end() :]
    try:
        meta = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, body


def chunk_by_headings(body: str, min_chunk_len: int = 50) -> list[tuple[str, str]]:
    """Split markdown body op ## headings. Retourneert [(heading, content), ...].

    Tekst vóór de eerste heading wordt opgenomen als chunk met heading "intro".
    Chunks korter dan min_chunk_len worden samengevoegd met de volgende chunk.
    """
    parts: list[tuple[str, str]] = []
    current_heading = "intro"
    current_lines: list[str] = []

    for line in body.split("\n"):
        if line.startswith("## "):
            # Sla vorige chunk op
            content = "\n".join(current_lines).strip()
            if content:
                parts.append((current_heading, content))
            current_heading = line.lstrip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Laatste chunk
    content = "\n".join(current_lines).strip()
    if content:
        parts.append((current_heading, content))

    # Merge te korte chunks
    if not parts:
        return parts

    merged: list[tuple[str, str]] = []
    for heading, content in parts:
        if merged and len(merged[-1][1]) < min_chunk_len:
            prev_heading, prev_content = merged[-1]
            merged[-1] = (prev_heading, f"{prev_content}\n\n## {heading}\n{content}")
        else:
            merged.append((heading, content))

    return merged


def _file_source_id(file_path: Path) -> str:
    """Genereer een stabiel source_id op basis van bestandspad."""
    return hashlib.md5(str(file_path.resolve()).encode()).hexdigest()[:12]


def _content_checksum(content: str) -> str:
    """Genereer een checksum van bestandsinhoud."""
    return hashlib.md5(content.encode()).hexdigest()[:12]


def _resolve_domain(domain_str: str) -> KnowledgeDomain:
    """Map een domein-string naar KnowledgeDomain enum."""
    try:
        return KnowledgeDomain(domain_str)
    except ValueError:
        return KnowledgeDomain.AI_ENGINEERING


def _resolve_ring(domain: KnowledgeDomain) -> str:
    """Bepaal de ring van een domein op basis van de KnowledgeDomain definitie."""
    core_domains = {
        KnowledgeDomain.AI_ENGINEERING,
        KnowledgeDomain.CLAUDE_SPECIFIC,
        KnowledgeDomain.PYTHON_ARCHITECTURE,
        KnowledgeDomain.DEVELOPMENT_METHODOLOGY,
        KnowledgeDomain.GOVERNANCE_COMPLIANCE,
    }
    agent_domains = {
        KnowledgeDomain.SPRINT_PLANNING,
        KnowledgeDomain.CODE_REVIEW,
        KnowledgeDomain.SECURITY_APPSEC,
        KnowledgeDomain.TESTING_QA,
        KnowledgeDomain.KNOWLEDGE_METHODOLOGY,
        KnowledgeDomain.COACHING_LEARNING,
        KnowledgeDomain.DOCUMENTATION,
        KnowledgeDomain.PRODUCT_OWNERSHIP,
    }
    if domain in core_domains:
        return "core"
    if domain in agent_domains:
        return "agent"
    return "project"


# ---------------------------------------------------------------------------
# KnowledgeIngestor
# ---------------------------------------------------------------------------


class KnowledgeIngestor:
    """Ingest knowledge/*.md bestanden naar de vectorstore.

    Args:
        knowledge_dir: Pad naar de knowledge/ directory.
        knowledge_store: KnowledgeStore voor vectorstore-opslag.
        curator: KnowledgeCurator voor kwaliteitsvalidatie.
        event_bus: Optionele event bus voor KnowledgeIngested events.
    """

    def __init__(
        self,
        knowledge_dir: Path,
        knowledge_store: KnowledgeStore,
        curator: KnowledgeCurator,
        event_bus: EventBusInterface | None = None,
    ) -> None:
        self._knowledge_dir = knowledge_dir
        self._store = knowledge_store
        self._curator = curator
        self._bus = event_bus
        self._ingested: set[str] = set()  # Track ingested article_ids

    def ingest_all(self) -> IngestionSummary:
        """Scan en ingest alle knowledge/*.md bestanden.

        Incrementeel: alleen nieuwe of gewijzigde bestanden worden verwerkt.
        """
        md_files = sorted(self._knowledge_dir.rglob("*.md"))
        results: list[IngestionResult] = []

        for md_file in md_files:
            result = self.ingest_file(md_file)
            results.append(result)

        ingested = sum(1 for r in results if r.status == "ingested")
        skipped = sum(1 for r in results if r.status == "skipped")
        rejected = sum(1 for r in results if r.status == "rejected")
        errors = sum(1 for r in results if r.status == "error")

        return IngestionSummary(
            total_files=len(results),
            ingested=ingested,
            skipped=skipped,
            rejected=rejected,
            errors=errors,
            results=tuple(results),
        )

    def ingest_file(self, file_path: Path) -> IngestionResult:
        """Ingest een enkel knowledge-bestand.

        Stappen:
        1. Parse YAML frontmatter
        2. Check of bestand al geïngest is (checksum)
        3. Chunk content op headings
        4. Bouw KnowledgeArticle
        5. Valideer via KnowledgeCurator
        6. Sla op via KnowledgeStore
        7. Publiceer KnowledgeIngested event
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return IngestionResult(
                file_path=str(file_path),
                status="error",
                message=f"Bestand niet leesbaar: {e}",
            )

        meta, body = parse_frontmatter(content)
        if not meta:
            return IngestionResult(
                file_path=str(file_path),
                status="error",
                message="Geen YAML frontmatter gevonden",
            )

        source_id = _file_source_id(file_path)
        checksum = _content_checksum(content)

        # Incrementeel: check of al geïngest met zelfde checksum
        if self._is_already_ingested(source_id, checksum):
            return IngestionResult(
                file_path=str(file_path),
                article_id=source_id,
                status="skipped",
                message="Al geïngest (ongewijzigd)",
            )

        # Chunk op headings
        chunks = chunk_by_headings(body)
        if not chunks:
            return IngestionResult(
                file_path=str(file_path),
                status="error",
                message="Geen content na frontmatter",
            )

        # Bouw KnowledgeArticle
        domain = _resolve_domain(meta.get("domain", "ai_engineering"))
        grade = meta.get("grade", "SPECULATIVE")
        sources_raw = meta.get("sources", [])
        sources = tuple(str(s) for s in sources_raw) if isinstance(sources_raw, list) else ()
        verification = float(meta.get("verification", meta.get("verification_pct", 0)))

        article = KnowledgeArticle(
            article_id=f"{source_id}-{checksum}",
            title=meta.get("title", file_path.stem),
            content=body.strip(),
            domain=domain,
            grade=grade,
            sources=sources,
            verification_pct=verification,
            date=str(meta.get("date", "")),
            author=str(meta.get("author", "researcher-agent")),
            domain_ring=_resolve_ring(domain),
        )

        # Kwaliteitspoort
        report = self._curator.validate_article(article)
        if not report.is_approved:
            return IngestionResult(
                file_path=str(file_path),
                article_id=article.article_id,
                status="rejected",
                message=f"Curator: {report.verdict.value} — {len(report.findings)} findings",
            )

        # Opslaan — per chunk een apart article voor granulaire retrieval
        chunk_ids: list[str] = []
        for i, (heading, chunk_content) in enumerate(chunks):
            chunk_article = KnowledgeArticle(
                article_id=f"{source_id}-{checksum}-c{i}",
                title=f"{article.title} — {heading}",
                content=chunk_content,
                domain=domain,
                grade=grade,
                sources=sources,
                verification_pct=verification,
                date=article.date,
                author=article.author,
                domain_ring=article.domain_ring,
            )
            chunk_id = self._store.store_article(chunk_article)
            chunk_ids.append(chunk_id)

        # Track als geïngest
        self._ingested.add(article.article_id)

        # Event publiceren
        if self._bus is not None:
            self._bus.publish(
                KnowledgeIngested(
                    source_agent="knowledge_ingestor",
                    article_id=article.article_id,
                    domain=domain.value,
                    chunk_count=len(chunk_ids),
                    grade=grade,
                )
            )

        return IngestionResult(
            file_path=str(file_path),
            article_id=article.article_id,
            chunk_count=len(chunk_ids),
            status="ingested",
            message=f"{len(chunk_ids)} chunks opgeslagen",
        )

    def _is_already_ingested(self, source_id: str, checksum: str) -> bool:
        """Check of een bestand al geïngest is met dezelfde checksum.

        Gebruikt een combinatie van in-memory tracking en vectorstore lookup.
        article_id format: {source_id}-{checksum}
        """
        article_id = f"{source_id}-{checksum}"

        # Check in-memory cache (snelste pad)
        if article_id in self._ingested:
            return True

        # Check vectorstore via metadata query
        existing = self._store.get_all_articles()
        for existing_article in existing:
            if existing_article.article_id.startswith(f"{source_id}-{checksum}"):
                self._ingested.add(article_id)
                return True

        return False
