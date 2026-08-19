from fastapi import APIRouter, HTTPException

from app.schemas import JobStatus, RiskScore
from app.services.job_service import get_job_by_document_id

router = APIRouter()


@router.get("/documents/{document_id}/risk", response_model=RiskScore)
def get_document_risk(document_id: str) -> RiskScore:
    try:
        job = get_job_by_document_id(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document analysis not found")

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=409,
            detail=f"Document analysis is not complete (status: {job.status.value})",
        )

    return job.result.risk