"""Research Agent — retrieves grounded information with citations."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.schemas.citizen import CitizenProfile
from app.schemas.research import ResearchResult, RetrievedChunk
from langsmith import traceable

MODES_WITH_DATA = {"scheme", "mentor"}
MIN_RERANK_SCORE = 0.5
# Cross-encoder logits are not probabilities. Reviewed career catalogues use a
# separate cutoff, checked against supported paraphrases and unrelated controls.
MIN_MENTOR_RERANK_SCORE = -1.0
STATE_BOOST = 5.0           # bigger boost for local schemes


def _build_query(profile: CitizenProfile) -> str:
    """Build a search query from the profile AND raw input."""
    parts = []

    if profile.retrieval_query.strip():
        parts.append(profile.retrieval_query.strip())

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
        parts.append("What education and courses lead to " + (profile.career_goal or "a suitable career") + "?")
        if profile.education_level:
            parts.append(profile.education_level)
        parts.extend(profile.subjects)
        parts.extend(profile.interests)
        parts.extend(profile.strengths)
        if profile.career_goal:
            parts.append(profile.career_goal)

    elif profile.mode == "journey":
        parts.append("travel guide route itinerary")

    elif profile.mode == "care":
        parts.append("emotional support helpline")

    elif profile.mode == "companion":
        parts.append("local news")

    # ALWAYS include raw_input words too — profile may be incomplete
    if profile.raw_input:
        parts.append(profile.raw_input)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in parts:
        if p.lower() not in seen:
            seen.add(p.lower())
            unique.append(p)
    return " ".join(unique)


def _source_matches_intent(doc_id: str, query: str) -> bool:
    """Avoid confusing exam bulletins that share school-subject vocabulary.

    Apply only to known, narrowly scoped entrance bulletins and explicit career
    terms. General exploration and comparisons retain both sources.
    """
    medical = bool(re.search(r"\b(doctor|medicine|medical|mbbs|bds|dentist|neet)\b", query, re.I))
    other = bool(re.search(r"\b(engineering|engineer|architecture|architect|jee|b[ .-]?tech|commerce|accounting|accountancy|business|finance|software|computer)\b", query, re.I))
    if doc_id == "nta_neet_2026" and other and not medical:
        return False
    if doc_id == "nta_jee_2026" and medical and not other:
        return False
    return True


@traceable(run_type="chain", name="2. Research Agent")
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
    vec_results = vector_search(query_vec, n_results=25, mode=profile.mode,
                                state=profile.state if profile.mode == "scheme" else None)

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
            "page": meta.get("page", 0),
            "edition": meta.get("edition", ""),
            "retrieved_on": meta.get("retrieved_on", ""),
        })

    # 2. BM25 search
    bm25 = get_bm25_index()
    bm25_hits = bm25.search(query, top_k=25, mode=profile.mode,
                             state=profile.state if profile.mode == "scheme" else None)

    # 3. RRF fusion
    fused = reciprocal_rank_fusion([vec_hits, bm25_hits], id_key="id")

    # Exclude clearly mismatched entrance bulletins before reranking.
    if profile.mode == "mentor":
        fused = [c for c in fused if _source_matches_intent(c.get("doc_id", ""), query)]

    # 4. Rerank with source context.
    for candidate in fused:
        candidate["ranking_text"] = candidate.get("name", "") + "\n" + candidate["text"]
    reranked = rerank(query, fused[:35], text_key="ranking_text", top_k=35)

    # 5. Filter + state boost + dedupe
    user_state = (profile.state or "").lower()

    scored = []
    for r in reranked:
        if r.get("mode") != profile.mode:
            continue
        chunk_state = (r.get("state", "") or "").lower()

        # State filter: if user has a state, allow only central + that state
        if profile.mode == "scheme" and user_state and chunk_state and chunk_state not in (user_state, "central"):
            continue

        score = r.get("_rerank_score", 0.0)
        cutoff = MIN_MENTOR_RERANK_SCORE if profile.mode == "mentor" else MIN_RERANK_SCORE
        if score < cutoff:
            continue

        # Boost local schemes
        if profile.mode == "scheme" and user_state and chunk_state == user_state:
            score += STATE_BOOST

        scored.append((r, score))

    # Re-sort by adjusted score
    scored.sort(key=lambda x: x[1], reverse=True)

    # Dedupe by document
    chunks = []
    seen_docs = {}
    max_per_doc = 3 if profile.mode == "scheme" else 1

    for r, adjusted_score in scored:
        doc_id = r.get("doc_id", "")
        if seen_docs.get(doc_id, 0) >= max_per_doc:
            continue
        seen_docs[doc_id] = seen_docs.get(doc_id, 0) + 1

        chunks.append(RetrievedChunk(
            chunk_id=r["id"], page=r.get("page", 0), edition=r.get("edition", ""),
            retrieved_on=r.get("retrieved_on", ""),
            doc_id=doc_id,
            name=r.get("name", doc_id),
            text=r["text"],
            rerank_score=adjusted_score,
            source_url=r.get("source_url", ""),
            citation=f"{r.get('name', doc_id)} — {r.get('source_url', 'source not recorded')}",
        ))

        if len(chunks) >= top_k:
            break

    # ------------------------------------------------------------------
    # Fallback: if the KB did not return strong, relevant content, try a
    # live web search so the citizen gets a starting point instead of an
    # empty "Let's narrow the search" screen.
    #
    # - Mentor mode: fire when fewer than 3 KB chunks were kept.
    # - Scheme mode: fire when 0 KB chunks were kept OR when every kept
    #   chunk is only weakly relevant (rerank_score < 1.0). This prevents
    #   a marginally-matching widow-pension chunk from blocking a real
    #   web result for an unrelated query (e.g. SC scholarship).
    # ------------------------------------------------------------------
    needs_web_fallback = False
    web_query = ""



    if profile.mode == "mentor" and profile.career_goal:
        career = profile.career_goal.strip()
        education = (profile.education_level or "beginner").strip()

        if any(
            word in career.lower()
            for word in (
                "software",
                "developer",
                "programming",
                "coding",
                "web development",
            )
        ):
            needs_web_fallback = True
            web_query = (
                "beginner web development curriculum Python JavaScript HTML CSS "
                "hands-on projects official documentation MDN freeCodeCamp"
            )



    elif profile.mode == "scheme":
        # "Weak" means below a real relevance threshold, not merely below 1.0
        # (a widow chunk scoring 0.98 is strong and must NOT trigger web).
        weak_only = all(c.rerank_score < 0.75 for c in chunks)
        if len(chunks) == 0 or (weak_only and len(chunks) < 3):
            needs_web_fallback = True
            parts = []
            if profile.retrieval_query:
                parts.append(profile.retrieval_query)
            else:
                parts.append(profile.raw_input)
            if profile.state:
                parts.append(profile.state)
            if profile.category and profile.category != "general":
                parts.append(profile.category.upper())
            parts.append("scheme")
            # Keep the query short (6-8 words). DuckDuckGo returns far better
            # snippets for focused queries than for full sentences.
            web_query = " ".join(" ".join(parts).split()[:8])

    if needs_web_fallback and web_query:
        try:
            from app.tools.web_search import search as web_search
            remaining = min(3, top_k) if profile.mode == "mentor" else max(0, top_k - len(chunks))
            web_results = (
                web_search(web_query, max_results=min(3, remaining))
                if remaining else []
            )
            if profile.mode == "mentor" and web_results:
                chunks = chunks[:max(0, top_k - len(web_results))]
            for i, r in enumerate(web_results):
                if not r.get("snippet"):
                    continue
                chunks.append(RetrievedChunk(
                    chunk_id=f"web_{i}",
                    doc_id=f"web_{i}",
                    name=r.get("title") or "Web result",
                    text=r["snippet"],
                    source_url=r.get("url") or "",
                    page=0,
                    edition="",
                    retrieved_on="",
                    rerank_score=1.0,
                    citation=r.get("url") or "",
                ))
        except Exception:
            pass

    return ResearchResult(
        query=query,
        mode=profile.mode,
        chunks=chunks,
        num_results=len(chunks),
        source="rag",
        diagnostics={"dense_doc_ids": list(dict.fromkeys(c["doc_id"] for c in vec_hits))[:5],
                     "sparse_doc_ids": list(dict.fromkeys(c["doc_id"] for c in bm25_hits))[:5],
                     "fused_doc_ids": list(dict.fromkeys(c["doc_id"] for c in fused))[:5],
                     "dense_candidates": len(vec_hits), "sparse_candidates": len(bm25_hits),
                     "fused_candidates": len(fused), "kept": len(chunks),
                     "web_fallback_used": needs_web_fallback,
                     "top_rerank_score": reranked[0].get("_rerank_score") if reranked else None},
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