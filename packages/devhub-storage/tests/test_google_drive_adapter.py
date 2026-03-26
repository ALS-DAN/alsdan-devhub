"""Tests voor GoogleDriveAdapter — mocked Google Drive API tests.

Geen Google API nodig — alle interacties zijn gemocked.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from devhub_storage.auth import StorageAuth
from devhub_storage.contracts import ItemType, StorageNotFoundError
from devhub_storage.adapters.google_drive_adapter import GoogleDriveAdapter


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


class MockAuth(StorageAuth):
    """Mock auth die altijd slaagt."""

    def authenticate(self) -> Any:
        return MagicMock()

    def is_valid(self) -> bool:
        return True


class MockDriveService:
    """Mock Google Drive API service."""

    def __init__(self):
        self._files: dict[str, dict] = {}
        self._file_list_responses: list[dict] = []
        self._about_response: dict = {
            "storageQuota": {
                "limit": "15000000000",
                "usage": "5000000000",
            }
        }
        self._files_mock = MockFilesResource(self)
        self._about_mock = MockAboutResource(self)

    def files(self):
        return self._files_mock

    def about(self):
        return self._about_mock

    def add_file(
        self,
        file_id: str,
        name: str,
        parent_id: str = "root",
        mime_type: str = "application/octet-stream",
        size: int = 100,
    ):
        """Voeg een mock-bestand toe."""
        self._files[file_id] = {
            "id": file_id,
            "name": name,
            "mimeType": mime_type,
            "size": str(size),
            "modifiedTime": "2026-03-26T10:00:00Z",
            "createdTime": "2026-03-26T09:00:00Z",
            "parents": [parent_id],
        }

    def add_folder(self, folder_id: str, name: str, parent_id: str = "root"):
        """Voeg een mock-folder toe."""
        self.add_file(
            folder_id,
            name,
            parent_id,
            mime_type="application/vnd.google-apps.folder",
            size=0,
        )


class MockFilesResource:
    """Mock voor service.files()."""

    def __init__(self, service: MockDriveService):
        self._service = service

    def list(self, **kwargs) -> MockRequest:
        q = kwargs.get("q", "")
        matching = []

        for f in self._service._files.values():
            match = True

            # Name exact match
            if "name = " in q:
                name_part = q.split("name = '")[1].split("'")[0]
                if f["name"] != name_part:
                    match = False

            # Parent filter — extract ID before "in parents"
            if match and "in parents" in q:
                # Pattern: "'<parent_id>' in parents"
                idx = q.index("in parents")
                before = q[:idx].rstrip()
                # Find the quoted parent ID
                if "'" in before:
                    parent_part = before.rstrip("' ").rsplit("'", 1)[-1]
                    if parent_part not in f.get("parents", []):
                        match = False

            # Name contains (search)
            if match and "name contains" in q:
                search = q.split("name contains '")[1].split("'")[0]
                if search.lower() not in f["name"].lower():
                    match = False

            # Folder-only filter
            if match and ("mimeType = 'application/vnd.google-apps.folder'" in q):
                if f.get("mimeType") != "application/vnd.google-apps.folder":
                    match = False

            if match:
                matching.append(f)

        page_size = kwargs.get("pageSize", 100)
        return MockRequest({"files": matching[:page_size], "nextPageToken": None})

    def create(self, **kwargs) -> MockRequest:
        body = kwargs.get("body", {})
        new_id = f"new_{body.get('name', 'file')}"
        return MockRequest({"id": new_id})

    def update(self, **kwargs) -> MockRequest:
        return MockRequest({})

    def get_media(self, **kwargs) -> MockRequest:
        return MockRequest(b"file content")


class MockAboutResource:
    """Mock voor service.about()."""

    def __init__(self, service: MockDriveService):
        self._service = service

    def get(self, **kwargs) -> MockRequest:
        return MockRequest(self._service._about_response)


class MockRequest:
    """Mock voor een API request met execute()."""

    def __init__(self, response: Any):
        self._response = response

    def execute(self) -> Any:
        return self._response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_service() -> MockDriveService:
    """Lege mock Drive service."""
    return MockDriveService()


@pytest.fixture
def mock_auth() -> MockAuth:
    return MockAuth()


@pytest.fixture
def adapter(mock_auth: MockAuth, mock_service: MockDriveService) -> GoogleDriveAdapter:
    """GoogleDriveAdapter met mock service."""
    return GoogleDriveAdapter(
        auth=mock_auth,
        root_folder_id="root",
        _service=mock_service,
    )


@pytest.fixture
def populated_service(mock_service: MockDriveService) -> MockDriveService:
    """Mock service met bestanden en folders."""
    mock_service.add_folder("folder1", "documents")
    mock_service.add_file("file1", "rapport.pdf", parent_id="folder1", size=5000)
    mock_service.add_file("file2", "readme.md", parent_id="root", size=200)
    mock_service.add_folder("folder2", "images", parent_id="folder1")
    mock_service.add_file("file3", "logo.png", parent_id="folder2", size=8000)
    return mock_service


@pytest.fixture
def populated_adapter(
    mock_auth: MockAuth, populated_service: MockDriveService
) -> GoogleDriveAdapter:
    return GoogleDriveAdapter(
        auth=mock_auth,
        root_folder_id="root",
        _service=populated_service,
    )


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestInitialization:
    def test_creates_adapter(self, adapter: GoogleDriveAdapter):
        assert adapter._root_folder_id == "root"

    def test_empty_root_folder_raises(self, mock_auth: MockAuth):
        with pytest.raises(ValueError, match="root_folder_id"):
            GoogleDriveAdapter(
                auth=mock_auth,
                root_folder_id="",
                _service=MagicMock(),
            )

    def test_folder_cache_initialized(self, adapter: GoogleDriveAdapter):
        assert "" in adapter._folder_cache
        assert adapter._folder_cache[""] == "root"


# ---------------------------------------------------------------------------
# Path normalization
# ---------------------------------------------------------------------------


class TestPathNormalization:
    def test_strip_slashes(self, adapter: GoogleDriveAdapter):
        assert adapter._normalize_path("/foo/bar/") == "foo/bar"

    def test_empty_path(self, adapter: GoogleDriveAdapter):
        assert adapter._normalize_path("") == ""

    def test_single_name(self, adapter: GoogleDriveAdapter):
        assert adapter._normalize_path("file.txt") == "file.txt"


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


class TestList:
    def test_list_root(self, populated_adapter: GoogleDriveAdapter):
        items = populated_adapter.list()
        names = [i.name for i in items]
        assert "documents" in names
        assert "readme.md" in names

    def test_list_subfolder(self, populated_adapter: GoogleDriveAdapter):
        items = populated_adapter.list("documents")
        names = [i.name for i in items]
        assert "rapport.pdf" in names

    def test_list_empty_folder(self, adapter: GoogleDriveAdapter):
        items = adapter.list()
        assert items == []

    def test_list_item_types(self, populated_adapter: GoogleDriveAdapter):
        items = populated_adapter.list()
        folders = [i for i in items if i.item_type == ItemType.DIRECTORY]
        files = [i for i in items if i.item_type == ItemType.FILE]
        assert len(folders) >= 1
        assert len(files) >= 1


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


class TestGet:
    def test_get_file(self, populated_adapter: GoogleDriveAdapter):
        item = populated_adapter.get("readme.md")
        assert item.name == "readme.md"
        assert item.item_type == ItemType.FILE
        assert item.size_bytes == 200

    def test_get_nested_file(self, populated_adapter: GoogleDriveAdapter):
        item = populated_adapter.get("documents/rapport.pdf")
        assert item.name == "rapport.pdf"

    def test_get_nonexistent_raises(self, adapter: GoogleDriveAdapter):
        with pytest.raises(StorageNotFoundError):
            adapter.get("nonexistent.txt")


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_by_name(self, populated_adapter: GoogleDriveAdapter):
        results = populated_adapter.search("rapport")
        names = [r.name for r in results]
        assert "rapport.pdf" in names

    def test_search_no_results(self, populated_adapter: GoogleDriveAdapter):
        results = populated_adapter.search("nonexistent_xyz")
        assert results == []


# ---------------------------------------------------------------------------
# put
# ---------------------------------------------------------------------------


class TestPut:
    def test_put_new_file(self, adapter: GoogleDriveAdapter):
        result = adapter.put("test.txt", b"Hello World")
        assert result.success is True
        assert result.path == "test.txt"
        assert result.operation == "put"
        assert result.bytes_written == 11

    def test_put_nested_path(
        self,
        populated_adapter: GoogleDriveAdapter,
    ):
        result = populated_adapter.put("documents/new_file.txt", b"Content")
        assert result.success is True


# ---------------------------------------------------------------------------
# mkdir
# ---------------------------------------------------------------------------


class TestMkdir:
    def test_mkdir(self, adapter: GoogleDriveAdapter):
        result = adapter.mkdir("new_folder")
        assert result.success is True
        assert result.operation == "mkdir"

    def test_mkdir_nested(self, adapter: GoogleDriveAdapter):
        result = adapter.mkdir("a/b/c")
        assert result.success is True
        assert result.path == "a/b/c"

    def test_mkdir_existing_cached(
        self,
        populated_adapter: GoogleDriveAdapter,
    ):
        result = populated_adapter.mkdir("documents")
        assert result.success is True


# ---------------------------------------------------------------------------
# move
# ---------------------------------------------------------------------------


class TestMove:
    def test_move_file(self, populated_adapter: GoogleDriveAdapter):
        result = populated_adapter.move("readme.md", "readme_old.md")
        assert result.success is True
        assert result.operation == "move"
        assert result.path == "readme_old.md"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_file(self, populated_adapter: GoogleDriveAdapter):
        result = populated_adapter.delete("readme.md")
        assert result.success is True
        assert result.operation == "delete"

    def test_delete_nonexistent_raises(
        self,
        adapter: GoogleDriveAdapter,
    ):
        with pytest.raises(StorageNotFoundError):
            adapter.delete("nonexistent.txt")


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_healthy(self, adapter: GoogleDriveAdapter):
        h = adapter.health()
        assert h.status == "UP"
        assert h.backend == "google_drive"
        assert h.readable is True
        assert h.writable is True

    def test_health_quota_info(self, adapter: GoogleDriveAdapter):
        h = adapter.health()
        assert "Quota" in h.message

    def test_health_down(
        self,
        mock_auth: MockAuth,
    ):
        """Service die een fout gooit."""
        service = MagicMock()
        service.about.return_value.get.return_value.execute.side_effect = Exception("API error")
        adapter = GoogleDriveAdapter(
            auth=mock_auth,
            root_folder_id="root",
            _service=service,
        )
        h = adapter.health()
        assert h.status == "DOWN"
        assert h.readable is False


# ---------------------------------------------------------------------------
# tree
# ---------------------------------------------------------------------------


class TestTree:
    def test_tree_root(self, populated_adapter: GoogleDriveAdapter):
        tree = populated_adapter.tree()
        assert tree.item.name == "root"
        assert tree.item.path == "/"
        assert tree.item.item_type == ItemType.DIRECTORY
        assert len(tree.children) >= 1

    def test_tree_max_depth(self, populated_adapter: GoogleDriveAdapter):
        tree = populated_adapter.tree(max_depth=0)
        assert tree.children == ()
