"""DistilBERT clause classifier fine-tuning script.

Fine-tunes distilbert-base-uncased on CUAD clause classification data
using Hugging Face Trainer API.  Saves the best checkpoint to
ml/models/clause_classifier/.

Usage:
    python ml/experiments/train_clause_classifier.py \
        --cuad-json data/CUAD_v1.json \
        --output-dir ml/models/clause_classifier \
        --epochs 3 \
        --batch-size 8

Requirements:
    pip install transformers>=4.40 torch datasets scikit-learn
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# CUAD categories mapped to binary clause labels
CLAUSE_CATEGORIES: list[str] = [
    "Auto-Renewal",
    "Indemnification",
    "Termination For Convenience",
    "Non-Compete",
    "Confidentiality",
    "Limitation Of Liability",
    "Governing Law",
    "Dispute Resolution",
    "Ip Ownership Assignment",
    "Price Restrictions",
]

MODEL_NAME = "distilbert-base-uncased"


def load_cuad_clause_dataset(json_path: Path) -> tuple[list[str], list[list[int]]]:
    """Convert CUAD QA format into multi-label classification examples.

    Returns:
        texts:  List of contract paragraph strings.
        labels: Parallel list of binary label vectors (len == len(CLAUSE_CATEGORIES)).
    """
    logger.info("Loading %s", json_path)
    with open(json_path, encoding="utf-8") as f:
        cuad = json.load(f)

    texts: list[str] = []
    labels: list[list[int]] = []

    for article in cuad.get("data", []):
        for para in article.get("paragraphs", []):
            context: str = para["context"]
            label_vec = [0] * len(CLAUSE_CATEGORIES)

            for qa in para.get("qas", []):
                title = qa.get("id", "")
                for idx, cat in enumerate(CLAUSE_CATEGORIES):
                    if cat.lower().replace(" ", "_") in title.lower().replace(" ", "_"):
                        if qa.get("answers"):
                            label_vec[idx] = 1

            if context.strip():
                texts.append(context)
                labels.append(label_vec)

    logger.info("Loaded %d examples with %d labels each.", len(texts), len(CLAUSE_CATEGORIES))
    return texts, labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune DistilBERT for clause classification")
    parser.add_argument("--cuad-json", required=True, type=Path)
    parser.add_argument("--output-dir", default="ml/models/clause_classifier", type=Path)
    parser.add_argument("--epochs", default=3, type=int)
    parser.add_argument("--batch-size", default=8, type=int)
    parser.add_argument("--max-length", default=512, type=int)
    parser.add_argument("--dev-ratio", default=0.15, type=float)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    try:
        import torch  # noqa: PLC0415
        from datasets import Dataset  # noqa: PLC0415
        from transformers import (  # noqa: PLC0415
            AutoTokenizer,
            AutoModelForSequenceClassification,
            TrainingArguments,
            Trainer,
        )
        from sklearn.metrics import f1_score  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415
    except ImportError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run: pip install transformers torch datasets scikit-learn")

    texts, labels = load_cuad_clause_dataset(args.cuad_json)

    # Train / dev split
    split = int(len(texts) * (1 - args.dev_ratio))
    train_texts, dev_texts = texts[:split], texts[split:]
    train_labels, dev_labels = labels[:split], labels[split:]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=args.max_length,
        )

    def make_dataset(txts, lbls):
        ds = Dataset.from_dict({"text": txts, "labels": [list(map(float, l)) for l in lbls]})
        return ds.map(tokenize, batched=True, remove_columns=["text"])

    train_ds = make_dataset(train_texts, train_labels)
    dev_ds = make_dataset(dev_texts, dev_labels)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(CLAUSE_CATEGORIES),
        problem_type="multi_label_classification",
    )

    def compute_metrics(eval_pred):
        logits, label_ids = eval_pred
        probs = 1 / (1 + np.exp(-logits))
        preds = (probs >= 0.5).astype(int)
        f1_micro = f1_score(label_ids, preds, average="micro", zero_division=0)
        f1_macro = f1_score(label_ids, preds, average="macro", zero_division=0)
        return {"f1_micro": f1_micro, "f1_macro": f1_macro}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    training_args = TrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_micro",
        seed=args.seed,
        logging_steps=50,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        compute_metrics=compute_metrics,
    )

    logger.info("Starting training with %s …", MODEL_NAME)
    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))

    # Save label mapping
    label_map_path = args.output_dir / "label_map.json"
    label_map_path.write_text(json.dumps(CLAUSE_CATEGORIES, indent=2))
    logger.info("Saved model + label map to %s", args.output_dir)


if __name__ == "__main__":
    main()
