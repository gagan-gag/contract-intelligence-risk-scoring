# Vector Index Metadata Contract

**Project:** Contract Intelligence & Risk Scoring (NLP)  
**Module:** Backend Vector Database (Chroma)  
**Version:** 1.0  
**Date:** Day 2 of Development  
**Author:** Backend & Vector Database Engineering Team

---

## Overview

This document defines the metadata schema for all document chunks stored in the Chroma vector database. Each chunk represents a semantically meaningful segment of a contract document, along with rich metadata enabling traceability, filtering, and retrieval in downstream NLP and risk-scoring pipelines.

### Design Principles

- **Traceability:** Every chunk can be traced back to its source document and exact location (character offsets).
- **Modularity:** Metadata fields are independent and can be extended without breaking existing queries.
- **Type Safety:** All fields are strictly typed using Pydantic models for validation at ingestion time.
- **Queryability:** Metadata supports filtering by document ID, clause type, page range, and confidence scores.
- **NLP Integration:** Clause labels and offsets support downstream entity extraction and risk scoring models.

---

## Schema Specification

### 1. Core Identifiers

#### Document ID (`document_id: str`)

- **Type:** String (UUID v4 recommended)
- **Purpose:** Uniquely identifies the source contract document
- **Constraints:**
  - Must be a valid UUID v4 or alphanumeric string (16-36 characters)
  - Immutable once set
  - Used as the primary foreign key linking chunks back to documents
- **Example:** `"550e8400-e29b-41d4-a716-446655440000"` or `"contract_2024_08_12_001"`

#### Chunk ID (`chunk_id: str`)

- **Type:** String (UUID v4 recommended)
- **Purpose:** Uniquely identifies this specific text segment within the corpus
- **Constraints:**
  - Must be a valid UUID v4 or alphanumeric string (16-36 characters)
  - Immutable once set
  - Globally unique across all documents
  - Used as the primary key for vector search results
- **Example:** `"7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8"`

#### Composite Key

For efficient retrieval, the tuple `(document_id, chunk_id)` serves as a unique composite identifier:

```python
composite_key: tuple[str, str] = (document_id, chunk_id)
```

---

### 2. Document Location Metadata

#### Page Number (`page_number: int`)

- **Type:** Positive integer
- **Purpose:** Identifies which page of the source document contains this chunk
- **Constraints:**
  - Must be ≥ 1
  - Must be ≤ total page count of document
- **Example:** `5` (chunk appears on page 5)

#### Page Range (`page_range: dict[str, int] | tuple[int, int]`)

- **Type:** Dictionary with `start` and `end` keys, or tuple `(start, end)`
- **Purpose:** Captures multi-page chunks (e.g., a clause spanning pages 3–5)
- **Constraints:**
  - `start` ≥ 1, `end` ≥ `start`
  - Both must be valid page numbers
  - If chunk is single-page, `start == end`
- **Example:** `{"start": 3, "end": 5}` or `(3, 5)`

#### Character Offsets (`char_offset: dict[str, int] | tuple[int, int]`)

- **Type:** Dictionary with `start_char` and `end_char` keys, or tuple `(start_char, end_char)`
- **Purpose:** Identifies the exact byte/character position of this chunk within the source document
- **Constraints:**
  - `start_char` ≥ 0
  - `end_char` > `start_char`
  - Both must reference valid positions in the original document text
  - Zero-indexed
- **Use Cases:**
  - Highlighting exact text in UI
  - Reconstructing original context
  - Validating chunk extraction accuracy
- **Example:** `{"start_char": 1024, "end_char": 2048}` or `(1024, 2048)`

#### Text Offsets (Page-Relative) (`text_offset: dict[str, int] | None`)

- **Type:** Optional dictionary with `start_char` and `end_char` keys
- **Purpose:** Character offset **relative to the current page** (not document)
- **Constraints:**
  - Only applicable for single-page chunks (`page_range.start == page_range.end`)
  - Useful for PDF text extraction where per-page offsets are available
  - `start_char` ≥ 0, `end_char` > `start_char`
- **Example:** `{"start_char": 256, "end_char": 512}` or `None` if multi-page

---

### 3. Content Classification

#### Clause Label (`clause_label: str`)

- **Type:** String (predefined enum values)
- **Purpose:** Semantically categorizes the type of contract clause
- **Valid Values** (extendable):
  - `"PARTIES"` — Definition of parties to the contract
  - `"CONSIDERATION"` — Exchange of value/payment terms
  - `"TERM_TERMINATION"` — Contract duration and termination conditions
  - `"LIABILITY"` — Liability limitations and indemnification
  - `"CONFIDENTIALITY"` — Confidentiality and NDA terms
  - `"GOVERNING_LAW"` — Jurisdiction and applicable law
  - `"DISPUTE_RESOLUTION"` — Arbitration, mediation, litigation terms
  - `"INTELLECTUAL_PROPERTY"` — IP ownership and licensing
  - `"WARRANTIES"` — Warranties and representations
  - `"FORCE_MAJEURE"` — Force majeure and events of impossibility
  - `"ASSIGNMENT"` — Assignment and delegation rights
  - `"COMPLIANCE"` — Regulatory and compliance obligations
  - `"GENERAL"` — Boilerplate, definitions, or uncategorized text
- **Constraints:**
  - Must be one of the predefined enum values
  - Cannot be null
  - Assigned by NLP classification model or human review
- **Example:** `"LIABILITY"` (indicates this chunk contains liability language)

#### Confidence Score (`confidence_score: float`)

- **Type:** Float between 0.0 and 1.0
- **Purpose:** Measures confidence of the clause label assignment
- **Constraints:**
  - 0.0 ≤ confidence_score ≤ 1.0
  - Typically comes from NLP model output
  - Allows filtering of high-confidence classifications (≥ 0.85)
- **Interpretation:**
  - 1.0 = 100% certain (e.g., human-labeled or definitional clauses)
  - 0.85+ = High confidence, suitable for automated pipelines
  - 0.70–0.85 = Medium confidence, review recommended
  - < 0.70 = Low confidence, manual review required
- **Example:** `0.92` (92% confidence this is a LIABILITY clause)

---

### 4. Chunk Content

#### Raw Text / Token Count (`chunk_text_length: int`)

- **Type:** Positive integer
- **Purpose:** Stores the character count of the chunk text
- **Constraints:**
  - Must be > 0
  - Represents `len(chunk_text)` in UTF-8 characters
- **Example:** `512` (this chunk contains 512 characters)
- **Note:** The actual text is stored in Chroma's document collection; metadata stores this for indexing/filtering.

#### Language / Encoding (`language: str`)

- **Type:** String (ISO 639-1 code)
- **Purpose:** Identifies the language of the chunk text
- **Constraints:**
  - Must be a valid ISO 639-1 language code (e.g., "en", "es", "fr")
  - Defaults to "en" for English contracts
- **Example:** `"en"` (English)

---

### 5. Provenance and Timestamps

#### Document Hash (`document_hash: str`)

- **Type:** String (SHA-256 hex digest)
- **Purpose:** Fingerprint of source document for integrity checking
- **Constraints:**
  - Must be a valid SHA-256 hash (64 hex characters)
  - Immutable; changes indicate document replacement
- **Example:** `"a3f5c8e2b1d9f4a7c6e8b2d5a9f1c4e7"`

#### Ingestion Timestamp (`ingested_at: str`)

- **Type:** ISO 8601 timestamp string
- **Purpose:** Records when this chunk was indexed into Chroma
- **Constraints:**
  - Must be valid ISO 8601 format (e.g., `"2024-08-12T14:30:45Z"`)
  - Immutable after creation
  - Set to current UTC time at ingestion
- **Example:** `"2024-08-12T14:30:45.123456Z"`

#### Extraction Method (`extraction_method: str`)

- **Type:** String (predefined enum values)
- **Purpose:** Identifies how the chunk was extracted from the document
- **Valid Values**:
  - `"PDF_TEXT_EXTRACTION"` — Extracted from PDF text layer
  - `"OCR"` — Extracted via Optical Character Recognition
  - `"MANUAL_ANNOTATION"` — Manually input by human reviewer
  - `"PARAGRAPH_SEGMENTATION"` — Automatic paragraph-level segmentation
  - `"SEMANTIC_SPLIT"` — Split using semantic boundaries (token-aware)
- **Example:** `"SEMANTIC_SPLIT"`

---

### 6. Quality Metrics

#### Quality Flags (`quality_flags: list[str]`)

- **Type:** List of strings
- **Purpose:** Flags indicating potential data quality issues
- **Valid Flags** (extendable):
  - `"HIGH_OCR_ERROR_RATE"` — Chunk may contain OCR errors
  - `"INCOMPLETE_PAGE"` — Chunk spans incomplete/corrupted page
  - `"ENCODING_MISMATCH"` — Text encoding issues detected
  - `"DUPLICATE_CONTENT"` — Chunk appears to duplicate another
  - `"CONFIDENTIALITY_REDACTED"` — Original contains redacted/masked text
  - `"AUTO_GENERATED_TEXT"` — Likely auto-generated (table of contents, headers)
- **Constraints:**
  - Can be empty list if no flags apply
  - Helps downstream systems decide filtering/handling strategies
- **Example:** `["INCOMPLETE_PAGE", "HIGH_OCR_ERROR_RATE"]`

#### Review Status (`review_status: str`)

- **Type:** String (predefined enum values)
- **Purpose:** Tracks human review state for validation and QA
- **Valid Values**:
  - `"UNREVIEWED"` — Not yet reviewed by human
  - `"APPROVED"` — Reviewed and approved
  - `"FLAGGED"` — Reviewed but flagged for issues
  - `"REJECTED"` — Reviewed and rejected (should be excluded)
- **Constraints:**
  - Defaults to `"UNREVIEWED"`
  - Allows filtering to approved-only chunks
- **Example:** `"APPROVED"`

---

## Complete Metadata Schema

### JSON Representation

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunk_id": "7c3d1a8f-9e2b-4c5a-b1d9-23f4e5a6b7c8",
  "page_number": 5,
  "page_range": {
    "start": 5,
    "end": 5
  },
  "char_offset": {
    "start_char": 1024,
    "end_char": 2048
  },
  "text_offset": {
    "start_char": 256,
    "end_char": 512
  },
  "clause_label": "LIABILITY",
  "confidence_score": 0.92,
  "chunk_text_length": 512,
  "language": "en",
  "document_hash": "a3f5c8e2b1d9f4a7c6e8b2d5a9f1c4e7",
  "ingested_at": "2024-08-12T14:30:45.123456Z",
  "extraction_method": "SEMANTIC_SPLIT",
  "quality_flags": [],
  "review_status": "APPROVED"
}
```

### Pydantic Model

See `backend/app/vector/schemas.py` for complete type-safe Pydantic models.

---

## Storage in Chroma

### Collection Structure

```
Collection: "contract_chunks"
├── Document IDs: [document_id]
├── Chunk IDs: [chunk_id]  (stored as Chroma ID)
├── Embeddings: [768-dim vectors from embedding model]
├── Documents: [original chunk text]
└── Metadata: [all fields above]
```

### Chroma Metadata Filtering

Chroma supports filtering on metadata fields. Example queries:

```python
# Filter by document ID
results = collection.query(
    query_embeddings=[...],
    where={"document_id": {"$eq": "550e8400-e29b-41d4-a716-446655440000"}},
    n_results=10
)

# Filter by clause label
results = collection.query(
    query_embeddings=[...],
    where={"clause_label": {"$eq": "LIABILITY"}},
    n_results=10
)

# Filter by confidence score
results = collection.query(
    query_embeddings=[...],
    where={"confidence_score": {"$gte": 0.85}},
    n_results=10
)

# Composite filter
results = collection.query(
    query_embeddings=[...],
    where={
        "$and": [
            {"document_id": {"$eq": "550e8400-e29b-41d4-a716-446655440000"}},
            {"clause_label": {"$eq": "LIABILITY"}},
            {"confidence_score": {"$gte": 0.85}}
        ]
    },
    n_results=10
)
```

---

## Ingestion Pipeline

### Step 1: Document Upload
- Assign unique `document_id` (UUID v4)
- Compute `document_hash` (SHA-256 of file contents)
- Record `ingested_at` timestamp

### Step 2: Text Extraction
- Extract text from PDF or source format
- Track `extraction_method` (PDF_TEXT_EXTRACTION, OCR, etc.)
- Record `chunk_text_length` for each chunk
- Capture `char_offset` and optionally `text_offset`

### Step 3: Segmentation
- Split document into semantic chunks
- Assign unique `chunk_id` (UUID v4) to each chunk
- Preserve `page_number` and `page_range` information

### Step 4: Classification
- Run NLP model to assign `clause_label`
- Capture model output confidence as `confidence_score`
- Assign initial `quality_flags` based on extraction confidence

### Step 5: Embedding & Storage
- Generate embeddings (768-dim, e.g., all-MiniLM-L6-v2)
- Insert into Chroma with:
  - `chunk_id` as Chroma document ID
  - Embeddings vector
  - Original chunk text
  - All metadata fields

### Step 6: Review & QA
- Set initial `review_status` to "UNREVIEWED"
- Allow human reviewers to update to "APPROVED", "FLAGGED", or "REJECTED"

---

## Best Practices

### Chunk Size Guidelines

- **Optimal range:** 128–512 tokens (~500–2000 characters)
- **Minimum:** 64 tokens (to avoid noise)
- **Maximum:** 1024 tokens (to avoid too-general embeddings)
- **Sweet spot:** 256 tokens (~1000 characters) for balanced context

### Metadata Validation

1. **Always validate** document_id and chunk_id are valid UUIDs or alphanumeric
2. **Ensure** confidence_score is between 0.0 and 1.0
3. **Check** that page_number ≤ total_pages for the document
4. **Verify** char_offset is monotonically increasing
5. **Confirm** clause_label is in predefined enum

### Querying Strategies

1. **High-confidence filtering:** Always filter `confidence_score >= 0.85` for production queries
2. **Document scoping:** Include document_id filter to isolate contract-specific results
3. **Review filtering:** Add `review_status == "APPROVED"` to use only QA-verified chunks
4. **Clause-specific queries:** Use `clause_label` filter for targeted risk scoring

### Performance Considerations

- **Indexing:** Chroma automatically indexes metadata; no manual index management needed
- **Query performance:** Filtering on `document_id` and `clause_label` are most efficient
- **Storage:** Each metadata field adds ~50–100 bytes per chunk; optimize for your scale
- **Batch ingestion:** Insert chunks in batches of 100–1000 for optimal throughput

---

## Evolution & Versioning

### Schema Versioning
- **Version 1.0** (current): Initial release with core metadata fields
- **Future versions** may add:
  - Entity mentions (person, company names within chunk)
  - Risk tags (HIGH_RISK, MEDIUM_RISK, LOW_RISK)
  - Regulatory framework (GDPR, SOX, CCPA, etc.)
  - Custom metadata extensions

### Adding New Fields
1. Add field to Pydantic model with default value
2. Update this documentation
3. Backfill existing chunks if necessary (or mark as nullable)
4. Increment schema version in `__version__` constant

---

## References

- **Chroma Documentation:** https://docs.trychroma.com
- **Pydantic Documentation:** https://docs.pydantic.dev
- **ISO 8601 Timestamps:** https://en.wikipedia.org/wiki/ISO_8601
- **UUID Standard (RFC 4122):** https://tools.ietf.org/html/rfc4122
- **SHA-256 Hashing:** https://en.wikipedia.org/wiki/SHA-2

---

## Appendix: Enum Reference

### ClauseLabel Enum

```
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
```

### ExtractionMethod Enum

```
PDF_TEXT_EXTRACTION = "pdf_text_extraction"
OCR = "ocr"
MANUAL_ANNOTATION = "manual_annotation"
PARAGRAPH_SEGMENTATION = "paragraph_segmentation"
SEMANTIC_SPLIT = "semantic_split"
```

### ReviewStatus Enum

```
UNREVIEWED = "unreviewed"
APPROVED = "approved"
FLAGGED = "flagged"
REJECTED = "rejected"
```

### QualityFlag Values (Extensible)

```
HIGH_OCR_ERROR_RATE = "high_ocr_error_rate"
INCOMPLETE_PAGE = "incomplete_page"
ENCODING_MISMATCH = "encoding_mismatch"
DUPLICATE_CONTENT = "duplicate_content"
CONFIDENTIALITY_REDACTED = "confidentiality_redacted"
AUTO_GENERATED_TEXT = "auto_generated_text"
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-08-12  
**Status:** Approved for Day 2 Implementation
