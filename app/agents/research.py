"""Research Agent — retrieves grounded information with citations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.schemas.citizen import CitizenProfile
from app.schemas.research import ResearchResult, RetrievedChunk


MODES_WITH_DATA = {"scheme"}
MIN_RERANK_SCORE = 0.5      # stricter — drop low relevance
STATE_BOOST = 5.0           # bigger boost for local schemes


def _build_query(profile: CitizenProfile) -> str:
    """Build a search query from the profile, mode-aware."""
    parts = []

    if profile.mode == "scheme":
        if profile.life_events:
            for event in profile.life_events:
                if event == "spouse_death":
                    parts.append("widow pension")
                elif event == "retirement":
                    parts.append("old age pension")
                elif event == "education_milestone":
                    parts.append("scholarship")
        if profile.category:
            parts.append(f"{profile.category} scholarship")
        if profile.age and profile.age >= 60:
            parts.append("senior citizen scheme")
        parts.append("government scheme")

    elif profile.mode == "mentor":
        parts.append("career guidance scholarship after 12th")

    elif profile.mode == "journey":
        parts.append("travel guide route itinerary")

    elif profile.mode == "care":
        parts.append("emotional support helpline")

    elif profile.mode == "companion":
        parts.append("local news")

    if not parts:
        parts.append(profile.raw_input)

    seen = set()
    unique = []
    for p in parts:
        if p.lower() not in seen:
            seen.add(p.lower())
            unique.append(p)
    return " ".join(unique)


def research(profile: CitizenProfile, top_k: int = 5) -> ResearchResult:
    """Find grounded information for the given profile."""
    # Lazy imports — heavy libraries only load when actually needed
    from app.rag.embed import embed_text
    from app.rag.vector_store import search as vector_search
    from app.rag.bm25 import get_bm25_index
    from app.rag.rrf import reciprocal_rank_fusion
    from app.rag.rerank import rerank

    query = _build_query(profile)

    if profile.mode not in MODES_WITH_DATA:
        return ResearchResult(
            query=query,
            mode=profile.mode,
            chunks=[],
            num_results=0,
            source="no_data_for_mode",
        )

    # 1. Vector search
    query_vec = embed_text(query)
    vec_results = vector_search(query_vec, n_results=15)

    vec_hits = []
    for i in range(len(vec_results["ids"][0])):
        meta = vec_results["metadatas"][0][i]
        vec_hits.append({
            "id": vec_results["ids"][0][i],
            "text": vec_results["documents"][0][i],
            "name": meta.get("name", ""),
            "doc_id": meta.get("doc_id", ""),
            "state": meta.get("state", ""),
            "mode": meta.get("mode", "scheme"),
            "source_url": meta.get("source_url", ""),
        })

    # 2. BM25 search
    bm25 = get_bm25_index()
    bm25_hits = bm25.search(query, top_k=15)

    # 3. RRF fusion
    fused = reciprocal_rank_fusion([vec_hits, bm25_hits], id_key="id")

    # 4. Rerank top 20
    reranked = rerank(query, fused[:20], text_key="text", top_k=20)

    # 5. Filter + state boost + dedupe
    user_state = (profile.state or "").lower()

    scored = []
    for r in reranked:
        chunk_state = (r.get("state", "") or "").lower()

        # State filter: if user has a state, allow only central + that state
        if user_state and chunk_state and chunk_state not in (user_state, "central"):
            continue

        score = r.get("_rerank_score", 0.0)
        if score < MIN_RERANK_SCORE:
            continue

        # Boost local schemes
        if user_state and chunk_state == user_state:
            score += STATE_BOOST

        scored.append((r, score))

    # Re-sort by adjusted score
    scored.sort(key=lambda x: x[1], reverse=True)

    # Dedupe by document
    chunks = []
    seen_docs = set()
    for r, adjusted_score in scored:
        doc_id = r.get("doc_id", "")
        if doc_id in seen_docs:
            continue
        seen_docs.add(doc_id)

        chunks.append(RetrievedChunk(
            doc_id=doc_id,
            name=r.get("name", doc_id),
            text=r["text"][:500],
            rerank_score=adjusted_score,
            source_url=r.get("source_url", ""),
            citation=f"{r.get('name', doc_id)} — {r.get('source_url', 'source not recorded')}",
        ))

        if len(chunks) >= top_k:
            break

    return ResearchResult(
        query=query,
        mode=profile.mode,
        chunks=chunks,
        num_results=len(chunks),
        source="rag",
    )


if __name__ == "__main__":
    from app.agents.understanding import understand

    sample = "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ"
    profile = understand(sample)

    print(f"\nProfile mode: {profile.mode}")
    print(f"Query built: {_build_query(profile)}\n")

    result = research(profile)
    print(f"Found {result.num_results} chunks:\n")
    for i, c in enumerate(result.chunks, 1):
        print(f"[{i}] {c.name}")
        print(f"    score: {c.rerank_score:.3f}")
        print(f"    {c.text[:150]}...\n")