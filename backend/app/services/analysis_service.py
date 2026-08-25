"""Contract analysis orchestrator.

Integrates:
  - spaCy NER entity extraction (with regex fallback)
  - DistilBERT clause classification (with regex fallback)
  - Rule-based risk scoring

All NLP calls are wrapped in try/except so a failure in either NLP layer
never prevents a valid ``AnalysisResponse`` from being returned.
"""
from __future__ import annotations

import logging

from app.schemas import AnalysisResponse, Clause, Document, Entity, EntityType
from app.services.legal_clause_extractor import classify_clauses
from app.services.ner_extractor import extract_entities
from app.services.risk_engine import calculate_risk_score

logger = logging.getLogger(__name__)

# Valid entity_type values from the schema
_VALID_ENTITY_TYPES: set[str] = {e.value for e in EntityType}


def _safe_entity(raw: dict) -> Entity | None:
    """Convert a raw NER dict to an Entity, returning None on validation error."""
    try:
        et = raw.get("entity_type", "")
        if et not in _VALID_ENTITY_TYPES:
            return None
        return Entity(
            text=raw["text"],
            entity_type=EntityType(et),
            page_number=int(raw.get("page_number", 1)),
            confidence=float(raw.get("confidence", 0.5)),
        )
    except Exception as exc:
        logger.debug("Skipping malformed entity dict %s: %s", raw, exc)
        return None


def _safe_clause(raw: dict) -> Clause | None:
    """Convert a raw clause dict to a Clause, returning None on validation error."""
    try:
        return Clause(
            clause_type=str(raw["clause_type"]),
            text=str(raw.get("text", ""))[:500],  # cap text length
            page_number=int(raw.get("page_number", 1)),
            confidence=float(raw.get("confidence", 0.5)),
        )
    except Exception as exc:
        logger.debug("Skipping malformed clause dict %s: %s", raw, exc)
        return None


def analyse_contract(
    document_id: str,
    filename: str,
    file_type: str,
    contract_text: str,
    page_count: int = 1,
) -> AnalysisResponse:
    """Analyse a contract document and return a structured response.

    Args:
        document_id:   Unique identifier for the uploaded document.
        filename:      Original filename of the uploaded document.
        file_type:     Detected file type (``"pdf"`` or ``"docx"``).
        contract_text: Full plain-text content of the contract.
        page_count:    Number of pages in the document (≥1).

    Returns:
        An ``AnalysisResponse`` with entities, clauses, and a risk score.
        Returns empty entity/clause lists if NLP extraction fails.
    """
    document = Document(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        page_count=page_count,
    )

    # --- Entity extraction (spaCy → regex fallback) ---
    entities: list[Entity] = []
    try:
        raw_entities = extract_entities(contract_text, page_number=1)
        entities = [e for raw in raw_entities if (e := _safe_entity(raw)) is not None]
    except Exception as exc:
        logger.warning("Entity extraction failed entirely: %s", exc)

    # --- Clause classification (DistilBERT → regex fallback) ---
    clauses: list[Clause] = []
    try:
        raw_clauses = classify_clauses(contract_text, page_number=1)
        clauses = [c for raw in raw_clauses if (c := _safe_clause(raw)) is not None]
    except Exception as exc:
        logger.warning("Clause classification failed entirely: %s", exc)

    # --- Risk scoring (always rule-based, always succeeds) ---
    risk = calculate_risk_score(contract_text)

    return AnalysisResponse(
        document=document,
        entities=entities,
        clauses=clauses,
        risk=risk,
    )