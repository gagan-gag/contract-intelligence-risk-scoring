"""Embedding adapter for local sentence-transformer models.

This module provides a lightweight adapter that loads a sentence-transformers
model using configuration from environment variables. It is intentionally local-
first and does not rely on any cloud-based embedding service.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Sequence

try:  # sentence-transformers is optional at import time to keep runtime errors explicit.
    from sentence_transformers import SentenceTransformer
except Exception as exc:  # pragma: no cover - covered by explicit import failures
    SentenceTransformer = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def _get_env_model_name() -> str:
    """Resolve the configured embedding model name from environment variables."""
    value = os.getenv("VECTOR_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    if not value or not value.strip():
        return "sentence-transformers/all-MiniLM-L6-v2"
    return value.strip()


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str | None = None) -> Any:
    """Load and cache the sentence-transformer model.

    Args:
        model_name: Optional overrides for the model name; defaults to the
            environment variable `VECTOR_EMBEDDING_MODEL`.

    Returns:
        A loaded `SentenceTransformer` instance.

    Raises:
        ImportError: If `sentence-transformers` is not installed.
    """
    if SentenceTransformer is None:
        raise ImportError(
            "sentence-transformers is not installed. Install the project dependencies "
            "to generate local embeddings."
        ) from _IMPORT_ERROR

    resolved_name = model_name or _get_env_model_name()
    return SentenceTransformer(resolved_name)


class EmbeddingAdapter:
    """Adapter for generating embeddings for contract text chunks.

    The adapter is intentionally simple: it loads a sentence-transformers model
    once and exposes a single `encode` method for both single strings and batches.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or _get_env_model_name()
        self._model = get_embedding_model(self.model_name)

    @property
    def model(self) -> Any:
        """Return the loaded sentence-transformer model instance."""
        return self._model

    @staticmethod
    def _normalize_vector(vector: Any) -> list[float]:
        """Normalize a single embedding result to a flat list of floats."""
        if hasattr(vector, "tolist"):
            vector = vector.tolist()
        if isinstance(vector, list) and vector and isinstance(vector[0], list):
            vector = vector[0]
        return [float(value) for value in vector]

    def encode(self, text: str | Sequence[str]) -> list[float] | list[list[float]]:
        """Generate embedding vectors for one or more text inputs.

        Args:
            text: Either a single string or a sequence of strings.

        Returns:
            A dense vector for a single string or a list of vectors for a batch.
        """
        if isinstance(text, str):
            vector = self._model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
            return self._normalize_vector(vector)

        if isinstance(text, Sequence):
            vectors = self._model.encode(
                list(text),
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return [self._normalize_vector(row) for row in vectors.tolist()]

        raise TypeError("text must be a string or a sequence of strings")


__all__ = ["EmbeddingAdapter", "get_embedding_model", "_get_env_model_name"]
