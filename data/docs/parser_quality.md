# Parser Quality Notes

## PDF Extraction

- Text-based PDFs generally work well with `fitz` extraction.
- Extraction quality depends on whether the PDF contains selectable text layers.
- For scanned or image-heavy PDFs, OCR fallback may be needed.

## OCR Fallback

- When extracted text is shorter than 50 characters, the system should try OCR.
- This is a targeted fallback for low-information or scanned pages.

## DOCX Extraction

- DOCX parsing is paragraph-based and works best for standard Word documents.
- Complex tables, tracked changes, or embedded images may reduce quality.

## Known Failures

- Scanned PDFs without text layers may still yield poor OCR quality.
- Legacy or malformed files can produce inconsistent whitespace and page markers.
- Some documents may require manual review if structure is heavily corrupted.
