"""
Google Drive Adapter — Cloud storage via Google Drive API.

Implementeert StorageInterface voor Google Drive. Gebruikt lazy imports
voor googleapiclient (optional dependency).

Credentials worden NOOIT in code opgeslagen (DEV_CONSTITUTION Art. 8).
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any

from devhub_storage.auth import StorageAuth
from devhub_storage.contracts import (
    ItemType,
    StorageHealth,
    StorageItem,
    StorageNotFoundError,
    StorageTree,
    WriteResult,
)
from devhub_storage.interface import StorageInterface

if TYPE_CHECKING:
    pass


def _get_drive_service() -> type:
    """Lazy import googleapiclient met duidelijke error."""
    try:
        from googleapiclient.discovery import build as _build

        return _build
    except ImportError:
        raise ImportError(
            "google-api-python-client is required for GoogleDriveAdapter. "
            "Install with: uv pip install 'devhub-storage[google]'"
        ) from None


class GoogleDriveAdapter(StorageInterface):
    """Google Drive storage-adapter via Google Drive API v3.

    Path-model: forward-slash gescheiden relatief aan root_folder_id.
    Folder-ID lookups worden gecached voor performance.
    """

    FOLDER_MIME = "application/vnd.google-apps.folder"

    def __init__(
        self,
        auth: StorageAuth,
        root_folder_id: str = "root",
        *,
        _service: Any | None = None,
    ) -> None:
        """Initialiseer GoogleDriveAdapter.

        Args:
            auth: StorageAuth implementatie voor credentials.
            root_folder_id: Google Drive folder ID als root.
            _service: Injecteerbare service voor testing.
        """
        if not root_folder_id:
            raise ValueError("root_folder_id is required")

        self._auth = auth
        self._root_folder_id = root_folder_id

        if _service is not None:
            self._service = _service
        else:
            build = _get_drive_service()
            credentials = auth.authenticate()
            self._service = build("drive", "v3", credentials=credentials)

        # Folder-ID cache: path → Drive folder ID
        self._folder_cache: dict[str, str] = {"": self._root_folder_id}

    def _normalize_path(self, path: str) -> str:
        """Normaliseer pad: strip leading/trailing slashes."""
        return path.strip("/")

    def _resolve_folder_id(self, path: str) -> str:
        """Resoleer een pad naar een Google Drive folder ID.

        Loopt het pad component-voor-component af en cachet elke stap.
        """
        path = self._normalize_path(path)
        if path in self._folder_cache:
            return self._folder_cache[path]

        parts = path.split("/")
        current_id = self._root_folder_id
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}".strip("/")
            if current_path in self._folder_cache:
                current_id = self._folder_cache[current_path]
                continue

            query = (
                f"name = '{part}' and "
                f"'{current_id}' in parents and "
                f"mimeType = '{self.FOLDER_MIME}' and "
                f"trashed = false"
            )
            results = (
                self._service.files().list(q=query, fields="files(id, name)", pageSize=1).execute()
            )
            files = results.get("files", [])
            if not files:
                raise StorageNotFoundError(f"Folder not found: {current_path}")

            current_id = files[0]["id"]
            self._folder_cache[current_path] = current_id

        return current_id

    def _resolve_file(self, path: str) -> dict[str, Any]:
        """Resoleer een pad naar file metadata.

        Splitst het pad in parent-folder + bestandsnaam.
        """
        path = self._normalize_path(path)
        if "/" in path:
            parent_path, filename = path.rsplit("/", 1)
            parent_id = self._resolve_folder_id(parent_path)
        else:
            filename = path
            parent_id = self._root_folder_id

        query = f"name = '{filename}' and " f"'{parent_id}' in parents and " f"trashed = false"
        results = (
            self._service.files()
            .list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, " "createdTime, md5Checksum)",
                pageSize=1,
            )
            .execute()
        )
        files = results.get("files", [])
        if not files:
            raise StorageNotFoundError(f"File not found: {path}")

        return files[0]

    def _file_to_storage_item(self, file_data: dict[str, Any], path: str) -> StorageItem:
        """Converteer Google Drive file metadata naar StorageItem."""
        is_folder = file_data.get("mimeType") == self.FOLDER_MIME
        return StorageItem(
            path=path,
            name=file_data.get("name", ""),
            item_type=ItemType.DIRECTORY if is_folder else ItemType.FILE,
            size_bytes=int(file_data.get("size", 0)),
            modified_at=file_data.get("modifiedTime", ""),
            created_at=file_data.get("createdTime"),
            content_hash=file_data.get("md5Checksum"),
        )

    def list(self, path: str = "", *, recursive: bool = False) -> list[StorageItem]:
        """Lijst items in een Drive folder."""
        path = self._normalize_path(path)
        folder_id = self._resolve_folder_id(path) if path else self._root_folder_id

        items: list[StorageItem] = []
        self._list_folder(folder_id, path, items, recursive=recursive)
        return items

    def _list_folder(
        self,
        folder_id: str,
        base_path: str,
        items: list[StorageItem],
        *,
        recursive: bool = False,
    ) -> None:
        """Intern: lijst items in een folder, optioneel recursief."""
        page_token = None
        while True:
            query = f"'{folder_id}' in parents and trashed = false"
            kwargs: dict[str, Any] = {
                "q": query,
                "fields": (
                    "nextPageToken, files(id, name, mimeType, size, "
                    "modifiedTime, createdTime, md5Checksum)"
                ),
                "pageSize": 100,
            }
            if page_token:
                kwargs["pageToken"] = page_token

            results = self._service.files().list(**kwargs).execute()

            for f in results.get("files", []):
                item_path = f"{base_path}/{f['name']}".strip("/")
                items.append(self._file_to_storage_item(f, item_path))

                if recursive and f.get("mimeType") == self.FOLDER_MIME:
                    self._list_folder(f["id"], item_path, items, recursive=True)

            page_token = results.get("nextPageToken")
            if not page_token:
                break

    def get(self, path: str) -> StorageItem:
        """Haal metadata op voor een bestand of folder."""
        path = self._normalize_path(path)
        file_data = self._resolve_file(path)
        return self._file_to_storage_item(file_data, path)

    def search(self, pattern: str, *, path: str = "") -> list[StorageItem]:
        """Zoek bestanden op naam (contains match)."""
        path = self._normalize_path(path)

        # Converteer glob-achtig patroon naar Drive name-contains
        search_term = pattern.replace("*", "").replace("?", "")
        if not search_term:
            return self.list(path, recursive=True)

        query_parts = [
            f"name contains '{search_term}'",
            "trashed = false",
        ]
        if path:
            folder_id = self._resolve_folder_id(path)
            query_parts.append(f"'{folder_id}' in parents")

        query = " and ".join(query_parts)
        results = (
            self._service.files()
            .list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, " "createdTime, md5Checksum)",
                pageSize=100,
            )
            .execute()
        )

        return [self._file_to_storage_item(f, f.get("name", "")) for f in results.get("files", [])]

    def tree(self, path: str = "", *, max_depth: int = -1) -> StorageTree:
        """Bouw een recursieve boomstructuur."""
        path = self._normalize_path(path)
        folder_id = self._resolve_folder_id(path) if path else self._root_folder_id

        # Root item
        if path:
            file_data = self._resolve_file(path)
            root_item = self._file_to_storage_item(file_data, path)
        else:
            root_item = StorageItem(
                path="/",
                name="root",
                item_type=ItemType.DIRECTORY,
                size_bytes=0,
                modified_at="",
            )

        children = self._build_tree_children(folder_id, path, max_depth, current_depth=0)
        return StorageTree(item=root_item, children=tuple(children))

    def _build_tree_children(
        self,
        folder_id: str,
        base_path: str,
        max_depth: int,
        current_depth: int,
    ) -> list[StorageTree]:
        """Intern: bouw tree-kinderen recursief."""
        if max_depth >= 0 and current_depth >= max_depth:
            return []

        query = f"'{folder_id}' in parents and trashed = false"
        results = (
            self._service.files()
            .list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, " "createdTime, md5Checksum)",
                pageSize=100,
            )
            .execute()
        )

        children: list[StorageTree] = []
        for f in results.get("files", []):
            item_path = f"{base_path}/{f['name']}".strip("/")
            item = self._file_to_storage_item(f, item_path)

            if f.get("mimeType") == self.FOLDER_MIME:
                sub_children = self._build_tree_children(
                    f["id"],
                    item_path,
                    max_depth,
                    current_depth + 1,
                )
                children.append(StorageTree(item=item, children=tuple(sub_children)))
            else:
                children.append(StorageTree(item=item))

        return children

    def put(self, path: str, content: bytes) -> WriteResult:
        """Upload of overschrijf een bestand."""
        path = self._normalize_path(path)

        if "/" in path:
            parent_path, filename = path.rsplit("/", 1)
            parent_id = self._resolve_folder_id(parent_path)
        else:
            filename = path
            parent_id = self._root_folder_id

        try:
            from googleapiclient.http import MediaIoBaseUpload

            media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/octet-stream")
        except ImportError:
            # Fallback voor testing zonder google-api-python-client
            media = None

        # Check of bestand al bestaat
        query = f"name = '{filename}' and " f"'{parent_id}' in parents and " f"trashed = false"
        existing = self._service.files().list(q=query, fields="files(id)", pageSize=1).execute()

        if existing.get("files"):
            # Update
            file_id = existing["files"][0]["id"]
            self._service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Create
            file_metadata = {"name": filename, "parents": [parent_id]}
            self._service.files().create(body=file_metadata, media_body=media).execute()

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
        current_id = self._root_folder_id
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}".strip("/")
            if current_path in self._folder_cache:
                current_id = self._folder_cache[current_path]
                continue

            # Check of folder al bestaat
            query = (
                f"name = '{part}' and "
                f"'{current_id}' in parents and "
                f"mimeType = '{self.FOLDER_MIME}' and "
                f"trashed = false"
            )
            results = self._service.files().list(q=query, fields="files(id)", pageSize=1).execute()

            if results.get("files"):
                current_id = results["files"][0]["id"]
            else:
                file_metadata = {
                    "name": part,
                    "mimeType": self.FOLDER_MIME,
                    "parents": [current_id],
                }
                created = self._service.files().create(body=file_metadata, fields="id").execute()
                current_id = created["id"]

            self._folder_cache[current_path] = current_id

        return WriteResult(success=True, path=path, operation="mkdir")

    def move(self, source: str, destination: str) -> WriteResult:
        """Verplaats of hernoem een item."""
        source = self._normalize_path(source)
        destination = self._normalize_path(destination)

        # Resoleer source
        source_file = self._resolve_file(source)
        source_id = source_file["id"]

        # Bepaal nieuwe parent en naam
        if "/" in destination:
            dest_parent, dest_name = destination.rsplit("/", 1)
            dest_parent_id = self._resolve_folder_id(dest_parent)
        else:
            dest_name = destination
            dest_parent_id = self._root_folder_id

        # Huidige parent
        if "/" in source:
            src_parent = source.rsplit("/", 1)[0]
            src_parent_id = self._resolve_folder_id(src_parent)
        else:
            src_parent_id = self._root_folder_id

        self._service.files().update(
            fileId=source_id,
            body={"name": dest_name},
            addParents=dest_parent_id,
            removeParents=src_parent_id,
        ).execute()

        # Invalideer cache
        self._folder_cache.pop(source, None)

        return WriteResult(success=True, path=destination, operation="move")

    def delete(self, path: str) -> WriteResult:
        """Verplaats een item naar de prullenbak (soft delete)."""
        path = self._normalize_path(path)
        file_data = self._resolve_file(path)
        file_id = file_data["id"]

        # Soft delete (trash) — niet permanent verwijderen
        self._service.files().update(fileId=file_id, body={"trashed": True}).execute()

        # Invalideer cache
        self._folder_cache.pop(path, None)

        return WriteResult(success=True, path=path, operation="delete")

    def health(self) -> StorageHealth:
        """Controleer connectiviteit met Google Drive."""
        try:
            about = self._service.about().get(fields="storageQuota").execute()
            quota = about.get("storageQuota", {})
            total = int(quota.get("limit", 0))
            used = int(quota.get("usage", 0))

            return StorageHealth(
                status="UP",
                backend="google_drive",
                root_path=self._root_folder_id,
                total_items=0,  # Expensive to count
                total_size_bytes=used,
                readable=True,
                writable=True,
                message=f"Quota: {used}/{total} bytes",
            )
        except Exception as e:
            return StorageHealth(
                status="DOWN",
                backend="google_drive",
                root_path=self._root_folder_id,
                total_items=0,
                total_size_bytes=0,
                readable=False,
                writable=False,
                message=str(e),
            )
