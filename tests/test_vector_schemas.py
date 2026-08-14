"""Tests for vector index metadata schemas.

Validates all Pydantic models conform to business rules and
support required filtering and serialization operations.
"""
from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.vector.schemas import (
    CharOffset,
    ClauseLabel,
    ExtractionMethod,
    PageRange,
    QualityFlag,
    ReviewStatus,
    VectorChunkBatch,
    VectorChunkMetadata,
    VectorSearchQuery,
)


class TestCharOffset:
    """Test CharOffset model validation."""

    def test_valid_char_offset(self) -> None:
        """Valid char offset should construct successfully."""
        offset = CharOffset(start_char=100, end_char=200)
        assert offset.start_char == 100
        assert offset.end_char == 200

    def test_char_offset_unpacking(self) -> None:
        """CharOffset should support tuple-like unpacking."""
        offset = CharOffset(start_char=100, end_char=200)
        start, end = offset
        assert start == 100
        assert end == 200

    def test_char_offset_indexing(self) -> None:
        """CharOffset should support indexing like a tuple."""
        offset = CharOffset(start_char=100, end_char=200)
        assert offset[0] == 100
        assert offset[1] == 200

    def test_char_offset_zero_start(self) -> None:
        """start_char=0 should be valid (beginning of document)."""
        offset = CharOffset(start_char=0, end_char=100)
        assert offset.start_char == 0

    def test_char_offset_end_must_exceed_start(self) -> None:
        """end_char must be > start_char."""
        with pytest.raises(ValidationError):
            CharOffset(start_char=100, end_char=100)

        with pytest.raises(ValidationError):
            CharOffset(start_char=100, end_char=50)

    def test_char_offset_negative_start_rejected(self) -> None:
        """Negative start_char should be rejected."""
        with pytest.raises(ValidationError):
            CharOffset(start_char=-1, end_char=100)


class TestPageRange:
    """Test PageRange model validation."""

    def test_valid_page_range(self) -> None:
        """Valid page range should construct successfully."""
        page_range = PageRange(start=3, end=5)
        assert page_range.start == 3
        assert page_range.end == 5

    def test_page_range_single_page(self) -> None:
        """Single-page chunk should have start == end."""
        page_range = PageRange(start=5, end=5)
        assert page_range.is_single_page is True

    def test_page_range_multi_page(self) -> None:
        """Multi-page chunk should have start < end."""
        page_range = PageRange(start=3, end=7)
        assert page_range.is_single_page is False

    def test_page_range_unpacking(self) -> None:
        """PageRange should support tuple-like unpacking."""
        page_range = PageRange(start=3, end=5)
        start, end = page_range
        assert start == 3
        assert end == 5

    def test_page_range_indexing(self) -> None:
        """PageRange should support indexing like a tuple."""
        page_range = PageRange(start=3, end=5)
        assert page_range[0] == 3
        assert page_range[1] == 5

    def test_page_range_must_be_positive(self) -> None:
        """Page numbers must be >= 1."""
        with pytest.raises(ValidationError):
            PageRange(start=0, end=5)

        with pytest.raises(ValidationError):
            PageRange(start=3, end=0)

    def test_page_range_end_must_exceed_start(self) -> None:
        """end must be >= start."""
        with pytest.raises(ValidationError):
            PageRange(start=5, end=3)


class TestEnums:
    """Test enum definitions."""

    def test_clause_label_values(self) -> None:
        """ClauseLabel should include all expected categories."""
        assert ClauseLabel.LIABILITY.value == "liability"
        assert ClauseLabel.CONFIDENTIALITY.value == "confidentiality"
        assert ClauseLabel.GOVERNING_LAW.value == "governing_law"
        assert ClauseLabel.GENERAL.value == "general"

    def test_extraction_method_values(self) -> None:
        """ExtractionMethod should include expected methods."""
        assert ExtractionMethod.PDF_TEXT_EXTRACTION.value == "pdf_text_extraction"
        assert ExtractionMethod.SEMANTIC_SPLIT.value == "semantic_split"
        assert ExtractionMethod.OCR.value == "ocr"

    def test_review_status_values(self) -> None:
        """ReviewStatus should include expected statuses."""
        assert ReviewStatus.UNREVIEWED.value == "unreviewed"
        assert ReviewStatus.APPROVED.value == "approved"
        assert ReviewStatus.FLAGGED.value == "flagged"
        assert ReviewStatus.REJECTED.value == "rejected"

    def test_quality_flag_values(self) -> None:
        """QualityFlag should include expected flags."""
        assert QualityFlag.HIGH_OCR_ERROR_RATE.value == "high_ocr_error_rate"
        assert QualityFlag.INCOMPLETE_PAGE.value == "incomplete_page"
        assert QualityFlag.DUPLICATE_CONTENT.value == "duplicate_content"


class TestVectorChunkMetadata:
    """Test VectorChunkMetadata model validation and behavior."""

    @staticmethod
    def create_valid_chunk(
        document_id: str = "550e8400-e29b-41d4-a716-446655440000",
        chunk_id: str = "7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
        **overrides,
    ) -> VectorChunkMetadata:
        """Helper to create valid chunk with optional overrides."""
        defaults = {
            "document_id": document_id,
            "chunk_id": chunk_id,
            "page_number": 5,
            "page_range": {"start": 5, "end": 5},
            "char_offset": {"start_char": 1024, "end_char": 2048},
            "clause_label": ClauseLabel.LIABILITY,
            "confidence_score": 0.92,
            "chunk_text_length": 512,
            "language": "en",
            "document_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "ingested_at": datetime.fromisoformat("2024-08-12T14:30:45.123456+00:00"),
            "extraction_method": ExtractionMethod.SEMANTIC_SPLIT,
        }
        defaults.update(overrides)
        return VectorChunkMetadata(**defaults)

    def test_valid_chunk_metadata(self) -> None:
        """Valid chunk metadata should construct successfully."""
        chunk = self.create_valid_chunk()
        assert chunk.document_id == "550e8400-e29b-41d4-a716-446655440000"
        assert chunk.chunk_id == "7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8"
        assert chunk.clause_label == ClauseLabel.LIABILITY
        assert chunk.confidence_score == 0.92

    def test_chunk_defaults(self) -> None:
        """Optional fields should have sensible defaults."""
        chunk = self.create_valid_chunk()
        assert chunk.language == "en"
        assert chunk.quality_flags == []
        assert chunk.review_status == ReviewStatus.UNREVIEWED

    def test_chunk_page_number_must_be_in_range(self) -> None:
        """page_number must be within page_range."""
        with pytest.raises(ValidationError) as exc_info:
            self.create_valid_chunk(
                page_number=10, page_range={"start": 3, "end": 5}
            )
        assert "page_number" in str(exc_info.value).lower()

    def test_chunk_page_number_at_start_valid(self) -> None:
        """page_number can equal page_range.start."""
        chunk = self.create_valid_chunk(
            page_number=3, page_range={"start": 3, "end": 5}
        )
        assert chunk.page_number == 3

    def test_chunk_page_number_at_end_valid(self) -> None:
        """page_number can equal page_range.end."""
        chunk = self.create_valid_chunk(
            page_number=5, page_range={"start": 3, "end": 5}
        )
        assert chunk.page_number == 5

    def test_chunk_text_offset_single_page_only(self) -> None:
        """text_offset is only valid for single-page chunks."""
        # Valid: single-page chunk with text_offset
        chunk = self.create_valid_chunk(
            page_range={"start": 5, "end": 5},
            text_offset={"start_char": 100, "end_char": 200},
        )
        assert chunk.text_offset is not None

        # Invalid: multi-page chunk with text_offset
        with pytest.raises(ValidationError) as exc_info:
            self.create_valid_chunk(
                page_range={"start": 3, "end": 5},
                text_offset={"start_char": 100, "end_char": 200},
            )
        assert "text_offset" in str(exc_info.value).lower()

    def test_chunk_text_offset_optional_for_multipage(self) -> None:
        """Multi-page chunks should allow text_offset=None."""
        chunk = self.create_valid_chunk(
            page_range={"start": 3, "end": 5}, text_offset=None
        )
        assert chunk.text_offset is None

    def test_chunk_confidence_score_range(self) -> None:
        """confidence_score must be between 0.0 and 1.0."""
        chunk = self.create_valid_chunk(confidence_score=0.0)
        assert chunk.confidence_score == 0.0

        chunk = self.create_valid_chunk(confidence_score=1.0)
        assert chunk.confidence_score == 1.0

        with pytest.raises(ValidationError):
            self.create_valid_chunk(confidence_score=-0.1)

        with pytest.raises(ValidationError):
            self.create_valid_chunk(confidence_score=1.1)

    def test_chunk_low_confidence_warning(self) -> None:
        """Low confidence scores should trigger a warning."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.create_valid_chunk(confidence_score=0.60)
            assert len(w) == 1
            assert "low confidence" in str(w[0].message).lower()

    def test_chunk_document_hash_must_be_sha256(self) -> None:
        """document_hash must be 64 hex characters (SHA-256)."""
        # Valid 64-char hash
        chunk = self.create_valid_chunk(
            document_hash="a" * 64
        )
        assert len(chunk.document_hash) == 64

        # Invalid: too short
        with pytest.raises(ValidationError):
            self.create_valid_chunk(document_hash="a" * 63)

        # Invalid: too long
        with pytest.raises(ValidationError):
            self.create_valid_chunk(document_hash="a" * 65)

    def test_chunk_chunk_text_length_must_be_positive(self) -> None:
        """chunk_text_length must be > 0."""
        with pytest.raises(ValidationError):
            self.create_valid_chunk(chunk_text_length=0)

        with pytest.raises(ValidationError):
            self.create_valid_chunk(chunk_text_length=-1)

    def test_chunk_to_chroma_metadata(self) -> None:
        """to_chroma_metadata should flatten nested objects."""
        chunk = self.create_valid_chunk(
            quality_flags=[QualityFlag.HIGH_OCR_ERROR_RATE]
        )
        metadata = chunk.to_chroma_metadata()

        assert metadata["document_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert metadata["page_range_start"] == 5
        assert metadata["page_range_end"] == 5
        assert metadata["char_offset_start"] == 1024
        assert metadata["char_offset_end"] == 2048
        assert metadata["clause_label"] == "liability"
        assert metadata["quality_flags"] == ["high_ocr_error_rate"]
        assert metadata["review_status"] == "unreviewed"

    def test_chunk_to_chroma_metadata_with_text_offset(self) -> None:
        """to_chroma_metadata should include text_offset when present."""
        chunk = self.create_valid_chunk(
            text_offset={"start_char": 200, "end_char": 300}
        )
        metadata = chunk.to_chroma_metadata()

        assert metadata["text_offset_start"] == 200
        assert metadata["text_offset_end"] == 300

    def test_chunk_to_chroma_metadata_without_text_offset(self) -> None:
        """to_chroma_metadata should set text_offset to None when absent."""
        chunk = self.create_valid_chunk(text_offset=None)
        metadata = chunk.to_chroma_metadata()

        assert metadata["text_offset_start"] is None
        assert metadata["text_offset_end"] is None


class TestVectorChunkBatch:
    """Test VectorChunkBatch model for bulk ingestion."""

    def test_valid_batch(self) -> None:
        """Valid batch should construct successfully."""
        chunk = VectorChunkMetadata(
            document_id="550e8400-e29b-41d4-a716-446655440000",
            chunk_id="7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
            page_number=5,
            page_range={"start": 5, "end": 5},
            char_offset={"start_char": 1024, "end_char": 2048},
            clause_label=ClauseLabel.LIABILITY,
            confidence_score=0.92,
            chunk_text_length=512,
            language="en",
            document_hash="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            ingested_at=datetime.fromisoformat("2024-08-12T14:30:45.123456+00:00"),
            extraction_method=ExtractionMethod.SEMANTIC_SPLIT,
        )
        batch = VectorChunkBatch(chunks=[chunk])
        assert len(batch.chunks) == 1

    def test_batch_min_items(self) -> None:
        """Batch must contain at least 1 chunk."""
        with pytest.raises(ValidationError):
            VectorChunkBatch(chunks=[])

    def test_batch_dry_run_flag(self) -> None:
        """Batch should support dry_run flag."""
        chunk = VectorChunkMetadata(
            document_id="550e8400-e29b-41d4-a716-446655440000",
            chunk_id="7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
            page_number=5,
            page_range={"start": 5, "end": 5},
            char_offset={"start_char": 1024, "end_char": 2048},
            clause_label=ClauseLabel.LIABILITY,
            confidence_score=0.92,
            chunk_text_length=512,
            language="en",
            document_hash="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            ingested_at=datetime.fromisoformat("2024-08-12T14:30:45.123456+00:00"),
            extraction_method=ExtractionMethod.SEMANTIC_SPLIT,
        )
        batch = VectorChunkBatch(chunks=[chunk], dry_run=True)
        assert batch.dry_run is True


class TestVectorSearchQuery:
    """Test VectorSearchQuery model for search filtering."""

    def test_valid_search_query(self) -> None:
        """Valid search query should construct successfully."""
        query = VectorSearchQuery(
            query_embedding=[0.0] * 768,
            n_results=10,
        )
        assert len(query.query_embedding) == 768
        assert query.n_results == 10

    def test_search_query_embedding_size(self) -> None:
        """query_embedding must be exactly 768 dimensions."""
        with pytest.raises(ValidationError):
            VectorSearchQuery(
                query_embedding=[0.0] * 767,  # Too short
                n_results=10,
            )

        with pytest.raises(ValidationError):
            VectorSearchQuery(
                query_embedding=[0.0] * 769,  # Too long
                n_results=10,
            )

    def test_search_query_n_results_bounds(self) -> None:
        """n_results must be between 1 and 100."""
        query = VectorSearchQuery(
            query_embedding=[0.0] * 768, n_results=1
        )
        assert query.n_results == 1

        query = VectorSearchQuery(
            query_embedding=[0.0] * 768, n_results=100
        )
        assert query.n_results == 100

        with pytest.raises(ValidationError):
            VectorSearchQuery(
                query_embedding=[0.0] * 768, n_results=0
            )

        with pytest.raises(ValidationError):
            VectorSearchQuery(
                query_embedding=[0.0] * 768, n_results=101
            )

    def test_search_query_optional_filters(self) -> None:
        """Optional filters should be None by default."""
        query = VectorSearchQuery(
            query_embedding=[0.0] * 768,
        )
        assert query.document_id is None
        assert query.clause_labels is None
        assert query.min_confidence is None

    def test_search_query_clause_labels_filter(self) -> None:
        """clause_labels should filter results by clause type."""
        query = VectorSearchQuery(
            query_embedding=[0.0] * 768,
            clause_labels=[ClauseLabel.LIABILITY, ClauseLabel.CONFIDENTIALITY],
        )
        assert len(query.clause_labels) == 2
        assert ClauseLabel.LIABILITY in query.clause_labels

    def test_search_query_min_confidence_filter(self) -> None:
        """min_confidence should filter by confidence threshold."""
        query = VectorSearchQuery(
            query_embedding=[0.0] * 768,
            min_confidence=0.85,
        )
        assert query.min_confidence == 0.85

    def test_search_query_only_approved_default(self) -> None:
        """only_approved should default to True."""
        query = VectorSearchQuery(
            query_embedding=[0.0] * 768,
        )
        assert query.only_approved is True
