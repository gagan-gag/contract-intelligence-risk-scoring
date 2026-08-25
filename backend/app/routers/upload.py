"""Document upload router.

On upload the document is analysed immediately (synchronously) so the job
is COMPLETE by the time the frontend polls /documents/{id}/risk or
/documents/{id}/analysis.  This fixes the "Failed to fetch" / 409 loop.
"""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.services.analysis_service import analyse_contract
from app.services.file_validation import FileValidationError, validate_file
from app.services.job_service import create_job, fail_job, complete_job, start_processing
from app.services.text_extractor import extract_text_from_bytes

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/documents/upload")
async def upload_document(file: UploadFile) -> dict:
    """Upload a contract file, extract text and run analysis immediately.

    Returns a completed job response so the frontend can fetch results
    without a polling delay.
    """
    contents = await file.read()
    file_size_bytes = len(contents)

    try:
        validate_file(filename=file.filename or "", file_size_bytes=file_size_bytes)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    document_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    filename = file.filename or "unknown"
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"

    # Create job and mark as processing
    create_job(job_id=job_id, document_id=document_id)
    start_processing(job_id)

    # Extract text from file bytes
    try:
        contract_text, page_count = extract_text_from_bytes(filename, contents)
    except Exception as exc:
        logger.warning("Text extraction failed for %s: %s", filename, exc)
        contract_text, page_count = "", 1

    # Run full NLP analysis synchronously
    try:
        result = analyse_contract(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            contract_text=contract_text,
            page_count=page_count,
        )
        complete_job(job_id, result)
    except Exception as exc:
        logger.error("Analysis failed for document %s: %s", document_id, exc)
        fail_job(job_id, str(exc))
        raise HTTPException(status_code=500, detail=f"Contract analysis failed: {exc}")

    return {
        "document_id": document_id,
        "job_id": job_id,
        "filename": filename,
        "status": "complete",
    }