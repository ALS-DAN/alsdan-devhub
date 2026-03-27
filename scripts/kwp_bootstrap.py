"""
KWP DEV Bootstrap — Laad seed articles in ChromaDB en draai health check.

Gebruik:
    uv run python scripts/kwp_bootstrap.py [--persist-dir .kwp-dev/chromadb]
"""

from __future__ import annotations

import argparse
import sys

from devhub_core.agents.knowledge_curator import KnowledgeCurator
from devhub_core.research.bootstrap import BootstrapPipeline
from devhub_core.research.knowledge_store import KnowledgeStore
from devhub_core.research.seed_articles import get_seed_articles
from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore
from devhub_vectorstore.embeddings.hash_provider import HashEmbeddingProvider


def main(persist_dir: str | None = None) -> int:
    """Bootstrap KWP DEV met seed articles."""
    vectorstore = ChromaDBZonedStore(persist_directory=persist_dir)
    embedding = HashEmbeddingProvider()
    store = KnowledgeStore(vectorstore, embedding)
    curator = KnowledgeCurator()

    pipeline = BootstrapPipeline(curator, store)
    articles = get_seed_articles()

    print(f"Seed articles laden: {len(articles)} articles")
    report = pipeline.run_seed(articles)

    print("\nResultaat:")
    print(f"  Submitted: {report.total_submitted}")
    print(f"  Approved:  {report.approved}")
    print(f"  Rejected:  {report.rejected}")
    print(f"  Needs rev: {report.needs_revision}")

    for r in report.reports:
        status = "OK" if not r.findings else f"{len(r.findings)} findings"
        print(f"  {r.article_id}: {r.verdict.value} ({status})")

    print("\nHealth check...")
    health = pipeline.health_check()
    print(f"  Overall score: {health.overall_score}")
    print(f"  Grading: {health.grading_distribution}")
    print(f"  Domains: {health.domain_coverage}")

    if health.findings:
        print(f"  Findings ({len(health.findings)}):")
        for f in health.findings:
            print(f"    - {f}")

    print("\nSearch test: 'multi-agent architectuur'")
    results = store.search("multi-agent architectuur", limit=3)
    for r in results:
        print(f"  - {r.article_id}: {r.title} [{r.grade}]")

    ok = report.approved > 0 and health.overall_score >= 50
    print(f"\n{'KWP DEV operationeel' if ok else 'KWP DEV NIET operationeel'}")
    return 0 if ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KWP DEV Bootstrap")
    parser.add_argument(
        "--persist-dir",
        default=None,
        help="ChromaDB persist directory (default: in-memory)",
    )
    args = parser.parse_args()
    sys.exit(main(args.persist_dir))
