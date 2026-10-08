"""Reciprocal Rank Fusion (RRF) — merge multiple ranked lists."""


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict]],
    k: int = 60,
    id_key: str = "id",
) -> list[dict]:
    """
    Merge multiple ranked lists using RRF.

    RRF score = sum over lists of 1 / (k + rank)

    Args:
        ranked_lists: list of ranked lists (each item must have id_key)
        k: RRF constant (default 60, from the original paper)
        id_key: which key identifies a unique item

    Returns:
        Merged list sorted by RRF score (descending).
    """
    scores = {}
    items_by_id = {}

    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            item_id = item[id_key]
            items_by_id[item_id] = item
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)

    merged = []
    for item_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        item = dict(items_by_id[item_id])
        item["_rrf_score"] = score
        merged.append(item)

    return merged


if __name__ == "__main__":
    list_a = [{"id": "x"}, {"id": "y"}, {"id": "z"}]
    list_b = [{"id": "y"}, {"id": "x"}, {"id": "w"}]

    merged = reciprocal_rank_fusion([list_a, list_b])
    print("Merged ranking:")
    for item in merged:
        print(f"  {item['id']}  rrf={item['_rrf_score']:.5f}")