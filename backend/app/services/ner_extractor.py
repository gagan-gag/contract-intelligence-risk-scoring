"""Legal Named Entity Recognition (NER) service.

Primary path  : spaCy ``en_core_web_sm`` model.
Fallback path : hand-crafted regex patterns that run with zero extra
                dependencies so the app always returns valid entities
                even when spaCy is not installed.

Returned dicts are directly compatible with the ``Entity`` Pydantic schema:
    {text, entity_type, page_number, confidence}
"""
from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy lazy-loading
# ---------------------------------------------------------------------------
_nlp: Any = None  # cached spaCy model
_SPACY_AVAILABLE: bool | None = None  # None = not yet checked


def _get_spacy_nlp() -> Any | None:
    """Return a cached spaCy pipeline, or *None* if unavailable."""
    global _nlp, _SPACY_AVAILABLE

    if _SPACY_AVAILABLE is False:
        return None
    if _nlp is not None:
        return _nlp

    try:
        import spacy  # noqa: PLC0415

        _nlp = spacy.load("en_core_web_sm")
        _SPACY_AVAILABLE = True
        logger.info("spaCy en_core_web_sm loaded successfully.")
        return _nlp
    except Exception as exc:  # OSError if model missing, ImportError if spacy absent
        _SPACY_AVAILABLE = False
        logger.warning(
            "spaCy unavailable – falling back to regex NER. Reason: %s", exc
        )
        return None


# ---------------------------------------------------------------------------
# spaCy label → Entity schema entity_type mapping
# ---------------------------------------------------------------------------
_SPACY_LABEL_MAP: dict[str, str] = {
    "ORG": "party",
    "PERSON": "party",
    "GPE": "jurisdiction",   # geopolitical entity
    "LOC": "jurisdiction",
    "DATE": "date",
    "TIME": "date",
    "MONEY": "money",
    "CARDINAL": "money",     # catches bare dollar amounts like "500,000"
    "LAW": "jurisdiction",
}


def _extract_spacy(text: str, page_number: int) -> list[dict[str, Any]]:
    """Run spaCy NER and return entity dicts."""
    nlp = _get_spacy_nlp()
    if nlp is None:
        return []

    try:
        doc = nlp(text[:100_000])  # spaCy has practical length limits
        seen: set[tuple[str, str]] = set()
        results: list[dict[str, Any]] = []

        for ent in doc.ents:
            entity_type = _SPACY_LABEL_MAP.get(ent.label_)
            if entity_type is None:
                continue
            key = (ent.text.strip(), entity_type)
            if key in seen:
                continue
            seen.add(key)
            results.append(
                {
                    "text": ent.text.strip(),
                    "entity_type": entity_type,
                    "page_number": page_number,
                    "confidence": round(float(ent._.get("score", 0.85)) if ent.has_extension("score") else 0.85, 3),
                }
            )
        return results
    except Exception as exc:
        logger.warning("spaCy inference failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Regex fallback patterns
# ---------------------------------------------------------------------------
_PARTY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:[A-Z][a-zA-Z&,.\s]{2,40}(?:Inc\.?|LLC|Ltd\.?|Corp\.?|LLP|PLC|GmbH|Co\.))\b"
    ),
    re.compile(
        r'\b(?:hereinafter\s+referred\s+to\s+as\s+["\']?([A-Z][A-Za-z\s]{1,30})["\']?)',
        re.IGNORECASE,
    ),
]

_DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
    r"|\d{4}[\/\-]\d{2}[\/\-]\d{2}"
    r"|(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}"
    r"|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b",
    re.IGNORECASE,
)

_MONEY_PATTERN = re.compile(
    r"\b(?:USD|EUR|GBP|INR|AUD|CAD)?\s*\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\s*(?:million|billion|thousand|USD|EUR|GBP|INR)?\b",
    re.IGNORECASE,
)

_JURISDICTION_PATTERN = re.compile(
    r"\b(?:laws?\s+of\s+(?:the\s+)?(?:State\s+of\s+)?([A-Z][A-Za-z\s]{2,30})"
    r"|jurisdiction\s+of\s+([A-Z][A-Za-z\s]{2,20})"
    r"|courts?\s+of\s+([A-Z][A-Za-z\s]{2,20}))\b",
    re.IGNORECASE,
)


def _extract_regex(text: str, page_number: int) -> list[dict[str, Any]]:
    """Fallback regex-based entity extraction."""
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(text_val: str, entity_type: str, conf: float) -> None:
        cleaned = text_val.strip()
        if not cleaned or cleaned in seen or len(cleaned) < 2:
            return
        seen.add(cleaned)
        results.append(
            {
                "text": cleaned,
                "entity_type": entity_type,
                "page_number": page_number,
                "confidence": conf,
            }
        )

    # Parties / organisations
    for pat in _PARTY_PATTERNS:
        for m in pat.finditer(text):
            _add(m.group(0), "party", 0.70)

    # Dates
    for m in _DATE_PATTERN.finditer(text):
        _add(m.group(0), "date", 0.75)

    # Money
    for m in _MONEY_PATTERN.finditer(text):
        val = m.group(0).strip()
        if re.search(r"\d", val):  # must contain a digit
            _add(val, "money", 0.72)

    # Jurisdictions
    for m in _JURISDICTION_PATTERN.finditer(text):
        capture = next((g for g in m.groups() if g), m.group(0))
        _add(capture, "jurisdiction", 0.68)

    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_entities(text: str, page_number: int = 1) -> list[dict[str, Any]]:
    """Extract legal entities from *text*.

    Tries spaCy first; falls back to regex patterns if spaCy is unavailable
    or raises an exception.  Always returns a (possibly empty) list of dicts.

    Args:
        text:        Raw contract text for the page / chunk.
        page_number: Page the text originates from (1-indexed).

    Returns:
        List of entity dicts with keys ``text``, ``entity_type``,
        ``page_number``, and ``confidence``.
    """
    if not text or not text.strip():
        return []

    spacy_results = _extract_spacy(text, page_number)
    if spacy_results:
        return spacy_results

    # Fallback
    return _extract_regex(text, page_number)
