"""Tests voor CredentialResolver — credential management buiten repo."""

from pathlib import Path

import pytest

from devhub_core.agents.credential_resolver import CredentialResolver


class TestCredentialResolver:
    def test_default_base_path(self):
        resolver = CredentialResolver()
        assert resolver.base_path == Path.home() / ".devhub" / "credentials"

    def test_custom_base_path(self, tmp_path: Path):
        resolver = CredentialResolver(base_path=tmp_path)
        assert resolver.base_path == tmp_path

    def test_has_google_credentials_false_when_missing(self, tmp_path: Path):
        resolver = CredentialResolver(base_path=tmp_path)
        assert resolver.has_google_credentials() is False

    def test_has_google_credentials_true_when_present(self, tmp_path: Path):
        secrets_file = tmp_path / "google_client_secrets.json"
        secrets_file.write_text('{"installed": {}}')
        resolver = CredentialResolver(base_path=tmp_path)
        assert resolver.has_google_credentials() is True

    def test_credentials_status_keys(self, tmp_path: Path):
        resolver = CredentialResolver(base_path=tmp_path)
        status = resolver.credentials_status()
        assert "google_client_secrets" in status
        assert "google_token_cached" in status
        assert "credentials_dir_exists" in status

    def test_credentials_status_values_when_empty(self, tmp_path: Path):
        empty_dir = tmp_path / "empty"
        resolver = CredentialResolver(base_path=empty_dir)
        status = resolver.credentials_status()
        assert status["google_client_secrets"] is False
        assert status["google_token_cached"] is False
        assert status["credentials_dir_exists"] is False

    def test_resolve_google_drive_auth_raises_when_missing(self, tmp_path: Path):
        resolver = CredentialResolver(base_path=tmp_path)
        with pytest.raises(FileNotFoundError, match="client secrets"):
            resolver.resolve_google_drive_auth()

    def test_client_secrets_path(self, tmp_path: Path):
        resolver = CredentialResolver(base_path=tmp_path)
        assert resolver.client_secrets_path == tmp_path / "google_client_secrets.json"

    def test_token_path(self, tmp_path: Path):
        resolver = CredentialResolver(base_path=tmp_path)
        assert resolver.token_path == tmp_path / ".google_token.json"
