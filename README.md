# Sahayak

**Multilingual Agentic System for Government Scheme Discovery**

A 5-agent system that takes a citizen's profile in their own language, researches all applicable government schemes, validates eligibility, and produces a cited action plan.

## The Story
My grandmother missed a pension she qualified for because the information was English-only and buried. Millions of Indians face the same problem. Sahayak solves it.

## Architecture
- **5 Agents:** Understanding · Research · Planning · Critic · Replanner
- **Orchestration:** LangGraph
- **RAG:** ChromaDB + hybrid retrieval + reranking
- **Live Data:** myScheme API + MCP server
- **ML:** XGBoost eligibility predictor + BERT document classifier
- **Backend:** FastAPI + PostgreSQL
- **UI:** Streamlit
- **Observability:** LangSmith

## Status
🚧 Week 1 — Planning
