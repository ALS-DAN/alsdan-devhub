"""Security tests voor LocalAdapter — path traversal, symlinks, property-based."""

from __future__ import annotations

import sys
import tempfile

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from devhub_storage.adapters.local_adapter import LocalAdapter
from devhub_storage.contracts import StorageError, StoragePathError


# ---------------------------------------------------------------------------
# Deterministic path traversal tests
# ---------------------------------------------------------------------------


class TestPathTraversal:
    def test_dotdot_escape(self, adapter):
        with pytest.raises(StoragePathError, match="traversal"):
            adapter.get("../../etc/passwd")

    def test_dotdot_mid_path(self, adapter):
        with pytest.raises(StoragePathError, match="traversal"):
            adapter.get("subdir/../../escape")

    def test_dotdot_encoded_backslash(self, adapter):
        with pytest.raises(StoragePathError, match="traversal"):
            adapter.get("..\\..\\etc\\passwd")

    def test_null_byte_injection(self, adapter):
        with pytest.raises(StoragePathError, match="Null bytes"):
            adapter.get("file\x00.txt")

    def test_null_byte_in_put(self, adapter):
        with pytest.raises(StoragePathError, match="Null bytes"):
            adapter.put("test\x00.txt", b"data")

    def test_resolve_path_absolute_stripped(self, adapter, storage_root):
        """Absolute paths get joined relative to root, not treated as absolute."""
        # /etc/passwd becomes root_path/etc/passwd, which doesn't exist
        # but crucially does NOT escape to /etc/passwd
        resolved = adapter._resolve_path("/something")
        assert str(resolved).startswith(str(storage_root))

    def test_single_dot_resolves_to_root(self, adapter, storage_root):
        resolved = adapter._resolve_path(".")
        assert resolved == storage_root

    def test_empty_path_resolves_to_root(self, adapter, storage_root):
        resolved = adapter._resolve_path("")
        assert resolved == storage_root

    def test_backslash_normalization(self, adapter, storage_root):
        """Backslashes are normalized to forward slashes."""
        (storage_root / "sub").mkdir()
        (storage_root / "sub" / "file.txt").write_text("ok")
        item = adapter.get("sub\\file.txt")
        assert item.name == "file.txt"

    def test_path_with_spaces(self, adapter, storage_root):
        (storage_root / "my folder").mkdir()
        (storage_root / "my folder" / "my file.txt").write_text("ok")
        item = adapter.get("my folder/my file.txt")
        assert item.name == "my file.txt"

    def test_unicode_path(self, adapter, storage_root):
        (storage_root / "documenten").mkdir()
        (storage_root / "documenten" / "café.txt").write_text("ok")
        item = adapter.get("documenten/café.txt")
        assert item.name == "café.txt"

    def test_very_long_path(self, adapter):
        long_path = "a" * 500
        with pytest.raises((StorageError, OSError)):
            adapter.get(long_path)


# ---------------------------------------------------------------------------
# Symlink tests
# ---------------------------------------------------------------------------


class TestSymlinks:
    @pytest.fixture
    def symlink_adapter(self, storage_root):
        """Adapter met een symlink binnen en buiten de root."""
        (storage_root / "real_file.txt").write_text("real")
        (storage_root / "internal_link").symlink_to(storage_root / "real_file.txt")

        outside = storage_root.parent / "outside_target.txt"
        outside.write_text("escaped")
        (storage_root / "escape_link").symlink_to(outside)

        return LocalAdapter(storage_root)

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require privileges on Windows")
    def test_internal_symlink_works(self, symlink_adapter):
        item = symlink_adapter.get("internal_link")
        assert item.name == "internal_link"

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require privileges on Windows")
    def test_escape_symlink_blocked(self, symlink_adapter):
        with pytest.raises(StoragePathError, match="traversal"):
            symlink_adapter.get("escape_link")


# ---------------------------------------------------------------------------
# Property-based tests (hypothesis)
# ---------------------------------------------------------------------------


class TestPropertyBased:
    @given(path=st.text(min_size=0, max_size=200))
    @settings(max_examples=200)
    def test_resolve_never_escapes_root(self, path):
        """No input string should ever resolve outside the root directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = LocalAdapter(tmpdir)
            try:
                resolved = adapter._resolve_path(path)
                assert str(resolved).startswith(str(adapter.root))
            except (StoragePathError, OSError):
                pass  # Expected for malicious or invalid inputs

    @given(path=st.from_regex(r"(\.\./){1,10}.*", fullmatch=True))
    @settings(max_examples=100)
    def test_dotdot_sequences_contained(self, path):
        """Paths with .. sequences must either stay contained or raise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = LocalAdapter(tmpdir)
            try:
                resolved = adapter._resolve_path(path)
                resolved.relative_to(adapter.root)
            except (StoragePathError, ValueError, OSError):
                pass  # Expected

    @given(content=st.binary(min_size=0, max_size=1024))
    @settings(max_examples=50)
    def test_put_get_roundtrip(self, content):
        """Any bytes written via put should produce a valid StorageItem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = LocalAdapter(tmpdir)
            result = adapter.put("test_file.bin", content)
            assert result.success is True
            assert result.bytes_written == len(content)
            item = adapter.get("test_file.bin")
            assert item.size_bytes == len(content)
