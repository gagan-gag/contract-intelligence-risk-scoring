"""Tests for the FastAPI semantic search endpoint."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routers.search import (
    _build_where_filter,
    get_search_collection,
    get_search_embedding_adapter,
)
from app.vector.client import create_chroma_client, get_or_create_collection
from app.vector.schemas import ClauseLabel


class FixtureEmbeddingAdapter:
    """Deterministic adapter matching the known query fixture."""

    def encode(self, text: str) -> list[float]:
        assert text == "confidentiality obligations"
        return [1.0, 0.0, 0.0]


def test_search_endpoint_returns_filtered_semantic_results(tmp_path: Path) -> None:
    """GET /search should return the nearest chunk and serialized metadata."""
    client = create_chroma_client(persist_directory=tmp_path / "chroma")
    collection = get_or_create_collection(client, "search_router_test_collection")
    collection.upsert(
        ids=["confidentiality-chunk", "payment-chunk"],
        embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        documents=[
            "The receiving party shall protect confidential information.",
            "The customer shall pay invoices within thirty days.",
        ],
        metadatas=[
            {
                "document_id": "contract-fixture-001",
                "chunk_id": "confidentiality-chunk",
                "page_number": 4,
                "clause_label": "confidentiality",
                "char_offset_start": 800,
                "char_offset_end": 875,
            },
            {
                "document_id": "contract-fixture-001",
                "chunk_id": "payment-chunk",
                "page_number": 7,
                "clause_label": "consideration",
                "char_offset_start": 1400,
                "char_offset_end": 1470,
            },
        ],
    )

    app.dependency_overrides[get_search_collection] = lambda: collection
    app.dependency_overrides[get_search_embedding_adapter] = FixtureEmbeddingAdapter
    try:
        response = TestClient(app).get(
            "/search",
            params={
                "query": "  confidentiality obligations  ",
                "top_k": 1,
                "document_id": "contract-fixture-001",
                "clause_label": "confidentiality",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "query": "confidentiality obligations",
        "top_k": 1,
        "results": [
            {
                "chunk_id": "confidentiality-chunk",
                "document_id": "contract-fixture-001",
                "chunk_text": "The receiving party shall protect confidential information.",
                "distance": 0.0,
                "metadata": {
                    "document_id": "contract-fixture-001",
                    "chunk_id": "confidentiality-chunk",
                    "page_number": 4,
                    "clause_label": "confidentiality",
                    "char_offset_start": 800,
                    "char_offset_end": 875,
                },
            }
        ],
    }


def test_search_endpoint_returns_empty_results_when_filter_matches_nothing(
    tmp_path: Path,
) -> None:
    """A valid query with no matching vectors should return an empty result list."""
    client = create_chroma_client(persist_directory=tmp_path / "chroma")
    collection = get_or_create_collection(client, "search_no_results_collection")
    collection.upsert(
        ids=["confidentiality-chunk"],
        embeddings=[[1.0, 0.0, 0.0]],
        documents=["The receiving party shall protect confidential information."],
        metadatas=[
            {
                "document_id": "contract-fixture-001",
                "chunk_id": "confidentiality-chunk",
                "page_number": 4,
                "clause_label": "confidentiality",
            }
        ],
    )

    app.dependency_overrides[get_search_collection] = lambda: collection
    app.dependency_overrides[get_search_embedding_adapter] = FixtureEmbeddingAdapter
    try:
        response = TestClient(app).get(
            "/search",
            params={
                "query": "confidentiality obligations",
                "document_id": "missing-contract-01",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "query": "confidentiality obligations",
        "top_k": 5,
        "results": [],
    }


def test_search_endpoint_validates_query_parameters() -> None:
    """Invalid query text and top_k values should return validation errors."""
    client = TestClient(app)
    app.dependency_overrides[get_search_embedding_adapter] = FixtureEmbeddingAdapter
    try:
        assert client.get("/search", params={"query": "", "top_k": 5}).status_code == 422
        assert client.get("/search", params={"query": "contract", "top_k": 0}).status_code == 422
        assert client.get("/search", params={"query": "contract", "top_k": 101}).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_search_endpoint_rejects_missing_and_malformed_query_parameters() -> None:
    """Missing query text and malformed top_k values should return 422 details."""
    client = TestClient(app)
    app.dependency_overrides[get_search_collection] = lambda: None
    app.dependency_overrides[get_search_embedding_adapter] = FixtureEmbeddingAdapter
    try:
        missing_query = client.get("/search", params={"top_k": 5})
        malformed_top_k = client.get(
            "/search",
            params={"query": "contract", "top_k": "not-an-integer"},
        )
    finally:
        app.dependency_overrides.clear()

    assert missing_query.status_code == 422
    assert any(error["loc"][-1] == "query" for error in missing_query.json()["detail"])
    assert malformed_top_k.status_code == 422
    assert any(
        error["loc"][-1] == "top_k"
        for error in malformed_top_k.json()["detail"]
    )


def test_build_where_filter_supports_document_and_clause_filters() -> None:
    """Supported metadata filters should produce valid Chroma predicates."""
    assert _build_where_filter("contract-fixture-001", None) == {
        "document_id": "contract-fixture-001"
    }
    assert _build_where_filter(None, ClauseLabel.CONFIDENTIALITY) == {
        "clause_label": "confidentiality"
    }
    assert _build_where_filter(
        "contract-fixture-001",
        ClauseLabel.CONFIDENTIALITY,
    ) == {
        "$and": [
            {"document_id": "contract-fixture-001"},
            {"clause_label": "confidentiality"},
        ]
    }
    assert _build_where_filter(None, None) is None


def test_search_endpoint_rejects_malformed_metadata_filters() -> None:
    """Malformed filter values should return clear FastAPI validation errors."""
    client = TestClient(app)
    app.dependency_overrides[get_search_collection] = lambda: None
    app.dependency_overrides[get_search_embedding_adapter] = FixtureEmbeddingAdapter
    try:
        invalid_document = client.get(
            "/search",
            params={"query": "contract", "document_id": "bad id"},
        )
        invalid_clause = client.get(
            "/search",
            params={"query": "contract", "clause_label": "not_a_clause"},
        )
    finally:
        app.dependency_overrides.clear()

    assert invalid_document.status_code == 422
    assert any(
        error["loc"][-1] == "document_id"
        for error in invalid_document.json()["detail"]
    )
    assert invalid_clause.status_code == 422
    assert any(
        error["loc"][-1] == "clause_label"
        for error in invalid_clause.json()["detail"]
    )
