"""Tests for semantic contract chunk retrieval."""

from pathlib import Path

from backend.app.vector.chroma_adapter import ChromaAdapter
from backend.app.vector.client import create_chroma_client, get_or_create_collection


class FixtureEmbeddingAdapter:
    """Deterministic embedding adapter for the known query fixture."""

    def encode(self, text: str) -> list[float]:
        assert text == "confidentiality obligations"
        return [1.0, 0.0, 0.0]


def test_semantic_search_retrieves_relevant_chunk_with_metadata(tmp_path: Path) -> None:
    """The nearest fixture chunk should be returned with its metadata."""
    client = create_chroma_client(persist_directory=tmp_path / "chroma")
    collection = get_or_create_collection(client, "semantic_query_test_collection")
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

    results = ChromaAdapter.semantic_search(
        collection,
        "confidentiality obligations",
        FixtureEmbeddingAdapter(),
        top_k=1,
        where={"document_id": "contract-fixture-001"},
    )

    assert results["ids"] == [["confidentiality-chunk"]]
    assert results["documents"] == [
        ["The receiving party shall protect confidential information."]
    ]
    assert results["metadatas"][0][0]["clause_label"] == "confidentiality"
    assert results["metadatas"][0][0]["page_number"] == 4
    assert results["metadatas"][0][0]["char_offset_start"] == 800
