"""Tests voor VectorStoreFactory."""

import pytest

from devhub_vectorstore.contracts.vectorstore_contracts import DataZone, VectorStoreInterface
from devhub_vectorstore.factory import VectorStoreFactory


class TestVectorStoreFactory:
    def test_create_chromadb(self):
        store = VectorStoreFactory.create("chromadb", zones=[DataZone.OPEN])
        assert isinstance(store, VectorStoreInterface)

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="Unknown vectorstore backend"):
            VectorStoreFactory.create("nonexistent")

    def test_kwargs_passed_through(self):
        store = VectorStoreFactory.create(
            "chromadb",
            zones=[DataZone.RESTRICTED],
            collection_prefix="custom",
        )
        assert store.health().collection_count == 1

    def test_string_zone_conversion(self):
        store = VectorStoreFactory.create("chromadb", zones=["OPEN", "RESTRICTED"])
        assert store.health().collection_count == 2

    def test_available_backends(self):
        backends = VectorStoreFactory.available_backends()
        assert "chromadb" in backends

    def test_default_backend(self):
        store = VectorStoreFactory.create()
        assert isinstance(store, VectorStoreInterface)
        assert store.health().backend == "chromadb"


class TestPackageImports:
    def test_import_contracts(self):
        from devhub_vectorstore import (
            DataZone,
        )

        assert DataZone.OPEN.value == "open"

    def test_import_factory(self):
        from devhub_vectorstore import VectorStoreFactory

        assert callable(VectorStoreFactory.create)

    def test_import_adapter(self):
        from devhub_vectorstore.adapters.chromadb_adapter import ChromaDBZonedStore

        assert issubclass(ChromaDBZonedStore, VectorStoreInterface)
