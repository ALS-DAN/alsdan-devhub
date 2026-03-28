"""Tests voor DriveSyncAdapter — Google Drive via filesystem sync."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from devhub_storage.adapters.drive_sync_adapter import (
    DriveSyncAdapter,
    detect_drive_sync_root,
)
from devhub_storage.contracts import StorageError, StorageNotFoundError
from devhub_storage.interface import StorageInterface

_MOD = "devhub_storage.adapters.drive_sync_adapter"


# ---------------------------------------------------------------------------
# detect_drive_sync_root
# ---------------------------------------------------------------------------


class TestDetectDriveSyncRoot:
    def test_returns_none_on_linux(self):
        with patch(f"{_MOD}.platform.system", return_value="Linux"):
            assert detect_drive_sync_root() is None

    def test_detects_macos_sync_folder(self, tmp_path):
        cloud_storage = tmp_path / "Library" / "CloudStorage"
        my_drive = cloud_storage / "GoogleDrive-test@gmail.com" / "My Drive"
        my_drive.mkdir(parents=True)

        with (
            patch(f"{_MOD}.platform.system", return_value="Darwin"),
            patch(f"{_MOD}.Path.home", return_value=tmp_path),
        ):
            result = detect_drive_sync_root()
            assert result is not None
            assert result == my_drive

    def test_returns_none_when_no_cloud_storage(self, tmp_path):
        with (
            patch(f"{_MOD}.platform.system", return_value="Darwin"),
            patch(f"{_MOD}.Path.home", return_value=tmp_path),
        ):
            assert detect_drive_sync_root() is None

    def test_returns_none_when_no_google_drive_folder(self, tmp_path):
        cloud_storage = tmp_path / "Library" / "CloudStorage"
        cloud_storage.mkdir(parents=True)

        with (
            patch(f"{_MOD}.platform.system", return_value="Darwin"),
            patch(f"{_MOD}.Path.home", return_value=tmp_path),
        ):
            assert detect_drive_sync_root() is None

    def test_returns_none_when_my_drive_missing(self, tmp_path):
        cloud_storage = tmp_path / "Library" / "CloudStorage"
        (cloud_storage / "GoogleDrive-test@gmail.com").mkdir(parents=True)
        # No "My Drive" subfolder

        with (
            patch(f"{_MOD}.platform.system", return_value="Darwin"),
            patch(f"{_MOD}.Path.home", return_value=tmp_path),
        ):
            assert detect_drive_sync_root() is None

    def test_picks_first_matching_account(self, tmp_path):
        cloud_storage = tmp_path / "Library" / "CloudStorage"
        drive_a = cloud_storage / "GoogleDrive-a@gmail.com" / "My Drive"
        drive_b = cloud_storage / "GoogleDrive-b@gmail.com" / "My Drive"
        drive_a.mkdir(parents=True)
        drive_b.mkdir(parents=True)

        with (
            patch(f"{_MOD}.platform.system", return_value="Darwin"),
            patch(f"{_MOD}.Path.home", return_value=tmp_path),
        ):
            result = detect_drive_sync_root()
            assert result is not None
            assert "GoogleDrive-" in str(result)


# ---------------------------------------------------------------------------
# DriveSyncAdapter — explicit path
# ---------------------------------------------------------------------------


class TestDriveSyncAdapterExplicitPath:
    @pytest.fixture()
    def drive_root(self, tmp_path):
        """Simulate a Google Drive sync folder."""
        my_drive = tmp_path / "My Drive"
        my_drive.mkdir()
        return my_drive

    @pytest.fixture()
    def adapter(self, drive_root):
        return DriveSyncAdapter(drive_root=drive_root, node_drive_root="DevHub")

    def test_is_storage_interface(self, adapter):
        assert isinstance(adapter, StorageInterface)

    def test_backend_name(self, adapter):
        assert adapter.BACKEND == "drive_sync"

    def test_sync_root(self, adapter, drive_root):
        assert adapter.sync_root == drive_root

    def test_target_root_created(self, adapter, drive_root):
        expected = drive_root / "DevHub"
        assert adapter.target_root == expected
        assert expected.is_dir()

    def test_put_and_get(self, adapter):
        result = adapter.put("test.md", b"# Hello")
        assert result.success
        assert result.path == "test.md"

        item = adapter.get("test.md")
        assert item.name == "test.md"
        assert item.size_bytes == 7

    def test_put_creates_subdirectories(self, adapter):
        result = adapter.put("knowledge/methodology/shape-up.md", b"# Shape Up")
        assert result.success

        item = adapter.get("knowledge/methodology/shape-up.md")
        assert item.name == "shape-up.md"

    def test_list_empty(self, adapter):
        items = adapter.list()
        assert items == []

    def test_list_with_files(self, adapter):
        adapter.put("a.md", b"a")
        adapter.put("b.md", b"b")
        items = adapter.list()
        names = [i.name for i in items]
        assert "a.md" in names
        assert "b.md" in names

    def test_search(self, adapter):
        adapter.put("docs/one.md", b"one")
        adapter.put("docs/two.txt", b"two")
        results = adapter.search("*.md", path="docs")
        assert len(results) == 1
        assert results[0].name == "one.md"

    def test_mkdir(self, adapter):
        result = adapter.mkdir("process/pattern")
        assert result.success
        items = adapter.list("process")
        assert any(i.name == "pattern" for i in items)

    def test_move(self, adapter):
        adapter.put("old.md", b"content")
        result = adapter.move("old.md", "new.md")
        assert result.success
        with pytest.raises(StorageNotFoundError):
            adapter.get("old.md")
        item = adapter.get("new.md")
        assert item.name == "new.md"

    def test_delete(self, adapter):
        adapter.put("temp.md", b"temp")
        result = adapter.delete("temp.md")
        assert result.success
        with pytest.raises(StorageNotFoundError):
            adapter.get("temp.md")

    def test_tree(self, adapter):
        adapter.put("a/b/c.md", b"deep")
        tree = adapter.tree()
        assert tree.item.name == "DevHub"


# ---------------------------------------------------------------------------
# DriveSyncAdapter — health check
# ---------------------------------------------------------------------------


class TestDriveSyncAdapterHealth:
    def test_health_up(self, tmp_path):
        my_drive = tmp_path / "My Drive"
        my_drive.mkdir()
        adapter = DriveSyncAdapter(drive_root=my_drive, node_drive_root="DevHub")

        health = adapter.health()
        assert health.status == "UP"
        assert health.backend == "drive_sync"
        assert "DevHub" in health.root_path

    def test_health_down_when_sync_root_removed(self, tmp_path):
        my_drive = tmp_path / "My Drive"
        my_drive.mkdir()
        adapter = DriveSyncAdapter(drive_root=my_drive, node_drive_root="DevHub")

        # Simulate Drive sync stopping (root disappears)
        import shutil

        shutil.rmtree(my_drive)

        health = adapter.health()
        assert health.status == "DOWN"
        assert "not available" in health.message


# ---------------------------------------------------------------------------
# DriveSyncAdapter — auto-detect
# ---------------------------------------------------------------------------


class TestDriveSyncAdapterAutoDetect:
    def test_raises_when_no_sync_folder(self):
        with patch(
            "devhub_storage.adapters.drive_sync_adapter.detect_drive_sync_root",
            return_value=None,
        ):
            with pytest.raises(StorageError, match="sync folder not found"):
                DriveSyncAdapter()

    def test_auto_detects_sync_folder(self, tmp_path):
        my_drive = tmp_path / "My Drive"
        my_drive.mkdir()

        with patch(
            "devhub_storage.adapters.drive_sync_adapter.detect_drive_sync_root",
            return_value=my_drive,
        ):
            adapter = DriveSyncAdapter(node_drive_root="TestNode")
            assert adapter.sync_root == my_drive
            assert (my_drive / "TestNode").is_dir()


# ---------------------------------------------------------------------------
# Factory integration
# ---------------------------------------------------------------------------


class TestDriveSyncFactory:
    def test_drive_sync_in_available_backends(self):
        from devhub_storage.factory import StorageFactory

        assert "drive_sync" in StorageFactory.available_backends()

    def test_factory_creates_drive_sync(self, tmp_path):
        my_drive = tmp_path / "My Drive"
        my_drive.mkdir()

        from devhub_storage.factory import StorageFactory

        adapter = StorageFactory.create(
            "drive_sync",
            drive_root=my_drive,
            node_drive_root="DevHub",
        )
        assert isinstance(adapter, DriveSyncAdapter)
        assert isinstance(adapter, StorageInterface)

    def test_import_from_package(self):
        from devhub_storage import DriveSyncAdapter as Imported

        assert Imported is DriveSyncAdapter
