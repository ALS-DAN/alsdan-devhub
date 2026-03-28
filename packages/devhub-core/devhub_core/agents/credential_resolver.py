"""
CredentialResolver — Lost credentials op buiten de repository.

Credentials worden opgeslagen in ~/.devhub/credentials/ en NOOIT
in de repository (DEV_CONSTITUTION Art. 8).

Google Drive OAuth2:
  ~/.devhub/credentials/google_client_secrets.json  (handmatig geplaatst)
  ~/.devhub/credentials/.google_token.json          (automatisch gecached)
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CredentialResolver:
    """Lost credentials op vanuit een veilige locatie buiten de repo.

    Standaard locatie: ~/.devhub/credentials/
    Overschrijfbaar via base_path parameter (voor tests).
    """

    DEFAULT_BASE = Path.home() / ".devhub" / "credentials"

    def __init__(self, base_path: Path | None = None) -> None:
        self._base = base_path or self.DEFAULT_BASE

    @property
    def base_path(self) -> Path:
        """De basis-directory voor credentials."""
        return self._base

    @property
    def client_secrets_path(self) -> Path:
        """Pad naar Google OAuth2 client secrets."""
        return self._base / "google_client_secrets.json"

    @property
    def token_path(self) -> Path:
        """Pad naar de gecachte Google OAuth2 token."""
        return self._base / ".google_token.json"

    def has_google_credentials(self) -> bool:
        """Controleer of Google client secrets beschikbaar zijn."""
        return self.client_secrets_path.exists()

    def resolve_google_drive_auth(self) -> object:
        """Maak een OAuth2Auth instance aan met de juiste paden.

        Returns:
            OAuth2Auth instantie (uit devhub-storage).

        Raises:
            FileNotFoundError: Als client_secrets niet gevonden.
            ImportError: Als devhub-storage[google] niet geïnstalleerd.
        """
        if not self.has_google_credentials():
            raise FileNotFoundError(
                f"Google client secrets niet gevonden op {self.client_secrets_path}. "
                f"Plaats het bestand handmatig vanuit Google Cloud Console."
            )

        from devhub_storage.auth import OAuth2Auth

        return OAuth2Auth(
            client_secrets_file=str(self.client_secrets_path),
            token_file=str(self.token_path),
        )

    def credentials_status(self) -> dict[str, bool]:
        """Overzicht van beschikbare credentials.

        Returns:
            Dict met credential-naam → beschikbaar (bool).
        """
        return {
            "google_client_secrets": self.client_secrets_path.exists(),
            "google_token_cached": self.token_path.exists(),
            "credentials_dir_exists": self._base.exists(),
        }
