"""Text normalization helpers for extracted contract content."""

from __future__ import annotations

import re


def normalize_text(raw_text: str, source_page_count: int) -> str:
    """Normalize extracted text by removing page markers and extra whitespace.

    Args:
        raw_text: Raw extraction result.
        source_page_count: Number of pages in the source document.

    Returns:
        Cleaned and normalized text.
    """
    text = raw_text or ""
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    text = re.sub(r"(?m)^Page\s+\d+\s*$", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    if source_page_count <= 0:
        return text
    return text
