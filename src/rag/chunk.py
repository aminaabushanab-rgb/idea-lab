def chunk_text(text: str, size: int = 1000, overlap: int = 150):
    if not text: return []
    out, step = [], max(1, size - overlap)
    for i in range(0, max(len(text) - overlap, 0), step):
        out.append(text[i:i+size])
    return out or [text]

