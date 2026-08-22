import pytest

from app.services.file_validation import FileValidationError, validate_file


def test_pdf_file_is_valid() -> None:
    validate_file("contract.pdf", 1024)


def test_docx_file_is_valid() -> None:
    validate_file("contract.docx", 1024)


def test_invalid_file_type_is_rejected() -> None:
    with pytest.raises(FileValidationError):
        validate_file("contract.exe", 1024)


def test_large_file_is_rejected() -> None:
    with pytest.raises(FileValidationError):
        validate_file("contract.pdf", 11 * 1024 * 1024)
        

def test_missing_filename_is_rejected() -> None:
    with pytest.raises(FileValidationError):
        validate_file("", 1024)


def test_filename_with_path_is_rejected() -> None:
    with pytest.raises(FileValidationError):
        validate_file("../contract.pdf", 1024)