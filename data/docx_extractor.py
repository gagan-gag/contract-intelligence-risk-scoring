"""DOCX text extraction utilities."""

from __future__ import annotations

from docx import Document


def extract_docx_text(docx_path: str) -> str:
    """Extract paragraph text from a DOCX file.

    Args:
        docx_path: Path to the DOCX document.

    Returns:
        Combined paragraph text from the document.
    """
    doc = Document(docx_path)
    paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)
