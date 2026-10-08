"""Cross-encoder reranker for precision."""
from sentence_transformers import CrossEncoder


_model = None
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_model() -> CrossEncoder:
    """Load the cross-encoder model lazily."""
    global _model
    if _model is None:
        print(f"Loading reranker model: {MODEL_NAME}")
        _model = CrossEncoder(MODEL_NAME)
    return _model


def rerank(query: str, candidates: list[dict], text_key: str = "text", top_k: int = 5) -> list[dict]:
    """
    Re-score candidates by relevance to the query.

    Args:
        query: user query
        candidates: list of dicts, each with a text field
        text_key: which key holds the text
        top_k: how many to return

    Returns:
        Top_k candidates sorted by relevance score (descending).
    """
    if not candidates:
        return []

    model = get_model()
    pairs = [(query, c[text_key]) for c in candidates]
    scores = model.predict(pairs)

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True,
    )
    results = []
    for cand, score in ranked[:top_k]:
        item = dict(cand)
        item["_rerank_score"] = float(score)
        results.append(item)
    return results


if __name__ == "__main__":
    query = "My husband died what help can I get"
    candidates = [
        {"id": "1", "text": "A pension scheme for widows of poor families."},
        {"id": "2", "text": "A scheme for farmers to get seeds at discount."},
        {"id": "3", "text": "Financial assistance to widows below poverty line."},
    ]
    ranked = rerank(query, candidates)
    for i, r in enumerate(ranked, 1):
        print(f"[{i}] score={r['_rerank_score']:.4f}  {r['text']}")