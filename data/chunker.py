def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    chunk_id = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            "chunk_id": f"chunk-{chunk_id}",
            "text": text[start:end],
            "char_offset_start": start,
            "char_offset_end": end,
        })
        chunk_id += 1
        start += chunk_size - overlap
    return chunks
