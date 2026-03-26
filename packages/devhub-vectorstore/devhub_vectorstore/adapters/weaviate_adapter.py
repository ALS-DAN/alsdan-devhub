"""
Weaviate Adapter — Productie vectorstore voor de VectorStoreInterface.

Gebruikt Weaviate v4 API met zone-isolatie en multi-tenancy.
Weaviate-client is een optional dependency — import faalt met duidelijke melding.

BORIS-compatibel: Weaviate 1.27.x, 384-dim vectoren.
Art. 6: BORIS code wordt NIET geimporteerd — adapter is generiek.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from devhub_vectorstore.contracts.vectorstore_contracts import (
    DataZone,
    DocumentChunk,
    RetrievalRequest,
    RetrievalResponse,
    SearchResult,
    TenantStrategy,
    VectorStoreHealth,
    VectorStoreInterface,
)

if TYPE_CHECKING:
    import weaviate


def _get_weaviate() -> Any:
    """Lazy import weaviate met duidelijke error."""
    try:
        import weaviate as _weaviate

        return _weaviate
    except ImportError as e:
        if "No module named 'weaviate'" in str(e):
            raise ImportError(
                "weaviate-client is required for WeaviateZonedStore. "
                "Install with: uv pip install 'devhub-vectorstore[weaviate]'"
            ) from None
        raise


class WeaviateZonedStore(VectorStoreInterface):
    """Weaviate-gebaseerde vectorstore met zone-isolatie en multi-tenancy.

    Elke DataZone krijgt een eigen Weaviate collection.
    Ondersteunt PER_ZONE (standaard) en PER_KWP tenant-strategieen.

    BORIS-compatibel: werkt met Weaviate 1.27.x en 384-dim vectoren.
    """

    def __init__(
        self,
        url: str = "http://localhost:8080",
        api_key: str | None = None,
        zones: list[DataZone] | None = None,
        collection_prefix: str = "devhub",
        tenant_strategy: TenantStrategy = TenantStrategy.PER_ZONE,
        *,
        _client: weaviate.WeaviateClient | None = None,
    ) -> None:
        """Initialiseer WeaviateZonedStore.

        Args:
            url: Weaviate server URL.
            api_key: Optionele API key voor authenticatie.
            zones: DataZones om te beheren (default: alle).
            collection_prefix: Prefix voor collection-namen.
            tenant_strategy: Multi-tenancy strategie.
            _client: Injecteerbare client voor testing.
        """
        if not url:
            raise ValueError("url is required")

        self._url = url
        self._zones = zones or list(DataZone)
        self._prefix = collection_prefix
        self._tenant_strategy = tenant_strategy
        self._tenants: set[str] = set()

        if _client is not None:
            self._client = _client
            self._owns_client = False
        else:
            weaviate_mod = _get_weaviate()
            connect_kwargs: dict[str, Any] = {}
            if api_key:
                connect_kwargs["auth_credentials"] = weaviate_mod.auth.AuthApiKey(api_key)
            self._client = weaviate_mod.connect_to_custom(
                http_host=self._extract_host(url),
                http_port=self._extract_port(url),
                http_secure=url.startswith("https"),
                grpc_host=self._extract_host(url),
                grpc_port=50051,
                grpc_secure=url.startswith("https"),
                **connect_kwargs,
            )
            self._owns_client = True

        self._collections: dict[str, Any] = {}
        self._ensure_collections()

    @staticmethod
    def _extract_host(url: str) -> str:
        """Extract hostname from URL."""
        host = url.split("://")[-1].split(":")[0].split("/")[0]
        return host

    @staticmethod
    def _extract_port(url: str) -> int:
        """Extract port from URL, default 8080."""
        parts = url.split("://")[-1].split("/")[0]
        if ":" in parts:
            try:
                return int(parts.split(":")[-1])
            except ValueError:
                pass
        return 443 if url.startswith("https") else 8080

    def _collection_name(self, zone: DataZone) -> str:
        """Genereer collection-naam voor een zone."""
        return f"{self._prefix}_{zone.value}"

    def _tenant_collection_name(self, tenant_id: str) -> str:
        """Genereer collection-naam voor een KWP-tenant."""
        safe_id = tenant_id.replace("-", "_").replace(" ", "_").lower()
        return f"{self._prefix}_kwp_{safe_id}"

    def _ensure_collections(self) -> None:
        """Maak zone-collecties aan als ze niet bestaan."""
        if self._tenant_strategy == TenantStrategy.PER_ZONE:
            for zone in self._zones:
                name = self._collection_name(zone)
                self._ensure_single_collection(name)
        # PER_KWP: collecties worden lazy aangemaakt bij ensure_tenant()

    def _ensure_single_collection(self, name: str) -> None:
        """Maak een enkele collectie aan als die niet bestaat."""
        try:
            if self._client.collections.exists(name):
                self._collections[name] = self._client.collections.get(name)
            else:
                weaviate_mod = _get_weaviate()
                self._collections[name] = self._client.collections.create(
                    name=name,
                    vectorizer_config=weaviate_mod.classes.config.Configure.Vectorizer.none(),
                    properties=[
                        weaviate_mod.classes.config.Property(
                            name="content",
                            data_type=weaviate_mod.classes.config.DataType.TEXT,
                        ),
                        weaviate_mod.classes.config.Property(
                            name="zone",
                            data_type=weaviate_mod.classes.config.DataType.TEXT,
                        ),
                        weaviate_mod.classes.config.Property(
                            name="source_id",
                            data_type=weaviate_mod.classes.config.DataType.TEXT,
                        ),
                        weaviate_mod.classes.config.Property(
                            name="created_at",
                            data_type=weaviate_mod.classes.config.DataType.TEXT,
                        ),
                        weaviate_mod.classes.config.Property(
                            name="chunk_metadata",
                            data_type=weaviate_mod.classes.config.DataType.TEXT,
                        ),
                    ],
                )
        except Exception:
            # Collection already exists or connection issue — try to get it
            try:
                self._collections[name] = self._client.collections.get(name)
            except Exception:
                pass

    def _get_collection_for_zone(self, zone: DataZone) -> Any:
        """Haal de juiste collectie op voor een zone."""
        name = self._collection_name(zone)
        return self._collections.get(name)

    def _chunk_to_properties(self, chunk: DocumentChunk) -> dict[str, Any]:
        """Converteer DocumentChunk naar Weaviate properties."""
        import json

        props: dict[str, Any] = {
            "content": chunk.content,
            "zone": chunk.zone.value,
            "source_id": chunk.source_id or "",
            "created_at": chunk.created_at or "",
            "chunk_metadata": json.dumps(chunk.metadata_dict) if chunk.metadata else "{}",
        }
        return props

    def _properties_to_chunk(
        self,
        uuid: str,
        properties: dict[str, Any],
        zone: DataZone,
    ) -> DocumentChunk:
        """Converteer Weaviate properties naar DocumentChunk."""
        import json

        metadata_str = properties.get("chunk_metadata", "{}")
        try:
            metadata_dict = json.loads(metadata_str) if metadata_str else {}
        except (json.JSONDecodeError, TypeError):
            metadata_dict = {}

        metadata_tuples = tuple((k, str(v)) for k, v in metadata_dict.items())

        return DocumentChunk(
            chunk_id=str(uuid),
            content=properties.get("content", ""),
            zone=zone,
            metadata=metadata_tuples,
            source_id=properties.get("source_id", ""),
            created_at=properties.get("created_at", ""),
        )

    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Voeg een chunk toe aan de zone-collectie."""
        if self._tenant_strategy == TenantStrategy.PER_ZONE:
            collection = self._get_collection_for_zone(chunk.zone)
        else:
            # PER_KWP: gebruik eerste tenant of default
            collection = self._get_collection_for_zone(chunk.zone)

        if collection is None:
            raise ValueError(f"No collection found for zone {chunk.zone}")

        props = self._chunk_to_properties(chunk)
        kwargs: dict[str, Any] = {
            "uuid": chunk.chunk_id,
            "properties": props,
        }
        if chunk.embedding is not None:
            kwargs["vector"] = list(chunk.embedding)

        collection.data.insert(**kwargs)

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Voeg meerdere chunks toe, gegroepeerd per zone."""
        count = 0
        by_zone: dict[DataZone, list[DocumentChunk]] = {}
        for chunk in chunks:
            by_zone.setdefault(chunk.zone, []).append(chunk)

        for zone, zone_chunks in by_zone.items():
            collection = self._get_collection_for_zone(zone)
            if collection is None:
                continue

            with collection.batch.dynamic() as batch:
                for chunk in zone_chunks:
                    props = self._chunk_to_properties(chunk)
                    kwargs: dict[str, Any] = {
                        "uuid": chunk.chunk_id,
                        "properties": props,
                    }
                    if chunk.embedding is not None:
                        kwargs["vector"] = list(chunk.embedding)
                    batch.add_object(**kwargs)
                    count += 1

        return count

    def query(self, request: RetrievalRequest) -> RetrievalResponse:
        """Zoek chunks in zone-collecties via vector similarity."""
        start = time.monotonic()

        target_zones = [request.zone] if request.zone else list(self._zones)
        all_results: list[SearchResult] = []

        for zone in target_zones:
            collection = self._get_collection_for_zone(zone)
            if collection is None:
                continue

            try:
                if request.query_embedding is not None:
                    response = collection.query.near_vector(
                        near_vector=list(request.query_embedding),
                        limit=request.limit,
                        return_metadata=["distance"],
                    )
                elif request.query_text:
                    # Near-text requires a text2vec module; fall back to fetch all
                    # if not available. In production, embeddings should be provided.
                    response = collection.query.near_text(
                        query=request.query_text,
                        limit=request.limit,
                        return_metadata=["distance"],
                    )
                else:
                    continue

                for obj in response.objects:
                    # Weaviate distance: lower = closer. Convert to similarity score.
                    raw = obj.metadata.distance if obj.metadata else None
                    distance = raw if raw is not None else 0.0
                    score = max(0.0, min(1.0, 1.0 - distance))

                    if score < request.min_score:
                        continue

                    # Apply metadata filter if specified
                    if request.metadata_filter:
                        import json

                        md_str = obj.properties.get("chunk_metadata", "{}")
                        try:
                            md = json.loads(md_str) if md_str else {}
                        except (json.JSONDecodeError, TypeError):
                            md = {}
                        match = all(md.get(k) == v for k, v in request.metadata_filter)
                        if not match:
                            continue

                    chunk = self._properties_to_chunk(
                        uuid=str(obj.uuid),
                        properties=obj.properties,
                        zone=zone,
                    )
                    all_results.append(SearchResult(chunk=chunk, score=score))

            except Exception:
                continue

        all_results.sort(key=lambda r: r.score, reverse=True)
        limited = all_results[: request.limit]

        duration_ms = (time.monotonic() - start) * 1000

        return RetrievalResponse(
            results=tuple(limited),
            total_found=len(all_results),
            query_duration_ms=round(duration_ms, 2),
        )

    def count(self) -> int:
        """Tel totaal aantal chunks over alle collecties."""
        total = 0
        for collection in self._collections.values():
            try:
                result = collection.aggregate.over_all(total_count=True)
                total += result.total_count or 0
            except Exception:
                pass
        return total

    def count_by_zone(self) -> dict[DataZone, int]:
        """Tel chunks per zone."""
        counts: dict[DataZone, int] = {}
        for zone in self._zones:
            name = self._collection_name(zone)
            collection = self._collections.get(name)
            if collection is None:
                counts[zone] = 0
                continue
            try:
                result = collection.aggregate.over_all(total_count=True)
                counts[zone] = result.total_count or 0
            except Exception:
                counts[zone] = 0
        return counts

    def reset(self) -> None:
        """Wis alle data en herinitialiseer collecties."""
        for name in list(self._collections.keys()):
            try:
                self._client.collections.delete(name)
            except Exception:
                pass
        self._collections.clear()
        self._tenants.clear()
        self._ensure_collections()

    def ensure_tenant(self, tenant_id: str) -> None:
        """Registreer een tenant.

        Bij PER_ZONE: metadata-based tracking.
        Bij PER_KWP: maak aparte collectie voor de tenant.
        """
        if not tenant_id:
            raise ValueError("tenant_id is required")

        self._tenants.add(tenant_id)

        if self._tenant_strategy == TenantStrategy.PER_KWP:
            name = self._tenant_collection_name(tenant_id)
            if name not in self._collections:
                self._ensure_single_collection(name)

    def list_tenants(self) -> list[str]:
        """Lijst alle geregistreerde tenants."""
        return sorted(self._tenants)

    def health(self) -> VectorStoreHealth:
        """Retourneer gezondheidsstatus van de Weaviate backend."""
        try:
            is_ready = self._client.is_ready()
            if not is_ready:
                return VectorStoreHealth(
                    status="DOWN",
                    backend="weaviate",
                )

            total = self.count()
            return VectorStoreHealth(
                status="UP",
                backend="weaviate",
                collection_count=len(self._collections),
                total_chunks=total,
                tenant_count=len(self._tenants),
            )
        except Exception:
            return VectorStoreHealth(
                status="DOWN",
                backend="weaviate",
            )

    def close(self) -> None:
        """Sluit de Weaviate client verbinding."""
        if self._owns_client and self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass

    def __del__(self) -> None:
        if hasattr(self, "_owns_client"):
            self.close()
