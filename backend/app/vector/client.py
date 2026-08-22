"""Local Chroma client factory and collection helpers.

This module keeps the Day 3 vector database setup local-first. It uses the
same `Settings` values configured in Day 2 so the application can initialize a
persistent Chroma client without any external cloud credentials or API keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import get_settings

try:  # Import is intentionally lazy so tests can fail with a clear message.
    import chromadb
except Exception as exc:  # pragma: no cover - exercised by import checks
    chromadb = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def create_chroma_client(
    persist_directory: str | Path | None = None,
) -> Any:
    """Create a persistent local Chroma client.

    The client is configured to use a filesystem-backed database under the
    directory defined by the project settings. When a custom path is supplied it
    is used instead, but the directory is still created automatically.

    Args:
        persist_directory: Optional path to a local Chroma data directory.

    Returns:
        A `chromadb.PersistentClient` instance.

    Raises:
        ImportError: If `chromadb` is not installed.
    """
    if chromadb is None:
        raise ImportError(
            "chromadb is not installed. Install the project requirements to use "
            "the local vector database."
        ) from _IMPORT_ERROR

    cfg = get_settings()
    target_dir = Path(persist_directory) if persist_directory is not None else cfg.chroma_persist_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=str(target_dir))


def get_or_create_collection(
    client: Any,
    collection_name: str,
    *,
    embedding_function: Any | None = None,
    metadata: dict[str, Any] | None = None,
) -> Any:
    """Return a collection, creating it if it does not already exist.

    This helper is intentionally defensive: it supports the local-only Chroma
    workflow used by tests and the FastAPI application for Day 3 development.

    Args:
        client: A Chroma client instance returned by `create_chroma_client`.
        collection_name: Name of the collection to fetch or create.
        embedding_function: Optional embedding function to attach to the collection.
        metadata: Optional collection metadata stored alongside the collection.

    Returns:
        A Chroma collection instance.
    """
    if client is None:
        raise ValueError("A Chroma client instance is required.")

    try:
        return client.get_collection(name=collection_name)
    except (ValueError, Exception):
        return client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata=metadata,
        )


def get_or_create_test_collection(
    client: Any,
    *,
    collection_name: str = "local_test_collection",
) -> Any:
    """Create or retrieve the default local test collection used by Day 3 tests."""
    return get_or_create_collection(
        client,
        collection_name,
        metadata={
            "description": "Local-only test collection for contract intelligence testing.",
            "environment": "local",
        },
    )


__all__ = [
    "create_chroma_client",
    "get_or_create_collection",
    "get_or_create_test_collection",
]
