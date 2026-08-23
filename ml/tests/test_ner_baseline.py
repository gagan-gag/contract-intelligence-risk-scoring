from ml.ner_baseline import extract_entities

def test_extracts_money():
    result = extract_entities("The fee is \,000.00 due monthly.")
    assert "\,000.00" in result["money"]

def test_extracts_dates():
    result = extract_entities("Effective 01/15/2026.")
    assert "01/15/2026" in result["dates"]
