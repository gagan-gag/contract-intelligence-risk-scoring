"""Chroma adapter skeleton for local persistent storage.

This module provides a small `ChromaAdapter` class that encapsulates
initialization of a local, persistent Chroma client. It is intentionally
lightweight for Day 1 — add indexing and query helpers as needed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from backend.app.config import get_settings

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


__all__ = ["ChromaAdapter"]
