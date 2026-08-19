from fastapi.testclient import TestClient

from app.main import app
from app.services.analysis_service import analyse_contract
from app.services.job_service import complete_job, create_job, fail_job

client = TestClient(app)


def test_get_risk_returns_score_for_complete_job() -> None:
    create_job(job_id="job-r1", document_id="doc-r1")

    result = analyse_contract(
        document_id="doc-r1",
        filename="sample-contract.pdf",
        file_type="pdf",
        contract_text="This contract has auto-renewal and unlimited liability.",
        page_count=2,
    )
    complete_job("job-r1", result)

    response = client.get("/documents/doc-r1/risk")

    assert response.status_code == 200
    body = response.json()
    assert body["level"] == "high"
    assert body["score"] == 65


def test_get_risk_404_for_missing_document() -> None:
    response = client.get("/documents/does-not-exist/risk")

    assert response.status_code == 404


def test_get_risk_409_for_incomplete_job() -> None:
    create_job(job_id="job-r2", document_id="doc-r2")
    fail_job("job-r2", "OCR extraction failed")

    response = client.get("/documents/doc-r2/risk")

    assert response.status_code == 409