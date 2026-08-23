from data.chunker import chunk_text

def test_chunk_boundaries():
    text = "a" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert all(c["char_offset_end"] <= len(text) for c in chunks)

def test_empty_document():
    assert chunk_text("") == []

def test_short_document():
    chunks = chunk_text("short text", chunk_size=500)
    assert len(chunks) == 1
