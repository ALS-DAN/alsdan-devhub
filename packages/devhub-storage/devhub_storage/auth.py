"""
Storage Auth — Abstractie voor authenticatie bij cloud storage-backends.

Elke cloud-adapter (Google Drive, SharePoint) gebruikt een StorageAuth
implementatie voor credential-management. Credentials worden NOOIT in
code opgeslagen (DEV_CONSTITUTION Art. 8).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class StorageAuth(ABC):
    """Abstract contract voor storage-authenticatie.

    Implementaties leveren credentials aan cloud storage-adapters.
    """

    @abstractmethod
    def authenticate(self) -> Any:
        """Authentiseer en retourneer credentials-object.

        Returns:
            Backend-specifiek credentials-object.

        Raises:
            StorageAuthError: Bij authenticatie-fout.
        """
        ...

    @abstractmethod
    def is_valid(self) -> bool:
        """Controleer of huidige credentials geldig zijn."""
        ...


class StorageAuthError(Exception):
    """Fout bij authenticatie voor storage-backend."""


@dataclass(frozen=True)
class ServiceAccountAuth(StorageAuth):
    """Google Service Account authenticatie via JSON key-file.

    Args:
        key_file: Pad naar het service account JSON key-bestand.
        scopes: OAuth2 scopes (default: Drive read/write).
    """

    key_file: str
    scopes: tuple[str, ...] = ("https://www.googleapis.com/auth/drive",)

    def __post_init__(self) -> None:
        if not self.key_file:
            raise ValueError("key_file is required")
        path = Path(self.key_file)
        if not path.exists():
            raise StorageAuthError(f"Service account key file not found: {self.key_file}")
        if not path.suffix == ".json":
            raise StorageAuthError(f"Key file must be .json, got: {path.suffix}")

    def authenticate(self) -> Any:
        """Authentiseer via service account key-file."""
        try:
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                self.key_file,
                scopes=list(self.scopes),
            )
            return credentials
        except ImportError:
            raise ImportError(
                "google-auth is required for ServiceAccountAuth. "
                "Install with: uv pip install 'devhub-storage[google]'"
            ) from None
        except Exception as e:
            raise StorageAuthError(f"Authentication failed: {e}") from e

    def is_valid(self) -> bool:
        """Controleer of de key-file leesbaar is."""
        try:
            path = Path(self.key_file)
            return path.exists() and path.stat().st_size > 0
        except Exception:
            return False


@dataclass(frozen=True)
class OAuth2Auth(StorageAuth):
    """OAuth2 authenticatie met client secrets + token cache.

    Args:
        client_secrets_file: Pad naar OAuth2 client secrets JSON.
        token_file: Pad voor token-cache (wordt aangemaakt).
        scopes: OAuth2 scopes.
    """

    client_secrets_file: str
    token_file: str = ".google_token.json"
    scopes: tuple[str, ...] = ("https://www.googleapis.com/auth/drive",)

    def __post_init__(self) -> None:
        if not self.client_secrets_file:
            raise ValueError("client_secrets_file is required")
        path = Path(self.client_secrets_file)
        if not path.exists():
            raise StorageAuthError(f"Client secrets file not found: {self.client_secrets_file}")

    def authenticate(self) -> Any:
        """Authentiseer via OAuth2 flow met token-cache."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise ImportError(
                "google-auth and google-auth-oauthlib are required "
                "for OAuth2Auth. Install with: "
                "uv pip install 'devhub-storage[google]'"
            ) from None

        token_path = Path(self.token_file)
        credentials = None

        # Probeer bestaand token
        if token_path.exists():
            try:
                credentials = Credentials.from_authorized_user_file(
                    str(token_path), list(self.scopes)
                )
            except Exception:
                credentials = None

        # Vernieuw of start flow
        if credentials and credentials.valid:
            return credentials

        if credentials and credentials.expired and credentials.refresh_token:
            try:
                from google.auth.transport.requests import Request

                credentials.refresh(Request())
                token_path.write_text(credentials.to_json())
                return credentials
            except Exception as e:
                raise StorageAuthError(f"Token refresh failed: {e}") from e

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, list(self.scopes)
            )
            credentials = flow.run_local_server(port=0)
            token_path.write_text(credentials.to_json())
            return credentials
        except Exception as e:
            raise StorageAuthError(f"OAuth2 flow failed: {e}") from e

    def is_valid(self) -> bool:
        """Controleer of er een geldig token bestaat."""
        token_path = Path(self.token_file)
        if not token_path.exists():
            return False
        try:
            from google.oauth2.credentials import Credentials

            creds = Credentials.from_authorized_user_file(str(token_path), list(self.scopes))
            return creds.valid or (creds.expired and creds.refresh_token is not None)
        except Exception:
            return False
