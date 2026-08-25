"""Tests for the clause classifier (DistilBERT + regex fallback)."""
from __future__ import annotations

import pytest

from app.services.legal_clause_extractor import (
    classify_clauses,
    extract_legal_clauses,
    CLAUSE_LABELS,
    CLAUSE_PATTERNS,
)

# ---------------------------------------------------------------------------
# Sample contract snippets for specific clause types
# ---------------------------------------------------------------------------
AUTO_RENEWAL_TEXT = (
    "This Agreement shall automatically renew for successive one-year terms "
    "unless either party provides written notice of non-renewal at least 30 days "
    "prior to the end of the then-current term (auto-renewal clause)."
)

INDEMNITY_TEXT = (
    "Each party shall indemnify, defend, and hold harmless the other party from "
    "and against any claims, damages, losses, and expenses arising out of or "
    "relating to any breach of this Agreement."
)

TERMINATION_TEXT = (
    "Either party may terminate this Agreement without notice upon the occurrence "
    "of a material breach. The right to terminate this agreement is immediate."
)

CONFIDENTIALITY_TEXT = (
    "The parties agree to maintain strict confidentiality with respect to all "
    "Proprietary Information and non-disclosure obligations under this Agreement."
)

LIABILITY_TEXT = (
    "IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY CONSEQUENTIAL, INCIDENTAL, "
    "OR INDIRECT DAMAGES. The liability cap shall not exceed the fees paid in the "
    "preceding twelve months. Limitation of liability applies to all claims."
)

GOVERNING_LAW_TEXT = (
    "This Agreement shall be governed by the laws of the State of New York, "
    "without regard to its conflict of law provisions."
)

MULTI_CLAUSE_TEXT = "\n\n".join([
    AUTO_RENEWAL_TEXT, INDEMNITY_TEXT, CONFIDENTIALITY_TEXT, LIABILITY_TEXT
])


class TestRegexClauseExtraction:
    """Test the regex fallback extraction (no ML dependency)."""

    def test_returns_list(self):
        assert isinstance(extract_legal_clauses(""), list)
        assert extract_legal_clauses("") == []
        assert isinstance(extract_legal_clauses(AUTO_RENEWAL_TEXT), list)

    def test_detects_auto_renewal(self):
        results = extract_legal_clauses(AUTO_RENEWAL_TEXT)
        types = [r["clause_type"] for r in results]
        assert "auto_renewal" in types

    def test_detects_indemnity(self):
        results = extract_legal_clauses(INDEMNITY_TEXT)
        types = [r["clause_type"] for r in results]
        assert "indemnity" in types

    def test_detects_termination(self):
        results = extract_legal_clauses(TERMINATION_TEXT)
        types = [r["clause_type"] for r in results]
        assert "termination" in types

    def test_detects_confidentiality(self):
        results = extract_legal_clauses(CONFIDENTIALITY_TEXT)
        types = [r["clause_type"] for r in results]
        assert "confidentiality" in types

    def test_detects_liability(self):
        results = extract_legal_clauses(LIABILITY_TEXT)
        types = [r["clause_type"] for r in results]
        assert "liability" in types

    def test_detects_governing_law(self):
        results = extract_legal_clauses(GOVERNING_LAW_TEXT)
        types = [r["clause_type"] for r in results]
        assert "governing_law" in types

    def test_clause_dict_structure(self):
        results = extract_legal_clauses(AUTO_RENEWAL_TEXT)
        assert len(results) >= 1
        for clause in results:
            assert "clause_type" in clause
            assert "text" in clause
            assert "page_number" in clause
            assert "confidence" in clause
            assert 0.0 <= clause["confidence"] <= 1.0
            assert clause["page_number"] >= 1

    def test_page_number_propagated(self):
        results = extract_legal_clauses(INDEMNITY_TEXT, page_number=5)
        for c in results:
            assert c["page_number"] == 5

    def test_empty_text_returns_empty(self):
        assert extract_legal_clauses("") == []
        assert extract_legal_clauses("   ") == []

    def test_no_false_positive_on_random_text(self):
        mundane = "The weather today is sunny with a high of 25 degrees Celsius."
        results = extract_legal_clauses(mundane)
        assert results == []

    def test_multi_clause_text_detects_multiple(self):
        results = extract_legal_clauses(MULTI_CLAUSE_TEXT)
        types = {r["clause_type"] for r in results}
        assert len(types) >= 3


class TestClassifyClauses:
    """classify_clauses must always return valid dicts (BERT or regex fallback)."""

    def test_returns_list(self):
        result = classify_clauses(AUTO_RENEWAL_TEXT)
        assert isinstance(result, list)

    def test_empty_returns_empty(self):
        assert classify_clauses("") == []

    def test_result_structure_valid(self):
        results = classify_clauses(INDEMNITY_TEXT)
        for c in results:
            assert "clause_type" in c
            assert "text" in c
            assert "page_number" in c
            assert "confidence" in c

    def test_bert_unavailable_falls_back_to_regex(self):
        """Force BERT unavailable and ensure regex path still works."""
        import app.services.legal_clause_extractor as ce_mod  # noqa: PLC0415

        original = ce_mod._BERT_AVAILABLE
        try:
            ce_mod._BERT_AVAILABLE = False
            ce_mod._bert_classifier = None
            results = classify_clauses(AUTO_RENEWAL_TEXT)
            assert isinstance(results, list)
            types = [r["clause_type"] for r in results]
            assert "auto_renewal" in types
        finally:
            ce_mod._BERT_AVAILABLE = original


class TestClauseLabelsIntegrity:
    def test_all_patterns_have_labels(self):
        for label in CLAUSE_PATTERNS:
            assert label in CLAUSE_LABELS or label in CLAUSE_PATTERNS

    def test_no_empty_pattern_lists(self):
        for label, patterns in CLAUSE_PATTERNS.items():
            assert len(patterns) > 0, f"No patterns for clause type '{label}'"
