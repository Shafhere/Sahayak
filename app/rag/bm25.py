"""BM25 keyword search over the knowledge base chunks."""
import json
from pathlib import Path
from rank_bm25 import BM25Okapi


KB_DIR = Path("data/knowledge_base")
CATEGORIES = ["central", "kerala", "general", "mentor", "journey"]


def load_all_chunks() -> list[dict]:
    """Load every chunk from knowledge_base JSONs."""
    chunks = []
    for category in CATEGORIES:
        folder = KB_DIR / category
        if not folder.exists():
            continue
        for json_file in sorted(folder.glob("*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                doc = json.load(f)
            meta = doc.get("metadata", {})
            for i, chunk_text in enumerate(doc["chunks"]):
                chunks.append({
                    "id": f"{doc['doc_id']}__chunk_{i}",
                    "text": chunk_text,
                    "doc_id": doc["doc_id"],
                    "name": meta.get("name", doc["doc_id"]),
                    "category": meta.get("category", "unknown"),
                    "state": meta.get("state") or "central",
                    "mode": meta.get("mode", "scheme"),
                })
    return chunks


class BM25Index:
    """In-memory BM25 index over chunks."""

    def __init__(self):
        self.chunks = load_all_chunks()
        tokenized = [c["text"].lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Return top_k chunks ranked by BM25 score."""
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        ranked = sorted(
            zip(self.chunks, scores),
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