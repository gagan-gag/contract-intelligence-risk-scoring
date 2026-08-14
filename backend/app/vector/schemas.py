"""Vector index metadata schemas for Chroma storage.

This module defines Pydantic models for all metadata associated with
contract chunks stored in the Chroma vector database. These schemas
enforce type safety, validation, and documentation at ingestion time.

Reference: docs/vector_index_contract.md
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ClauseLabel(str, Enum):
    """Enumeration of valid contract clause categories.

    These labels classify chunks into semantic categories for
    filtering, risk scoring, and downstream NLP tasks.
    """

    PARTIES = "parties"
    CONSIDERATION = "consideration"
    TERM_TERMINATION = "term_termination"
    LIABILITY = "liability"
    CONFIDENTIALITY = "confidentiality"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    WARRANTIES = "warranties"
    FORCE_MAJEURE = "force_majeure"
    ASSIGNMENT = "assignment"
    COMPLIANCE = "compliance"
    GENERAL = "general"


class ExtractionMethod(str, Enum):
    """Methods for extracting text chunks from source documents."""

    PDF_TEXT_EXTRACTION = "pdf_text_extraction"
    OCR = "ocr"
    MANUAL_ANNOTATION = "manual_annotation"
    PARAGRAPH_SEGMENTATION = "paragraph_segmentation"
    SEMANTIC_SPLIT = "semantic_split"


class ReviewStatus(str, Enum):
    """Quality assurance review status for individual chunks."""

    UNREVIEWED = "unreviewed"
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class QualityFlag(str, Enum):
    """Flags indicating potential data quality issues in chunks."""

    HIGH_OCR_ERROR_RATE = "high_ocr_error_rate"
    INCOMPLETE_PAGE = "incomplete_page"
    ENCODING_MISMATCH = "encoding_mismatch"
    DUPLICATE_CONTENT = "duplicate_content"
    CONFIDENTIALITY_REDACTED = "confidentiality_redacted"
    AUTO_GENERATED_TEXT = "auto_generated_text"


class CharOffset(BaseModel):
    """Character offset range within a document or page."""

    start_char: int = Field(
        ge=0,
        description="Zero-indexed start character position",
    )
    end_char: int = Field(
        gt=0,
        description="Zero-indexed end character position (exclusive)",
    )

    @field_validator("end_char")
    @classmethod
    def validate_end_after_start(cls, v: int, info) -> int:
        """Ensure end_char > start_char."""
        if "start_char" in info.data and v <= info.data["start_char"]:
            raise ValueError("end_char must be > start_char")
        return v

    def __iter__(self):
        """Allow unpacking as tuple: start_char, end_char = offset."""
        return iter((self.start_char, self.end_char))

    def __getitem__(self, index: int) -> int:
        """Allow tuple-like indexing."""
        if index == 0:
            return self.start_char
        elif index == 1:
            return self.end_char
        raise IndexError("offset index out of range")


class PageRange(BaseModel):
    """Page number range for multi-page chunks."""

    start: int = Field(
        ge=1,
        description="Starting page number (1-indexed, inclusive)",
    )
    end: int = Field(
        ge=1,
        description="Ending page number (1-indexed, inclusive)",
    )

    @field_validator("end")
    @classmethod
    def validate_end_after_start(cls, v: int, info) -> int:
        """Ensure end >= start."""
        if "start" in info.data and v < info.data["start"]:
            raise ValueError("end must be >= start")
        return v

    def __iter__(self):
        """Allow unpacking as tuple: start, end = page_range."""
        return iter((self.start, self.end))

    def __getitem__(self, index: int) -> int:
        """Allow tuple-like indexing."""
        if index == 0:
            return self.start
        elif index == 1:
            return self.end
        raise IndexError("page range index out of range")

    @property
    def is_single_page(self) -> bool:
        """Return True if chunk spans only one page."""
        return self.start == self.end


class VectorChunkMetadata(BaseModel):
    """Complete metadata for a contract chunk in the vector database.

    This is the canonical schema for all chunks stored in Chroma.
    Every chunk inserted into the vector database must conform to
    this schema and pass all validation rules.

    Attributes:
        document_id: UUID of the source contract document.
        chunk_id: UUID of this specific chunk (Chroma document ID).
        page_number: Page containing this chunk (1-indexed).
        page_range: Multi-page span (start, end inclusive).
        char_offset: Character offset within full document.
        text_offset: Character offset within current page (optional).
        clause_label: Semantic category of chunk content.
        confidence_score: Confidence of clause label (0.0–1.0).
        chunk_text_length: Character count of chunk text.
        language: ISO 639-1 language code (default: "en").
        document_hash: SHA-256 fingerprint of source document.
        ingested_at: ISO 8601 timestamp of Chroma insertion.
        extraction_method: How chunk was extracted from document.
        quality_flags: List of quality concerns (if any).
        review_status: QA review status (default: "unreviewed").
    """

    # === Core Identifiers ===
    document_id: str = Field(
        ...,
        description="UUID v4 or alphanumeric ID of source contract document",
        min_length=16,
        max_length=36,
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    chunk_id: str = Field(
        ...,
        description="UUID v4 or alphanumeric ID of this chunk (Chroma document ID)",
        min_length=16,
        max_length=36,
        examples=["7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8"],
    )

    # === Location Metadata ===
    page_number: int = Field(
        ge=1,
        description="Page number containing this chunk (1-indexed)",
        examples=[5],
    )
    page_range: PageRange = Field(
        description="Multi-page span if chunk spans multiple pages",
        examples=[{"start": 3, "end": 5}],
    )
    char_offset: CharOffset = Field(
        description="Character offset within full document (0-indexed)",
        examples=[{"start_char": 1024, "end_char": 2048}],
    )
    text_offset: Optional[CharOffset] = Field(
        default=None,
        description="Character offset within current page (optional, for single-page chunks)",
        examples=[{"start_char": 256, "end_char": 512}],
    )

    # === Content Classification ===
    clause_label: ClauseLabel = Field(
        description="Semantic category of chunk (NLP model or human assigned)",
        examples=["liability"],
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence of clause_label assignment (0.0–1.0)",
        examples=[0.92],
    )

    # === Chunk Content ===
    chunk_text_length: int = Field(
        gt=0,
        description="Character count of chunk text (UTF-8)",
        examples=[512],
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=5,
        description="ISO 639-1 language code",
        examples=["en"],
    )

    # === Provenance ===
    document_hash: str = Field(
        description="SHA-256 fingerprint of source document (64 hex chars)",
        min_length=64,
        max_length=64,
        examples=["a3f5c8e2b1d9f4a7c6e8b2d5a9f1c4e7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5"],
    )
    ingested_at: datetime = Field(
        description="ISO 8601 timestamp of chunk insertion into Chroma (UTC)",
        examples=["2024-08-12T14:30:45.123456Z"],
    )
    extraction_method: ExtractionMethod = Field(
        description="Method used to extract text from source document",
        examples=["semantic_split"],
    )

    # === Quality Assurance ===
    quality_flags: list[QualityFlag] = Field(
        default_factory=list,
        description="List of quality concerns (empty if none)",
        examples=[["incomplete_page", "high_ocr_error_rate"]],
    )
    review_status: ReviewStatus = Field(
        default=ReviewStatus.UNREVIEWED,
        description="QA review status of this chunk",
        examples=["approved"],
    )

    @field_validator("page_number")
    @classmethod
    def validate_page_number(cls, v: int, info) -> int:
        """Page number must be >= 1."""
        return v

    @field_validator("text_offset")
    @classmethod
    def validate_text_offset_single_page_only(cls, v: Optional[CharOffset], info) -> Optional[CharOffset]:
        """text_offset is only valid for single-page chunks."""
        if v is not None and "page_range" in info.data:
            page_range = info.data["page_range"]
            if not page_range.is_single_page:
                raise ValueError(
                    "text_offset is only valid for single-page chunks "
                    "(page_range.start == page_range.end)"
                )
        return v

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Log a warning for low-confidence assignments."""
        if v < 0.70:
            import warnings

            warnings.warn(
                f"Low confidence score {v:.2f} for clause_label assignment. "
                "Manual review recommended.",
                UserWarning,
            )
        return v

    @model_validator(mode="after")
    def validate_page_number_in_range(self) -> VectorChunkMetadata:
        """Ensure page_number is within page_range."""
        if self.page_number < self.page_range.start or self.page_number > self.page_range.end:
            raise ValueError(
                f"page_number {self.page_number} must be within page_range "
                f"[{self.page_range.start}, {self.page_range.end}]"
            )
        return self

    def to_chroma_metadata(self) -> dict:
        """Convert to dictionary suitable for Chroma metadata storage.

        Chroma metadata supports filtering on all these fields.
        Nested objects are flattened for compatibility.

        Returns:
            Dictionary with flattened metadata fields.
        """
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "page_number": self.page_number,
            "page_range_start": self.page_range.start,
            "page_range_end": self.page_range.end,
            "char_offset_start": self.char_offset.start_char,
            "char_offset_end": self.char_offset.end_char,
            "text_offset_start": self.text_offset.start_char if self.text_offset else None,
            "text_offset_end": self.text_offset.end_char if self.text_offset else None,
            "clause_label": self.clause_label.value,
            "confidence_score": self.confidence_score,
            "chunk_text_length": self.chunk_text_length,
            "language": self.language,
            "document_hash": self.document_hash,
            "ingested_at": self.ingested_at.isoformat(),
            "extraction_method": self.extraction_method.value,
            "quality_flags": [flag.value for flag in self.quality_flags],
            "review_status": self.review_status.value,
        }

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "chunk_id": "7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
                "page_number": 5,
                "page_range": {"start": 5, "end": 5},
                "char_offset": {"start_char": 1024, "end_char": 2048},
                "text_offset": {"start_char": 256, "end_char": 512},
                "clause_label": "liability",
                "confidence_score": 0.92,
                "chunk_text_length": 512,
                "language": "en",
                "document_hash": "a3f5c8e2b1d9f4a7c6e8b2d5a9f1c4e7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5",
                "ingested_at": "2024-08-12T14:30:45.123456Z",
                "extraction_method": "semantic_split",
                "quality_flags": [],
                "review_status": "approved",
            }
        },
        use_enum_values=False,
    )


class VectorChunkBatch(BaseModel):
    """Request schema for batch ingestion of chunks into Chroma.

    Used when uploading multiple chunks at once (recommended for
    performance: batch sizes of 100–1000 chunks).
    """

    chunks: list[VectorChunkMetadata] = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="List of chunk metadata to ingest",
    )
    dry_run: bool = Field(
        default=False,
        description="If True, validate without persisting to Chroma",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chunks": [
                    {
                        "document_id": "550e8400-e29b-41d4-a716-446655440000",
                        "chunk_id": "7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
                        "page_number": 5,
                        "page_range": {"start": 5, "end": 5},
                        "char_offset": {"start_char": 1024, "end_char": 2048},
                        "text_offset": {"start_char": 256, "end_char": 512},
                        "clause_label": "liability",
                        "confidence_score": 0.92,
                        "chunk_text_length": 512,
                        "language": "en",
                        "document_hash": "a3f5c8e2b1d9f4a7c6e8b2d5a9f1c4e7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5",
                        "ingested_at": "2024-08-12T14:30:45.123456Z",
                        "extraction_method": "semantic_split",
                        "quality_flags": [],
                        "review_status": "approved",
                    }
                ],
                "dry_run": False,
            }
        }
    )


class VectorChunkResponse(BaseModel):
    """Response schema after successfully ingesting a chunk.

    Confirms that a chunk was stored with its metadata.
    """

    chunk_id: str = Field(description="UUID of ingested chunk")
    document_id: str = Field(description="UUID of source document")
    status: str = Field(
        default="success",
        pattern="^(success|validation_warning)$",
        description="Ingestion status (success or validation_warning)",
    )
    message: str = Field(
        default="Chunk ingested successfully",
        description="Status message",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings generated during ingestion",
    )


class VectorSearchResult(BaseModel):
    """Result from a vector similarity search in Chroma.

    Combines embedding similarity score with chunk metadata
    and original text for ranked retrieval.
    """

    chunk_id: str = Field(description="UUID of retrieved chunk")
    document_id: str = Field(description="UUID of source document")
    similarity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (0.0–1.0)",
    )
    clause_label: ClauseLabel = Field(
        description="Semantic category of chunk",
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence of clause label assignment",
    )
    page_number: int = Field(description="Page number of chunk")
    page_range: PageRange = Field(description="Multi-page span of chunk")
    chunk_text: str = Field(
        description="Original chunk text (truncated to 500 chars for display)"
    )
    char_offset: CharOffset = Field(
        description="Character offset within document",
    )
    review_status: ReviewStatus = Field(
        description="QA review status",
    )
    ingested_at: datetime = Field(
        description="Timestamp of Chroma ingestion",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chunk_id": "7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "similarity_score": 0.85,
                "clause_label": "liability",
                "confidence_score": 0.92,
                "page_number": 5,
                "page_range": {"start": 5, "end": 5},
                "chunk_text": "The Company shall not be liable for...",
                "char_offset": {"start_char": 1024, "end_char": 2048},
                "review_status": "approved",
                "ingested_at": "2024-08-12T14:30:45.123456Z",
            }
        }
    )


class VectorSearchQuery(BaseModel):
    """Request schema for vector similarity search.

    Allows filtering and ranking of results based on metadata.
    """

    query_embedding: list[float] = Field(
        ...,
        min_length=768,
        max_length=768,
        description="Query embedding vector (768-dim for all-MiniLM-L6-v2)",
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Filter results to single document (optional)",
    )
    clause_labels: Optional[list[ClauseLabel]] = Field(
        default=None,
        description="Filter results to specific clause types (optional)",
    )
    min_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Filter results to confidence >= threshold (optional, default: 0.0)",
    )
    only_approved: bool = Field(
        default=True,
        description="Filter to approved chunks only (default: True)",
    )
    n_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of top results to return (default: 10, max: 100)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query_embedding": [0.1, 0.2, 0.3] + [0.0] * 765,
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "clause_labels": ["liability", "confidentiality"],
                "min_confidence": 0.85,
                "only_approved": True,
                "n_results": 10,
            }
        }
    )


__all__ = [
    "ClauseLabel",
    "ExtractionMethod",
    "ReviewStatus",
    "QualityFlag",
    "CharOffset",
    "PageRange",
    "VectorChunkMetadata",
    "VectorChunkBatch",
    "VectorChunkResponse",
    "VectorSearchResult",
    "VectorSearchQuery",
]
