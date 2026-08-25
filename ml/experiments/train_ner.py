"""spaCy NER training script for legal entities.

Trains a custom NER model on preprocessed CUAD data and saves the best
model to ml/models/legal_ner/.

Prerequisites:
    1. Run cuad_preprocess.py to generate ml/data/train.spacy and dev.spacy
    2. pip install spacy>=3.7 torch

Usage:
    python ml/experiments/train_ner.py \
        --train ml/data/train.spacy \
        --dev ml/data/dev.spacy \
        --output-dir ml/models/legal_ner \
        --epochs 20
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NER_LABELS = ["PARTY", "DATE", "MONEY", "JURISDICTION"]


def build_config(train_path: Path, dev_path: Path, output_dir: Path) -> str:
    """Generate a minimal spaCy config for NER training."""
    return f"""
[paths]
train = "{train_path.as_posix()}"
dev = "{dev_path.as_posix()}"

[system]
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["tok2vec", "ner"]

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 96
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"
moves = null
update_with_oracle_cut_size = 100

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true
nO = null

[components.ner.model.tok2vec]
@ref = "components.tok2vec.model"

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"
seed = 42
gpu_allocator = null
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
max_steps = 20000
eval_frequency = 200
frozen_components = []
annotating_components = []
before_to_disk = null
before_update = null

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2
get_length = null

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
t = 0.0

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = false
eps = 1e-8

[training.optimizer.learn_rate]
@schedules = "warmup_linear.v1"
warmup_steps = 250
total_steps = 20000
initial_rate = 5e-4

[training.score_weights]
ents_f = 1.0
ents_p = 0.0
ents_r = 0.0
ents_per_type = null

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${{paths.train}}
max_length = 0
gold_preproc = false
limit = 0
augmenter = null

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${{paths.dev}}
max_length = 0
gold_preproc = false
limit = 0
augmenter = null
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Train spaCy NER on CUAD data")
    parser.add_argument("--train", default="ml/data/train.spacy", type=Path)
    parser.add_argument("--dev", default="ml/data/dev.spacy", type=Path)
    parser.add_argument("--output-dir", default="ml/models/legal_ner", type=Path)
    parser.add_argument("--epochs", default=20, type=int)
    args = parser.parse_args()

    try:
        import spacy  # noqa: PLC0415
        from spacy.cli.train import train  # noqa: PLC0415
    except ImportError:
        raise SystemExit("spaCy is required: pip install spacy>=3.7")

    if not args.train.exists():
        raise SystemExit(f"Training data not found: {args.train}. Run cuad_preprocess.py first.")
    if not args.dev.exists():
        raise SystemExit(f"Dev data not found: {args.dev}. Run cuad_preprocess.py first.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    config_path = args.output_dir / "config.cfg"
    config_path.write_text(build_config(args.train, args.dev, args.output_dir))

    logger.info("Starting spaCy NER training → %s", args.output_dir)
    train(config_path, output_path=args.output_dir, use_gpu=-1)
    logger.info("Training complete. Model saved to %s", args.output_dir)
    logger.info("To use: spacy.load('%s')", args.output_dir / "model-best")


if __name__ == "__main__":
    main()
