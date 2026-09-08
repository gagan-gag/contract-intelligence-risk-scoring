from fastapi import APIRouter, HTTPException

from app.schemas import AnalysisResponse, AnalysisStatusResponse, JobStatus, RiskScore
from app.services.job_service import get_job_by_document_id

router = APIRouter(tags=["analysis"])


@router.get("/documents/{document_id}/status", response_model=AnalysisStatusResponse)
def get_document_status(document_id: str) -> AnalysisStatusResponse:
    """Return the current processing status for a document."""
    try:
        job = get_job_by_document_id(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")

    return AnalysisStatusResponse(
        document_id=document_id,
        status=job.status.value,
        message=f"Job is {job.status.value}" + (f": {job.error}" if job.error else ""),
    )


@router.get("/documents/{document_id}/risk", response_model=RiskScore)
def get_document_risk(document_id: str) -> RiskScore:
    """Return the calculated risk score for a document once analysis completes."""
    try:
        job = get_job_by_document_id(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document analysis not found")

    if job.status != JobStatus.COMPLETE or job.result is None:
        raise HTTPException(
            status_code=409,
            detail=f"Document analysis is not complete (status: {job.status.value})",
        )

    return job.result.risk


@router.get("/documents/{document_id}/analysis", response_model=AnalysisResponse)
def get_document_analysis(document_id: str) -> AnalysisResponse:
    """Return full contract intelligence report: entities, classified clauses, risk score."""
    try:
        job = get_job_by_document_id(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document analysis not found")

    if job.status != JobStatus.COMPLETE or job.result is None:
        raise HTTPException(
            status_code=409,
            detail=f"Document analysis is not complete (status: {job.status.value})",
        )

    return job.result