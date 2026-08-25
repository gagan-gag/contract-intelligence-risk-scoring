import pytest

from data.extraction import extract_text_from_document


def test_extract_text_handles_plain_text() -> None:
    text = extract_text_from_document("sample.txt", b"This contract has an auto-renewal clause.")
    assert "auto-renewal" in text.lower()


def test_extract_text_rejects_password_protected_pdf_gracefully() -> None:
    with pytest.raises(ValueError, match="password"):
        extract_text_from_document("locked.pdf", b"%PDF-1.4\n<< /Encrypt 1 >>")


def test_extract_text_handles_malformed_input() -> None:
    result = extract_text_from_document("broken.pdf", b"not a real pdf")
    assert isinstance(result, str)
    assert result.strip() == ""
