from app.schemas import RiskLevel, RiskScore


RISK_RULES = {
    "auto-renewal": ("Auto-renewal clause detected.", 30),
    "automatic renewal": ("Automatic renewal language detected.", 30),
    "unlimited liability": ("Unlimited liability language detected.", 35),
    "indemnify": ("Indemnification obligation detected.", 30),
    "terminate without notice": ("Termination without notice detected.", 25),
}


def calculate_risk_score(contract_text: str) -> RiskScore:
    text = contract_text.lower()
    score = 0
    reasons: list[str] = []

    for keyword, (reason, points) in RISK_RULES.items():
        if keyword in text:
            score += points
            reasons.append(reason)

    score = min(score, 100)

    if score >= 60:
        level = RiskLevel.HIGH
    elif score >= 30:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return RiskScore(score=score, level=level, reasons=reasons)
