"""Tests voor SharePointAdapter — mocked Microsoft Graph API tests.

Geen Microsoft API nodig — alle interacties zijn gemocked.
Volgt het GoogleDriveAdapter test-patroon.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from devhub_storage.adapters.sharepoint_adapter import SharePointAdapter
from devhub_storage.auth import StorageAuth
from devhub_storage.contracts import ItemType, StorageNotFoundError, StorageError


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


class MockAuth(StorageAuth):
    """Mock auth die altijd slaagt."""

    def authenticate(self) -> Any:
        return {"access_token": "mock-token-123"}

    def is_valid(self) -> bool:
        return True


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text or json.dumps(self._data)

    def json(self) -> dict:
        return self._data


class MockHttpClient:
    """Mock HTTP client die Graph API responses simuleert."""

    def __init__(self) -> None:
        self._responses: dict[tuple[str, str], MockResponse] = {}
        self._request_log: list[tuple[str, str]] = []

    def register(self, method: str, url_contains: str, response: MockResponse) -> None:
        """Registreer een mock response voor een URL-patroon."""
        self._responses[(method.upper(), url_contains)] = response

    def request(self, method: str, url: str, **kwargs: Any) -> MockResponse:
        """Voer een mock request uit. Langste patroon-match wint."""
        self._request_log.append((method.upper(), url))
        best_match: tuple[int, MockResponse] | None = None
        for (m, pattern), resp in self._responses.items():
            if m == method.upper() and pattern in url:
                if best_match is None or len(pattern) > best_match[0]:
                    best_match = (len(pattern), resp)
        if best_match:
            return best_match[1]
        return MockResponse(404, text="Not found")

    def put(self, url: str, **kwargs: Any) -> MockResponse:
        return self.request("PUT", url, **kwargs)


def _make_drive_item(
    name: str = "test.txt",
    item_id: str = "item-1",
    is_folder: bool = False,
    size: int = 100,
    child_count: int = 0,
) -> dict:
    """Maak een Graph API driveItem response."""
    item: dict[str, Any] = {
        "id": item_id,
        "name": name,
        "size": size,
        "lastModifiedDateTime": "2026-03-27T10:00:00Z",
        "createdDateTime": "2026-03-27T09:00:00Z",
    }
    if is_folder:
        item["folder"] = {"childCount": child_count}
    else:
        item["file"] = {
            "mimeType": "application/octet-stream",
            "hashes": {"sha256Hash": "abc123"},
        }
    return item


def _make_adapter(client: MockHttpClient | None = None) -> SharePointAdapter:
    """Maak een SharePointAdapter met mock client."""
    return SharePointAdapter(
        auth=MockAuth(),
        site_id="contoso.sharepoint.com,site-id,web-id",
        drive_id="drive-123",
        _client=client or MockHttpClient(),
    )


# ---------------------------------------------------------------------------
# Tests: constructie
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_site_id_of_drive_id_vereist(self) -> None:
        with pytest.raises(ValueError, match="site_id or drive_id"):
            SharePointAdapter(auth=MockAuth(), site_id="", drive_id="")

    def test_met_drive_id_alleen(self) -> None:
        adapter = SharePointAdapter(
            auth=MockAuth(),
            drive_id="drive-123",
            _client=MockHttpClient(),
        )
        assert adapter._drive_id == "drive-123"

    def test_met_site_id_alleen(self) -> None:
        adapter = SharePointAdapter(
            auth=MockAuth(),
            site_id="contoso.sharepoint.com,id,id",
            _client=MockHttpClient(),
        )
        assert adapter._site_id == "contoso.sharepoint.com,id,id"


# ---------------------------------------------------------------------------
# Tests: path normalisatie
# ---------------------------------------------------------------------------


class TestPathNormalization:
    def test_strip_leading_trailing_slashes(self) -> None:
        adapter = _make_adapter()
        assert adapter._normalize_path("/docs/test/") == "docs/test"

    def test_empty_path_stays_empty(self) -> None:
        adapter = _make_adapter()
        assert adapter._normalize_path("") == ""

    def test_root_slash_becomes_empty(self) -> None:
        adapter = _make_adapter()
        assert adapter._normalize_path("/") == ""


# ---------------------------------------------------------------------------
# Tests: URL constructie
# ---------------------------------------------------------------------------


class TestUrlConstruction:
    def test_drive_url_met_drive_id(self) -> None:
        adapter = _make_adapter()
        assert "drives/drive-123" in adapter._drive_url()

    def test_item_url_root(self) -> None:
        adapter = _make_adapter()
        url = adapter._item_url("")
        assert url.endswith("/root")

    def test_item_url_nested(self) -> None:
        adapter = _make_adapter()
        url = adapter._item_url("docs/rapport.md")
        assert "root:/docs/rapport.md:" in url

    def test_children_url_root(self) -> None:
        adapter = _make_adapter()
        url = adapter._children_url("")
        assert url.endswith("/root/children")

    def test_children_url_nested(self) -> None:
        adapter = _make_adapter()
        url = adapter._children_url("docs")
        assert "root:/docs:/children" in url


# ---------------------------------------------------------------------------
# Tests: list()
# ---------------------------------------------------------------------------


class TestList:
    def test_list_root_retourneert_items(self) -> None:
        client = MockHttpClient()
        client.register(
            "GET",
            "/root/children",
            MockResponse(
                200,
                {
                    "value": [
                        _make_drive_item("file1.txt", "f1"),
                        _make_drive_item("docs", "d1", is_folder=True),
                    ]
                },
            ),
        )
        adapter = _make_adapter(client)
        items = adapter.list()
        assert len(items) == 2
        assert items[0].name == "file1.txt"
        assert items[0].item_type == ItemType.FILE
        assert items[1].name == "docs"
        assert items[1].item_type == ItemType.DIRECTORY

    def test_list_leeg_resultaat(self) -> None:
        client = MockHttpClient()
        client.register("GET", "/root/children", MockResponse(200, {"value": []}))
        adapter = _make_adapter(client)
        items = adapter.list()
        assert items == []


# ---------------------------------------------------------------------------
# Tests: get()
# ---------------------------------------------------------------------------


class TestGet:
    def test_get_bestand(self) -> None:
        client = MockHttpClient()
        client.register(
            "GET",
            "root:/test.txt:",
            MockResponse(200, _make_drive_item("test.txt")),
        )
        adapter = _make_adapter(client)
        item = adapter.get("test.txt")
        assert item.name == "test.txt"
        assert item.item_type == ItemType.FILE
        assert item.size_bytes == 100

    def test_get_folder(self) -> None:
        client = MockHttpClient()
        client.register(
            "GET",
            "root:/docs:",
            MockResponse(200, _make_drive_item("docs", is_folder=True)),
        )
        adapter = _make_adapter(client)
        item = adapter.get("docs")
        assert item.item_type == ItemType.DIRECTORY

    def test_get_niet_gevonden_raises(self) -> None:
        adapter = _make_adapter()  # Default returns 404
        with pytest.raises(StorageNotFoundError):
            adapter.get("nonexistent.txt")


# ---------------------------------------------------------------------------
# Tests: search()
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_retourneert_matches(self) -> None:
        client = MockHttpClient()
        client.register(
            "GET",
            "search",
            MockResponse(
                200,
                {
                    "value": [
                        {
                            **_make_drive_item("rapport.md"),
                            "parentReference": {"path": "/root:/docs"},
                        }
                    ]
                },
            ),
        )
        adapter = _make_adapter(client)
        items = adapter.search("rapport")
        assert len(items) == 1
        assert items[0].name == "rapport.md"


# ---------------------------------------------------------------------------
# Tests: put()
# ---------------------------------------------------------------------------


class TestPut:
    def test_put_upload_succeeds(self) -> None:
        client = MockHttpClient()
        client.register(
            "PUT",
            "content",
            MockResponse(200, _make_drive_item("newfile.txt")),
        )
        adapter = _make_adapter(client)
        result = adapter.put("newfile.txt", b"hello world")
        assert result.success is True
        assert result.operation == "put"
        assert result.bytes_written == 11

    def test_put_upload_failure_raises(self) -> None:
        client = MockHttpClient()
        client.register("PUT", "content", MockResponse(500, text="Server error"))
        adapter = _make_adapter(client)
        with pytest.raises(StorageError):
            adapter.put("fail.txt", b"data")


# ---------------------------------------------------------------------------
# Tests: mkdir()
# ---------------------------------------------------------------------------


class TestMkdir:
    def test_mkdir_creates_folder(self) -> None:
        client = MockHttpClient()
        # get() returns 404 (folder doesn't exist)
        # POST to children creates it
        client.register(
            "POST",
            "/children",
            MockResponse(201, _make_drive_item("newdir", is_folder=True)),
        )
        adapter = _make_adapter(client)
        result = adapter.mkdir("newdir")
        assert result.success is True
        assert result.operation == "mkdir"

    def test_mkdir_bestaande_folder_geen_error(self) -> None:
        client = MockHttpClient()
        # get() returns 200 (folder exists)
        client.register(
            "GET",
            "root:/existing:",
            MockResponse(200, _make_drive_item("existing", is_folder=True)),
        )
        adapter = _make_adapter(client)
        result = adapter.mkdir("existing")
        assert result.success is True


# ---------------------------------------------------------------------------
# Tests: delete()
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_succeeds(self) -> None:
        client = MockHttpClient()
        client.register("DELETE", "root:/old.txt:", MockResponse(204))
        adapter = _make_adapter(client)
        result = adapter.delete("old.txt")
        assert result.success is True
        assert result.operation == "delete"


# ---------------------------------------------------------------------------
# Tests: move()
# ---------------------------------------------------------------------------


class TestMove:
    def test_move_succeeds(self) -> None:
        client = MockHttpClient()
        client.register(
            "PATCH",
            "root:/old.txt:",
            MockResponse(200, _make_drive_item("new.txt")),
        )
        adapter = _make_adapter(client)
        result = adapter.move("old.txt", "new.txt")
        assert result.success is True
        assert result.path == "new.txt"
        assert result.operation == "move"


# ---------------------------------------------------------------------------
# Tests: health()
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health_up(self) -> None:
        client = MockHttpClient()
        client.register(
            "GET",
            "/root",
            MockResponse(
                200,
                {
                    "name": "Documents",
                    "size": 50000,
                    "folder": {"childCount": 10},
                },
            ),
        )
        adapter = _make_adapter(client)
        health = adapter.health()
        assert health.status == "UP"
        assert health.backend == "sharepoint"
        assert health.total_items == 10
        assert health.readable is True

    def test_health_down_bij_error(self) -> None:
        client = MockHttpClient()
        # Default 404 response
        adapter = _make_adapter(client)
        health = adapter.health()
        assert health.status == "DOWN"
        assert health.readable is False


# ---------------------------------------------------------------------------
# Tests: tree()
# ---------------------------------------------------------------------------


class TestTree:
    def test_tree_root(self) -> None:
        client = MockHttpClient()
        client.register(
            "GET",
            "/root",
            MockResponse(
                200,
                {
                    "name": "root",
                    "size": 0,
                    "lastModifiedDateTime": "2026-03-27T10:00:00Z",
                    "folder": {"childCount": 1},
                },
            ),
        )
        client.register(
            "GET",
            "/root/children",
            MockResponse(200, {"value": [_make_drive_item("file.txt")]}),
        )
        adapter = _make_adapter(client)
        tree = adapter.tree(max_depth=1)
        assert tree.item.name == "root"
        assert len(tree.children) == 1
        assert tree.children[0].item.name == "file.txt"


# ---------------------------------------------------------------------------
# Tests: graph_item conversie
# ---------------------------------------------------------------------------


class TestGraphItemConversion:
    def test_file_item_conversie(self) -> None:
        adapter = _make_adapter()
        data = _make_drive_item("rapport.md", size=1024)
        item = adapter._graph_item_to_storage_item(data, "docs/rapport.md")
        assert item.path == "docs/rapport.md"
        assert item.name == "rapport.md"
        assert item.item_type == ItemType.FILE
        assert item.size_bytes == 1024
        assert item.content_hash == "abc123"

    def test_folder_item_conversie(self) -> None:
        adapter = _make_adapter()
        data = _make_drive_item("docs", is_folder=True, child_count=5)
        item = adapter._graph_item_to_storage_item(data, "docs")
        assert item.item_type == ItemType.DIRECTORY
        assert item.content_hash is None

    def test_metadata_bevat_id_en_weburl(self) -> None:
        adapter = _make_adapter()
        data = {**_make_drive_item("file.txt"), "webUrl": "https://sp.com/file.txt"}
        item = adapter._graph_item_to_storage_item(data, "file.txt")
        assert "id" in item.metadata
        assert "webUrl" in item.metadata


# ---------------------------------------------------------------------------
# Tests: SharePointAuth
# ---------------------------------------------------------------------------


class TestSharePointAuth:
    def test_missing_tenant_id_raises(self) -> None:
        from devhub_storage.auth import SharePointAuth

        with pytest.raises(ValueError, match="tenant_id"):
            SharePointAuth(tenant_id="", client_id="c", client_secret="s")

    def test_missing_client_id_raises(self) -> None:
        from devhub_storage.auth import SharePointAuth

        with pytest.raises(ValueError, match="client_id"):
            SharePointAuth(tenant_id="t", client_id="", client_secret="s")

    def test_missing_client_secret_raises(self) -> None:
        from devhub_storage.auth import SharePointAuth

        with pytest.raises(ValueError, match="client_secret"):
            SharePointAuth(tenant_id="t", client_id="c", client_secret="")

    def test_is_valid_met_credentials(self) -> None:
        from devhub_storage.auth import SharePointAuth

        auth = SharePointAuth(tenant_id="t", client_id="c", client_secret="s")
        assert auth.is_valid() is True

    def test_default_scopes(self) -> None:
        from devhub_storage.auth import SharePointAuth

        auth = SharePointAuth(tenant_id="t", client_id="c", client_secret="s")
        assert "graph.microsoft.com" in auth.scopes[0]
