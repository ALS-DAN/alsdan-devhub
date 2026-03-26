"""
StorageInterface — Abstract contract voor storage-backends.

Elke storage-backend (lokaal filesystem, Google Drive, SharePoint)
implementeert deze interface. Geen backend-specifieke types in de interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from devhub_storage.contracts import StorageHealth, StorageItem, StorageTree, WriteResult


class StorageInterface(ABC):
    """Abstract contract dat elke storage-backend moet implementeren.

    Alle paden zijn relatief t.o.v. de storage root, forward-slash gescheiden.
    De adapter normaliseert backend-specifieke padformaten.
    """

    @abstractmethod
    def list(self, path: str = "", *, recursive: bool = False) -> list[StorageItem]:
        """Lijst items in een directory."""
        ...

    @abstractmethod
    def get(self, path: str) -> StorageItem:
        """Haal metadata op voor één item."""
        ...

    @abstractmethod
    def search(self, pattern: str, *, path: str = "") -> list[StorageItem]:
        """Zoek items op glob-patroon."""
        ...

    @abstractmethod
    def tree(self, path: str = "", *, max_depth: int = -1) -> StorageTree:
        """Bouw een recursieve boomstructuur."""
        ...

    @abstractmethod
    def put(self, path: str, content: bytes) -> WriteResult:
        """Schrijf of overschrijf een bestand."""
        ...

    @abstractmethod
    def mkdir(self, path: str) -> WriteResult:
        """Maak een directory (inclusief ouders)."""
        ...

    @abstractmethod
    def move(self, source: str, destination: str) -> WriteResult:
        """Verplaats of hernoem een item."""
        ...

    @abstractmethod
    def delete(self, path: str) -> WriteResult:
        """Verwijder een item."""
        ...

    @abstractmethod
    def health(self) -> StorageHealth:
        """Controleer de gezondheid van de backend."""
        ...
