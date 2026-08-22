from app.schemas import RiskLevel
from app.services.risk_engine import calculate_risk_score


def test_low_risk_contract() -> None:
    result = calculate_risk_score("This agreement is valid for one year.")

    assert result.level == RiskLevel.LOW
    assert result.score == 0


def test_medium_risk_contract() -> None:
    result = calculate_risk_score("The customer agrees to indemnify the supplier.")

    assert result.level == RiskLevel.MEDIUM
    assert result.score == 30


def test_high_risk_contract() -> None:
    result = calculate_risk_score(
        "This contract has auto-renewal and unlimited liability."
    )

    assert result.level == RiskLevel.HIGH
    assert result.score == 65