from app.services.legal_clause_extractor import extract_legal_clauses


def test_extract_legal_clauses_finds_common_clause_patterns() -> None:
    text = """
    This agreement contains an automatic renewal clause. The parties agree to indemnify each other.
    Termination without notice is permitted. Confidentiality obligations remain in force.
    """

    clauses = extract_legal_clauses(text)

    assert any(clause["clause_type"] == "auto_renewal" for clause in clauses)
    assert any(clause["clause_type"] == "indemnity" for clause in clauses)
    assert any(clause["clause_type"] == "termination" for clause in clauses)
    assert any(clause["clause_type"] == "confidentiality" for clause in clauses)
    assert all(clause["page_number"] >= 1 for clause in clauses)
