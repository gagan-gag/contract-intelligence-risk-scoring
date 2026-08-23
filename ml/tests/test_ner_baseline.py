"""Tests for the regex-based entity extraction baseline."""

from ml.ner_baseline import extract_entities


def test_extract_entities_finds_money_values():
    text = "The fee is $1,250.00 due within 30 days from 2025-01-15."
    entities = extract_entities(text)

    assert "$1,250.00" in entities["money"]
    assert "2025-01-15" in entities["dates"]


def test_extract_entities_finds_dates_and_parties():
    text = "Vendor Contoso shall begin on Jan 15, 2025 and end before 2026-02-01."
    entities = extract_entities(text)

    assert "Jan 15, 2025" in entities["dates"]
    assert "2026-02-01" in entities["dates"]
    assert "Contoso" in entities["parties"]
