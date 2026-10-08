"""Test hybrid search: vector + BM25 + RRF + rerank."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.embed import embed_text
from app.rag.vector_store import search as vector_search, count
from app.rag.bm25 import BM25Index
from app.rag.rrf import reciprocal_rank_fusion
from app.rag.rerank import rerank


_bm25_index = None


def get_bm25_index():
    global _bm25_index
    if _bm25_index is None:
        print("Loading BM25 index...")
        _bm25_index = BM25Index()
    return _bm25_index


def hybrid_search(query: str, top_k: int = 5, verbose: bool = True):
    """Run vector + BM25, fuse with RRF, rerank."""
    # 1. Vector search
    query_vec = embed_text(query)
    vec_results = vector_search(query_vec, n_results=10)
    vec_hits = []
    for i in range(len(vec_results["ids"][0])):
        vec_hits.append({
            "id": vec_results["ids"][0][i],
            "text": vec_results["documents"][0][i],
            "name": vec_results["metadatas"][0][i].get("name", ""),
            "doc_id": vec_results["metadatas"][0][i].get("doc_id", ""),
            "state": vec_results["metadatas"][0][i].get("state", ""),
            "mode": vec_results["metadatas"][0][i].get("mode", "scheme"),
        })

    # 2. BM25 search
    bm25_hits = get_bm25_index().search(query, top_k=10)

    # 3. RRF fusion
    fused = reciprocal_rank_fusion([vec_hits, bm25_hits], id_key="id")

    # 4. Rerank top 20
    reranked = rerank(query, fused[:20], text_key="text", top_k=top_k)

    if verbose:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")
        for i, r in enumerate(reranked, 1):
            print(f"\n[{i}] {r.get('name', r.get('doc_id'))}")
            print(f"    rerank: {r['_rerank_score']:.4f}  rrf: {r.get('_rrf_score', 0):.5f}")
            print(f"    {r['text'][:180]}...")

    return reranked


if __name__ == "__main__":
    print(f"Total chunks in DB: {count()}")

    queries = [
        "My husband died, what help can I get?",
        "I need money for my daughter's college",
        "Kerala government health scheme",
        "I am a widow and need pension",
        "Scholarship for OBC students after 12th",
    ]

    for q in queries:
        hybrid_search(q, top_k=3)