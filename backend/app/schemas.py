from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PARTY = "party"
    DATE = "date"
    MONEY = "money"
    JURISDICTION = "jurisdiction"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Document(BaseModel):
    document_id: str
    filename: str
    file_type: str
    page_count: int = Field(gt=0)


class Entity(BaseModel):
    text: str
    entity_type: EntityType
    page_number: int = Field(gt=0)
    confidence: float = Field(ge=0, le=1)


class Clause(BaseModel):
    clause_type: str
    text: str
    page_number: int = Field(gt=0)
    confidence: float = Field(ge=0, le=1)


class RiskScore(BaseModel):
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    reasons: list[str]


class AnalysisResponse(BaseModel):
    document: Document
    entities: list[Entity]
    clauses: list[Clause]
    risk: RiskScore
    nlp_backend: Optional[str] = None  # "spacy" | "bert" | "regex" | "heuristic"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class AnalysisJob(BaseModel):
    job_id: str
    document_id: str
    status: JobStatus = JobStatus.QUEUED
    result: Optional[AnalysisResponse] = None
    error: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: str = "queued"


class AnalysisStatusResponse(BaseModel):
    document_id: str
    status: str
    message: str