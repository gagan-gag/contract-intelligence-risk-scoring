"""Tests for the spaCy NER extractor with graceful fallback validation."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.ner_extractor import extract_entities, _extract_regex

# ---------------------------------------------------------------------------
# Sample contract text representative of CUAD-style documents
# ---------------------------------------------------------------------------
SAMPLE_CONTRACT = """
SERVICES AGREEMENT

This Services Agreement ("Agreement") is entered into as of January 15, 2024,
by and between Acme Corporation Inc. (hereinafter referred to as "Company"),
a Delaware corporation, and GlobalTech Solutions LLC ("Vendor"), a California
limited liability company.

1. PAYMENT TERMS
The Company shall pay Vendor $150,000 USD per quarter, subject to a maximum
annual commitment of $600,000.

2. GOVERNING LAW
This Agreement shall be governed by the laws of the State of California.
Any disputes shall be resolved in the courts of San Francisco County.

3. TERM
This Agreement commences on January 15, 2024 and expires on December 31, 2026,
unless terminated earlier pursuant to Section 8.
"""


class TestExtractEntities:
    def test_returns_list(self):
        result = extract_entities(SAMPLE_CONTRACT)
        assert isinstance(result, list)

    def test_empty_text_returns_empty_list(self):
        assert extract_entities("") == []
        assert extract_entities("   ") == []

    def test_none_like_empty_returns_empty(self):
        assert extract_entities("") == []

    def test_entity_dict_structure(self):
        results = extract_entities(SAMPLE_CONTRACT)
        for entity in results:
            assert "text" in entity
            assert "entity_type" in entity
            assert "page_number" in entity
            assert "confidence" in entity
            assert entity["entity_type"] in {"party", "date", "money", "jurisdiction"}
            assert 0.0 <= entity["confidence"] <= 1.0
            assert entity["page_number"] >= 1

    def test_detects_dates(self):
        text = "This agreement is dated January 15, 2024 and expires December 31, 2026."
        results = extract_entities(text)
        date_entities = [e for e in results if e["entity_type"] == "date"]
        assert len(date_entities) >= 1

    def test_detects_money(self):
        text = "The fee is $150,000 USD per quarter, totalling $600,000 annually."
        results = extract_entities(text)
        money_entities = [e for e in results if e["entity_type"] == "money"]
        assert len(money_entities) >= 1

    def test_page_number_propagated(self):
        results = extract_entities("Payment of $10,000 due on March 1, 2024.", page_number=3)
        for e in results:
            assert e["page_number"] == 3


class TestRegexFallback:
    """Ensure regex NER runs correctly independent of spaCy availability."""

    def test_regex_detects_organisation(self):
        text = "Acme Corporation Inc. and GlobalTech Solutions LLC agree as follows."
        results = _extract_regex(text, page_number=1)
        party_texts = [r["text"] for r in results if r["entity_type"] == "party"]
        assert any("Inc" in t or "LLC" in t for t in party_texts)

    def test_regex_detects_date(self):
        results = _extract_regex("Effective 01/15/2024 through 12/31/2026.", 1)
        dates = [r for r in results if r["entity_type"] == "date"]
        assert len(dates) >= 1

    def test_regex_detects_money(self):
        results = _extract_regex("Total value: $500,000 USD.", 1)
        money = [r for r in results if r["entity_type"] == "money"]
        assert len(money) >= 1

    def test_regex_detects_jurisdiction(self):
        results = _extract_regex("Governed by laws of the State of California.", 1)
        jur = [r for r in results if r["entity_type"] == "jurisdiction"]
        assert len(jur) >= 1

    def test_spacy_unavailable_falls_back_to_regex(self):
        """When spaCy cannot be loaded, extract_entities must still return results."""
        import app.services.ner_extractor as ner_mod  # noqa: PLC0415

        original = ner_mod._SPACY_AVAILABLE
        try:
            ner_mod._SPACY_AVAILABLE = False
            ner_mod._nlp = None
            results = extract_entities(
                "Acme Corp Inc. signed on January 1, 2024 for $50,000."
            )
            assert isinstance(results, list)
        finally:
            ner_mod._SPACY_AVAILABLE = original
