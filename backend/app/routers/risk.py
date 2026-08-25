"""Risk and analysis routers.

Endpoints:
  GET /documents/{document_id}/risk      – Returns RiskScore (backward-compatible)
  GET /documents/{document_id}/analysis  – Returns full AnalysisResponse with
                                           entities, clauses, and risk score
"""
from fastapi import APIRouter, HTTPException

from app.schemas import AnalysisResponse, JobStatus, RiskScore
from app.services.job_service import get_job_by_document_id

router = APIRouter()


def _require_complete_job(document_id: str):
    """Retrieve a completed job or raise the appropriate HTTP error."""
    try:
        job = get_job_by_document_id(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document analysis not found")

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=409,
            detail=f"Document analysis is not complete (status: {job.status.value})",
        )
    return job


@router.get("/documents/{document_id}/risk", response_model=RiskScore)
def get_document_risk(document_id: str) -> RiskScore:
    """Return the risk score for an analysed document.

    Backward-compatible endpoint – preserves original API contract.
    """
    job = _require_complete_job(document_id)
    return job.result.risk


@router.get("/documents/{document_id}/analysis", response_model=AnalysisResponse)
def get_document_analysis(document_id: str) -> AnalysisResponse:
    """Return the full analysis result including entities and clauses."""
    job = _require_complete_job(document_id)
    return job.result