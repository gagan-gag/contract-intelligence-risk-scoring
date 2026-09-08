import re
from typing import Optional
from app.schemas import AnalysisResponse, Clause, Document, Entity, EntityType
from app.services.risk_engine import calculate_risk_score

REDLINE_PLAYBOOK = {
    "indemnification": {
        "mitigation": "Cap indemnification liability to 1x-2x annual contract value and make obligation mutual.",
        "redline": "Each party agrees to defend, indemnify, and hold harmless the other party from and against third-party claims arising out of gross negligence or willful misconduct, provided aggregate indemnification liability shall not exceed the total fees paid under this Agreement in the preceding twelve (12) months.",
    },
    "auto_renewal": {
        "mitigation": "Replace automatic lock-in with standard affirmative written renewal or a 30-day notice window.",
        "redline": "This Agreement shall renew for successive one (1) year periods only upon mutual written agreement of the parties executed at least thirty (30) days prior to the expiration of the then-current term.",
    },
    "liability_cap": {
        "mitigation": "Insert a clear reciprocal aggregate liability ceiling equal to 12 months fees paid.",
        "redline": "Except for breach of confidentiality obligations, neither party's aggregate liability arising under or related to this Agreement shall exceed the total amounts actually paid or payable by Customer in the twelve (12) months preceding the event giving rise to liability.",
    },
    "termination": {
        "mitigation": "Require a 30-day cure period for material breach and mutual termination for convenience without penalty.",
        "redline": "Either party may terminate this Agreement: (a) for material breach upon thirty (30) days prior written notice if such breach remains uncured; or (b) for convenience upon sixty (60) days prior written notice without penalty or early termination fee.",
    },
    "confidentiality": {
        "mitigation": "Ensure mutual confidentiality with a standard 3-5 year survival term and standard carve-outs.",
        "redline": "The receiving party shall protect disclosing party's confidential information with the same degree of care it uses for its own confidential information, surviving for a period of three (3) years from disclosure.",
    },
}


def extract_entities_from_text(text: str) -> list[Entity]:
    """Extract parties, dates, monetary values (including INR/Rupees), and jurisdictions."""
    entities: list[Entity] = []
    
    # Extract Monetary amounts (Rupees ₹, Rs., INR, USD $, Lakhs, Crores)
    money_pattern = r'((?:₹|Rs\.?|INR|\$)\s?[\d,]+(?:\.\d{1,2})?(?:\s?(?:Lakh|Lakhs|Crore|Crores|million|billion|USD|dollars|Rupees|rupees))?|[\d,]+(?:\.\d{1,2})?\s?(?:Lakh|Lakhs|Crore|Crores|INR|Rupees))'
    for match in re.finditer(money_pattern, text, re.IGNORECASE):
        val = match.group(1).strip()
        if len(val) > 1 and not any(e.text == val for e in entities):
            entities.append(
                Entity(
                    text=val,
                    entity_type=EntityType.MONEY,
                    page_number=1,
                    confidence=0.94,
                )
            )

    # Extract Dates
    date_pattern = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})'
    for match in re.finditer(date_pattern, text, re.IGNORECASE):
        val = match.group(1).strip()
        if not any(e.text == val for e in entities):
            entities.append(
                Entity(
                    text=val,
                    entity_type=EntityType.DATE,
                    page_number=1,
                    confidence=0.91,
                )
            )

    # Extract Parties (e.g. Pvt Ltd, Limited, Inc, LLC, Ltd, Corp)
    party_pattern = r'([A-Z][A-Za-z0-9\s,&.-]+(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|Limited|Ltd\.?|LLC|LLP|Inc\.?|Corporation|Corp\.?|Solutions|Enterprises|Technologies))'
    for match in re.finditer(party_pattern, text):
        val = match.group(1).strip()
        if 4 < len(val) < 65 and not any(e.text == val for e in entities):
            entities.append(
                Entity(
                    text=val,
                    entity_type=EntityType.PARTY,
                    page_number=1,
                    confidence=0.90,
                )
            )

    # Extract Jurisdictions (Indian & International jurisdictions)
    jurisdiction_pattern = r'(State of [A-Z][a-z]+|laws of [A-Z][a-z]+|High Court of [A-Z][a-z]+|Bengaluru|Bangalore|Mumbai|New Delhi|Delhi|Hyderabad|Chennai|Karnataka|Maharashtra|Delaware|New York|California|United Kingdom|England and Wales)'
    for match in re.finditer(jurisdiction_pattern, text, re.IGNORECASE):
        val = match.group(1).strip()
        if not any(e.text == val for e in entities):
            entities.append(
                Entity(
                    text=val,
                    entity_type=EntityType.JURISDICTION,
                    page_number=1,
                    confidence=0.95,
                )
            )

    return entities[:15]


def extract_clauses_from_text(text: str) -> list[Clause]:
    """Extract key risk clauses and attach AI Redline suggestions."""
    clauses: list[Clause] = []
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 25:
            continue
        s_lower = s_clean.lower()
        
        clause_type: Optional[str] = None
        confidence = 0.90

        if "indemnif" in s_lower or "hold harmless" in s_lower:
            clause_type = "indemnification"
            confidence = 0.95
        elif "automatic" in s_lower and "renew" in s_lower or "auto-renew" in s_lower:
            clause_type = "auto_renewal"
            confidence = 0.92
        elif "unlimited liability" in s_lower or "aggregate liability" in s_lower or "limitation of liability" in s_lower:
            clause_type = "liability_cap"
            confidence = 0.90
        elif "terminate without notice" in s_lower or "termination for convenience" in s_lower or "notice of termination" in s_lower:
            clause_type = "termination"
            confidence = 0.93
        elif "confidential" in s_lower and ("disclos" in s_lower or "proprietary" in s_lower or "obligation" in s_lower):
            clause_type = "confidentiality"
            confidence = 0.94

        if clause_type:
            playbook = REDLINE_PLAYBOOK.get(clause_type, {})
            clauses.append(
                Clause(
                    clause_type=clause_type,
                    text=s_clean[:320],
                    page_number=1,
                    confidence=confidence,
                    redline_suggestion=playbook.get("redline"),
                    risk_mitigation=playbook.get("mitigation"),
                )
            )

    return clauses[:10]


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
    entities = extract_entities_from_text(contract_text)
    clauses = extract_clauses_from_text(contract_text)

    return AnalysisResponse(
        document=document,
        entities=entities,
        clauses=clauses,
        risk=risk,
    )