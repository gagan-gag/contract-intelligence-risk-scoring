import pytest

from ml.clause_baseline import ClauseBaselineModel, calibrate_confidence, score_clause_text


def test_score_clause_text_detects_risk_terms() -> None:
    score = score_clause_text("Auto-renewal clause with unlimited liability and indemnity obligations")
    assert score["risk_level"] == "high"
    assert score["score"] >= 70
    assert "auto_renewal" in score["matched_terms"]


def test_calibrate_confidence_clamps_to_valid_range() -> None:
    assert 0.0 <= calibrate_confidence(1.2) <= 1.0
    assert 0.0 <= calibrate_confidence(-0.2) <= 1.0
    assert calibrate_confidence(0.75) == pytest.approx(0.75)


def test_clause_baseline_model_predicts_labels() -> None:
    model = ClauseBaselineModel()
    result = model.predict("This agreement may auto-renew with indemnity obligations")
    assert result["predicted_label"] in {"risk", "compliance", "liability"}
    assert result["confidence"] >= 0.0
