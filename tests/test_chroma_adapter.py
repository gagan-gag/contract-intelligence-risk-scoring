"""Tests for the Chroma adapter skeleton.

These tests verify the adapter can be constructed and attempts to
initialize a client. The test is deliberately simple — if `chromadb`
is not installed the test will assert that an ImportError is raised.
"""
from pathlib import Path

import pytest

from backend.app.vector.chroma_adapter import ChromaAdapter


def test_adapter_constructs(tmp_path: Path) -> None:
    dst = tmp_path / "chroma_test"
    adapter = ChromaAdapter(persist_directory=dst)
    assert dst.exists()


def test_adapter_init_client_or_informative_error(tmp_path: Path) -> None:
    adapter = ChromaAdapter(persist_directory=tmp_path / "chroma_test2")
    try:
        client = adapter.get_client()
        # If we got here, chromadb is installed and returned a client-like object
        assert client is not None
    except ImportError as exc:
        # Chromadb not installed in the environment — this is an expected
        # failure mode for local Day 1 scaffolding. Assert the error message
        # mentions chromadb so maintainers get a helpful hint.
        assert "chromadb" in str(exc).lower()
