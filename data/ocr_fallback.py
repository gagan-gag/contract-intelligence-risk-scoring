"""OCR fallback for PDFs when text extraction returns limited content."""

from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image

from data.pdf_extractor import extract_pdf_text


def extract_with_ocr_fallback(pdf_path: str) -> str:
    """Extract text from a PDF and fallback to OCR for low-confidence content.

    Args:
        pdf_path: Path to the input PDF.

    Returns:
        Extracted text or OCR result when the original extraction is sparse.
    """
    text = extract_pdf_text(pdf_path)
    if len(text.strip()) >= 50:
        return text

    image_path = Path(pdf_path).with_suffix(".png")
    if not image_path.exists():
        return text

    image = Image.open(image_path)
    return pytesseract.image_to_string(image)
