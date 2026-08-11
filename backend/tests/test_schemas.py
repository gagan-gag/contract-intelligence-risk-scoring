from app.schemas import (
    AnalysisResponse,
    Clause,
    Document,
    Entity,
    EntityType,
    RiskLevel,
    RiskScore,
)


def test_analysis_response_schema() -> None:
    response = AnalysisResponse(
        document=Document(
            document_id="doc-001",
            filename="sample-contract.pdf",
            file_type="pdf",
            page_count=5,
        ),
        entities=[
            Entity(
                text="Acme Pvt Ltd",
                entity_type=EntityType.PARTY,
                page_number=1,
                confidence=0.95,
            )
        ],
        clauses=[
            Clause(
                clause_type="termination",
                text="Either party may terminate...",
                page_number=3,
                confidence=0.90,
            )
        ],
        risk=RiskScore(
            score=72,
            level=RiskLevel.HIGH,
            reasons=["Auto-renewal clause detected"],
        ),
    )

    assert response.document.document_id == "doc-001"
    assert response.risk.level == RiskLevel.HIGH
    assert response.risk.score == 72