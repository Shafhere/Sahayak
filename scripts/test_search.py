"""Test semantic search on the ChromaDB index."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.embed import embed_text
from app.rag.vector_store import search, count


def run_query(query: str, n: int = 3):
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")

    embedding = embed_text(query)
    results = search(embedding, n_results=n)

    for i in range(len(results["ids"][0])):
        chunk_id = results["ids"][0][i]
        meta = results["metadatas"][0][i]
        dist = results["distances"][0][i]
        doc = results["documents"][0][i]

        print(f"\n[{i+1}] {meta['name']} (distance: {dist:.4f})")
        print(f"    Doc: {meta['doc_id']}")
        print(f"    Text: {doc[:200]}...")


if __name__ == "__main__":
    print(f"Total chunks in DB: {count()}")

    run_query("My husband died, what help can I get?")
    run_query("I need money for my daughter's college")
    run_query("Kerala government health scheme")