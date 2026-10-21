"""Warm up models so first query is fast."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print("Loading embedding model...")
from app.rag.embed import get_model
get_model()

print("Loading BM25 index...")
from app.rag.bm25 import get_bm25_index
get_bm25_index()

print("Loading reranker...")
from app.rag.rerank import get_model as get_rerank_model
get_rerank_model()

print("✅ All models loaded. First query will be fast.")