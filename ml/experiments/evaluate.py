"""Model evaluation script for both NER and clause classifier.

Evaluates:
  1. spaCy NER model on a held-out CUAD dev set (.spacy)
  2. DistilBERT clause classifier on CUAD JSON dev split

Prints precision, recall, F1 per entity/clause type.

Usage:
    # Evaluate NER
    python ml/experiments/evaluate.py ner \
        --model ml/models/legal_ner/model-best \
        --dev ml/data/dev.spacy

    # Evaluate clause classifier
    python ml/experiments/evaluate.py classifier \
        --model ml/models/clause_classifier \
        --cuad-json data/CUAD_v1.json
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# NER evaluation
# ---------------------------------------------------------------------------

def evaluate_ner(model_path: Path, dev_path: Path) -> None:
    try:
        import spacy  # noqa: PLC0415
        from spacy.tokens import DocBin  # noqa: PLC0415
        from spacy.scorer import Scorer  # noqa: PLC0415
        from spacy.training import Example  # noqa: PLC0415
    except ImportError:
        raise SystemExit("spaCy required: pip install spacy>=3.7")

    logger.info("Loading model from %s", model_path)
    nlp = spacy.load(str(model_path))

    logger.info("Loading dev data from %s", dev_path)
    db = DocBin().from_disk(dev_path)
    docs = list(db.get_docs(nlp.vocab))

    examples = []
    for gold_doc in docs:
        pred_doc = nlp(gold_doc.text)
        examples.append(Example(pred_doc, gold_doc))

    scorer = Scorer()
    results = scorer.score(examples)

    print("\n=== NER Evaluation ===")
    ents_p = results.get("ents_p", 0)
    ents_r = results.get("ents_r", 0)
    ents_f = results.get("ents_f", 0)
    print(f"Overall  P={ents_p:.3f}  R={ents_r:.3f}  F1={ents_f:.3f}")

    per_type = results.get("ents_per_type", {})
    if per_type:
        print("\nPer-entity-type:")
        header = f"{'Label':<20} {'P':>7} {'R':>7} {'F1':>7}"
        print(header)
        print("-" * len(header))
        for label, scores in sorted(per_type.items()):
            p = scores.get("p", 0)
            r = scores.get("r", 0)
            f = scores.get("f", 0)
            print(f"{label:<20} {p:>7.3f} {r:>7.3f} {f:>7.3f}")


# ---------------------------------------------------------------------------
# Clause classifier evaluation
# ---------------------------------------------------------------------------

def evaluate_classifier(model_path: Path, cuad_json: Path, dev_ratio: float = 0.15) -> None:
    try:
        import numpy as np  # noqa: PLC0415
        import torch  # noqa: PLC0415
        from transformers import AutoTokenizer, AutoModelForSequenceClassification  # noqa: PLC0415
        from sklearn.metrics import classification_report  # noqa: PLC0415
    except ImportError as exc:
        raise SystemExit(f"Missing dependency: {exc}")

    label_map_path = model_path / "label_map.json"
    if not label_map_path.exists():
        raise SystemExit(f"label_map.json not found in {model_path}")

    clause_labels = json.loads(label_map_path.read_text())
    logger.info("Clause labels: %s", clause_labels)

    # Load CUAD and take the dev split (last dev_ratio fraction, reproducible)
    from ml.experiments.train_clause_classifier import load_cuad_clause_dataset  # noqa: PLC0415
    texts, labels = load_cuad_clause_dataset(cuad_json)
    split = int(len(texts) * (1 - dev_ratio))
    dev_texts = texts[split:]
    dev_labels = labels[split:]

    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
    model.eval()

    all_preds: list[list[int]] = []
    batch_size = 16
    for i in range(0, len(dev_texts), batch_size):
        batch = dev_texts[i : i + batch_size]
        enc = tokenizer(batch, truncation=True, padding=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            logits = model(**enc).logits
        probs = torch.sigmoid(logits).numpy()
        preds = (probs >= 0.5).astype(int)
        all_preds.extend(preds.tolist())

    print("\n=== Clause Classifier Evaluation ===")
    report = classification_report(
        dev_labels,
        all_preds,
        target_names=clause_labels,
        zero_division=0,
    )
    print(report)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate NER or clause classifier")
    sub = parser.add_subparsers(dest="command", required=True)

    ner_p = sub.add_parser("ner", help="Evaluate spaCy NER model")
    ner_p.add_argument("--model", required=True, type=Path, help="Path to model-best/")
    ner_p.add_argument("--dev", required=True, type=Path, help="dev.spacy path")

    cls_p = sub.add_parser("classifier", help="Evaluate clause classifier")
    cls_p.add_argument("--model", required=True, type=Path, help="Path to saved classifier")
    cls_p.add_argument("--cuad-json", required=True, type=Path)
    cls_p.add_argument("--dev-ratio", default=0.15, type=float)

    args = parser.parse_args()

    if args.command == "ner":
        evaluate_ner(args.model, args.dev)
    else:
        evaluate_classifier(args.model, args.cuad_json, args.dev_ratio)


if __name__ == "__main__":
    main()
