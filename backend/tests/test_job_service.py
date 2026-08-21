import pytest

from app.schemas import JobStatus
from app.services.job_service import (
    complete_job,
    create_job,
    fail_job,
    get_job,
    start_processing,
)
from app.services.analysis_service import analyse_contract


def test_job_starts_queued() -> None:
    job = create_job(job_id="job-001", document_id="doc-001")
    assert job.status == JobStatus.QUEUED
    assert job.result is None


def test_job_transitions_to_processing() -> None:
    create_job(job_id="job-002", document_id="doc-002")
    job = start_processing("job-002")
    assert job.status == JobStatus.PROCESSING


def test_job_completes_with_result() -> None:
    create_job(job_id="job-003", document_id="doc-003")
    start_processing("job-003")

    result = analyse_contract(
        document_id="doc-003",
        filename="sample-contract.pdf",
        file_type="pdf",
        contract_text="This agreement includes auto-renewal and unlimited liability.",
        page_count=4,
    )

    job = complete_job("job-003", result)
    assert job.status == JobStatus.COMPLETE
    assert job.result.document.document_id == "doc-003"


def test_job_fails_with_error() -> None:
    create_job(job_id="job-004", document_id="doc-004")
    job = fail_job("job-004", "OCR extraction failed")
    assert job.status == JobStatus.FAILED
    assert job.error == "OCR extraction failed"


def test_get_missing_job_raises() -> None:
    with pytest.raises(KeyError):
        get_job("does-not-exist")