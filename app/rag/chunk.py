"""Chunk clean text into overlapping pieces."""


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """
    Split text into chunks of approximately `chunk_size` characters
    with `overlap` characters of overlap between consecutive chunks.

    Args:
        text: clean text to split
        chunk_size: target characters per chunk
        overlap: characters shared between chunks

    Returns:
        List of chunk strings.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary (period + space)
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size // 2:
                chunk = chunk[: last_period + 1]
                end = start + last_period + 1

        chunks.append(chunk.strip())
        start = end

    return [c for c in chunks if c]


if __name__ == "__main__":
    sample = "This is a sentence. " * 200
    chunks = chunk_text(sample)
    print(f"Text length: {len(sample)} chars")
    print(f"Number of chunks: {len(chunks)}")
    print(f"First chunk length: {len(chunks[0])} chars")
    print(f"Last chunk length: {len(chunks[-1])} chars")