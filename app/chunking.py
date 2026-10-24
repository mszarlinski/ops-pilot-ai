"""Document chunking.

Splits long document text into overlapping fixed-size chunks so each chunk is
small enough to be a useful retrieval unit, while the overlap preserves
context that would otherwise be lost at a chunk boundary.
"""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks of at most chunk_size characters.

    Lab 02 Step 1 exercise: implement fixed-size chunking with overlap.

    Requirements:
    - Each chunk (except possibly the last) is exactly chunk_size characters.
    - Consecutive chunks overlap by `overlap` characters.
    - The last chunk may be shorter than chunk_size.
    - If text is shorter than or equal to chunk_size, return it as a single
      chunk.

    Raises ValueError if overlap >= chunk_size, which would stop `start` from
    advancing and loop forever.
    """
    if overlap >= chunk_size:
        raise ValueError(f"overlap must be smaller than chunk_size, got {overlap} >= {chunk_size}")

    chunks = []
    start = 0

    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        if start + chunk_size >= len(text):
            break
        start += chunk_size - overlap

    return chunks
