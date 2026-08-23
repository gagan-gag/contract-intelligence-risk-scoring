"""Validation helpers for extracted document text."""

from __future__ import annotations


class ExtractionValidationError(ValueError):
    """Raised when extracted document fields do not pass validation rules."""


def validate_extraction(document_id: str, filename: str, file_type: str, page_count: int) -> None:
    """Validate document extraction metadata before indexing or storage.

    Args:
        document_id: Stable identifier for the document.
        filename: Original file name.
        file_type: Normalized file extension or type.
        page_count: Number of pages in the source document.

    Raises:
        ExtractionValidationError: If the metadata is invalid.
    """
    if not document_id or not str(document_id).strip():
        raise ExtractionValidationError("document_id is required")
    if not filename or not str(filename).strip():
        raise ExtractionValidationError("filename is required")
    if not file_type or not str(file_type).strip():
        raise ExtractionValidationError("file_type is required")
    if page_count < 1:
        raise ExtractionValidationError("page_count must be at least 1")
