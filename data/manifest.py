"""Utilities for building a document manifest from fixture directories."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List


def build_manifest(fixture_dir: str) -> List[Dict[str, Any]]:
    """Build a manifest for files in a fixture directory.

    Args:
        fixture_dir: Directory path containing source documents.

    Returns:
        A list of manifest records with document id, path, and checksum.
    """
    root = Path(fixture_dir)
    if not root.exists():
        return []

    manifest: List[Dict[str, Any]] = []
    for file_path in sorted(root.iterdir()):
        if not file_path.is_file():
            continue

        digest = hashlib.sha256()
        for chunk in iter(lambda: file_path.read_bytes(), b""):
            digest.update(chunk)

        manifest.append(
            {
                "document_id": file_path.stem,
                "path": str(file_path),
                "checksum": digest.hexdigest(),
            }
        )

    return manifest
