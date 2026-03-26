"""Tests voor Storage Mixins — ABC enforcement en compositie."""

import pytest

from devhub_storage.interface import StorageInterface
from devhub_storage.mixins import Organizable, Reconcilable, Watchable


# ---------------------------------------------------------------------------
# ABC enforcement
# ---------------------------------------------------------------------------


class TestABCEnforcement:
    def test_organizable_not_instantiable(self):
        with pytest.raises(TypeError):
            Organizable()  # type: ignore[abstract]

    def test_watchable_not_instantiable(self):
        with pytest.raises(TypeError):
            Watchable()  # type: ignore[abstract]

    def test_reconcilable_not_instantiable(self):
        with pytest.raises(TypeError):
            Reconcilable()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


class TestComposition:
    def test_local_adapter_not_organizable(self, adapter):
        assert not isinstance(adapter, Organizable)

    def test_local_adapter_not_watchable(self, adapter):
        assert not isinstance(adapter, Watchable)

    def test_local_adapter_not_reconcilable(self, adapter):
        assert not isinstance(adapter, Reconcilable)

    def test_composite_adapter_isinstance(self):
        """Mock adapter that implements StorageInterface + Organizable."""

        class MockComposite(StorageInterface, Organizable):
            def list(self, path="", *, recursive=False):
                return []

            def get(self, path): ...
            def search(self, pattern, *, path=""):
                return []

            def tree(self, path="", *, max_depth=-1): ...
            def put(self, path, content): ...
            def mkdir(self, path): ...
            def move(self, source, destination): ...
            def delete(self, path): ...
            def health(self): ...
            def tag(self, path, tags): ...
            def get_tags(self, path):
                return []

            def relate(self, source, target, relation): ...
            def get_relations(self, path):
                return []

            def version(self, path):
                return []

        obj = MockComposite()
        assert isinstance(obj, StorageInterface)
        assert isinstance(obj, Organizable)
        assert not isinstance(obj, Watchable)
        assert not isinstance(obj, Reconcilable)

    def test_full_composite(self):
        """Mock adapter implementing all interfaces."""

        class FullComposite(StorageInterface, Organizable, Watchable, Reconcilable):
            def list(self, path="", *, recursive=False):
                return []

            def get(self, path): ...
            def search(self, pattern, *, path=""):
                return []

            def tree(self, path="", *, max_depth=-1): ...
            def put(self, path, content): ...
            def mkdir(self, path): ...
            def move(self, source, destination): ...
            def delete(self, path): ...
            def health(self): ...
            def tag(self, path, tags): ...
            def get_tags(self, path):
                return []

            def relate(self, source, target, relation): ...
            def get_relations(self, path):
                return []

            def version(self, path):
                return []

            def watch(self, path="", *, since=None):
                return []

            def drift_report(self, desired_spec): ...
            def reconcile(self, desired_spec, *, dry_run=True): ...

        obj = FullComposite()
        assert isinstance(obj, StorageInterface)
        assert isinstance(obj, Organizable)
        assert isinstance(obj, Watchable)
        assert isinstance(obj, Reconcilable)
