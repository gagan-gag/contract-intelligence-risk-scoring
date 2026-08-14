"""Tests for the local embedding adapter."""

from __future__ import annotations

import numpy as np

from backend.app.vector import embeddings


class FakeSentenceTransformer:
    """Minimal stand-in for SentenceTransformer used in unit tests."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(self, texts, *, normalize_embeddings: bool = True, convert_to_numpy: bool = True):
        values = []
        for _ in texts:
            values.append([0.1, 0.2, 0.3, 0.4])
        return np.asarray(values, dtype=float)


def test_embedding_adapter_returns_dense_vector_for_text(monkeypatch) -> None:
    """Text should be transformed into a dense numeric vector with expected dimensions."""
    monkeypatch.setenv("VECTOR_EMBEDDING_MODEL", "test-model")
    embeddings.get_embedding_model.cache_clear()
    monkeypatch.setattr(embeddings, "SentenceTransformer", FakeSentenceTransformer)

    adapter = embeddings.EmbeddingAdapter()
    vector = adapter.encode("This is a contract clause about confidentiality.")

    assert isinstance(vector, list)
    assert len(vector) == 4
    assert vector == [0.1, 0.2, 0.3, 0.4]
    assert adapter.model_name == "test-model"


def test_embedding_adapter_handles_batch_text_input(monkeypatch) -> None:
    """Batch input should return a matrix of vectors, one per text item."""
    monkeypatch.setenv("VECTOR_EMBEDDING_MODEL", "batch-model")
    embeddings.get_embedding_model.cache_clear()
    monkeypatch.setattr(embeddings, "SentenceTransformer", FakeSentenceTransformer)

    adapter = embeddings.EmbeddingAdapter(model_name="batch-model")
    vectors = adapter.encode(["First clause", "Second clause"])

    assert isinstance(vectors, list)
    assert len(vectors) == 2
    assert all(len(row) == 4 for row in vectors)
    assert vectors[0] == [0.1, 0.2, 0.3, 0.4]
