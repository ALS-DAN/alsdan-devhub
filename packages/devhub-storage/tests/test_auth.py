"""Tests voor StorageAuth — auth-abstractie voor cloud storage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from devhub_storage.auth import (
    OAuth2Auth,
    ServiceAccountAuth,
    StorageAuth,
    StorageAuthError,
)


# ---------------------------------------------------------------------------
# StorageAuth ABC
# ---------------------------------------------------------------------------


class TestStorageAuthABC:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            StorageAuth()

    def test_concrete_implementation(self):
        class ConcreteAuth(StorageAuth):
            def authenticate(self):
                return "token"

            def is_valid(self):
                return True

        auth = ConcreteAuth()
        assert auth.authenticate() == "token"
        assert auth.is_valid() is True


# ---------------------------------------------------------------------------
# ServiceAccountAuth
# ---------------------------------------------------------------------------


class TestServiceAccountAuth:
    def test_empty_key_file_raises(self):
        with pytest.raises(ValueError, match="key_file is required"):
            ServiceAccountAuth(key_file="")

    def test_nonexistent_key_file_raises(self):
        with pytest.raises(StorageAuthError, match="not found"):
            ServiceAccountAuth(key_file="/nonexistent/path.json")

    def test_non_json_key_file_raises(self, tmp_path: Path):
        txt_file = tmp_path / "key.txt"
        txt_file.write_text("not json")
        with pytest.raises(StorageAuthError, match=".json"):
            ServiceAccountAuth(key_file=str(txt_file))

    def test_valid_key_file(self, tmp_path: Path):
        key_file = tmp_path / "service_account.json"
        key_file.write_text(json.dumps({"type": "service_account"}))
        auth = ServiceAccountAuth(key_file=str(key_file))
        assert auth.key_file == str(key_file)

    def test_default_scopes(self, tmp_path: Path):
        key_file = tmp_path / "sa.json"
        key_file.write_text(json.dumps({"type": "service_account"}))
        auth = ServiceAccountAuth(key_file=str(key_file))
        assert "drive" in auth.scopes[0]

    def test_custom_scopes(self, tmp_path: Path):
        key_file = tmp_path / "sa.json"
        key_file.write_text(json.dumps({"type": "service_account"}))
        auth = ServiceAccountAuth(
            key_file=str(key_file),
            scopes=("https://www.googleapis.com/auth/drive.readonly",),
        )
        assert "readonly" in auth.scopes[0]

    def test_is_valid_with_existing_file(self, tmp_path: Path):
        key_file = tmp_path / "sa.json"
        key_file.write_text(json.dumps({"type": "service_account"}))
        auth = ServiceAccountAuth(key_file=str(key_file))
        assert auth.is_valid() is True

    def test_is_valid_with_empty_file(self, tmp_path: Path):
        key_file = tmp_path / "empty.json"
        key_file.write_text("")
        # Can't create with empty file — size check
        auth = ServiceAccountAuth.__new__(ServiceAccountAuth)
        object.__setattr__(auth, "key_file", str(key_file))
        object.__setattr__(auth, "scopes", ("https://www.googleapis.com/auth/drive",))
        assert auth.is_valid() is False

    def test_frozen_dataclass(self, tmp_path: Path):
        key_file = tmp_path / "sa.json"
        key_file.write_text(json.dumps({"type": "service_account"}))
        auth = ServiceAccountAuth(key_file=str(key_file))
        with pytest.raises(AttributeError):
            auth.key_file = "other"


# ---------------------------------------------------------------------------
# OAuth2Auth
# ---------------------------------------------------------------------------


class TestOAuth2Auth:
    def test_empty_client_secrets_raises(self):
        with pytest.raises(ValueError, match="client_secrets_file is required"):
            OAuth2Auth(client_secrets_file="")

    def test_nonexistent_secrets_raises(self):
        with pytest.raises(StorageAuthError, match="not found"):
            OAuth2Auth(client_secrets_file="/nonexistent/secrets.json")

    def test_valid_client_secrets(self, tmp_path: Path):
        secrets = tmp_path / "client_secrets.json"
        secrets.write_text(json.dumps({"installed": {}}))
        auth = OAuth2Auth(client_secrets_file=str(secrets))
        assert auth.client_secrets_file == str(secrets)

    def test_default_token_file(self, tmp_path: Path):
        secrets = tmp_path / "client_secrets.json"
        secrets.write_text(json.dumps({"installed": {}}))
        auth = OAuth2Auth(client_secrets_file=str(secrets))
        assert auth.token_file == ".google_token.json"

    def test_custom_token_file(self, tmp_path: Path):
        secrets = tmp_path / "client_secrets.json"
        secrets.write_text(json.dumps({"installed": {}}))
        auth = OAuth2Auth(
            client_secrets_file=str(secrets),
            token_file=str(tmp_path / "custom_token.json"),
        )
        assert "custom_token" in auth.token_file

    def test_is_valid_without_token(self, tmp_path: Path):
        secrets = tmp_path / "client_secrets.json"
        secrets.write_text(json.dumps({"installed": {}}))
        auth = OAuth2Auth(
            client_secrets_file=str(secrets),
            token_file=str(tmp_path / "nonexistent_token.json"),
        )
        assert auth.is_valid() is False

    def test_frozen_dataclass(self, tmp_path: Path):
        secrets = tmp_path / "client_secrets.json"
        secrets.write_text(json.dumps({"installed": {}}))
        auth = OAuth2Auth(client_secrets_file=str(secrets))
        with pytest.raises(AttributeError):
            auth.client_secrets_file = "other"  # pragma: allowlist secret
