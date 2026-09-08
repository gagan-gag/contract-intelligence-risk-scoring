import io
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from app.services.analysis_service import analyse_contract
from app.services.file_validation import FileValidationError, validate_file
from app.services.job_service import (
    complete_job,
    create_job,
    fail_job,
    start_processing,
)

router = APIRouter()


def _extract_text_and_pages(filename: str, contents: bytes) -> tuple[str, int]:
    """Extract plain text and page count safely from PDF or DOCX bytes."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"
    text = ""
    page_count = 1

    if ext == "pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(contents))
            page_count = max(1, len(reader.pages))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            try:
                import fitz  # pymupdf
                doc = fitz.open(stream=contents, filetype="pdf")
                page_count = max(1, len(doc))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except Exception:
                text = contents.decode("utf-8", errors="ignore")
    elif ext == "docx":
        try:
            import docx
            doc = docx.Document(io.BytesIO(contents))
            text = "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            text = contents.decode("utf-8", errors="ignore")
    else:
        text = contents.decode("utf-8", errors="ignore")

    if not text.strip():
        text = contents.decode("utf-8", errors="ignore")

    return text, page_count


def _run_background_analysis(
    job_id: str,
    document_id: str,
    filename: str,
    contents: bytes,
) -> None:
    """Run analysis in the background and record results in the job store."""
    try:
        start_processing(job_id)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"
        text, page_count = _extract_text_and_pages(filename, contents)
        
        result = analyse_contract(
            document_id=document_id,
            filename=filename,
            file_type=ext,
            contract_text=text,
            page_count=page_count,
        )

        # Attempt to index chunks into local Chroma vector store if available
        try:
            from app.vector.chroma_adapter import ChromaAdapter
            from app.vector.client import create_chroma_client, get_or_create_collection
            from app.vector.embeddings import EmbeddingAdapter
            import os

            adapter = ChromaAdapter()
            client = create_chroma_client(persist_directory=adapter.persist_directory)
            collection_name = os.getenv("VECTOR_COLLECTION_NAME", "contract_chunks")
            collection = get_or_create_collection(client, collection_name)
            embedding_adapter = EmbeddingAdapter()

            paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 30]
            if not paragraphs:
                paragraphs = [text[:1000]] if text else ["Sample contract text"]

            from app.vector.schemas import VectorChunkMetadata, PageRange, CharOffset, ClauseLabel, ExtractionMethod
            from datetime import datetime, timezone

            text_chunks: list[str] = []
            metadata_list: list[VectorChunkMetadata] = []

            for idx, paragraph in enumerate(paragraphs[:20]):
                chunk_id = f"{document_id[:28]}-{idx:04d}"
                meta = VectorChunkMetadata(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    page_number=1,
                    page_range=PageRange(start=1, end=1),
                    char_offset=CharOffset(start_char=0, end_char=len(paragraph)),
                    clause_label=ClauseLabel.GENERAL,
                    confidence_score=0.9,
                    chunk_text_length=len(paragraph),
                    document_hash=str(hash(contents)),
                    ingested_at=datetime.now(timezone.utc),
                    extraction_method=ExtractionMethod.PARAGRAPH_SEGMENTATION,
                )
                text_chunks.append(paragraph)
                metadata_list.append(meta)

            embeddings = embedding_adapter.encode(text_chunks)
            adapter.upsert_chunks(collection, text_chunks, embeddings, metadata_list)
        except Exception:
            # Vector indexing is non-blocking
            pass

        complete_job(job_id, result)
    except Exception as exc:
        fail_job(job_id, str(exc))


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
) -> dict:
    contents = await file.read()
    file_size_bytes = len(contents)

    try:
        validate_file(filename=file.filename or "", file_size_bytes=file_size_bytes)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    document_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    create_job(job_id=job_id, document_id=document_id)

    background_tasks.add_task(
        _run_background_analysis,
        job_id,
        document_id,
        file.filename or "contract.pdf",
        contents,
    )

    return {
        "document_id": document_id,
        "job_id": job_id,
        "filename": file.filename,
        "status": "queued",
    }