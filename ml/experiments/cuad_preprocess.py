"""CUAD Dataset Preprocessor for spaCy NER Training.

Converts the CUAD JSON annotation format into spaCy binary training files
(train.spacy / dev.spacy) ready for `spacy train`.

Usage:
    python ml/experiments/cuad_preprocess.py \
        --cuad-json data/CUAD_v1.json \
        --output-dir ml/data \
        --dev-ratio 0.15

CUAD source: https://huggingface.co/datasets/theatticusproject/cuad
"""
from __future__ import annotations

import argparse
import json
import logging
import random
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Map CUAD question categories → spaCy NER labels
CUAD_CATEGORY_TO_LABEL: dict[str, str] = {
    "Parties": "PARTY",
    "Agreement Date": "DATE",
    "Effective Date": "DATE",
    "Expiration Date": "DATE",
    "Governing Law": "JURISDICTION",
    "Jurisdiction": "JURISDICTION",
    "Notice Period To Terminate Renewal": "DATE",
    "Revenue/Profit Sharing": "MONEY",
    "Minimum Commitment": "MONEY",
    "Price Restrictions": "MONEY",
}


def load_cuad(json_path: Path) -> dict:
    logger.info("Loading CUAD from %s", json_path)
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def cuad_to_spacy_examples(cuad_data: dict) -> list[tuple[str, dict]]:
    """Convert CUAD annotations to spaCy (text, entities) tuples."""
    try:
        import spacy  # noqa: PLC0415
        from spacy.tokens import DocBin  # noqa: PLC0415
    except ImportError:
        raise SystemExit("spaCy is required: pip install spacy>=3.7")

    examples: list[tuple[str, dict]] = []

    for article in cuad_data.get("data", []):
        for para in article.get("paragraphs", []):
            context: str = para["context"]
            spans: list[tuple[int, int, str]] = []

            for qa in para.get("qas", []):
                category = qa.get("id", "").split("__")[-1] if "__" in qa.get("id", "") else ""
                label = CUAD_CATEGORY_TO_LABEL.get(category)
                if label is None:
                    continue
                for answer in qa.get("answers", []):
                    start = answer["answer_start"]
                    end = start + len(answer["text"])
                    spans.append((start, end, label))

            if spans:
                examples.append((context, {"entities": spans}))

    logger.info("Extracted %d annotated examples from CUAD.", len(examples))
    return examples


def build_docbin(
    examples: list[tuple[str, dict]],
    nlp,
) -> "DocBin":  # type: ignore[name-defined]
    from spacy.tokens import DocBin  # noqa: PLC0415

    db = DocBin()
    skipped = 0
    for text, annotations in examples:
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                skipped += 1
                continue
            ents.append(span)
        doc.ents = ents
        db.add(doc)
    logger.info("Skipped %d misaligned spans.", skipped)
    return db


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess CUAD for spaCy NER")
    parser.add_argument("--cuad-json", required=True, type=Path, help="Path to CUAD_v1.json")
    parser.add_argument("--output-dir", default="ml/data", type=Path, help="Output directory")
    parser.add_argument("--dev-ratio", default=0.15, type=float, help="Fraction for dev set")
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    import spacy  # noqa: PLC0415

    nlp = spacy.blank("en")
    cuad_data = load_cuad(args.cuad_json)
    examples = cuad_to_spacy_examples(cuad_data)

    random.seed(args.seed)
    random.shuffle(examples)
    split = int(len(examples) * (1 - args.dev_ratio))
    train_examples = examples[:split]
    dev_examples = examples[split:]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_db = build_docbin(train_examples, nlp)
    dev_db = build_docbin(dev_examples, nlp)

    train_path = args.output_dir / "train.spacy"
    dev_path = args.output_dir / "dev.spacy"
    train_db.to_disk(train_path)
    dev_db.to_disk(dev_path)

    logger.info("Saved %d train / %d dev examples.", len(train_examples), len(dev_examples))
    logger.info("  Train: %s", train_path)
    logger.info("  Dev  : %s", dev_path)


if __name__ == "__main__":
    main()
