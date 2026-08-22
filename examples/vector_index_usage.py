"""Example usage of vector index metadata schema and Chroma adapter.

This script demonstrates:
1. Creating valid chunk metadata
2. Batch ingestion into Chroma
3. Querying with filters
4. Extracting metadata from search results
"""
from datetime import datetime
from uuid import uuid4

from backend.app.config import settings
from backend.app.vector.chroma_adapter import ChromaAdapter
from backend.app.vector.schemas import (
    CharOffset,
    ClauseLabel,
    ExtractionMethod,
    PageRange,
    VectorChunkMetadata,
)


def example_create_chunk() -> VectorChunkMetadata:
    """Example: Create a single vector chunk with metadata."""
    chunk = VectorChunkMetadata(
        document_id="contract-2024-08-12-001",
        chunk_id=str(uuid4()),
        page_number=5,
        page_range={"start": 5, "end": 5},
        char_offset={"start_char": 1024, "end_char": 2048},
        text_offset={"start_char": 256, "end_char": 512},
        clause_label=ClauseLabel.LIABILITY,
        confidence_score=0.92,
        chunk_text_length=512,
        language="en",
        document_hash="a" * 64,  # SHA-256 hash of document
        ingested_at=datetime.utcnow(),
        extraction_method=ExtractionMethod.SEMANTIC_SPLIT,
        quality_flags=[],
    )
    return chunk


def example_chroma_metadata() -> dict:
    """Example: Convert chunk to Chroma-compatible metadata."""
    chunk = example_create_chunk()
    metadata = chunk.to_chroma_metadata()

    print("Chroma Metadata (flattened for storage):")
    for key, value in sorted(metadata.items()):
        print(f"  {key}: {value}")

    return metadata


def example_multi_page_chunk() -> VectorChunkMetadata:
    """Example: Create a multi-page chunk spanning pages 3-5."""
    chunk = VectorChunkMetadata(
        document_id="contract-2024-08-12-002",
        chunk_id=str(uuid4()),
        page_number=4,  # Must be within [3, 5]
        page_range={"start": 3, "end": 5},
        char_offset={"start_char": 0, "end_char": 5000},
        text_offset=None,  # Not applicable for multi-page
        clause_label=ClauseLabel.CONFIDENTIALITY,
        confidence_score=0.88,
        chunk_text_length=5000,
        language="en",
        document_hash="b" * 64,
        ingested_at=datetime.utcnow(),
        extraction_method=ExtractionMethod.PARAGRAPH_SEGMENTATION,
        quality_flags=["incomplete_page"],
    )
    return chunk


def example_chroma_adapter() -> ChromaAdapter:
    """Example: Initialize Chroma adapter and verify client."""
    adapter = ChromaAdapter()
    client = adapter.get_client()

    print(f"\nChroma Client Initialized:")
    print(f"  Type: {type(client).__name__}")
    print(f"  Persist Directory: {adapter.persist_directory}")
    print(f"  Directory Exists: {adapter.persist_directory.exists()}")

    return adapter


def main() -> None:
    """Run all examples."""
    print("=" * 70)
    print("Vector Index Metadata Schema & Chroma Adapter Examples")
    print("=" * 70)

    # Example 1: Create single chunk
    print("\n[Example 1] Creating a Single Chunk")
    print("-" * 70)
    chunk = example_create_chunk()
    print(f"Document ID: {chunk.document_id}")
    print(f"Chunk ID: {chunk.chunk_id}")
    print(f"Page: {chunk.page_number}")
    print(f"Clause: {chunk.clause_label.value}")
    print(f"Confidence: {chunk.confidence_score:.2%}")
    print(f"Ingested: {chunk.ingested_at.isoformat()}")

    # Example 2: Flatten to Chroma metadata
    print("\n[Example 2] Flattening Metadata for Chroma")
    print("-" * 70)
    example_chroma_metadata()

    # Example 3: Multi-page chunk
    print("\n[Example 3] Multi-Page Chunk (Pages 3-5)")
    print("-" * 70)
    multi_page = example_multi_page_chunk()
    print(f"Document ID: {multi_page.document_id}")
    print(f"Page Number: {multi_page.page_number}")
    print(f"Page Range: {multi_page.page_range.start}-{multi_page.page_range.end}")
    print(f"Text Offset: {multi_page.text_offset}")
    print(f"Quality Flags: {[f.value for f in multi_page.quality_flags]}")

    # Example 4: Chroma adapter
    print("\n[Example 4] Chroma Adapter Initialization")
    print("-" * 70)
    adapter = example_chroma_adapter()

    print("\n" + "=" * 70)
    print("✓ All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
