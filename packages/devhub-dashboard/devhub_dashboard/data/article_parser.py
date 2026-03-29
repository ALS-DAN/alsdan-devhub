"""Knowledge Article Parser — fuzzy frontmatter parsing met normalisatie.

Ondersteunt twee formaten:
- Formaat A (research): ``# Title`` boven ``---`` YAML frontmatter
- Formaat B (retrospectives): standaard ``---`` YAML frontmatter bovenaan
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class ParsedArticle:
    """Genormaliseerd kennisartikel uit filesystem."""

    file_path: str
    title: str
    domain: str
    grade: str  # GOLD | SILVER | BRONZE | SPECULATIVE
    date: str  # ISO 8601 of leeg
    author: str
    summary: str
    freshness_days: int
    sprint: str
    sources: list[str] = field(default_factory=list)
    rq_tags: list[str] = field(default_factory=list)
    raw_metadata: dict = field(default_factory=dict)

    @property
    def article_id(self) -> str:
        """Stabiel ID op basis van bestandspad relatief aan knowledge/."""
        return self.file_path

    @property
    def ring(self) -> str:
        """Infer ring uit domain."""
        core_domains = {
            "python_architecture",
            "ai_engineering",
            "testing_qa",
            "security_appsec",
            "development_methodology",
        }
        agent_domains = {
            "coaching_learning",
            "governance_compliance",
            "documentation",
        }
        if self.domain in core_domains:
            return "core"
        if self.domain in agent_domains:
            return "agent"
        return "project"

    @property
    def freshness_color(self) -> str:
        """Freshness kleurcodering."""
        if self.freshness_days < 30:
            return "positive"
        if self.freshness_days < 90:
            return "warning"
        return "negative"


class KnowledgeArticleParser:
    """Parse knowledge/*.md bestanden in beide frontmatter-formaten."""

    _GRADE_PATTERN = re.compile(r"\b(GOLD|SILVER|BRONZE|SPECULATIVE)\b", re.IGNORECASE)

    def parse(self, file_path: Path, knowledge_root: Path | None = None) -> ParsedArticle | None:
        """Parse een markdown bestand naar een ParsedArticle.

        Args:
            file_path: Absoluut pad naar het .md bestand.
            knowledge_root: Root van de knowledge directory (voor relatief pad).
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError:
            return None

        # Probeer standaard frontmatter eerst (Formaat B)
        metadata = self._parse_standard_frontmatter(content)

        # Dan header+frontmatter (Formaat A)
        if not metadata:
            metadata = self._parse_header_frontmatter(content)

        if not metadata:
            # Minimale fallback: geen frontmatter gevonden
            metadata = {}

        return self._normalize(file_path, metadata, content, knowledge_root)

    def _parse_standard_frontmatter(self, content: str) -> dict | None:
        """Formaat B: ``---\\nyaml\\n---`` bovenaan het bestand."""
        match = re.match(r"\A---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        return self._parse_yaml_block(match.group(1))

    def _parse_header_frontmatter(self, content: str) -> dict | None:
        """Formaat A: ``# Title\\n\\n---\\nyaml\\n---``."""
        match = re.match(r"\A#[^\n]+\n\s*---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        return self._parse_yaml_block(match.group(1))

    def _parse_yaml_block(self, block: str) -> dict:
        """Simpele key: value YAML parsing (geen nested structuren nodig)."""
        result: dict = {}
        for line in block.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            colon_idx = line.find(":")
            if colon_idx < 1:
                continue
            key = line[:colon_idx].strip()
            value = line[colon_idx + 1 :].strip()
            # Strip quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            result[key] = value
        return result

    def _normalize(
        self,
        path: Path,
        meta: dict,
        content: str,
        knowledge_root: Path | None,
    ) -> ParsedArticle:
        """Map varierende veldnamen naar uniform model."""
        title = (
            meta.get("title")
            or self._extract_h1(content)
            or path.stem.replace("_", " ").replace("-", " ")
        )

        grade = (
            meta.get("grade")
            or meta.get("kennisgradering")
            or self._infer_grade(content)
            or "SPECULATIVE"
        ).upper()

        date_str = meta.get("date") or meta.get("datum") or ""
        domain = meta.get("domain") or self._infer_domain(path, knowledge_root)
        author = meta.get("author") or meta.get("auteur") or "unknown"
        sprint = meta.get("sprint") or ""
        summary = self._extract_summary(content)

        # Freshness berekening
        freshness_days = self._calc_freshness(date_str)

        # Sources
        sources: list[str] = []
        bron = meta.get("bron")
        if bron:
            sources.append(bron)

        # RQ-tags
        rq_tags: list[str] = []
        for key, val in meta.items():
            if key.startswith("rq") or key.startswith("RQ"):
                rq_tags.append(f"{key}: {val}")

        # Relatief pad als file_path
        if knowledge_root and path.is_relative_to(knowledge_root):
            rel_path = str(path.relative_to(knowledge_root))
            # Strip .md extensie
            rel_path = rel_path.removesuffix(".md")
        else:
            rel_path = path.stem

        return ParsedArticle(
            file_path=rel_path,
            title=title,
            domain=domain,
            grade=grade,
            date=date_str,
            author=author,
            summary=summary,
            freshness_days=freshness_days,
            sprint=str(sprint),
            sources=sources,
            rq_tags=rq_tags,
            raw_metadata=meta,
        )

    def _extract_h1(self, content: str) -> str:
        """Haal de eerste H1 header uit content."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    def _infer_grade(self, content: str) -> str:
        """Probeer grade te vinden in de eerste 1000 chars."""
        match = self._GRADE_PATTERN.search(content[:1000])
        return match.group(1).upper() if match else ""

    def _infer_domain(self, path: Path, knowledge_root: Path | None) -> str:
        """Leid domein af uit directory-structuur."""
        if knowledge_root and path.parent != knowledge_root:
            return path.parent.name
        return "general"

    def _extract_summary(self, content: str) -> str:
        """Haal eerste 2-3 zinnen na headers/frontmatter."""
        # Strip frontmatter
        cleaned = re.sub(r"\A---.*?---\s*", "", content, flags=re.DOTALL)
        # Strip header+frontmatter variant
        cleaned = re.sub(r"\A#[^\n]+\n\s*---.*?---\s*", "", cleaned, flags=re.DOTALL)
        # Strip alle markdown headers
        cleaned = re.sub(r"^#+\s+.*$", "", cleaned, flags=re.MULTILINE)
        # Strip lege regels en leading whitespace
        cleaned = cleaned.strip()

        if not cleaned:
            return ""

        # Pak eerste 2-3 zinnen (tot 300 chars)
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        result = ""
        for s in sentences[:3]:
            if len(result) + len(s) > 300:
                break
            result += s + " "
        return result.strip()

    def _calc_freshness(self, date_str: str) -> int:
        """Bereken dagen sinds publicatie. Returns 9999 als datum niet parseerbaar."""
        if not date_str:
            return 9999
        try:
            pub_date = date.fromisoformat(date_str[:10])
            delta = date.today() - pub_date
            return max(0, delta.days)
        except (ValueError, IndexError):
            return 9999
