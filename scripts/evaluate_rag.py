"""Evaluate RAG retrieval quality against a golden dataset."""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

GOLDEN_PATH = Path("data/eval/golden_queries.json")


def load_golden() -> list[dict]:
    """Load the golden query dataset."""
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["queries"]


def run_retrieval(query: str, top_k: int = 5) -> list[str]:
    """Run hybrid retrieval, return list of doc_ids in ranked order."""
    from app.rag.embed import embed_text
    from app.rag.vector_store import search as vector_search
    from app.rag.bm25 import get_bm25_index
    from app.rag.rrf import reciprocal_rank_fusion
    from app.rag.rerank import rerank

    # Vector search
    query_vec = embed_text(query)
    vec_results = vector_search(query_vec, n_results=15, mode="scheme")
    vec_hits = []
    for i in range(len(vec_results["ids"][0])):
        meta = vec_results["metadatas"][0][i]
        vec_hits.append({
            "id": vec_results["ids"][0][i],
            "text": vec_results["documents"][0][i],
            "doc_id": meta.get("doc_id", ""),
            "name": meta.get("name", ""),
        })

    # BM25
    bm25 = get_bm25_index()
    bm25_hits = bm25.search(query, top_k=15, mode="scheme")

    # RRF
    fused = reciprocal_rank_fusion([vec_hits, bm25_hits], id_key="id")

    # Rerank
    reranked = rerank(query, fused[:20], text_key="text", top_k=top_k)

    # Extract doc_ids in ranked order (dedupe by doc)
    doc_ids = []
    seen = set()
    for r in reranked:
        doc_id = r.get("doc_id", "")
        if doc_id and doc_id not in seen:
            seen.add(doc_id)
            doc_ids.append(doc_id)
    return doc_ids


def evaluate() -> dict:
    """Run evaluation across all golden queries."""
    queries = load_golden()
    results = []

    for item in queries:
        qid = item["id"]
        query = item["query"]
        expected = item["expected_docs"]

        ranked = run_retrieval(query, top_k=5)

        # Find rank of first expected doc
        rank = None
        for i, doc_id in enumerate(ranked):
            if doc_id in expected:
                rank = i + 1  # 1-based
                break

        results.append({
            "id": qid,
            "query": query,
            "expected": expected,
            "retrieved": ranked,
            "rank": rank,
        })

    # Calculate metrics
    total = len(results)
    top1 = sum(1 for r in results if r["rank"] == 1)
    top3 = sum(1 for r in results if r["rank"] and r["rank"] <= 3)
    top5 = sum(1 for r in results if r["rank"] and r["rank"] <= 5)

    # MRR (Mean Reciprocal Rank)
    mrr = sum(1 / r["rank"] if r["rank"] else 0 for r in results) / total

    # Precision@3 (fraction of top 3 that are expected)
    prec_at_3_sum = 0
    for r in results:
        top_3 = r["retrieved"][:3]
        relevant = sum(1 for d in top_3 if d in r["expected"])
        prec_at_3_sum += relevant / 3 if top_3 else 0
    precision_at_3 = prec_at_3_sum / total

    return {
        "total": total,
        "top1": top1,
        "top3": top3,
        "top5": top5,
        "top1_pct": round(100 * top1 / total, 2),
        "top3_pct": round(100 * top3 / total, 2),
        "top5_pct": round(100 * top5 / total, 2),
        "mrr": round(mrr, 4),
        "precision_at_3": round(precision_at_3, 4),
        "results": results,
    }


def print_report(metrics: dict, save_path: str = None) -> None:
    """Print a clean report and optionally save as JSON."""
    print("=" * 70)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 70)
    print(f"\nTotal queries: {metrics['total']}")
    print(f"Top-1 accuracy: {metrics['top1']}/{metrics['total']} "
          f"({metrics['top1_pct']}%)")
    print(f"Top-3 accuracy: {metrics['top3']}/{metrics['total']} "
          f"({metrics['top3_pct']}%)")
    print(f"Top-5 accuracy: {metrics['top5']}/{metrics['total']} "
          f"({metrics['top5_pct']}%)")
    print(f"MRR: {metrics['mrr']}")
    print(f"Precision@3: {metrics['precision_at_3']}")

    print("\n" + "-" * 70)
    print("PER-QUERY BREAKDOWN")
    print("-" * 70)
    for r in metrics["results"]:
        mark = "OK " if r["rank"] == 1 else ("-- " if r["rank"] is None else "..")
        rank_str = f"#{r['rank']}" if r["rank"] else "MISS"
        print(f"  [{mark}] {r['id']}  {rank_str:6s}  {r['query'][:50]}")

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"\nFull results saved to {save_path}")


if __name__ == "__main__":
    start = time.time()
    metrics = evaluate()
    elapsed = time.time() - start

    print_report(metrics, save_path="data/eval/baseline_results.json")
    print(f"\nTotal time: {elapsed:.1f}s")