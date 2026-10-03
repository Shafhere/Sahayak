"""ChromaDB wrapper for storing and searching embeddings."""
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = "schemes"


def get_client():
    """Return a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_or_create_collection():
    """Get the schemes collection, or create it if missing."""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunks: list[dict]) -> None:
    """
    Add chunks to the collection.

    Each chunk dict must have:
      - id: unique string
      - text: the chunk text
      - embedding: list of floats
      - metadata: dict of extra fields
    """
    collection = get_or_create_collection()
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )


def search(query_embedding: list[float], n_results: int = 5) -> dict:
    """Search for the most similar chunks to a query embedding."""
    collection = get_or_create_collection()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


def count() -> int:
    """Return the number of chunks stored."""
    collection = get_or_create_collection()
    return collection.count()


def reset() -> None:
    """Delete the collection (useful for re-building the index)."""
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted collection: {COLLECTION_NAME}")
    except Exception:
        pass


if __name__ == "__main__":
    reset()
    print(f"Collection reset. Current count: {count()}")