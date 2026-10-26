# Mentor retrieval repair

## What changed

The research agent now accepts Mentor mode. Sparse retrieval and the dense index builder share a corpus loader that derives mode from the source folder. The existing mentor documents did not contain mode metadata, and the old dense index builder excluded that folder.

Both retrieval channels filter by mode before selecting candidates. Scheme state filtering stays within Scheme mode; mentor pathways are not discarded because of the citizen's home state. The mentor query includes interests, strengths and career_goal from follow-up answers, without assuming everyone has finished class 12.

Full retrieved passages reach the planner instead of being truncated to 500 characters. A document title no longer has to match English query words for relevant evidence to be retained. Mentor does not substitute unverified web snippets when evidence is insufficient.

The UI displays a compact next-step message for empty plans and labels mentor results as Career options. An evidence panel lists retrieved documents and explicitly marks missing source URLs. These are retrieved sources, not a claim-by-claim factual verification system.

## Required migration

Rebuild the local vector index once from the repository root:

```powershell
python scripts/build_index.py
```

This regenerates Chroma retrieval data from the JSON knowledge base. Embeddings are prepared before replacing the existing collection. Restart Streamlit afterward to refresh the in-memory BM25 corpus.

## Verification and limits

20 tests pass locally on Python 3.14.3, including real corpus loading/BM25 search, mocked dense/reranker calls, LangGraph routing and Streamlit interactions. The corpus contains 149 scheme passages and 111 mentor passages across 10 mentor documents. Biology/NEET keyword queries retrieve the NEET bulletin.

All 10 mentor documents currently lack source URLs. No URLs have been invented. Live LLM generation, real cross-encoder rankings, embedding/index rebuilding on the user's environment, and multilingual answer quality have not been verified here. The existing 0.5 reranker threshold still needs calibration. The critic remains a limited rule checker.

Next: improve source metadata and claim validation, evaluate representative questions end to end, then refine the result cards and reports.
