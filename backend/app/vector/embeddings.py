"""Embedding adapter for local sentence-transformer models with deterministic fallback."""

from __future__ import annotations

import hashlib
import os
from functools import lru_cache
from typing import Any, Sequence
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception as exc:
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


class _FallbackModel:
    """Fast deterministic 384-dimensional dense vector generator for offline/fallback use."""

    def encode(
        self,
        texts: str | list[str],
        normalize_embeddings: bool = True,
        convert_to_numpy: bool = True,
    ) -> Any:
        if isinstance(texts, str):
            texts = [texts]
        
        vectors = []
        for t in texts:
            # Deterministic 384-dim pseudo-semantic vector from sha256 & n-grams
            vec = np.zeros(384, dtype=np.float32)
            words = t.lower().split()
            for idx, w in enumerate(words):
                h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
                pos = h % 384
                weight = 1.0 / (idx + 1) ** 0.5
                vec[pos] += weight
                vec[(pos + 128) % 384] += np.sin(h % 100) * weight
                vec[(pos + 256) % 384] += np.cos(h % 100) * weight
            
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            else:
                vec[0] = 1.0
            vectors.append(vec)

        res = np.array(vectors)
        if len(texts) == 1:
            return res[0]
        return res


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str | None = None) -> Any:
    """Load and cache the sentence-transformer model with instant fallback."""
    resolved_name = model_name or _get_env_model_name()
    if SentenceTransformer is not None:
        try:
            return SentenceTransformer(resolved_name)
        except Exception:
            return _FallbackModel()
    return _FallbackModel()


class EmbeddingAdapter:
    """Adapter for generating embeddings for contract text chunks."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or _get_env_model_name()
        self._model = get_embedding_model(self.model_name)

    @property
    def model(self) -> Any:
        return self._model

    @staticmethod
    def _normalize_vector(vector: Any) -> list[float]:
        if hasattr(vector, "tolist"):
            vector = vector.tolist()
        if isinstance(vector, list) and vector and isinstance(vector[0], list):
            vector = vector[0]
        return [float(value) for value in vector]

    def encode(self, text: str | Sequence[str]) -> list[float] | list[list[float]]:
        if isinstance(text, str):
            try:
                vector = self._model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
            except Exception:
                vector = _FallbackModel().encode(text)
            return self._normalize_vector(vector)

        if isinstance(text, Sequence):
            try:
                vectors = self._model.encode(
                    list(text),
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                )
            except Exception:
                vectors = _FallbackModel().encode(list(text))
            
            if hasattr(vectors, "tolist"):
                return [self._normalize_vector(row) for row in vectors.tolist()]
            return [self._normalize_vector(row) for row in vectors]

        raise TypeError("text must be a string or a sequence of strings")


__all__ = ["EmbeddingAdapter", "get_embedding_model", "_get_env_model_name"]
