"""
DriveSyncAdapter — Google Drive via filesystem sync.

Dunne wrapper rond LocalAdapter die schrijft naar de Google Drive for Desktop
sync-map. Geen API, geen OAuth, geen Cloud Console — alleen een lokale map
die Google automatisch synct.

Autodetectie: zoekt ~/Library/CloudStorage/GoogleDrive-*/My Drive/ op macOS.
"""

from __future__ import annotations

import platform
from pathlib import Path

from devhub_storage.adapters.local_adapter import LocalAdapter
from devhub_storage.contracts import (
    StorageError,
    StorageHealth,
    StorageItem,
    StorageTree,
    WriteResult,
)
from devhub_storage.interface import StorageInterface


def detect_drive_sync_root() -> Path | None:
    """Auto-detect Google Drive for Desktop sync folder.

    Returns the first matching path, or None if not found.
    """
    system = platform.system()
    home = Path.home()

    if system == "Darwin":
        cloud_storage = home / "Library" / "CloudStorage"
        if cloud_storage.is_dir():
            for entry in cloud_storage.iterdir():
                if entry.name.startswith("GoogleDrive-") and entry.is_dir():
                    my_drive = entry / "My Drive"
                    if my_drive.is_dir():
                        return my_drive
    elif system == "Windows":
        # Common Windows paths for Google Drive
        for letter in "GHIJKLMNOPQRSTUVWXYZ":
            candidate = Path(f"{letter}:\\My Drive")
            if candidate.is_dir():
                return candidate
    # Linux: Google Drive for Desktop not supported
    return None


class DriveSyncAdapter(StorageInterface):
    """Storage adapter that writes to Google Drive's local sync folder.

    Delegeert alle operaties naar LocalAdapter met de sync-map als root.
    Google Drive for Desktop synct wijzigingen automatisch naar de cloud.
    """

    BACKEND = "drive_sync"

    def __init__(
        self,
        drive_root: str | Path = "",
        node_drive_root: str = "DevHub",
    ) -> None:
        """Initialize DriveSyncAdapter.

        Args:
            drive_root: Explicit path to Drive sync folder.
                        Empty string triggers auto-detection.
            node_drive_root: Subfolder within Drive (e.g. "DevHub", "BORIS").
                            From documents.yml drive_root config.
        """
        if drive_root:
            self._sync_root = Path(drive_root)
        else:
            detected = detect_drive_sync_root()
            if detected is None:
                raise StorageError(
                    "Google Drive sync folder not found. "
                    "Install Google Drive for Desktop and log in, "
                    "or provide an explicit drive_root path."
                )
            self._sync_root = detected

        # Target directory: {sync_root}/{node_drive_root}
        self._target = self._sync_root / node_drive_root
        self._target.mkdir(parents=True, exist_ok=True)

        self._delegate = LocalAdapter(root_path=self._target)
        self._node_drive_root = node_drive_root

    @property
    def sync_root(self) -> Path:
        """The Google Drive sync folder (e.g. ~/Library/CloudStorage/GoogleDrive-.../My Drive/)."""
        return self._sync_root

    @property
    def target_root(self) -> Path:
        """The node-specific folder within Drive (e.g. .../My Drive/DevHub/)."""
        return self._target

    # ------------------------------------------------------------------
    # StorageInterface — delegated to LocalAdapter
    # ------------------------------------------------------------------

    def list(self, path: str = "", *, recursive: bool = False) -> list[StorageItem]:
        return self._delegate.list(path, recursive=recursive)

    def get(self, path: str) -> StorageItem:
        return self._delegate.get(path)

    def search(self, pattern: str, *, path: str = "") -> list[StorageItem]:
        return self._delegate.search(pattern, path=path)

    def tree(self, path: str = "", *, max_depth: int = -1) -> StorageTree:
        return self._delegate.tree(path, max_depth=max_depth)

    def put(self, path: str, content: bytes) -> WriteResult:
        return self._delegate.put(path, content)

    def mkdir(self, path: str) -> WriteResult:
        return self._delegate.mkdir(path)

    def move(self, source: str, destination: str) -> WriteResult:
        return self._delegate.move(source, destination)

    def delete(self, path: str) -> WriteResult:
        return self._delegate.delete(path)

    def health(self) -> StorageHealth:
        """Health check with Drive-specific context."""
        base_health = self._delegate.health()

        # Add Drive-specific info to message
        drive_available = self._sync_root.is_dir()
        if not drive_available:
            return StorageHealth(
                status="DOWN",
                backend=self.BACKEND,
                root_path=str(self._target),
                total_items=0,
                total_size_bytes=0,
                readable=False,
                writable=False,
                message=(
                    "Google Drive sync folder not available. "
                    "Is Google Drive for Desktop running?"
                ),
            )

        return StorageHealth(
            status=base_health.status,
            backend=self.BACKEND,
            root_path=str(self._target),
            total_items=base_health.total_items,
            total_size_bytes=base_health.total_size_bytes,
            readable=base_health.readable,
            writable=base_health.writable,
            message=base_health.message or f"Syncing to Google Drive via {self._sync_root}",
        )
