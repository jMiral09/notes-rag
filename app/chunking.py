"""Text chunking helpers (pure Python, no heavy dependencies)."""

import uuid

CHUNK_SIZE = 500     # approx characters per chunk
CHUNK_OVERLAP = 80   # characters of overlap between chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping character-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap  # step forward, keeping overlap
    return chunks


def build_chunks_with_metadata(pages: list[tuple[int, str]], pillar: str) -> list[dict]:
    """Chunk each page's text and attach metadata (pillar, page number)."""
    records = []
    for page_num, page_text in pages:
        for chunk in chunk_text(page_text):
            records.append({
                "id": str(uuid.uuid4()),
                "text": chunk,
                "pillar": pillar,
                "page": page_num,
            })
    return records
