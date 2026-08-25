"""Document text extraction utilities.

Supports PDF (via pypdf) and DOCX (via python-docx).
Both dependencies are optional – falls back to empty string with a warning
so the analysis pipeline still runs (risk engine works on empty text,
returning a zero-risk score rather than crashing).
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def extract_text_from_bytes(filename: str, file_bytes: bytes) -> tuple[str, int]:
    """Extract plain text and page count from raw file bytes.

    Args:
        filename:   Original filename (used to determine file type).
        file_bytes: Raw content of the uploaded file.

    Returns:
        A ``(text, page_count)`` tuple.  ``page_count`` is always ≥ 1.
    """
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    if ext == "docx":
        return _extract_docx(file_bytes)

    logger.warning("Unsupported extension '%s'; returning empty text.", ext)
    return "", 1


def _extract_pdf(file_bytes: bytes) -> tuple[str, int]:
    """Extract text from a PDF using pypdf."""
    try:
        import io

        from pypdf import PdfReader  # noqa: PLC0415

        reader = PdfReader(io.BytesIO(file_bytes))
        pages = reader.pages
        page_count = max(len(pages), 1)
        text = "\n\n".join(
            (page.extract_text() or "") for page in pages
        )
        return text.strip(), page_count
    except ImportError:
        logger.warning("pypdf not installed – PDF text extraction unavailable.")
        return "", 1
    except Exception as exc:
        logger.warning("PDF extraction failed: %s", exc)
        return "", 1


def _extract_docx(file_bytes: bytes) -> tuple[str, int]:
    """Extract text from a DOCX using python-docx."""
    try:
        import io

        from docx import Document  # noqa: PLC0415

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        # Estimate pages: ~250 words per page
        word_count = len(text.split())
        page_count = max(1, round(word_count / 250))
        return text.strip(), page_count
    except ImportError:
        logger.warning("python-docx not installed – DOCX text extraction unavailable.")
        return "", 1
    except Exception as exc:
        logger.warning("DOCX extraction failed: %s", exc)
        return "", 1
