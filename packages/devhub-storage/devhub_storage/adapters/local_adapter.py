"""
LocalAdapter — Filesystem-backend voor StorageInterface.

Alle paden worden genormaliseerd en gevalideerd tegen path traversal.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

from devhub_storage.contracts import (
    ItemType,
    StorageError,
    StorageHealth,
    StorageItem,
    StorageNotFoundError,
    StoragePathError,
    StorageTree,
    WriteResult,
)
from devhub_storage.interface import StorageInterface


class LocalAdapter(StorageInterface):
    """Filesystem-based storage adapter."""

    BACKEND = "local"

    def __init__(self, root_path: str | Path) -> None:
        self._root = Path(root_path).resolve()
        if not self._root.is_dir():
            raise StorageError(f"Root path is not a directory: {root_path}")

    @property
    def root(self) -> Path:
        return self._root

    # ------------------------------------------------------------------
    # Path safety
    # ------------------------------------------------------------------

    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve a relative path safely within the root directory.

        Returns the resolved (symlink-followed) path for security validation.
        Use _safe_path() when you also need the unresolved path for display.

        Raises StoragePathError for path traversal attempts, null bytes,
        and symlinks that escape the root.
        """
        if "\x00" in relative_path:
            raise StoragePathError("Null bytes in path")

        cleaned = relative_path.replace("\\", "/").strip("/")
        if not cleaned:
            return self._root

        target = (self._root / cleaned).resolve()

        try:
            target.relative_to(self._root)
        except ValueError:
            raise StoragePathError(
                f"Path traversal detected: '{relative_path}' resolves outside root"
            ) from None

        return target

    def _safe_path(self, relative_path: str) -> tuple[Path, Path]:
        """Return (unresolved_path, resolved_path) for safe access.

        The resolved path is used for security checks and file I/O.
        The unresolved path preserves symlink names for display.
        """
        if "\x00" in relative_path:
            raise StoragePathError("Null bytes in path")

        cleaned = relative_path.replace("\\", "/").strip("/")
        if not cleaned:
            return self._root, self._root

        unresolved = self._root / cleaned
        resolved = unresolved.resolve()

        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise StoragePathError(
                f"Path traversal detected: '{relative_path}' resolves outside root"
            ) from None

        return unresolved, resolved

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_storage_item(
        self,
        full_path: Path,
        *,
        original_path: Path | None = None,
    ) -> StorageItem:
        """Convert a filesystem path to a StorageItem.

        When original_path is provided (e.g. for symlinks), use it for
        the name and relative path while using the resolved path for stat.
        """
        display_path = original_path or full_path
        stat = full_path.stat()
        rel = str(display_path.relative_to(self._root)).replace("\\", "/")
        is_dir = full_path.is_dir()

        return StorageItem(
            path=rel,
            name=display_path.name,
            item_type=ItemType.DIRECTORY if is_dir else ItemType.FILE,
            size_bytes=0 if is_dir else stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
            created_at=datetime.fromtimestamp(stat.st_ctime, tz=UTC).isoformat(),
            content_hash=self._compute_hash(full_path) if not is_dir else None,
        )

    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        """Compute SHA-256 hash of a file in 8KB chunks."""
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    # ------------------------------------------------------------------
    # StorageInterface implementation
    # ------------------------------------------------------------------

    def list(self, path: str = "", *, recursive: bool = False) -> list[StorageItem]:
        target = self._resolve_path(path)
        if not target.exists():
            raise StorageNotFoundError(f"Path not found: {path!r}")
        if not target.is_dir():
            raise StorageError(f"Not a directory: {path!r}")

        if recursive:
            return [self._to_storage_item(p) for p in sorted(target.rglob("*"))]
        return [self._to_storage_item(p) for p in sorted(target.iterdir())]

    def get(self, path: str) -> StorageItem:
        unresolved, resolved = self._safe_path(path)
        if not resolved.exists():
            raise StorageNotFoundError(f"Item not found: {path!r}")
        return self._to_storage_item(resolved, original_path=unresolved)

    def search(self, pattern: str, *, path: str = "") -> list[StorageItem]:
        base = self._resolve_path(path)
        if not base.exists():
            raise StorageNotFoundError(f"Base path not found: {path!r}")

        results = []
        for match in sorted(base.glob(pattern)):
            try:
                match.relative_to(self._root)
            except ValueError:
                continue
            results.append(self._to_storage_item(match))
        return results

    def tree(self, path: str = "", *, max_depth: int = -1) -> StorageTree:
        target = self._resolve_path(path)
        if not target.exists():
            raise StorageNotFoundError(f"Path not found: {path!r}")
        return self._build_tree(target, max_depth, current_depth=0)

    def _build_tree(self, full_path: Path, max_depth: int, current_depth: int) -> StorageTree:
        item = self._to_storage_item(full_path)

        if item.item_type == ItemType.FILE:
            return StorageTree(item=item)

        if max_depth >= 0 and current_depth >= max_depth:
            return StorageTree(item=item)

        children = tuple(
            self._build_tree(child, max_depth, current_depth + 1)
            for child in sorted(full_path.iterdir())
        )
        return StorageTree(item=item, children=children)

    def put(self, path: str, content: bytes) -> WriteResult:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return WriteResult(
            success=True,
            path=path,
            operation="put",
            bytes_written=len(content),
        )

    def mkdir(self, path: str) -> WriteResult:
        target = self._resolve_path(path)
        target.mkdir(parents=True, exist_ok=True)
        return WriteResult(success=True, path=path, operation="mkdir")

    def move(self, source: str, destination: str) -> WriteResult:
        src = self._resolve_path(source)
        dst = self._resolve_path(destination)

        if not src.exists():
            raise StorageNotFoundError(f"Source not found: {source!r}")

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return WriteResult(success=True, path=destination, operation="move")

    def delete(self, path: str) -> WriteResult:
        target = self._resolve_path(path)
        if not target.exists():
            raise StorageNotFoundError(f"Item not found: {path!r}")

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

        return WriteResult(success=True, path=path, operation="delete")

    def health(self) -> StorageHealth:
        if not self._root.exists():
            return StorageHealth(
                status="DOWN",
                backend=self.BACKEND,
                root_path=str(self._root),
                total_items=0,
                total_size_bytes=0,
                readable=False,
                writable=False,
                message="Root directory does not exist",
            )

        readable = os.access(self._root, os.R_OK)
        writable = os.access(self._root, os.W_OK)

        total_items = 0
        total_size = 0
        for entry in self._root.rglob("*"):
            total_items += 1
            if entry.is_file():
                total_size += entry.stat().st_size

        status: str = "UP"
        message = ""
        if not readable:
            status = "DOWN"
            message = "Root directory is not readable"
        elif not writable:
            status = "DEGRADED"
            message = "Root directory is not writable"

        return StorageHealth(
            status=status,
            backend=self.BACKEND,
            root_path=str(self._root),
            total_items=total_items,
            total_size_bytes=total_size,
            readable=readable,
            writable=writable,
            message=message,
        )
