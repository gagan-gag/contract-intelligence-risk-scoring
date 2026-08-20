from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import JobStatus
from app.services.analysis_service import analyse_contract
from app.services.job_service import (
    complete_job,
    create_job,
    get_job,
)

client = TestClient(app)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_contract.txt"


def _load_fixture_text() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_full_pipeline_queued_to_risk_endpoint() -> None:
    document_id = "doc-int-001"
    job_id = "job-int-001"
    contract_text = _load_fixture_text()
    print("SCORE:", result.risk.score, "LEVEL:", result.risk.level, "REASONS:", result.risk.reasons)

    # Step 1: job starts queued
    job = create_job(job_id=job_id, document_id=document_id)
    assert job.status == JobStatus.QUEUED

    # Step 2: orchestration service processes the fixture text
    # (stands in for M3's real parser/OCR output and M2's future model calls)
    result = analyse_contract(
        document_id=document_id,
        filename="sample_contract.txt",
        file_type="txt",
        contract_text=contract_text,
        page_count=1,
    )

    # Step 3: job completes with the analysis result
    completed = complete_job(job_id, result)
    assert completed.status == JobStatus.COMPLETE
    assert completed.result is not None

    # Step 4: risk is retrievable via the API
    response = client.get(f"/documents/{document_id}/risk")
    assert response.status_code == 200

    body = response.json()
    assert body["level"] == "high"
    assert body["score"] == 65
    assert "Auto-renewal clause detected." in body["reasons"]
    assert "Indemnification obligation detected." in body["reasons"]
    assert "Termination without notice detected." in body["reasons"]


def test_pipeline_job_state_persists_correctly() -> None:
    document_id = "doc-int-002"
    job_id = "job-int-002"

    create_job(job_id=job_id, document_id=document_id)

    result = analyse_contract(
        document_id=document_id,
        filename="short.txt",
        file_type="txt",
        contract_text="This agreement is valid for one year with standard terms.",
        page_count=1,
    )
    complete_job(job_id, result)

    stored_job = get_job(job_id)
    assert stored_job.document_id == document_id
    assert stored_job.status == JobStatus.COMPLETE
    assert stored_job.result.risk.level.value == "low"