"""Persistent document-analysis metadata repository.

Document-level analysis data is stored in a small SQLite sidecar next to the
local Chroma database. Chroma remains responsible for vector retrieval, while
this repository provides durable document metadata lookup by ``document_id``.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.app.config import get_settings
from backend.app.schemas import RiskLevel


ProcessingStatus = Literal["pending", "processing", "completed", "failed"]


class DocumentAnalysisMetadata(BaseModel):
    """Validated document details and analysis output persisted by the store."""

    document_id: str = Field(min_length=1, max_length=128)
    filename: str = Field(min_length=1, max_length=512)
    file_type: str = Field(min_length=1, max_length=100)
    page_count: int = Field(gt=0)
    processing_status: ProcessingStatus = "pending"
    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    risk_reasons: list[str] = Field(default_factory=list)
    summary: str | None = None
    chunk_count: int = Field(default=0, ge=0)
    entities: list[dict[str, Any]] = Field(default_factory=list)
    clauses: list[dict[str, Any]] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentAnalysisStore:
    """SQLite-backed repository for document-level analysis metadata.

    The repository uses an upsert keyed by ``document_id``. Saving the same
    document after additional chunks or analysis have been processed replaces
    the previous snapshot, keeping retrieval deterministic and idempotent.
    """

    def __init__(self, database_path: str | Path | None = None) -> None:
        """Create the repository and initialize its local database schema."""
        if database_path is None:
            database_path = get_settings().chroma_persist_dir / "document_analysis.sqlite3"
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        """Open a connection configured to return rows by column name."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        """Create the metadata table if this is a new local database."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS document_analysis (
                    document_id TEXT PRIMARY KEY,
                    metadata_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save_document_analysis(
        self,
        metadata: DocumentAnalysisMetadata | dict[str, Any],
    ) -> DocumentAnalysisMetadata:
        """Validate and persist a document-analysis metadata snapshot.

        Args:
            metadata: A validated model or a mapping accepted by the model.

        Returns:
            The normalized metadata that was persisted.
        """
        record = (
            metadata
            if isinstance(metadata, DocumentAnalysisMetadata)
            else DocumentAnalysisMetadata.model_validate(metadata)
        )
        record_json = record.model_dump(mode="json")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO document_analysis (document_id, metadata_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
                """,
                (
                    record.document_id,
                    json.dumps(record_json, sort_keys=True),
                    record.updated_at.isoformat(),
                ),
            )
        return record

    def get_document_analysis(self, document_id: str) -> DocumentAnalysisMetadata | None:
        """Fetch document-analysis metadata by ID, or return ``None`` if absent."""
        if not document_id or not document_id.strip():
            raise ValueError("document_id must not be blank.")

        with self._connect() as connection:
            row = connection.execute(
                "SELECT metadata_json FROM document_analysis WHERE document_id = ?",
                (document_id,),
            ).fetchone()

        if row is None:
            return None
        try:
            return DocumentAnalysisMetadata.model_validate(json.loads(row["metadata_json"]))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Stored metadata for document_id={document_id!r} is invalid."
            ) from exc

    def delete_document_analysis(self, document_id: str) -> bool:
        """Delete a document snapshot and report whether a row was removed."""
        if not document_id or not document_id.strip():
            raise ValueError("document_id must not be blank.")

        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM document_analysis WHERE document_id = ?",
                (document_id,),
            )
        return cursor.rowcount > 0


__all__ = [
    "DocumentAnalysisMetadata",
    "DocumentAnalysisStore",
    "ProcessingStatus",
]
