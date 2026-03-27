"""Tests voor AnalysisPipeline — Golf 3 kern.

Alle externe afhankelijkheden worden inline gemockt als FakeX klassen.
"""

from __future__ import annotations


from devhub_core.agents.analysis_pipeline import AnalysisPipeline
from devhub_core.contracts.analysis_contracts import (
    AnalysisRequest,
    AnalysisStepStatus,
    AnalysisType,
)
from devhub_core.contracts.curator_contracts import KnowledgeArticle, KnowledgeDomain
from devhub_core.contracts.research_contracts import ResearchDepth
from devhub_core.research.in_memory_queue import InMemoryResearchQueue


# ---------------------------------------------------------------------------
# Fake helpers
# ---------------------------------------------------------------------------


def _make_article(article_id: str = "ART-001", grade: str = "SILVER") -> KnowledgeArticle:
    return KnowledgeArticle(
        article_id=article_id,
        title=f"Artikel {article_id}",
        content="Dit is een kennisartikel over een relevant onderwerp.",
        domain=KnowledgeDomain.AI_ENGINEERING,
        grade=grade,
        sources=("bron-a", "bron-b"),
        verification_pct=70.0,
        date="2026-01-01",
        author="researcher",
    )


class FakeKnowledgeStore:
    def __init__(self, articles: list | None = None) -> None:
        self._articles = articles or []
        self.search_calls: list[dict] = []

    def search(self, query: str, domain=None, limit: int = 10):
        self.search_calls.append({"query": query, "domain": domain, "limit": limit})
        return self._articles[:limit]


class FakeDocumentInterface:
    def __init__(self, path: str = "docs/analyses/test.md") -> None:
        self._path = path
        self.create_calls: list = []

    def create(self, request):
        self.create_calls.append(request)
        return FakeDocumentResult(self._path)

    def from_template(self, template_path, data):
        return FakeDocumentResult(self._path)

    def supported_formats(self):
        return ["markdown"]


class FakeDocumentResult:
    def __init__(self, path: str) -> None:
        self.path = path


class FakeStorageInterface:
    def __init__(self, fail: bool = False) -> None:
        self._fail = fail
        self.put_calls: list[str] = []

    def put(self, path: str, content: bytes):
        if self._fail:
            raise RuntimeError("Storage gefaald")
        self.put_calls.append(path)
        return None


def _make_request(
    skip_research: bool = False,
    analysis_type: AnalysisType = AnalysisType.FREE,
    output_format: str = "markdown",
) -> AnalysisRequest:
    return AnalysisRequest(
        request_id="REQ-001",
        title="Test Analyse",
        question="Wat weet ik over embeddings?",
        analysis_type=analysis_type,
        domains=("ai_engineering",),
        depth=ResearchDepth.STANDARD,
        skip_research=skip_research,
        output_format=output_format,
        output_dir="",
    )


def _make_pipeline(
    articles: list | None = None,
    doc_path: str = "docs/analyses/test.md",
    local_fail: bool = False,
    remote_storage=None,
) -> tuple[
    AnalysisPipeline,
    FakeKnowledgeStore,
    FakeDocumentInterface,
    FakeStorageInterface,
    InMemoryResearchQueue,
]:
    store = FakeKnowledgeStore(articles)
    doc_interface = FakeDocumentInterface(doc_path)
    local_storage = FakeStorageInterface(fail=local_fail)
    research_queue = InMemoryResearchQueue()
    pipeline = AnalysisPipeline(
        knowledge_store=store,
        research_queue=research_queue,
        document_interface=doc_interface,
        local_storage=local_storage,
        remote_storage=remote_storage,
    )
    return pipeline, store, doc_interface, local_storage, research_queue


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_pipeline_run_returns_result():
    articles = [_make_article("A1"), _make_article("A2"), _make_article("A3")]
    pipeline, *_ = _make_pipeline(articles=articles)
    result = pipeline.run(_make_request())
    assert result.request_id == "REQ-001"
    assert result.title == "Test Analyse"


def test_pipeline_result_has_six_step_results():
    pipeline, *_ = _make_pipeline(articles=[_make_article()])
    result = pipeline.run(_make_request())
    assert len(result.step_results) == 6


def test_pipeline_retrieval_step_calls_search():
    pipeline, store, *_ = _make_pipeline(articles=[_make_article()])
    pipeline.run(_make_request())
    assert len(store.search_calls) == 1
    assert store.search_calls[0]["query"] == "Wat weet ik over embeddings?"


def test_pipeline_articles_in_result():
    articles = [_make_article("A1"), _make_article("A2"), _make_article("A3")]
    pipeline, *_ = _make_pipeline(articles=articles)
    result = pipeline.run(_make_request())
    assert "A1" in result.knowledge_articles_used
    assert "A2" in result.knowledge_articles_used


# ---------------------------------------------------------------------------
# Lacune-detectie
# ---------------------------------------------------------------------------


def test_pipeline_gap_detection_creates_gap_when_few_articles():
    pipeline, *_ = _make_pipeline(articles=[_make_article()])  # slechts 1, <3
    result = pipeline.run(_make_request())
    assert len(result.gaps_detected) >= 1


def test_pipeline_no_gap_when_enough_articles():
    articles = [_make_article(f"A{i}") for i in range(5)]
    pipeline, *_ = _make_pipeline(articles=articles)
    result = pipeline.run(_make_request())
    assert len(result.gaps_detected) == 0


# ---------------------------------------------------------------------------
# Research stap
# ---------------------------------------------------------------------------


def test_pipeline_research_step_submits_to_queue():
    pipeline, _, _, _, queue = _make_pipeline(articles=[])  # lege store → gap
    pipeline.run(_make_request(skip_research=False))
    assert len(queue.pending()) > 0


def test_pipeline_skip_research_skips_step_3():
    pipeline, _, _, _, queue = _make_pipeline(articles=[])
    result = pipeline.run(_make_request(skip_research=True))
    research_step = next(s for s in result.step_results if s.step_name == "research")
    assert research_step.status == AnalysisStepStatus.SKIPPED
    assert len(queue.pending()) == 0


def test_pipeline_research_request_ids_in_result():
    pipeline, _, _, _, queue = _make_pipeline(articles=[])
    result = pipeline.run(_make_request(skip_research=False))
    assert len(result.research_requests_created) >= 1


# ---------------------------------------------------------------------------
# Document-generatie
# ---------------------------------------------------------------------------


def test_pipeline_document_interface_called(tmp_path):
    pipeline, _, doc_interface, *_ = _make_pipeline(
        articles=[_make_article()],
        doc_path=str(tmp_path / "test.md"),
    )
    # Schrijf dummy bestand voor storage-stap
    (tmp_path / "test.md").write_bytes(b"test content")
    pipeline.run(_make_request())
    assert len(doc_interface.create_calls) == 1


def test_pipeline_document_path_in_result(tmp_path):
    doc_path = str(tmp_path / "output.md")
    pipeline, *_ = _make_pipeline(
        articles=[_make_article()],
        doc_path=doc_path,
    )
    (tmp_path / "output.md").write_bytes(b"output")
    result = pipeline.run(_make_request())
    assert result.document_path == doc_path
    assert result.document_generated is True


# ---------------------------------------------------------------------------
# Opslag
# ---------------------------------------------------------------------------


def test_pipeline_local_storage_used(tmp_path):
    doc_path = str(tmp_path / "test.md")
    (tmp_path / "test.md").write_bytes(b"document")
    pipeline, _, _, local_storage, _ = _make_pipeline(
        articles=[_make_article()],
        doc_path=doc_path,
    )
    pipeline.run(_make_request())
    assert len(local_storage.put_calls) == 1


def test_pipeline_remote_storage_graceful_degradation(tmp_path):
    doc_path = str(tmp_path / "test.md")
    (tmp_path / "test.md").write_bytes(b"document")
    remote_storage = FakeStorageInterface(fail=True)
    pipeline, _, _, local_storage, _ = _make_pipeline(
        articles=[_make_article()],
        doc_path=doc_path,
        remote_storage=remote_storage,
    )
    # Moet niet crashen
    result = pipeline.run(_make_request())
    # Lokaal geslaagd ondanks remote fail
    assert len(local_storage.put_calls) == 1
    storage_step = next(s for s in result.step_results if s.step_name == "storage")
    assert storage_step.status == AnalysisStepStatus.COMPLETED


def test_pipeline_remote_storage_none_no_error(tmp_path):
    doc_path = str(tmp_path / "test.md")
    (tmp_path / "test.md").write_bytes(b"document")
    pipeline, *_ = _make_pipeline(
        articles=[_make_article()],
        doc_path=doc_path,
        remote_storage=None,
    )
    result = pipeline.run(_make_request())
    assert result is not None
