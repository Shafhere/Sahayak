"""Embed text using sentence-transformers (local, free)."""
from sentence_transformers import SentenceTransformer

# Load model once, reuse forever
_model = None
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def get_model() -> SentenceTransformer:
    """Load the model lazily (only when first needed)."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """Embed a single string into a 384-dim vector."""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple strings at once (much faster than one by one)."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings.tolist()


if __name__ == "__main__":
    # Quick test
    v1 = embed_text("My husband died")
    v2 = embed_text("widow")
    v3 = embed_text("I love pizza")

    print(f"Vector length: {len(v1)}")
    print(f"'husband died' → first 5: {v1[:5]}")
    print(f"'widow'        → first 5: {v2[:5]}")
    print(f"'I love pizza' → first 5: {v3[:5]}")