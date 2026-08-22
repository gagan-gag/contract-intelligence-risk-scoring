"""Semantic search HTTP endpoint for contract chunks."""

from __future__ import annotations

import os
from typing import Any, Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.vector.chroma_adapter import ChromaAdapter
from app.vector.client import create_chroma_client, get_or_create_collection
from app.vector.embeddings import EmbeddingAdapter
from app.vector.schemas import ClauseLabel

router = APIRouter(tags=["search"])


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
