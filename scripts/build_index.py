"""Read knowledge_base JSONs, embed all chunks, store in ChromaDB."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.embed import embed_batch
from app.rag.vector_store import add_chunks, reset, count


KB_DIR = Path("data/knowledge_base")
CATEGORIES = ["central", "kerala", "general"]
BATCH_SIZE = 32  # how many chunks to embed at once


def collect_chunks() -> list[dict]:
    """Walk the knowledge_base folder and collect every chunk with metadata."""
    all_chunks = []
    for category in CATEGORIES:
        folder = KB_DIR / category
        if not folder.exists():
            continue

        for json_file in sorted(folder.glob("*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                doc = json.load(f)

            meta = doc.get("metadata", {})
            for i, chunk_text in enumerate(doc["chunks"]):
                chunk_id = f"{doc['doc_id']}__chunk_{i}"
                # ChromaDB metadata must be primitive types
                chunk_meta = {
                    "doc_id": doc["doc_id"],
                    "category": meta.get("category", "unknown"),
                    "state": meta.get("state") or "central",
                    "name": meta.get("name", doc["doc_id"]),
                    "life_events": ",".join(meta.get("life_events", [])),
                    "source_url": meta.get("source_url", ""),
                    "chunk_index": i,
                }
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": chunk_meta,
                })
    return all_chunks


def main():
    print("Resetting collection...")
    reset()

    print("Collecting chunks from knowledge_base...")
    chunks = collect_chunks()
    print(f"Total chunks: {len(chunks)}")

    if not chunks:
        print("No chunks found. Run run_ingestion.py first.")
        return

    print("\nEmbedding chunks (this may take 1-2 minutes)...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_batch(texts)

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    print(f"\nStoring {len(chunks)} chunks in ChromaDB...")
    # Add in batches to avoid memory issues
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        add_chunks(batch)
        print(f"  Stored {i + len(batch)} / {len(chunks)}")

    print(f"\n✅ Done. Total chunks in ChromaDB: {count()}")


if __name__ == "__main__":
    main()