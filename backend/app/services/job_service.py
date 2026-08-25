from __future__ import annotations

from typing import Callable

from app.schemas import AnalysisJob, AnalysisResponse, JobStatus

_jobs: dict[str, AnalysisJob] = {}


def create_job(job_id: str, document_id: str) -> AnalysisJob:
    job = AnalysisJob(job_id=job_id, document_id=document_id, status=JobStatus.QUEUED)
    _jobs[job_id] = job
    return job


def start_processing(job_id: str) -> AnalysisJob:
    job = _get_job(job_id)
    job.status = JobStatus.PROCESSING
    return job


def complete_job(job_id: str, result: AnalysisResponse) -> AnalysisJob:
    job = _get_job(job_id)
    job.status = JobStatus.COMPLETE
    job.result = result
    return job


def fail_job(job_id: str, error: str) -> AnalysisJob:
    job = _get_job(job_id)
    job.status = JobStatus.FAILED
    job.error = error
    return job


def queue_async_job(job_id: str, document_id: str, task: Callable[[], AnalysisResponse]) -> AnalysisJob:
    """Hook for asynchronous document processing orchestration.

    This is a lightweight async orchestration layer that can later be backed by Celery or
    a queue service without changing the API contract.
    """
    job = create_job(job_id=job_id, document_id=document_id)
    start_processing(job_id)
    try:
        result = task()
        return complete_job(job_id, result)
    except Exception as exc:  # pragma: no cover - defensive hook
        fail_job(job_id, str(exc))
        raise


def get_job(job_id: str) -> AnalysisJob:
    return _get_job(job_id)


def _get_job(job_id: str) -> AnalysisJob:
    if job_id not in _jobs:
        raise KeyError(f"Job '{job_id}' not found")
    return _jobs[job_id]


def get_job_by_document_id(document_id: str) -> AnalysisJob:
    for job in _jobs.values():
        if job.document_id == document_id:
            return job
    raise KeyError(f"No job found for document '{document_id}'")