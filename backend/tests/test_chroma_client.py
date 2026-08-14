"""Tests for the local Chroma client factory and collection helpers."""

from __future__ import annotations

from pathlib import Path

from backend.app.vector.client import create_chroma_client, get_or_create_collection


def test_create_chroma_client_connects_to_persistent_local_storage(tmp_path: Path) -> None:
    """A persistent client should initialize against a local directory."""
    persist_dir = tmp_path / "local_chroma_test"

    client = create_chroma_client(persist_directory=persist_dir)

    assert client is not None
    assert persist_dir.exists()


def test_get_or_create_collection_reuses_existing_local_collection(tmp_path: Path) -> None:
    """The collection helper should create once and reuse later without keys or cloud config."""
    persist_dir = tmp_path / "local_collection_test"
    client = create_chroma_client(persist_directory=persist_dir)

    collection = get_or_create_collection(
        client=client,
        collection_name="contract_risk_test_collection",
    )
    assert collection.name == "contract_risk_test_collection"
    assert collection.count() == 0

    collection.add(
        ids=["doc-1"],
        embeddings=[[0.1, 0.2, 0.3]],
        documents=["This is a contract clause about confidentiality."],
    )
    assert collection.count() == 1

    cached_collection = get_or_create_collection(
        client=client,
        collection_name="contract_risk_test_collection",
    )
    assert cached_collection.count() == 1
    assert cached_collection.get(ids=["doc-1"])["ids"] == ["doc-1"]
