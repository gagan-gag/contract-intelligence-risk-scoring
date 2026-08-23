"""Utility for chunking long text into fixed-size windows."""

from __future__ import annotations

from typing import Any, Dict, List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """Chunk text into overlapping windows.

    Args:
        text: Source text to split.
        chunk_size: Maximum size of each chunk.
        overlap: Number of shared characters between adjacent chunks.

    Returns:
        List of chunk dictionaries with chunk metadata.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    content = text or ""
    if not content:
        return []

    chunks: List[Dict[str, Any]] = []
    step = chunk_size - overlap
    start = 0
    index = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunks.append(
            {
                "chunk_id": index,
                "text": content[start:end],
                "char_offset_start": start,
                "char_offset_end": end,
            }
        )
        index += 1
        if end == len(content):
            break
        start += step

    return chunks
