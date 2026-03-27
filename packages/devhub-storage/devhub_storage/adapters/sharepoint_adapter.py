"""
SharePoint Adapter — Cloud storage via Microsoft Graph API.

Implementeert StorageInterface voor SharePoint Online document libraries.
Gebruikt lazy imports voor httpx (optional dependency).

Credentials worden NOOIT in code opgeslagen (DEV_CONSTITUTION Art. 8).
Volgt het GoogleDriveAdapter-patroon: path normalisatie, folder-cache, lazy imports.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import quote

from devhub_storage.auth import StorageAuth
from devhub_storage.contracts import (
    ItemType,
    StorageError,
    StorageHealth,
    StorageItem,
    StorageNotFoundError,
    StorageTree,
    WriteResult,
)
from devhub_storage.interface import StorageInterface

logger = logging.getLogger(__name__)


def _get_httpx() -> Any:
    """Lazy import httpx met duidelijke error."""
    try:
        import httpx

        return httpx
    except ImportError:
        raise ImportError(
            "httpx is required for SharePointAdapter. "
            "Install with: uv pip install 'devhub-storage[sharepoint]'"
        ) from None


class SharePointAdapter(StorageInterface):
    """SharePoint Online storage-adapter via Microsoft Graph API.

    Path-model: forward-slash gescheiden relatief aan de document library root.
    Gebruikt de /drives/{drive_id}/root:/{path}: endpoint pattern.

    Args:
        auth: SharePointAuth of compatible StorageAuth.
        site_id: SharePoint site ID (format: {host},{site-id},{web-id}).
        drive_id: Document library drive ID. Als None, wordt de default drive gebruikt.
        _client: Injecteerbare HTTP client voor testing.
    """

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"

    def __init__(
        self,
        auth: StorageAuth,
        site_id: str = "",
        drive_id: str = "",
        *,
        _client: Any | None = None,
    ) -> None:
        if not site_id and not drive_id:
            raise ValueError("site_id or drive_id is required")

        self._auth = auth
        self._site_id = site_id
        self._drive_id = drive_id
        self._client = _client

    def _get_headers(self) -> dict[str, str]:
        """Haal authorization headers op."""
        token_result = self._auth.authenticate()
        if isinstance(token_result, dict):
            access_token = token_result.get("access_token", "")
        else:
            access_token = str(token_result)
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _get_client(self) -> Any:
        """Lazy-initialiseer HTTP client."""
        if self._client is not None:
            return self._client
        httpx = _get_httpx()
        self._client = httpx.Client(timeout=30.0)
        return self._client

    def _drive_url(self) -> str:
        """Bouw de base drive-URL."""
        if self._drive_id:
            return f"{self.GRAPH_BASE}/drives/{self._drive_id}"
        return f"{self.GRAPH_BASE}/sites/{self._site_id}/drive"

    def _item_url(self, path: str) -> str:
        """Bouw een item-URL op basis van pad."""
        path = self._normalize_path(path)
        if not path:
            return f"{self._drive_url()}/root"
        encoded = quote(path, safe="/")
        return f"{self._drive_url()}/root:/{encoded}:"

    def _children_url(self, path: str) -> str:
        """Bouw een children-URL op basis van pad."""
        path = self._normalize_path(path)
        if not path:
            return f"{self._drive_url()}/root/children"
        encoded = quote(path, safe="/")
        return f"{self._drive_url()}/root:/{encoded}:/children"

    def _normalize_path(self, path: str) -> str:
        """Normaliseer pad: strip leading/trailing slashes."""
        return path.strip("/")

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Voer een HTTP request uit met error handling."""
        client = self._get_client()
        headers = self._get_headers()
        response = client.request(method, url, headers=headers, **kwargs)

        if response.status_code == 404:
            raise StorageNotFoundError(f"Item not found: {url}")
        if response.status_code >= 400:
            raise StorageError(
                f"SharePoint API error {response.status_code}: {response.text[:200]}"
            )

        if response.status_code == 204:
            return {}
        return response.json()

    def _graph_item_to_storage_item(self, data: dict[str, Any], path: str) -> StorageItem:
        """Converteer Microsoft Graph driveItem naar StorageItem."""
        is_folder = "folder" in data
        name = data.get("name", "")

        return StorageItem(
            path=path or name,
            name=name,
            item_type=ItemType.DIRECTORY if is_folder else ItemType.FILE,
            size_bytes=data.get("size", 0),
            modified_at=data.get("lastModifiedDateTime", ""),
            created_at=data.get("createdDateTime"),
            content_hash=data.get("file", {}).get("hashes", {}).get("sha256Hash"),
            metadata={
                k: str(v)
                for k, v in {
                    "id": data.get("id"),
                    "webUrl": data.get("webUrl"),
                    "mimeType": data.get("file", {}).get("mimeType"),
                }.items()
                if v
            },
        )

    # --- StorageInterface implementatie ---

    def list(self, path: str = "", *, recursive: bool = False) -> list[StorageItem]:
        """Lijst items in een SharePoint folder."""
        url = self._children_url(path)
        items: list[StorageItem] = []
        base_path = self._normalize_path(path)

        while url:
            data = self._request("GET", url)
            for item_data in data.get("value", []):
                name = item_data.get("name", "")
                item_path = f"{base_path}/{name}".strip("/")
                items.append(self._graph_item_to_storage_item(item_data, item_path))

                if recursive and "folder" in item_data:
                    items.extend(self.list(item_path, recursive=True))

            url = data.get("@odata.nextLink")

        return items

    def get(self, path: str) -> StorageItem:
        """Haal metadata op voor één item."""
        url = self._item_url(path)
        data = self._request("GET", url)
        return self._graph_item_to_storage_item(data, self._normalize_path(path))

    def search(self, pattern: str, *, path: str = "") -> list[StorageItem]:
        """Zoek items op naam (SharePoint search)."""
        search_term = pattern.replace("*", "").replace("?", "")
        if not search_term:
            return self.list(path, recursive=True)

        url = f"{self._drive_url()}/root/search(q='{quote(search_term)}')"
        data = self._request("GET", url)

        items: list[StorageItem] = []
        for item_data in data.get("value", []):
            parent_ref = item_data.get("parentReference", {})
            parent_path = parent_ref.get("path", "").split("root:")[-1].strip("/")
            name = item_data.get("name", "")
            item_path = f"{parent_path}/{name}".strip("/")
            items.append(self._graph_item_to_storage_item(item_data, item_path))

        return items

    def tree(self, path: str = "", *, max_depth: int = -1) -> StorageTree:
        """Bouw een recursieve boomstructuur."""
        path = self._normalize_path(path)

        if path:
            root_data = self._request("GET", self._item_url(path))
            root_item = self._graph_item_to_storage_item(root_data, path)
        else:
            root_data = self._request("GET", f"{self._drive_url()}/root")
            root_item = StorageItem(
                path="/",
                name="root",
                item_type=ItemType.DIRECTORY,
                size_bytes=root_data.get("size", 0),
                modified_at=root_data.get("lastModifiedDateTime", ""),
            )

        children = self._build_tree_children(path, max_depth, current_depth=0)
        return StorageTree(item=root_item, children=tuple(children))

    def _build_tree_children(
        self,
        base_path: str,
        max_depth: int,
        current_depth: int,
    ) -> list[StorageTree]:
        """Intern: bouw tree-kinderen recursief."""
        if max_depth >= 0 and current_depth >= max_depth:
            return []

        url = self._children_url(base_path)
        data = self._request("GET", url)

        children: list[StorageTree] = []
        for item_data in data.get("value", []):
            name = item_data.get("name", "")
            item_path = f"{base_path}/{name}".strip("/")
            item = self._graph_item_to_storage_item(item_data, item_path)

            if "folder" in item_data:
                sub_children = self._build_tree_children(item_path, max_depth, current_depth + 1)
                children.append(StorageTree(item=item, children=tuple(sub_children)))
            else:
                children.append(StorageTree(item=item))

        return children

    def put(self, path: str, content: bytes) -> WriteResult:
        """Upload of overschrijf een bestand via Graph API."""
        path = self._normalize_path(path)
        encoded = quote(path, safe="/")
        url = f"{self._drive_url()}/root:/{encoded}:/content"

        client = self._get_client()
        headers = self._get_headers()
        headers["Content-Type"] = "application/octet-stream"
        response = client.put(url, headers=headers, content=content)

        if response.status_code >= 400:
            raise StorageError(
                f"SharePoint upload failed {response.status_code}: {response.text[:200]}"
            )

        return WriteResult(
            success=True,
            path=path,
            operation="put",
            bytes_written=len(content),
        )

    def mkdir(self, path: str) -> WriteResult:
        """Maak een folder aan (inclusief tussenliggende folders)."""
        path = self._normalize_path(path)
        parts = path.split("/")
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}".strip("/")

            # Check of folder al bestaat
            try:
                self.get(current_path)
                continue  # Bestaat al
            except StorageNotFoundError:
                pass  # Maak aan

            # Creëer de folder
            parent_path = current_path.rsplit("/", 1)[0] if "/" in current_path else ""
            parent_url = self._children_url(parent_path)

            body = json.dumps(
                {
                    "name": part,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "fail",
                }
            )
            self._request("POST", parent_url, content=body)

        return WriteResult(success=True, path=path, operation="mkdir")

    def move(self, source: str, destination: str) -> WriteResult:
        """Verplaats of hernoem een item via PATCH."""
        source = self._normalize_path(source)
        destination = self._normalize_path(destination)

        source_url = self._item_url(source)

        # Bepaal nieuwe parent en naam
        if "/" in destination:
            dest_parent, dest_name = destination.rsplit("/", 1)
            dest_parent_encoded = quote(dest_parent, safe="/")
            parent_ref = {"path": f"/root:/{dest_parent_encoded}"}
        else:
            dest_name = destination
            parent_ref = {"path": "/root"}

        body = json.dumps(
            {
                "parentReference": parent_ref,
                "name": dest_name,
            }
        )
        self._request("PATCH", source_url, content=body)

        return WriteResult(success=True, path=destination, operation="move")

    def delete(self, path: str) -> WriteResult:
        """Verwijder een item."""
        url = self._item_url(path)
        self._request("DELETE", url)
        return WriteResult(success=True, path=self._normalize_path(path), operation="delete")

    def health(self) -> StorageHealth:
        """Controleer connectiviteit met SharePoint."""
        try:
            data = self._request("GET", f"{self._drive_url()}/root")
            return StorageHealth(
                status="UP",
                backend="sharepoint",
                root_path=self._site_id or self._drive_id,
                total_items=data.get("folder", {}).get("childCount", 0),
                total_size_bytes=data.get("size", 0),
                readable=True,
                writable=True,
                message=f"Drive: {data.get('name', 'unknown')}",
            )
        except Exception as e:
            return StorageHealth(
                status="DOWN",
                backend="sharepoint",
                root_path=self._site_id or self._drive_id,
                total_items=0,
                total_size_bytes=0,
                readable=False,
                writable=False,
                message=str(e),
            )
