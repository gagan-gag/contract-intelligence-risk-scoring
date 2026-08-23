"""PDF text extraction utilities."""

from __future__ import annotations

import fitz


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF document.

    Returns:
        Extracted plain text content.
    """
    doc = fitz.open(pdf_path)
    text_parts: list[str] = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)
