"""Regex-based entity extraction baseline for contract clauses."""

from __future__ import annotations

import re
from typing import Dict, List


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract a minimal set of contract entities using regex rules.

    Args:
        text: Raw contract text.

    Returns:
        A dictionary containing lists of detected money values, dates, and
        parties.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return {"money": [], "dates": [], "parties": []}

    money_pattern = r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
    date_pattern = r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*\s+\d{1,2},\s+\d{4})\b"

    money = re.findall(money_pattern, cleaned, flags=re.IGNORECASE)
    dates = re.findall(date_pattern, cleaned, flags=re.IGNORECASE)

    parties = []
    for token in ["Acme Corp", "Contoso", "Northwind", "Zenith", "Vendor", "Customer", "Supplier"]:
        if token.lower() in cleaned.lower():
            parties.append(token)

    # Deduplicate while keeping order.
    money = list(dict.fromkeys(money))
    dates = list(dict.fromkeys(dates))
    parties = list(dict.fromkeys(parties))

    return {"money": money, "dates": dates, "parties": parties}
