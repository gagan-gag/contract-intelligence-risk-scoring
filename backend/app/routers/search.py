"""Semantic search HTTP endpoint for contract chunks."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.vector.chroma_adapter import ChromaAdapter
from app.vector.client import create_chroma_client, get_or_create_collection
from app.vector.embeddings import EmbeddingAdapter
from app.vector.schemas import (
    CharOffset,
    ClauseLabel,
    ExtractionMethod,
    PageRange,
    VectorChunkMetadata,
)

router = APIRouter(tags=["search"])

DEFAULT_SAMPLE_CHUNKS = [
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0001",
        "Vendor shall defend, indemnify, and hold harmless Customer, its affiliates, directors, and employees against any and all third-party claims, liabilities, losses, damages, and costs arising out of any breach of warranty or intellectual property infringement without limitation of liability.",
        ClauseLabel.LIABILITY,
    ),
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0002",
        "This Agreement shall automatically renew for additional successive twelve (12) month terms unless either party provides written notice of non-renewal at least ninety (90) days prior to the expiration of the then-current term.",
        ClauseLabel.TERM_TERMINATION,
    ),
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0003",
        "Either party may terminate this Agreement for convenience without cause by providing thirty (30) days prior written notice, provided all outstanding service fees through the termination date are paid in full.",
        ClauseLabel.TERM_TERMINATION,
    ),
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0004",
        "Except for indemnification obligations and breach of confidentiality, neither party's aggregate liability arising under or in connection with this Agreement shall exceed the total fees paid in the twelve (12) months preceding the claim.",
        ClauseLabel.LIABILITY,
    ),
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0005",
        "Recipient agrees to retain all Proprietary Information in strict confidence and shall not disclose such information to any third party for a period of five (5) years following termination or expiration of this Agreement.",
        ClauseLabel.CONFIDENTIALITY,
    ),
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0006",
        "This Agreement shall be governed by and construed in accordance with the substantive laws of the State of Delaware, without giving effect to any choice of law principles.",
        ClauseLabel.GOVERNING_LAW,
    ),
    (
        "contract-2026-sample-001",
        "contract-2026-sample-001-0007",
        "Provider warrants that the Services will be performed in a professional and workmanlike manner consistent with prevailing legal industry standards.",
        ClauseLabel.WARRANTIES,
    ),
]


class SearchResult(BaseModel):
    """Serialized semantic search result returned to API clients."""

    chunk_id: str = Field(description="Stable Chroma ID for the matching chunk")
    document_id: str = Field(description="Source contract document ID")
    chunk_text: str = Field(description="Original text stored for the chunk")
    distance: float = Field(ge=0.0, description="Chroma distance; lower is more similar")
    metadata: dict[str, Any] = Field(description="Flattened chunk metadata")


class SearchResponse(BaseModel):
    """Response envelope for a semantic search request."""

    query: str = Field(description="Normalized search text")
    top_k: int = Field(ge=1, description="Maximum number of requested results")
    results: list[SearchResult] = Field(description="Nearest matching contract chunks")


def _ensure_seeded_collection(collection: Any, adapter: ChromaAdapter, embedding_adapter: EmbeddingAdapter) -> None:
    """Seed sample chunks if default collection is currently empty."""
    try:
        # Only seed the default contract_chunks collection
        if hasattr(collection, "name") and collection.name == "contract_chunks" and collection.count() == 0:
            text_chunks = [item[2] for item in DEFAULT_SAMPLE_CHUNKS]
            metadata_list = [
                VectorChunkMetadata(
                    document_id=item[0],
                    chunk_id=item[1],
                    page_number=1,
                    page_range=PageRange(start=1, end=1),
                    char_offset=CharOffset(start_char=0, end_char=len(item[2])),
                    clause_label=item[3],
                    confidence_score=0.95,
                    chunk_text_length=len(item[2]),
                    document_hash="seed-sample-hash",
                    ingested_at=datetime.now(timezone.utc),
                    extraction_method=ExtractionMethod.PARAGRAPH_SEGMENTATION,
                )
                for item in DEFAULT_SAMPLE_CHUNKS
            ]
            embeddings = embedding_adapter.encode(text_chunks)
            adapter.upsert_chunks(collection, text_chunks, embeddings, metadata_list)
    except Exception:
        pass


def get_search_collection() -> Any:
    """Resolve the configured local Chroma collection for a request."""
    adapter = ChromaAdapter()
    client = create_chroma_client(persist_directory=adapter.persist_directory)
    collection_name = os.getenv("VECTOR_COLLECTION_NAME", "contract_chunks")
    return get_or_create_collection(client, collection_name)


def get_search_embedding_adapter() -> EmbeddingAdapter:
    """Resolve the configured embedding adapter lazily for a request."""
    return EmbeddingAdapter()


def _build_where_filter(
    document_id: str | None,
    clause_label: ClauseLabel | None,
) -> dict[str, Any] | None:
    """Build a Chroma filter from the supported query parameters."""
    filters: list[dict[str, str]] = []
    if document_id is not None:
        filters.append({"document_id": document_id})
    if clause_label is not None:
        filters.append({"clause_label": clause_label.value})

    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def _serialize_results(raw_results: dict[str, Any]) -> list[SearchResult]:
    """Convert Chroma's grouped query response into API response models."""
    ids = raw_results.get("ids", [[]])[0]
    documents = raw_results.get("documents", [[]])[0]
    metadatas = raw_results.get("metadatas", [[]])[0]
    distances = raw_results.get("distances", [[]])[0]

    results: list[SearchResult] = []
    for index, chunk_id in enumerate(ids):
        metadata = metadatas[index] or {}
        results.append(
            SearchResult(
                chunk_id=chunk_id,
                document_id=str(metadata.get("document_id", "")),
                chunk_text=documents[index],
                distance=float(distances[index]),
                metadata=metadata,
            )
        )
    return results


@router.get("/search", response_model=SearchResponse, summary="Search contract chunks")
def search_chunks(
    query: Annotated[
        str,
        Query(min_length=1, max_length=2000, description="Natural-language search text"),
    ],
    top_k: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of results to return"),
    ] = 5,
    document_id: Annotated[
        str | None,
        Query(
            min_length=16,
            max_length=36,
            pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{15,35}$",
            description="Filter by contract ID (16-36 alphanumeric characters, hyphens, or underscores)",
        ),
    ] = None,
    clause_label: Annotated[
        ClauseLabel | None,
        Query(description="Filter by clause classification"),
    ] = None,
    collection: Any = Depends(get_search_collection),
    embedding_adapter: EmbeddingAdapter = Depends(get_search_embedding_adapter),
) -> SearchResponse:
    """Return the nearest contract chunks for a natural-language query."""
    normalized_query = query.strip()
    
    # Auto-seed default collection if empty
    _ensure_seeded_collection(collection, ChromaAdapter(), embedding_adapter)

    raw_results = ChromaAdapter.semantic_search(
        collection,
        normalized_query,
        embedding_adapter,
        top_k=top_k,
        where=_build_where_filter(document_id, clause_label),
    )
    
    return SearchResponse(
        query=normalized_query,
        top_k=top_k,
        results=_serialize_results(raw_results),
    )


__all__ = [
    "SearchResponse",
    "SearchResult",
    "get_search_collection",
    "get_search_embedding_adapter",
    "router",
    "search_chunks",
]
