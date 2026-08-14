"""Vector storage package for local Chroma-backed implementations.

This package contains the persistence adapter for Day 1, the Chroma client
factory for Day 3, and the embedding adapter for Day 4.
"""

from .chroma_adapter import ChromaAdapter
from .client import create_chroma_client, get_or_create_collection, get_or_create_test_collection
from .embeddings import EmbeddingAdapter, get_embedding_model

__all__ = [
    "ChromaAdapter",
    "EmbeddingAdapter",
    "create_chroma_client",
    "get_or_create_collection",
    "get_or_create_test_collection",
    "get_embedding_model",
]
