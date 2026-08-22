"""Tests for idempotent contract chunk upserts."""

from datetime import datetime, timezone
from pathlib import Path

from backend.app.vector.chroma_adapter import ChromaAdapter
from backend.app.vector.client import create_chroma_client, get_or_create_collection
from backend.app.vector.schemas import (
    CharOffset,
    ClauseLabel,
    ExtractionMethod,
    PageRange,
    VectorChunkMetadata,
)


def _metadata(chunk_id: str, *, page: int = 2) -> VectorChunkMetadata:
    """Build valid metadata for a test chunk."""
    return VectorChunkMetadata(
        document_id="document-12345678",
        chunk_id=chunk_id,
        page_number=page,
        page_range=PageRange(start=page, end=page),
        char_offset=CharOffset(start_char=100, end_char=180),
        text_offset=CharOffset(start_char=20, end_char=100),
        clause_label=ClauseLabel.CONFIDENTIALITY,
        confidence_score=0.95,
        chunk_text_length=80,
        document_hash="a" * 64,
        ingested_at=datetime.now(timezone.utc),
        extraction_method=ExtractionMethod.PDF_TEXT_EXTRACTION,
    )


def test_upsert_chunks_stores_metadata_and_is_idempotent(tmp_path: Path) -> None:
    """Repeated upserts with the same chunk IDs must not create duplicates."""
    client = create_chroma_client(persist_directory=tmp_path / "chroma")
    collection = get_or_create_collection(client, "upsert_test_collection")
    adapter = ChromaAdapter(persist_directory=tmp_path / "adapter")
    text_chunks = [
        "The parties must keep contract information confidential.",
        "Confidential information may only be used for the agreement.",
    ]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    metadata = [
        _metadata("chunk-1234567890"),
        _metadata("chunk-8765432109", page=3),
    ]

    submitted_ids = adapter.upsert_chunks(collection, text_chunks, embeddings, metadata)
    stored = collection.get(ids=submitted_ids, include=["documents", "metadatas"])

    assert submitted_ids == ["chunk-1234567890", "chunk-8765432109"]
    assert collection.count() == 2
    assert stored["documents"] == text_chunks
    assert stored["metadatas"][0]["document_id"] == "document-12345678"
    assert stored["metadatas"][0]["clause_label"] == "confidentiality"
    assert stored["metadatas"][0]["char_offset_start"] == 100

    adapter.upsert_chunks(collection, text_chunks, embeddings, metadata)

    assert collection.count() == 2
    assert collection.get(ids=submitted_ids)["ids"] == submitted_ids
