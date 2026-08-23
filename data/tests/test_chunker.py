"""Tests for the text chunking utility."""

from data.chunker import chunk_text


def test_chunker_keeps_boundaries_within_text_length():
    text = "A" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert all(chunk["char_offset_end"] <= len(text) for chunk in chunks)
    assert all(chunk["char_offset_start"] < chunk["char_offset_end"] for chunk in chunks)


def test_chunker_returns_no_chunks_for_empty_document():
    assert chunk_text("") == []


def test_chunker_returns_single_chunk_for_short_document():
    text = "This is a short document."
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert len(chunks) == 1
    assert chunks[0]["text"] == text
    assert chunks[0]["char_offset_start"] == 0
    assert chunks[0]["char_offset_end"] == len(text)
