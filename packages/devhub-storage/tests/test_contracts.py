"""Tests voor Storage Contracts — frozen dataclasses en exceptions."""

import pytest

from devhub_storage.contracts import (
    ChangeEvent,
    DriftItem,
    DriftReport,
    ItemType,
    ReconcileResult,
    StorageAlreadyExistsError,
    StorageError,
    StorageHealth,
    StorageItem,
    StorageNotFoundError,
    StoragePathError,
    StoragePermissionError,
    StorageTree,
    WriteResult,
)


# ---------------------------------------------------------------------------
# StorageItem
# ---------------------------------------------------------------------------


class TestStorageItem:
    def test_valid_item(self):
        item = StorageItem(
            path="docs/readme.md",
            name="readme.md",
            item_type=ItemType.FILE,
            size_bytes=1024,
            modified_at="2026-03-25T10:00:00+00:00",
        )
        assert item.path == "docs/readme.md"
        assert item.item_type == ItemType.FILE
        assert item.size_bytes == 1024

    def test_frozen(self):
        item = StorageItem(
            path="a.txt",
            name="a.txt",
            item_type=ItemType.FILE,
            size_bytes=0,
            modified_at="2026-01-01T00:00:00+00:00",
        )
        with pytest.raises(AttributeError):
            item.path = "b.txt"  # type: ignore[misc]

    def test_empty_path_raises(self):
        with pytest.raises(ValueError, match="path is required"):
            StorageItem(
                path="",
                name="a.txt",
                item_type=ItemType.FILE,
                size_bytes=0,
                modified_at="2026-01-01T00:00:00+00:00",
            )

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="name is required"):
            StorageItem(
                path="a.txt",
                name="",
                item_type=ItemType.FILE,
                size_bytes=0,
                modified_at="2026-01-01T00:00:00+00:00",
            )

    def test_negative_size_raises(self):
        with pytest.raises(ValueError, match="size_bytes cannot be negative"):
            StorageItem(
                path="a.txt",
                name="a.txt",
                item_type=ItemType.FILE,
                size_bytes=-1,
                modified_at="2026-01-01T00:00:00+00:00",
            )

    def test_directory_item(self):
        item = StorageItem(
            path="subdir",
            name="subdir",
            item_type=ItemType.DIRECTORY,
            size_bytes=0,
            modified_at="2026-01-01T00:00:00+00:00",
        )
        assert item.item_type == ItemType.DIRECTORY
        assert item.content_hash is None

    def test_metadata_default_empty(self):
        item = StorageItem(
            path="a.txt",
            name="a.txt",
            item_type=ItemType.FILE,
            size_bytes=0,
            modified_at="2026-01-01T00:00:00+00:00",
        )
        assert item.metadata == {}


# ---------------------------------------------------------------------------
# StorageTree
# ---------------------------------------------------------------------------


class TestStorageTree:
    def _make_file(self, path: str = "f.txt") -> StorageItem:
        return StorageItem(
            path=path,
            name=path,
            item_type=ItemType.FILE,
            size_bytes=10,
            modified_at="2026-01-01T00:00:00+00:00",
        )

    def _make_dir(self, path: str = "dir") -> StorageItem:
        return StorageItem(
            path=path,
            name=path,
            item_type=ItemType.DIRECTORY,
            size_bytes=0,
            modified_at="2026-01-01T00:00:00+00:00",
        )

    def test_valid_tree(self):
        tree = StorageTree(item=self._make_dir(), children=(StorageTree(item=self._make_file()),))
        assert len(tree.children) == 1

    def test_file_with_children_raises(self):
        child = StorageTree(item=self._make_file("c.txt"))
        with pytest.raises(ValueError, match="FILE items cannot have children"):
            StorageTree(item=self._make_file(), children=(child,))

    def test_empty_dir(self):
        tree = StorageTree(item=self._make_dir())
        assert tree.children == ()

    def test_frozen(self):
        tree = StorageTree(item=self._make_dir())
        with pytest.raises(AttributeError):
            tree.children = ()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# StorageHealth
# ---------------------------------------------------------------------------


class TestStorageHealth:
    def test_valid_health(self):
        h = StorageHealth(
            status="UP",
            backend="local",
            root_path="/tmp/test",
            total_items=10,
            total_size_bytes=1024,
            readable=True,
            writable=True,
        )
        assert h.status == "UP"
        assert h.backend == "local"

    def test_empty_backend_raises(self):
        with pytest.raises(ValueError, match="backend is required"):
            StorageHealth(
                status="UP",
                backend="",
                root_path="/tmp",
                total_items=0,
                total_size_bytes=0,
                readable=True,
                writable=True,
            )

    def test_negative_total_items_raises(self):
        with pytest.raises(ValueError, match="total_items cannot be negative"):
            StorageHealth(
                status="UP",
                backend="local",
                root_path="/tmp",
                total_items=-1,
                total_size_bytes=0,
                readable=True,
                writable=True,
            )

    def test_negative_total_size_raises(self):
        with pytest.raises(ValueError, match="total_size_bytes cannot be negative"):
            StorageHealth(
                status="UP",
                backend="local",
                root_path="/tmp",
                total_items=0,
                total_size_bytes=-1,
                readable=True,
                writable=True,
            )

    def test_frozen(self):
        h = StorageHealth(
            status="UP",
            backend="local",
            root_path="/tmp",
            total_items=0,
            total_size_bytes=0,
            readable=True,
            writable=True,
        )
        with pytest.raises(AttributeError):
            h.status = "DOWN"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WriteResult
# ---------------------------------------------------------------------------


class TestWriteResult:
    def test_valid_result(self):
        r = WriteResult(success=True, path="new.txt", operation="put", bytes_written=100)
        assert r.success is True
        assert r.bytes_written == 100

    def test_empty_path_raises(self):
        with pytest.raises(ValueError, match="path is required"):
            WriteResult(success=True, path="", operation="put")

    def test_frozen(self):
        r = WriteResult(success=True, path="a.txt", operation="put")
        with pytest.raises(AttributeError):
            r.success = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ChangeEvent
# ---------------------------------------------------------------------------


class TestChangeEvent:
    def test_valid_event(self):
        e = ChangeEvent(
            path="a.txt",
            event_type="created",
            timestamp="2026-03-25T10:00:00+00:00",
        )
        assert e.event_type == "created"

    def test_moved_without_old_path_raises(self):
        with pytest.raises(ValueError, match="old_path is required"):
            ChangeEvent(
                path="b.txt",
                event_type="moved",
                timestamp="2026-03-25T10:00:00+00:00",
            )

    def test_moved_with_old_path(self):
        e = ChangeEvent(
            path="b.txt",
            event_type="moved",
            timestamp="2026-03-25T10:00:00+00:00",
            old_path="a.txt",
        )
        assert e.old_path == "a.txt"

    def test_empty_path_raises(self):
        with pytest.raises(ValueError, match="path is required"):
            ChangeEvent(path="", event_type="created", timestamp="2026-01-01T00:00:00+00:00")

    def test_empty_timestamp_raises(self):
        with pytest.raises(ValueError, match="timestamp is required"):
            ChangeEvent(path="a.txt", event_type="created", timestamp="")

    def test_frozen(self):
        e = ChangeEvent(path="a.txt", event_type="created", timestamp="2026-01-01T00:00:00+00:00")
        with pytest.raises(AttributeError):
            e.path = "b.txt"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DriftItem
# ---------------------------------------------------------------------------


class TestDriftItem:
    def test_valid_drift(self):
        d = DriftItem(path="missing.txt", drift_type="missing")
        assert d.drift_type == "missing"

    def test_empty_path_raises(self):
        with pytest.raises(ValueError, match="path is required"):
            DriftItem(path="", drift_type="missing")

    def test_frozen(self):
        d = DriftItem(path="a.txt", drift_type="extra")
        with pytest.raises(AttributeError):
            d.path = "b.txt"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DriftReport
# ---------------------------------------------------------------------------


class TestDriftReport:
    def test_empty_report_in_sync(self):
        r = DriftReport()
        assert r.in_sync is True
        assert r.drifts == ()

    def test_drifts_auto_set_not_in_sync(self):
        d = DriftItem(path="x.txt", drift_type="missing")
        r = DriftReport(drifts=(d,), in_sync=True)
        assert r.in_sync is False  # auto-corrected

    def test_explicit_not_in_sync(self):
        r = DriftReport(drifts=(), in_sync=False)
        assert r.in_sync is False

    def test_frozen(self):
        r = DriftReport()
        with pytest.raises(AttributeError):
            r.in_sync = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ReconcileResult
# ---------------------------------------------------------------------------


class TestReconcileResult:
    def test_valid_dry_run(self):
        r = ReconcileResult(dry_run=True, actions_planned=3, actions_executed=0)
        assert r.dry_run is True
        assert r.actions_executed == 0

    def test_valid_execution(self):
        d = DriftItem(path="x.txt", drift_type="missing")
        r = ReconcileResult(
            dry_run=False,
            actions_planned=1,
            actions_executed=1,
            drifts_resolved=(d,),
        )
        assert r.actions_executed == 1
        assert len(r.drifts_resolved) == 1

    def test_frozen(self):
        r = ReconcileResult(dry_run=True, actions_planned=0, actions_executed=0)
        with pytest.raises(AttributeError):
            r.dry_run = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptions:
    def test_storage_error_is_base(self):
        assert issubclass(StorageNotFoundError, StorageError)
        assert issubclass(StoragePermissionError, StorageError)
        assert issubclass(StoragePathError, StorageError)
        assert issubclass(StorageAlreadyExistsError, StorageError)

    def test_storage_error_is_exception(self):
        assert issubclass(StorageError, Exception)
