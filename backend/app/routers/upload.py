import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.services.file_validation import FileValidationError, validate_file
from app.services.job_service import create_job

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(file: UploadFile) -> dict:
    contents = await file.read()
    file_size_bytes = len(contents)

    try:
        validate_file(filename=file.filename or "", file_size_bytes=file_size_bytes)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    document_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    create_job(job_id=job_id, document_id=document_id)

    return {
        "document_id": document_id,
        "job_id": job_id,
        "filename": file.filename,
        "status": "queued",
    }