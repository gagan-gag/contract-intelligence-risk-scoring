from app.schemas import AnalysisStatusResponse, DocumentUploadResponse


def test_document_upload_response_schema() -> None:
    response = DocumentUploadResponse(
        document_id="doc-001",
        filename="sample-contract.pdf",
        file_type="pdf",
    )

    assert response.status == "queued"
    assert response.filename == "sample-contract.pdf"


def test_analysis_status_response_schema() -> None:
    response = AnalysisStatusResponse(
        document_id="doc-001",
        status="processing",
        message="Document analysis has started.",
    )

    assert response.status == "processing"