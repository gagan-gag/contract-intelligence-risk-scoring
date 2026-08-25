import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_rejects_disallowed_extension() -> None:
    file_content = io.BytesIO(b"some content")
    response = client.post(
        "/documents/upload",
        files={"file": ("contract.txt", file_content, "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF and DOCX files are allowed."


def test_upload_rejects_empty_file() -> None:
    file_content = io.BytesIO(b"")
    response = client.post(
        "/documents/upload",
        files={"file": ("contract.pdf", file_content, "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File must not be empty."


def test_upload_rejects_oversized_file() -> None:
    oversized_content = b"a" * (10 * 1024 * 1024 + 1)
    file_content = io.BytesIO(oversized_content)
    response = client.post(
        "/documents/upload",
        files={"file": ("contract.pdf", file_content, "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File size must not exceed 10 MB."


def test_upload_accepts_valid_pdf() -> None:
    file_content = io.BytesIO(b"%PDF-1.4 valid pdf content")
    response = client.post(
        "/documents/upload",
        files={"file": ("contract.pdf", file_content, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("queued", "complete")
    assert body["filename"] == "contract.pdf"
    assert "document_id" in body
    assert "job_id" in body