"""Tests voor LocalAdapter — CRUD operaties."""

import pytest

from devhub_storage.adapters.local_adapter import LocalAdapter
from devhub_storage.contracts import (
    ItemType,
    StorageError,
    StorageNotFoundError,
)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


class TestConstructor:
    def test_valid_root(self, storage_root):
        adapter = LocalAdapter(storage_root)
        assert adapter.root == storage_root

    def test_nonexistent_root_raises(self, tmp_path):
        with pytest.raises(StorageError, match="not a directory"):
            LocalAdapter(tmp_path / "nonexistent")

    def test_file_as_root_raises(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        with pytest.raises(StorageError, match="not a directory"):
            LocalAdapter(f)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


class TestList:
    def test_empty_dir(self, adapter):
        assert adapter.list() == []

    def test_flat_files(self, populated_adapter):
        items = populated_adapter.list()
        names = {i.name for i in items}
        assert "file1.txt" in names
        assert "file2.py" in names
        assert "subdir" in names

    def test_recursive(self, populated_adapter):
        items = populated_adapter.list(recursive=True)
        paths = {i.path for i in items}
        assert "subdir/nested.txt" in paths
        assert "subdir/deep/deep_file.md" in paths

    def test_subdir(self, populated_adapter):
        items = populated_adapter.list("subdir")
        names = {i.name for i in items}
        assert "nested.txt" in names
        assert "deep" in names

    def test_nonexistent_raises(self, adapter):
        with pytest.raises(StorageNotFoundError):
            adapter.list("nonexistent")

    def test_file_path_raises(self, populated_adapter):
        with pytest.raises(StorageError, match="Not a directory"):
            populated_adapter.list("file1.txt")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


class TestGet:
    def test_get_file(self, populated_adapter):
        item = populated_adapter.get("file1.txt")
        assert item.name == "file1.txt"
        assert item.item_type == ItemType.FILE
        assert item.size_bytes == 5  # "hello"
        assert item.content_hash is not None

    def test_get_directory(self, populated_adapter):
        item = populated_adapter.get("subdir")
        assert item.item_type == ItemType.DIRECTORY
        assert item.content_hash is None

    def test_get_nested(self, populated_adapter):
        item = populated_adapter.get("subdir/nested.txt")
        assert item.name == "nested.txt"

    def test_missing_raises(self, adapter):
        with pytest.raises(StorageNotFoundError):
            adapter.get("nope.txt")


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


class TestSearch:
    def test_glob_txt(self, populated_adapter):
        results = populated_adapter.search("*.txt")
        names = {i.name for i in results}
        assert "file1.txt" in names
        assert "file2.py" not in names

    def test_recursive_glob(self, populated_adapter):
        results = populated_adapter.search("**/*.txt")
        names = {i.name for i in results}
        assert "file1.txt" in names
        assert "nested.txt" in names

    def test_no_matches(self, populated_adapter):
        results = populated_adapter.search("*.xyz")
        assert results == []

    def test_search_in_subdir(self, populated_adapter):
        results = populated_adapter.search("*.txt", path="subdir")
        names = {i.name for i in results}
        assert "nested.txt" in names
        assert "file1.txt" not in names


# ---------------------------------------------------------------------------
# tree
# ---------------------------------------------------------------------------


class TestTree:
    def test_empty_tree(self, adapter):
        tree = adapter.tree()
        assert tree.item.item_type == ItemType.DIRECTORY
        assert tree.children == ()

    def test_populated_tree(self, populated_adapter):
        tree = populated_adapter.tree()
        child_names = {c.item.name for c in tree.children}
        assert "file1.txt" in child_names
        assert "subdir" in child_names

    def test_max_depth_zero(self, populated_adapter):
        tree = populated_adapter.tree(max_depth=0)
        assert tree.children == ()

    def test_max_depth_one(self, populated_adapter):
        tree = populated_adapter.tree(max_depth=1)
        subdir_nodes = [c for c in tree.children if c.item.name == "subdir"]
        assert len(subdir_nodes) == 1
        # subdir children not expanded at depth 1
        assert subdir_nodes[0].children == ()

    def test_max_depth_two(self, populated_adapter):
        tree = populated_adapter.tree(max_depth=2)
        subdir_nodes = [c for c in tree.children if c.item.name == "subdir"]
        assert len(subdir_nodes) == 1
        nested_names = {c.item.name for c in subdir_nodes[0].children}
        assert "nested.txt" in nested_names
        assert "deep" in nested_names
        # deep's children not expanded at depth 2
        deep_nodes = [c for c in subdir_nodes[0].children if c.item.name == "deep"]
        assert deep_nodes[0].children == ()

    def test_nonexistent_raises(self, adapter):
        with pytest.raises(StorageNotFoundError):
            adapter.tree("nope")


# ---------------------------------------------------------------------------
# put
# ---------------------------------------------------------------------------


class TestPut:
    def test_new_file(self, adapter, storage_root):
        result = adapter.put("new.txt", b"content")
        assert result.success is True
        assert result.operation == "put"
        assert result.bytes_written == 7
        assert (storage_root / "new.txt").read_bytes() == b"content"

    def test_overwrite(self, populated_adapter, storage_root):
        result = populated_adapter.put("file1.txt", b"overwritten")
        assert result.success is True
        assert (storage_root / "file1.txt").read_bytes() == b"overwritten"

    def test_creates_parent_dirs(self, adapter, storage_root):
        result = adapter.put("a/b/c.txt", b"deep")
        assert result.success is True
        assert (storage_root / "a" / "b" / "c.txt").read_bytes() == b"deep"

    def test_empty_content(self, adapter, storage_root):
        result = adapter.put("empty.txt", b"")
        assert result.bytes_written == 0
        assert (storage_root / "empty.txt").exists()


# ---------------------------------------------------------------------------
# mkdir
# ---------------------------------------------------------------------------


class TestMkdir:
    def test_new_dir(self, adapter, storage_root):
        result = adapter.mkdir("newdir")
        assert result.success is True
        assert result.operation == "mkdir"
        assert (storage_root / "newdir").is_dir()

    def test_nested_parents(self, adapter, storage_root):
        result = adapter.mkdir("a/b/c")
        assert result.success is True
        assert (storage_root / "a" / "b" / "c").is_dir()

    def test_idempotent(self, populated_adapter):
        result = populated_adapter.mkdir("subdir")
        assert result.success is True


# ---------------------------------------------------------------------------
# move
# ---------------------------------------------------------------------------


class TestMove:
    def test_rename_file(self, populated_adapter, storage_root):
        result = populated_adapter.move("file1.txt", "renamed.txt")
        assert result.success is True
        assert result.operation == "move"
        assert not (storage_root / "file1.txt").exists()
        assert (storage_root / "renamed.txt").exists()

    def test_move_to_subdir(self, populated_adapter, storage_root):
        result = populated_adapter.move("file1.txt", "subdir/moved.txt")
        assert result.success is True
        assert (storage_root / "subdir" / "moved.txt").exists()

    def test_move_creates_parent(self, populated_adapter, storage_root):
        result = populated_adapter.move("file1.txt", "new_dir/file1.txt")
        assert result.success is True
        assert (storage_root / "new_dir" / "file1.txt").exists()

    def test_missing_source_raises(self, adapter):
        with pytest.raises(StorageNotFoundError):
            adapter.move("nope.txt", "dest.txt")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_file(self, populated_adapter, storage_root):
        result = populated_adapter.delete("file1.txt")
        assert result.success is True
        assert result.operation == "delete"
        assert not (storage_root / "file1.txt").exists()

    def test_delete_dir(self, populated_adapter, storage_root):
        result = populated_adapter.delete("subdir")
        assert result.success is True
        assert not (storage_root / "subdir").exists()

    def test_delete_nested(self, populated_adapter, storage_root):
        result = populated_adapter.delete("subdir/nested.txt")
        assert result.success is True
        assert not (storage_root / "subdir" / "nested.txt").exists()
        assert (storage_root / "subdir").exists()  # parent still there

    def test_missing_raises(self, adapter):
        with pytest.raises(StorageNotFoundError):
            adapter.delete("nope.txt")


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_healthy_root(self, populated_adapter):
        h = populated_adapter.health()
        assert h.status == "UP"
        assert h.backend == "local"
        assert h.readable is True
        assert h.writable is True
        assert h.total_items > 0
        assert h.total_size_bytes > 0

    def test_empty_root(self, adapter):
        h = adapter.health()
        assert h.status == "UP"
        assert h.total_items == 0
        assert h.total_size_bytes == 0
