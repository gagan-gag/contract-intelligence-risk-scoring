from app.schemas import RiskLevel
from app.services.analysis_service import analyse_contract


def test_contract_analysis_returns_document_and_risk() -> None:
    result = analyse_contract(
        document_id="doc-001",
        filename="sample-contract.pdf",
        file_type="pdf",
        contract_text="This agreement includes auto-renewal and unlimited liability.",
        page_count=4,
    )

    assert result.document.document_id == "doc-001"
    assert result.document.page_count == 4
    assert result.risk.level == RiskLevel.HIGH
    assert result.risk.score == 65
    assert result.entities == []
    assert result.clauses == []