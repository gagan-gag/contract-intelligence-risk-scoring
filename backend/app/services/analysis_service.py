from app.schemas import AnalysisResponse, Document
from app.services.risk_engine import calculate_risk_score


def analyse_contract(
    document_id: str,
    filename: str,
    file_type: str,
    contract_text: str,
    page_count: int = 1,
) -> AnalysisResponse:
    document = Document(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        page_count=page_count,
    )

    risk = calculate_risk_score(contract_text)

    return AnalysisResponse(
        document=document,
        entities=[],
        clauses=[],
        risk=risk,
    )