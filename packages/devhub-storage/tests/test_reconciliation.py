"""Tests voor ReconciliationEngine — drift detectie en reconciliatie."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devhub_storage.contracts import (
    ItemType,
    StorageItem,
    StorageNotFoundError,
    WriteResult,
)
from devhub_storage.reconciliation import (
    ReconciliationEngine,
    ReconciliationSpec,
    SpecItem,
    parse_spec,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _item(path: str, item_type: str = "file", content_hash: str | None = None) -> StorageItem:
    """Helper om snel een StorageItem aan te maken."""
    name = path.rstrip("/").split("/")[-1]
    return StorageItem(
        path=path,
        name=name or path,
        item_type=ItemType.FILE if item_type == "file" else ItemType.DIRECTORY,
        size_bytes=100,
        modified_at="2026-03-27T12:00:00Z",
        content_hash=content_hash,
    )


@pytest.fixture
def mock_adapter() -> MagicMock:
    """Mock StorageInterface adapter."""
    adapter = MagicMock()
    adapter.list.return_value = []
    adapter.mkdir.return_value = WriteResult(success=True, path="placeholder", operation="mkdir")
    adapter.delete.return_value = WriteResult(success=True, path="placeholder", operation="delete")
    return adapter


@pytest.fixture
def engine(mock_adapter: MagicMock) -> ReconciliationEngine:
    """ReconciliationEngine met mock adapter."""
    return ReconciliationEngine(adapter=mock_adapter)


# ---------------------------------------------------------------------------
# Spec parsing
# ---------------------------------------------------------------------------


class TestParseSpec:
    """Tests voor parse_spec."""

    def test_valid_spec(self) -> None:
        raw = {
            "root": "projects/kb",
            "items": [
                {"path": "docs/", "type": "directory"},
                {"path": "docs/README.md", "type": "file", "content_hash": "abc123"},
            ],
        }
        spec = parse_spec(raw)
        assert spec.root == "projects/kb"
        assert len(spec.items) == 2
        assert spec.items[0].item_type == ItemType.DIRECTORY
        assert spec.items[1].content_hash == "abc123"

    def test_empty_items(self) -> None:
        spec = parse_spec({"root": "", "items": []})
        assert spec.items == ()

    def test_missing_root_defaults_empty(self) -> None:
        spec = parse_spec({"items": []})
        assert spec.root == ""

    def test_not_a_dict(self) -> None:
        with pytest.raises(ValueError, match="spec must be a dict"):
            parse_spec("invalid")  # type: ignore[arg-type]

    def test_items_not_a_list(self) -> None:
        with pytest.raises(ValueError, match="spec.items must be a list"):
            parse_spec({"root": "", "items": "bad"})

    def test_item_not_a_dict(self) -> None:
        with pytest.raises(ValueError, match="spec.items\\[0\\] must be a dict"):
            parse_spec({"root": "", "items": ["bad"]})

    def test_item_missing_path(self) -> None:
        with pytest.raises(ValueError, match="path is required"):
            parse_spec({"root": "", "items": [{"type": "file"}]})

    def test_item_invalid_type(self) -> None:
        with pytest.raises(ValueError, match="must be 'file' or 'directory'"):
            parse_spec({"root": "", "items": [{"path": "x", "type": "symlink"}]})

    def test_item_missing_type(self) -> None:
        with pytest.raises(ValueError, match="must be 'file' or 'directory'"):
            parse_spec({"root": "", "items": [{"path": "x"}]})


# ---------------------------------------------------------------------------
# SpecItem / ReconciliationSpec dataclass
# ---------------------------------------------------------------------------


class TestSpecDataclasses:
    """Tests voor SpecItem en ReconciliationSpec frozen dataclasses."""

    def test_spec_item_frozen(self) -> None:
        item = SpecItem(path="test.md", item_type=ItemType.FILE)
        with pytest.raises(AttributeError):
            item.path = "other.md"  # type: ignore[misc]

    def test_spec_item_empty_path(self) -> None:
        with pytest.raises(ValueError, match="path is required"):
            SpecItem(path="", item_type=ItemType.FILE)

    def test_reconciliation_spec_frozen(self) -> None:
        spec = ReconciliationSpec(root="r")
        with pytest.raises(AttributeError):
            spec.root = "x"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Drift detectie
# ---------------------------------------------------------------------------


class TestDriftReport:
    """Tests voor drift_report — read-only vergelijking."""

    def test_in_sync(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [
            _item("root/docs", "directory"),
            _item("root/docs/README.md", "file"),
        ]
        spec = {
            "root": "root",
            "items": [
                {"path": "docs", "type": "directory"},
                {"path": "docs/README.md", "type": "file"},
            ],
        }
        report = engine.drift_report(spec)
        assert report.in_sync is True
        assert report.drifts == ()

    def test_missing_item(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = []
        spec = {"root": "", "items": [{"path": "missing.md", "type": "file"}]}
        report = engine.drift_report(spec)
        assert report.in_sync is False
        assert len(report.drifts) == 1
        assert report.drifts[0].drift_type == "missing"
        assert report.drifts[0].path == "missing.md"

    def test_extra_item(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [
            _item("root/unexpected.txt", "file"),
        ]
        spec = {"root": "root", "items": []}
        report = engine.drift_report(spec)
        assert report.in_sync is False
        assert len(report.drifts) == 1
        assert report.drifts[0].drift_type == "extra"

    def test_wrong_type(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [
            _item("docs", "directory"),
        ]
        spec = {"root": "", "items": [{"path": "docs", "type": "file"}]}
        report = engine.drift_report(spec)
        assert report.in_sync is False
        assert report.drifts[0].drift_type == "wrong_type"
        assert report.drifts[0].expected == "file"
        assert report.drifts[0].actual == "directory"

    def test_wrong_content(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [
            _item("f.md", "file", content_hash="actual_hash"),
        ]
        spec = {
            "root": "",
            "items": [{"path": "f.md", "type": "file", "content_hash": "expected_hash"}],
        }
        report = engine.drift_report(spec)
        assert report.in_sync is False
        assert report.drifts[0].drift_type == "wrong_content"

    def test_content_hash_match(
        self,
        engine: ReconciliationEngine,
        mock_adapter: MagicMock,
    ) -> None:
        mock_adapter.list.return_value = [
            _item("f.md", "file", content_hash="same_hash"),
        ]
        spec = {
            "root": "",
            "items": [{"path": "f.md", "type": "file", "content_hash": "same_hash"}],
        }
        report = engine.drift_report(spec)
        assert report.in_sync is True

    def test_content_hash_ignored_when_not_in_spec(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = [
            _item("f.md", "file", content_hash="any_hash"),
        ]
        spec = {"root": "", "items": [{"path": "f.md", "type": "file"}]}
        report = engine.drift_report(spec)
        assert report.in_sync is True

    def test_root_not_found(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.side_effect = StorageNotFoundError("not found")
        spec = {"root": "nonexistent", "items": [{"path": "f.md", "type": "file"}]}
        report = engine.drift_report(spec)
        assert report.in_sync is False
        assert report.drifts[0].drift_type == "missing"

    def test_empty_spec_empty_backend(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = []
        spec = {"root": "", "items": []}
        report = engine.drift_report(spec)
        assert report.in_sync is True
        assert report.drifts == ()

    def test_multiple_drifts(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [
            _item("root/extra.txt", "file"),
        ]
        spec = {
            "root": "root",
            "items": [
                {"path": "missing/", "type": "directory"},
                {"path": "also_missing.md", "type": "file"},
            ],
        }
        report = engine.drift_report(spec)
        assert report.in_sync is False
        assert len(report.drifts) == 3  # 2 missing + 1 extra

    def test_accepts_parsed_spec(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = []
        spec = ReconciliationSpec(root="", items=(SpecItem(path="a.md", item_type=ItemType.FILE),))
        report = engine.drift_report(spec)
        assert report.in_sync is False


# ---------------------------------------------------------------------------
# Reconcile
# ---------------------------------------------------------------------------


class TestReconcile:
    """Tests voor reconcile — apply corrections."""

    def test_in_sync_no_actions(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = [_item("f.md", "file")]
        spec = {"root": "", "items": [{"path": "f.md", "type": "file"}]}
        result = engine.reconcile(spec)
        assert result.actions_planned == 0
        assert result.actions_executed == 0
        assert result.dry_run is True

    def test_dry_run_no_mutations(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = []
        spec = {"root": "", "items": [{"path": "new/", "type": "directory"}]}
        result = engine.reconcile(spec, dry_run=True)
        assert result.actions_planned == 1
        assert result.actions_executed == 0
        assert result.dry_run is True
        mock_adapter.mkdir.assert_not_called()

    def test_mkdir_on_missing_directory(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = []
        mock_adapter.mkdir.return_value = WriteResult(success=True, path="new", operation="mkdir")
        spec = {"root": "", "items": [{"path": "new/", "type": "directory"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_planned == 1
        assert result.actions_executed == 1
        assert len(result.drifts_resolved) == 1
        mock_adapter.mkdir.assert_called_once_with("new/")

    def test_missing_file_error(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = []
        spec = {"root": "", "items": [{"path": "missing.md", "type": "file"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_planned == 1
        assert result.actions_executed == 0
        assert "no content in spec" in result.errors[0]

    def test_extra_not_removed_by_default(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = [_item("extra.txt", "file")]
        spec = {"root": "", "items": []}
        result = engine.reconcile(spec, dry_run=False, remove_extra=False)
        assert result.actions_planned == 0
        mock_adapter.delete.assert_not_called()

    def test_extra_removed_when_flag_set(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = [_item("extra.txt", "file")]
        mock_adapter.delete.return_value = WriteResult(
            success=True, path="extra.txt", operation="delete"
        )
        spec = {"root": "", "items": []}
        result = engine.reconcile(spec, dry_run=False, remove_extra=True)
        assert result.actions_planned == 1
        assert result.actions_executed == 1
        mock_adapter.delete.assert_called_once_with("extra.txt")

    def test_wrong_type_error(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [_item("docs", "directory")]
        spec = {"root": "", "items": [{"path": "docs", "type": "file"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_planned == 1
        assert result.actions_executed == 0
        assert "manual intervention" in result.errors[0]

    def test_wrong_content_error(
        self, engine: ReconciliationEngine, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.list.return_value = [_item("f.md", "file", content_hash="old")]
        spec = {"root": "", "items": [{"path": "f.md", "type": "file", "content_hash": "new"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_planned == 1
        assert "no content in spec" in result.errors[0]

    def test_mkdir_failure(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = []
        mock_adapter.mkdir.return_value = WriteResult(
            success=False, path="new", operation="mkdir", message="permission denied"
        )
        spec = {"root": "", "items": [{"path": "new/", "type": "directory"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_executed == 0
        assert "mkdir failed" in result.errors[0]

    def test_mkdir_exception(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = []
        mock_adapter.mkdir.side_effect = RuntimeError("boom")
        spec = {"root": "", "items": [{"path": "new/", "type": "directory"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_executed == 0
        assert "boom" in result.errors[0]

    def test_idempotence(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        """Na succesvolle reconcile moet drift_report in_sync tonen."""
        # Eerste call: missing directory
        mock_adapter.list.return_value = []
        mock_adapter.mkdir.return_value = WriteResult(success=True, path="docs", operation="mkdir")
        spec = {"root": "", "items": [{"path": "docs/", "type": "directory"}]}
        result = engine.reconcile(spec, dry_run=False)
        assert result.actions_executed == 1

        # Simuleer dat de directory nu bestaat
        mock_adapter.list.return_value = [_item("docs/", "directory")]
        report = engine.drift_report(spec)
        assert report.in_sync is True

    def test_root_path_joining(self, engine: ReconciliationEngine, mock_adapter: MagicMock) -> None:
        mock_adapter.list.return_value = [
            _item("project/docs", "directory"),
        ]
        spec = {
            "root": "project",
            "items": [{"path": "docs", "type": "directory"}],
        }
        report = engine.drift_report(spec)
        assert report.in_sync is True
