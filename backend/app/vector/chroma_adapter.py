"""Chroma adapter skeleton for local persistent storage.

This module provides a small `ChromaAdapter` class that encapsulates
initialization of a local, persistent Chroma client. It is intentionally
lightweight for Day 1 — add indexing and query helpers as needed.
"""
from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence
from typing import Any, Optional

from app.config import get_settings
from app.vector.schemas import VectorChunkMetadata

try:  # chromadb is optional for Day 1 scaffolding; importing here makes
    # runtime error explicit when tests or app attempt to initialize.
    import chromadb
except Exception:  # pragma: no cover - import errors surfaced in tests
    chromadb = None


class ChromaAdapter:
    """Adapter to manage a local persistent Chroma client.

    Example:
        adapter = ChromaAdapter()
        client = adapter.get_client()  # initializes lazily
    """

    def __init__(self, persist_directory: Optional[Path] = None) -> None:
        cfg = get_settings()
        self.persist_directory: Path = (
            Path(persist_directory) if persist_directory is not None else cfg.chroma_persist_dir
        )
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = None

    def init_client(self):
        """Create and return a persistent Chroma client.

        This method uses the modern chromadb.PersistentClient API for local,
        persistent storage. If `chromadb` is not importable an ImportError is
        raised so calling code can provide a helpful message.

        Returns:
            chromadb.PersistentClient: A persistent Chroma client instance.

        Raises:
            ImportError: If chromadb is not installed.
        """
        if chromadb is None:
            raise ImportError(
                "chromadb is not installed — install chromadb to use the adapter"
            )

        # Use the modern PersistentClient API for local storage
        client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._client = client
        return client

    def get_client(self):
        """Return an initialized client, initializing if necessary.

        Returns:
            chromadb.Client: A persistent Chroma client instance.

        Raises:
            ImportError: If chromadb is not installed.
        """
        if self._client is None:
            return self.init_client()
        return self._client

    def upsert_chunks(
        self,
        collection: Any,
        text_chunks: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        metadata: Sequence[VectorChunkMetadata],
    ) -> list[str]:
        """Upsert embedded contract chunks into a Chroma collection.

        ``chunk_id`` is used as the Chroma ID. Chroma replaces an existing
        record when an upsert uses the same ID, so retrying this operation is
        idempotent and cannot create duplicate chunks.

        Args:
            collection: Chroma collection exposing its ``upsert`` method.
            text_chunks: Original text for each chunk.
            embeddings: Embedding vector corresponding to each text chunk.
            metadata: Validated metadata corresponding to each text chunk.

        Returns:
            The chunk IDs submitted to Chroma.

        Raises:
            ValueError: If inputs are empty, lengths differ, or IDs repeat.
        """
        if not text_chunks:
            raise ValueError("At least one text chunk is required.")
        if len(text_chunks) != len(embeddings) or len(text_chunks) != len(metadata):
            raise ValueError("text_chunks, embeddings, and metadata must have the same length.")

        chunk_ids = [chunk.chunk_id for chunk in metadata]
        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("chunk_id values must be unique within an upsert batch.")

        collection.upsert(
            ids=chunk_ids,
            embeddings=[list(embedding) for embedding in embeddings],
            documents=list(text_chunks),
            metadatas=[self._to_chroma_metadata(chunk) for chunk in metadata],
        )
        return chunk_ids

    @staticmethod
    def _to_chroma_metadata(chunk: VectorChunkMetadata) -> dict[str, Any]:
        """Convert schema metadata to Chroma's scalar metadata format."""
        values = chunk.to_chroma_metadata()
        return {
            key: ",".join(values[key]) if key == "quality_flags" else value
            for key, value in values.items()
            if value is not None
        }

    @staticmethod
    def semantic_search(
        collection: Any,
        query_text: str,
        embedding_adapter: Any,
        *,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Find the nearest contract chunks for a natural-language query.

        The adapter is expected to expose ``encode(text)`` and return one
        embedding vector for the supplied query. Chroma returns each result
        field in a list grouped by query, so the returned mapping contains the
        first (and only) query result set in Chroma's native format.

        Args:
            collection: Chroma collection exposing its ``query`` method.
            query_text: Natural-language text to search for.
            embedding_adapter: Embedding adapter with an ``encode`` method.
            top_k: Maximum number of nearest chunks to return.
            where: Optional Chroma metadata filter, such as
                ``{"document_id": "document-12345678"}``.

        Returns:
            Chroma query results containing IDs, documents, metadata, and
            distances.

        Raises:
            ValueError: If the query is blank or ``top_k`` is invalid.
            TypeError: If the embedding adapter returns a batch instead of a
                single query vector.
        """
        if not query_text or not query_text.strip():
            raise ValueError("query_text must not be blank.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_embedding = embedding_adapter.encode(query_text)
        if not query_embedding or isinstance(query_embedding[0], (list, tuple)):
            raise TypeError("embedding_adapter.encode must return one query vector.")

        query_kwargs: dict[str, Any] = {
            "query_embeddings": [list(query_embedding)],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where is not None:
            query_kwargs["where"] = where

        return collection.query(**query_kwargs)


__all__ = ["ChromaAdapter"]
