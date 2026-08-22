"""Tests for persistent document-analysis metadata storage."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.app.schemas import RiskLevel
from backend.app.vector.store import DocumentAnalysisMetadata, DocumentAnalysisStore


def _metadata(*, status: str = "completed", chunk_count: int = 3) -> DocumentAnalysisMetadata:
    """Build a representative completed document-analysis record."""
    return DocumentAnalysisMetadata(
        document_id="contract-fixture-001",
        filename="master-services-agreement.pdf",
        file_type="pdf",
        page_count=12,
        processing_status=status,
        risk_score=72,
        risk_level=RiskLevel.HIGH,
        risk_reasons=["Broad indemnity obligation"],
        summary="Agreement contains elevated indemnity and renewal risk.",
        chunk_count=chunk_count,
        entities=[
            {"text": "Acme Ltd", "entity_type": "party", "page_number": 1},
        ],
        clauses=[
            {"clause_type": "indemnity", "page_number": 8, "confidence": 0.94},
        ],
    )


def test_document_analysis_round_trip_survives_repository_reopen(tmp_path: Path) -> None:
    """Saved metadata should be retrievable by ID from a new store instance."""
    database_path = tmp_path / "vector" / "document_analysis.sqlite3"
    first_store = DocumentAnalysisStore(database_path)

    saved = first_store.save_document_analysis(_metadata())
    fetched = DocumentAnalysisStore(database_path).get_document_analysis(
        "contract-fixture-001"
    )

    assert saved.document_id == "contract-fixture-001"
    assert fetched == saved
    assert fetched is not None
    assert fetched.risk_score == 72
    assert fetched.risk_level is RiskLevel.HIGH
    assert fetched.clauses[0]["clause_type"] == "indemnity"


def test_save_document_analysis_updates_existing_document_id(tmp_path: Path) -> None:
    """Saving a later processing snapshot should replace, not duplicate, a row."""
    store = DocumentAnalysisStore(tmp_path / "document_analysis.sqlite3")

    store.save_document_analysis(_metadata(status="processing", chunk_count=0))
    updated = store.save_document_analysis(_metadata(status="completed", chunk_count=5))

    fetched = store.get_document_analysis("contract-fixture-001")
    assert fetched == updated
    assert fetched is not None
    assert fetched.processing_status == "completed"
    assert fetched.chunk_count == 5

    with store._connect() as connection:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM document_analysis WHERE document_id = ?",
            ("contract-fixture-001",),
        ).fetchone()[0]
    assert row_count == 1


def test_document_analysis_validation_rejects_invalid_values() -> None:
    """Risk and processing fields should reject malformed analysis metadata."""
    with pytest.raises(ValidationError):
        DocumentAnalysisMetadata(
            document_id="contract-fixture-001",
            filename="contract.pdf",
            file_type="pdf",
            page_count=0,
            risk_score=101,
            processing_status="unknown",
        )


def test_missing_document_analysis_returns_none_and_delete_is_explicit(
    tmp_path: Path,
) -> None:
    """Missing records are distinguishable from invalid IDs or storage errors."""
    store = DocumentAnalysisStore(tmp_path / "document_analysis.sqlite3")

    assert store.get_document_analysis("missing-document") is None
    assert store.delete_document_analysis("missing-document") is False
    store.save_document_analysis(_metadata())
    assert store.delete_document_analysis("contract-fixture-001") is True
    assert store.get_document_analysis("contract-fixture-001") is None

    with pytest.raises(ValueError, match="document_id"):
        store.get_document_analysis(" ")
