"""Legal clause extraction service.

Two-tier extraction:
  Tier 1 (primary)  : High-precision legal clause pattern matching (instant, reliable).
  Tier 2 (ML layer) : DistilBERT zero-shot classification via Hugging Face
                      ``transformers`` pipeline if loaded locally.

The extractor executes instantly and falls back gracefully with zero blocking.
"""
from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Clause labels
# ---------------------------------------------------------------------------
CLAUSE_LABELS: list[str] = [
    "auto_renewal",
    "indemnity",
    "termination",
    "confidentiality",
    "liability",
    "governing_law",
    "dispute_resolution",
    "intellectual_property",
    "payment_terms",
    "force_majeure",
]

_BERT_THRESHOLD: float = 0.50

# ---------------------------------------------------------------------------
# DistilBERT lazy-loading (optional, non-blocking)
# ---------------------------------------------------------------------------
_bert_classifier: Any = None
_BERT_AVAILABLE: bool = False  # False by default; does not block request threads


def set_bert_classifier(pipeline_instance: Any) -> None:
    """Explicitly set a pre-loaded BERT pipeline instance."""
    global _bert_classifier, _BERT_AVAILABLE
    _bert_classifier = pipeline_instance
    _BERT_AVAILABLE = True


def _classify_bert(text: str, page_number: int) -> list[dict[str, Any]]:
    """Run DistilBERT zero-shot classification over *text* if model is loaded."""
    if not _BERT_AVAILABLE or _bert_classifier is None:
        return []

    try:
        chunk = text[:1500]
        result = _bert_classifier(chunk, CLAUSE_LABELS, multi_label=True)
        found: list[dict[str, Any]] = []
        for label, score in zip(result["labels"], result["scores"]):
            if score >= _BERT_THRESHOLD:
                found.append(
                    {
                        "clause_type": label,
                        "text": text.strip()[:500],
                        "page_number": page_number,
                        "confidence": round(float(score), 3),
                    }
                )
        return found
    except Exception as exc:
        logger.debug("BERT inference skipped: %s", exc)
        return []


# ---------------------------------------------------------------------------
# High-precision Legal Clause Patterns
# ---------------------------------------------------------------------------
CLAUSE_PATTERNS: dict[str, list[str]] = {
    "auto_renewal": [
        r"automatic\s+renewal",
        r"auto-?renewal",
        r"renewal\s+clause",
        r"renew(?:s|ed|ing)?\s+automatically",
        r"unless\s+terminated.*?renew",
    ],
    "indemnity": [
        r"indemnif",
        r"hold\s+harmless",
        r"defend.*?against.*?claims",
    ],
    "termination": [
        r"termination\s+without\s+notice",
        r"terminate\s+this\s+agreement",
        r"termination\s+clause",
        r"right\s+to\s+terminate",
    ],
    "confidentiality": [
        r"confidentiality",
        r"non-disclosure",
        r"nondisclosure",
        r"proprietary\s+information",
    ],
    "liability": [
        r"unlimited\s+liability",
        r"liability\s+cap",
        r"cap\s+on\s+liability",
        r"limitation\s+of\s+liability",
        r"consequential\s+damages",
    ],
    "governing_law": [
        r"governed\s+by\s+the\s+laws",
        r"governing\s+law",
        r"applicable\s+law",
        r"jurisdiction",
    ],
    "dispute_resolution": [
        r"arbitration",
        r"dispute\s+resolution",
        r"mediation",
        r"binding\s+arbitration",
    ],
    "intellectual_property": [
        r"intellectual\s+property",
        r"work\s+for\s+hire",
        r"assigns.*?all\s+rights",
        r"ownership\s+of\s+(?:work|deliverables)",
    ],
    "payment_terms": [
        r"payment\s+terms",
        r"net\s+\d+\s+days",
        r"invoice.*?due",
        r"late\s+payment\s+(?:fee|penalty|interest)",
    ],
    "force_majeure": [
        r"force\s+majeure",
        r"act\s+of\s+god",
        r"circumstances\s+beyond.*?control",
    ],
}


def extract_legal_clauses(text: str, page_number: int = 1) -> list[dict[str, Any]]:
    """Pattern-based clause extraction."""
    found: list[dict[str, Any]] = []
    normalized = re.sub(r"\s+", " ", text or "").strip()

    for clause_type, patterns in CLAUSE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                found.append(
                    {
                        "clause_type": clause_type,
                        "text": text.strip()[:500],
                        "page_number": page_number,
                        "confidence": 0.88,
                    }
                )
                break

    return found


def classify_clauses(text: str, page_number: int = 1) -> list[dict[str, Any]]:
    """Extract and classify legal clauses in *text*.

    Always returns instant results using legal patterns, and combines with
    transformer classification if model is available.
    """
    if not text or not text.strip():
        return []

    # Instant pattern extraction ensures fast response with zero blocking
    pattern_results = extract_legal_clauses(text, page_number)
    if pattern_results:
        return pattern_results

    # Use BERT if loaded, otherwise return empty list
    bert_results = _classify_bert(text, page_number)
    return bert_results or []
