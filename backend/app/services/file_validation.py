from pathlib import Path


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class FileValidationError(ValueError):
    pass


def validate_file(filename: str, file_size_bytes: int) -> None:
    if not filename:
        raise FileValidationError("Filename is required.")

    if Path(filename).name != filename:
        raise FileValidationError("Filename must not contain a path.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise FileValidationError("Only PDF and DOCX files are allowed.")

    if file_size_bytes <= 0:
        raise FileValidationError("File must not be empty.")

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        raise FileValidationError("File size must not exceed 10 MB.")