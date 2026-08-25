"""Tests for the analysis orchestrator service."""
from __future__ import annotations

from app.schemas import RiskLevel
from app.services.analysis_service import analyse_contract


CONTRACT_WITH_RISK = (
    "This agreement includes auto-renewal and unlimited liability. "
    "Each party shall indemnify the other. "
    "Acme Corporation Inc. signed on January 15, 2024."
)

PLAIN_CONTRACT = (
    "This simple service agreement between Vendor LLC and Client Corp "
    "is effective March 1, 2024."
)


def test_contract_analysis_returns_document_and_risk() -> None:
    result = analyse_contract(
        document_id="doc-001",
        filename="sample-contract.pdf",
        file_type="pdf",
        contract_text=CONTRACT_WITH_RISK,
        page_count=4,
    )

    assert result.document.document_id == "doc-001"
    assert result.document.page_count == 4
    assert result.risk.level == RiskLevel.HIGH
    assert result.risk.score >= 60


def test_entities_is_always_a_list() -> None:
    result = analyse_contract(
        document_id="doc-002",
        filename="contract.pdf",
        file_type="pdf",
        contract_text=CONTRACT_WITH_RISK,
        page_count=1,
    )
    assert isinstance(result.entities, list)


def test_clauses_is_always_a_list() -> None:
    result = analyse_contract(
        document_id="doc-003",
        filename="contract.pdf",
        file_type="pdf",
        contract_text=CONTRACT_WITH_RISK,
        page_count=1,
    )
    assert isinstance(result.clauses, list)


def test_entity_schema_compliance() -> None:
    """Every entity must have required fields with valid types."""
    result = analyse_contract(
        document_id="doc-004",
        filename="contract.pdf",
        file_type="pdf",
        contract_text=PLAIN_CONTRACT,
        page_count=1,
    )
    for entity in result.entities:
        assert hasattr(entity, "text")
        assert hasattr(entity, "entity_type")
        assert 0.0 <= entity.confidence <= 1.0
        assert entity.page_number >= 1


def test_clause_schema_compliance() -> None:
    """Every clause must have required fields with valid types."""
    result = analyse_contract(
        document_id="doc-005",
        filename="contract.pdf",
        file_type="pdf",
        contract_text=CONTRACT_WITH_RISK,
        page_count=1,
    )
    for clause in result.clauses:
        assert hasattr(clause, "clause_type")
        assert hasattr(clause, "text")
        assert 0.0 <= clause.confidence <= 1.0
        assert clause.page_number >= 1


def test_empty_text_still_returns_valid_response() -> None:
    """Even with empty text, all required fields are present."""
    result = analyse_contract(
        document_id="doc-006",
        filename="empty.pdf",
        file_type="pdf",
        contract_text="",
        page_count=1,
    )
    assert result.document.document_id == "doc-006"
    assert isinstance(result.entities, list)
    assert isinstance(result.clauses, list)
    assert result.risk.score == 0
    assert result.risk.level == RiskLevel.LOW