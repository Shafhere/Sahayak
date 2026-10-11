"""Research result — output of the Research Agent."""
from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    """One retrieved chunk with its source."""
    doc_id: str
    name: str
    text: str
    rerank_score: float
    source_url: str = ""
    citation: str = ""


class ResearchResult(BaseModel):
    """Result of research — retrieved chunks with metadata."""
    query: str
    mode: str
    chunks: list[RetrievedChunk] = []
    num_results: int = 0
    source: str = "rag"  # "rag" | "llm_only" | "live_api"