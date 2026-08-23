"""Clause classification baseline using TF-IDF and logistic regression."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def train_baseline(texts: Sequence[str], labels: Sequence[str]) -> Pipeline:
    """Train a TF-IDF + logistic regression clause classifier.

    Args:
        texts: Contract text snippets.
        labels: Clause labels for each snippet.

    Returns:
        A fitted sklearn pipeline.
    """
    model = Pipeline(
        steps=[
            ("vectorizer", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                    multi_class="auto",
                ),
            ),
        ]
    )
    model.fit(list(texts), list(labels))
    return model


def predict(vectorizer: TfidfVectorizer, model: LogisticRegression, text: str) -> str:
    """Predict a clause label for a single text snippet.

    Args:
        vectorizer: Fitted vectorizer used to encode text.
        model: Fitted logistic regression model.
        text: Input text to classify.

    Returns:
        The predicted label.
    """
    if not text or not text.strip():
        raise ValueError("text must be a non-empty string")

    features = vectorizer.transform([text])
    prediction = model.predict(features)
    return prediction[0]
