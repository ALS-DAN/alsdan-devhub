"""Tests voor StorageFactory."""

import pytest

from devhub_storage.factory import StorageFactory
from devhub_storage.interface import StorageInterface


class TestStorageFactory:
    def test_create_local(self, tmp_path):
        store = StorageFactory.create("local", root_path=tmp_path)
        assert isinstance(store, StorageInterface)

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="Unknown storage backend"):
            StorageFactory.create("nonexistent")

    def test_available_backends(self):
        backends = StorageFactory.available_backends()
        assert "local" in backends
        assert "google_drive" in backends

    def test_default_backend(self, tmp_path):
        store = StorageFactory.create(root_path=tmp_path)
        assert isinstance(store, StorageInterface)
        h = store.health()
        # LocalAdapter returns its backend name
        assert h.status == "UP"

    def test_available_backends_sorted(self):
        backends = StorageFactory.available_backends()
        assert backends == sorted(backends)


class TestPackageImports:
    def test_import_interface(self):
        from devhub_storage import StorageInterface

        assert StorageInterface is not None

    def test_import_local_adapter(self):
        from devhub_storage import LocalAdapter

        assert issubclass(LocalAdapter, StorageInterface)

    def test_import_google_drive_adapter(self):
        from devhub_storage.adapters.google_drive_adapter import (
            GoogleDriveAdapter,
        )

        assert issubclass(GoogleDriveAdapter, StorageInterface)
