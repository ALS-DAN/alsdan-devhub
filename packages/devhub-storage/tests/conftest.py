"""Shared fixtures voor devhub-storage tests."""

from __future__ import annotations

import pytest

from devhub_storage.adapters.local_adapter import LocalAdapter


@pytest.fixture
def storage_root(tmp_path):
    """Lege storage root directory."""
    return tmp_path


@pytest.fixture
def adapter(storage_root):
    """LocalAdapter met lege tmp_path als root."""
    return LocalAdapter(storage_root)


@pytest.fixture
def populated_adapter(storage_root):
    """LocalAdapter met vooraf aangemaakte bestanden."""
    (storage_root / "file1.txt").write_text("hello")
    (storage_root / "file2.py").write_text("print('hi')")
    sub = storage_root / "subdir"
    sub.mkdir()
    (sub / "nested.txt").write_text("nested content")
    (sub / "deep").mkdir()
    (sub / "deep" / "deep_file.md").write_text("# Deep")
    return LocalAdapter(storage_root)
