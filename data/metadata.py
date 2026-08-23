"""Metadata extraction helpers for documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def extract_metadata(file_path: str, page_count: int) -> Dict[str, Any]:
    """Extract lightweight metadata for a document.

    Args:
        file_path: File path for the uploaded document.
        page_count: Number of pages in the file.

    Returns:
        Metadata dictionary with filename, file type, and page count.
    """
    path = Path(file_path)
    suffix = path.suffix.lower().lstrip(".")
    file_type = suffix if suffix else "unknown"

    return {
        "filename": path.name,
        "file_type": file_type,
        "page_count": int(page_count),
    }
