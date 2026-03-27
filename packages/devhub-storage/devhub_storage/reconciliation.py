"""
ReconciliationEngine — Declaratief state management voor storage-backends.

Vergelijkt een gewenste staat (spec) met de actuele staat van een
StorageInterface-backend en kan afwijkingen oplossen.

Veiligheidsgates:
- dry_run=True is default — toont wat er zou gebeuren zonder mutaties
- remove_extra=False is default — verwijdert nooit onverwachte bestanden
- Destructieve acties worden gelogd
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from devhub_storage.contracts import (
    DriftItem,
    DriftReport,
    ItemType,
    ReconcileResult,
    StorageNotFoundError,
)
from devhub_storage.interface import StorageInterface

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Spec dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpecItem:
    """Eén gewenst item in de desired-state spec."""

    path: str
    item_type: ItemType
    content_hash: str | None = None

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path is required")


@dataclass(frozen=True)
class ReconciliationSpec:
    """Gewenste staat voor een storage-backend."""

    root: str
    items: tuple[SpecItem, ...] = ()

    def __post_init__(self) -> None:
        if self.root is None:
            raise ValueError("root is required")


# ---------------------------------------------------------------------------
# Spec parsing
# ---------------------------------------------------------------------------

_TYPE_MAP = {
    "file": ItemType.FILE,
    "directory": ItemType.DIRECTORY,
}


def parse_spec(raw: dict) -> ReconciliationSpec:
    """Parseer een dict (uit YAML) naar een ReconciliationSpec.

    Verwacht formaat::

        {
            "root": "projects/kennisbank",
            "items": [
                {"path": "protocols/", "type": "directory"},
                {"path": "protocols/README.md", "type": "file", "content_hash": "abc123"},
            ]
        }

    Raises:
        ValueError: bij ongeldige of ontbrekende velden.
    """
    if not isinstance(raw, dict):
        raise ValueError("spec must be a dict")

    root = raw.get("root", "")
    raw_items = raw.get("items", [])

    if not isinstance(raw_items, list):
        raise ValueError("spec.items must be a list")

    spec_items: list[SpecItem] = []
    for i, item in enumerate(raw_items):
        if not isinstance(item, dict):
            raise ValueError(f"spec.items[{i}] must be a dict")

        path = item.get("path")
        if not path:
            raise ValueError(f"spec.items[{i}].path is required")

        raw_type = item.get("type")
        if raw_type not in _TYPE_MAP:
            raise ValueError(
                f"spec.items[{i}].type must be 'file' or 'directory', got {raw_type!r}"
            )

        spec_items.append(
            SpecItem(
                path=path,
                item_type=_TYPE_MAP[raw_type],
                content_hash=item.get("content_hash"),
            )
        )

    return ReconciliationSpec(root=root, items=tuple(spec_items))


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


@dataclass
class ReconciliationEngine:
    """Adapter-agnostische reconciliation engine.

    Werkt via de StorageInterface — kan elke backend reconcilen
    zonder backend-specifieke logica.

    Gebruik::

        engine = ReconciliationEngine(adapter=local_adapter)
        report = engine.drift_report(spec)
        result = engine.reconcile(spec, dry_run=True)
    """

    adapter: StorageInterface
    _logger: logging.Logger = field(default_factory=lambda: logger, repr=False)

    def drift_report(self, spec: dict | ReconciliationSpec) -> DriftReport:
        """Vergelijk gewenste staat met actuele staat (read-only).

        Args:
            spec: Desired-state spec als dict of ReconciliationSpec.

        Returns:
            DriftReport met alle gevonden afwijkingen.
        """
        parsed = self._ensure_spec(spec)
        drifts: list[DriftItem] = []

        # Haal actuele staat op
        actual_items = self._scan_actual(parsed.root)

        # Check spec items tegen actuele staat
        for item in parsed.items:
            full_path = self._full_path(parsed.root, item.path)
            actual = actual_items.pop(full_path, None)

            if actual is None:
                drifts.append(
                    DriftItem(
                        path=full_path,
                        drift_type="missing",
                        expected=item.item_type.value,
                        actual="",
                    )
                )
            elif actual.item_type != item.item_type:
                drifts.append(
                    DriftItem(
                        path=full_path,
                        drift_type="wrong_type",
                        expected=item.item_type.value,
                        actual=actual.item_type.value,
                    )
                )
            elif (
                item.content_hash
                and actual.content_hash
                and item.content_hash != actual.content_hash
            ):
                drifts.append(
                    DriftItem(
                        path=full_path,
                        drift_type="wrong_content",
                        expected=item.content_hash,
                        actual=actual.content_hash,
                    )
                )

        # Overige items op backend maar niet in spec
        for path, actual in actual_items.items():
            drifts.append(
                DriftItem(
                    path=path,
                    drift_type="extra",
                    expected="",
                    actual=actual.item_type.value,
                )
            )

        return DriftReport(drifts=tuple(drifts))

    def reconcile(
        self,
        spec: dict | ReconciliationSpec,
        *,
        dry_run: bool = True,
        remove_extra: bool = False,
    ) -> ReconcileResult:
        """Breng actuele staat in lijn met gewenste staat.

        Args:
            spec: Desired-state spec als dict of ReconciliationSpec.
            dry_run: Als True, voer geen mutaties uit (default True).
            remove_extra: Als True, verwijder items die niet in spec staan.

        Returns:
            ReconcileResult met uitgevoerde acties.
        """
        report = self.drift_report(spec)

        if report.in_sync:
            return ReconcileResult(
                dry_run=dry_run,
                actions_planned=0,
                actions_executed=0,
            )

        actions_planned = 0
        actions_executed = 0
        resolved: list[DriftItem] = []
        errors: list[str] = []

        for drift in report.drifts:
            if drift.drift_type == "missing" and drift.expected == "directory":
                actions_planned += 1
                if not dry_run:
                    try:
                        result = self.adapter.mkdir(drift.path)
                        if result.success:
                            actions_executed += 1
                            resolved.append(drift)
                            self._logger.info("mkdir: %s", drift.path)
                        else:
                            errors.append(f"mkdir failed: {drift.path} — {result.message}")
                    except Exception as e:
                        errors.append(f"mkdir error: {drift.path} — {e}")

            elif drift.drift_type == "missing" and drift.expected == "file":
                actions_planned += 1
                # Geen content beschikbaar in spec — kan niet aanmaken
                errors.append(f"missing file: {drift.path} — no content in spec, cannot create")

            elif drift.drift_type == "extra" and remove_extra:
                actions_planned += 1
                if not dry_run:
                    try:
                        result = self.adapter.delete(drift.path)
                        if result.success:
                            actions_executed += 1
                            resolved.append(drift)
                            self._logger.info("delete extra: %s", drift.path)
                        else:
                            errors.append(f"delete failed: {drift.path} — {result.message}")
                    except Exception as e:
                        errors.append(f"delete error: {drift.path} — {e}")

            elif drift.drift_type == "extra" and not remove_extra:
                # Skip — veiligheidsgate: verwijder niet zonder expliciete toestemming
                pass

            elif drift.drift_type == "wrong_type":
                actions_planned += 1
                errors.append(
                    f"wrong_type: {drift.path} — expected {drift.expected}, "
                    f"got {drift.actual} (requires manual intervention)"
                )

            elif drift.drift_type == "wrong_content":
                actions_planned += 1
                errors.append(f"wrong_content: {drift.path} — no content in spec, cannot fix")

        return ReconcileResult(
            dry_run=dry_run,
            actions_planned=actions_planned,
            actions_executed=actions_executed,
            drifts_resolved=tuple(resolved),
            errors=tuple(errors),
        )

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _ensure_spec(spec: dict | ReconciliationSpec) -> ReconciliationSpec:
        """Parseer spec als het een dict is."""
        if isinstance(spec, ReconciliationSpec):
            return spec
        return parse_spec(spec)

    @staticmethod
    def _full_path(root: str, relative: str) -> str:
        """Combineer root en relatief pad."""
        if not root:
            return relative
        return f"{root.rstrip('/')}/{relative.lstrip('/')}"

    def _scan_actual(self, root: str) -> dict:
        """Scan actuele items op backend onder root.

        Returns:
            Dict van {full_path: StorageItem}.
        """
        try:
            items = self.adapter.list(root, recursive=True)
        except StorageNotFoundError:
            return {}
        except Exception:
            self._logger.warning("Could not scan root '%s', treating as empty", root)
            return {}

        return {item.path: item for item in items}
