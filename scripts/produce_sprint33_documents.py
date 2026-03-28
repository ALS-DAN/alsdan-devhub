#!/usr/bin/env python3
"""Sprint 33 — Produceer documenten via de DocumentService pipeline.

Genereert 4 documenten:
1. Pattern: ABC + Adapter Pattern in DevHub
2. Methodology: Shape Up in DevHub
3. Tutorial: Je eerste sprint intake maken
4. Methodology: Hoe een project de DevHub documentatie-pipeline overneemt (BORIS-blauwdruk)

Uitvoering:
    uv run python scripts/produce_sprint33_documents.py

Optioneel met Google Drive publicatie (als credentials beschikbaar):
    uv run python scripts/produce_sprint33_documents.py --publish
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Zorg dat het project root in sys.path zit
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CONFIG_PATH = PROJECT_ROOT / "config" / "documents.yml"
OUTPUT_DIR = PROJECT_ROOT / "output" / "documents"


def main() -> None:
    parser = argparse.ArgumentParser(description="Sprint 33 document productie")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publiceer naar Google Drive (vereist credentials in ~/.devhub/credentials/)",
    )
    args = parser.parse_args()

    from devhub_documents.factory import DocumentFactory
    from devhub_core.agents.content_builders import SPRINT_33_BUILDERS
    from devhub_core.agents.document_service import DocumentService
    from devhub_core.agents.folder_router import FolderRouter

    # Setup
    factory = DocumentFactory(config_path=CONFIG_PATH)
    router = FolderRouter(config_path=CONFIG_PATH)

    # Storage: lokaal of Google Drive
    storage = None
    if args.publish:
        from devhub_core.agents.credential_resolver import CredentialResolver

        resolver = CredentialResolver()
        if resolver.has_google_credentials():
            from devhub_storage.adapters.google_drive_adapter import GoogleDriveAdapter

            auth = resolver.resolve_google_drive_auth()
            storage = GoogleDriveAdapter(auth=auth)
            print("Google Drive storage geconfigureerd")
        else:
            print("Geen Google credentials gevonden, alleen lokale output")

    service = DocumentService(
        document_factory=factory,
        folder_router=router,
        storage=storage,
    )

    # Produceer documenten
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nSprint 33 — {len(SPRINT_33_BUILDERS)} documenten produceren\n")

    for i, builder in enumerate(SPRINT_33_BUILDERS, 1):
        request = builder()
        print(f"[{i}/{len(SPRINT_33_BUILDERS)}] {request.topic}")
        print(f"  Category: {request.category.value} ({request.category.layer()})")

        result = service.produce(request)

        print(f"  Lokaal: {result.document_result.path}")
        print(f"  Storage: {result.storage_path}")
        print(f"  Status: {result.publish_status.value}")
        print(f"  Size: {result.document_result.size_bytes} bytes")
        print()

    print("Klaar!")


if __name__ == "__main__":
    main()
