"""BM25 keyword search over the knowledge base chunks."""
import json
from pathlib import Path
from rank_bm25 import BM25Okapi


from app.rag.corpus import load_chunks


def load_all_chunks() -> list[dict]:
    return load_chunks()


class BM25Index:
    """In-memory BM25 index over chunks."""

    def __init__(self):
        self.chunks = load_all_chunks()
        tokenized = [(c["name"] + " " + c["text"]).lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized) if tokenized else None

    def search(self, query: str, top_k: int = 10, mode: str | None = None, state: str | None = None) -> list[dict]:
        """Return top_k chunks ranked by BM25 score."""
        if self.bm25 is None:
            return []
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        ranked = sorted(
            ((c, score) for c, score in zip(self.chunks, scores)
             if (mode is None or c["mode"] == mode)
             and (not state or c["state"] in (state.lower(), "central"))
             and score > 0),
            key=lambda x: x[1],
            reverse=True,
        )
        results = []
        for chunk, score in ranked[:top_k]:
            results.append({**chunk, "score": float(score)})
        return results


if __name__ == "__main__":
    index = BM25Index()
    print(f"Loaded {len(index.chunks)} chunks")
    results = index.search("My husband died what help can I get", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['name']} (score: {r['score']:.4f})")
        print(f"    {r['text'][:150]}...")

# Module-level singleton â€” created once, reused forever
_index_instance = None


def get_bm25_index() -> BM25Index:
    """Get or create the singleton BM25 index."""
    global _index_instance
    if _index_instance is None:
        _index_instance = BM25Index()
    return _index_instance