# Sahayak — Technology Selection

Every technology is here for a reason. No decoration.

---

## Agentic Orchestration

| Tech | Why |
|------|-----|
| **LangGraph** | The workflow has branches (documents needed?) and loops (Critic → Replanner). LangGraph handles stateful multi-agent flows with conditional edges. |
| **LangChain** | Foundation LangGraph builds on — LLM abstractions, tool calling, prompt templates. |
| **5 Agents** | Understanding · Research · Planning · Critic · Replanner. Each does one job. Together they form the pipeline. |

## RAG Layer

| Tech | Why |
|------|-----|
| **ChromaDB** | Local vector store. Simple, free, supports metadata filtering. |
| **Dense retrieval** | Semantic search — finds schemes by meaning, not just keywords. |
| **BM25 (sparse)** | Exact keyword matching — finds scheme names verbatim. |
| **RRF (Reciprocal Rank Fusion)** | Merges dense + sparse rankings into one balanced list. |
| **Cross-Encoder Reranker** | Re-scores top candidates so the most relevant appear first. |
| **Metadata filtering** | Filter schemes by state, category, gender, income bracket. |
| **Citations** | Every scheme claim links to source. Grounds the output. |

## Live Data

| Tech | Why |
|------|-----|
| **myScheme API** | Live scheme search and eligibility data. Free. |
| **MoSPI MCP Server** | Official statistics queried live — no file downloads. |
| **Tavily / DuckDuckGo API** | Web search fallback when KB has no coverage. |

## Machine Learning

| Tech | Why |
|------|-----|
| **XGBoost** | Eligibility prediction — given profile, predict which schemes match. Fast, explainable. |
| **BERT** | Semantic embeddings for scheme text understanding. |
| **scikit-learn** | Preprocessing, train/test split, evaluation metrics. |
| **pandas / NumPy** | Data cleaning and transformation. |

*(CNN/BiLSTM moved to Future Roadmap — V1 keeps ML focused.)*

## NLP & Gen AI

| Tech | Why |
|------|-----|
| **GPT-4o-mini or Groq Llama-3.1-70B** | LLM reasoning across all agents. |
| **Pydantic structured output** | Every agent returns validated JSON. No hallucinated formats. |
| **Multilingual NLU** | Detect language → reason in English → respond in user's language. |
| **Prompt versioning (YAML)** | Traceable prompts, easy A/B testing. |

## Backend

| Tech | Why |
|------|-----|
| **FastAPI** | Clean REST API, async, fast. |
| **PostgreSQL** | Persistent user profiles, agent runs, retrieval logs. |
| **SQLAlchemy** | Standard ORM. |

## Frontend

| Tech | Why |
|------|-----|
| **Streamlit** | Fast UI development. Sufficient for demo and interview. |
| **Plotly** | Interactive charts for scheme distribution and benefit estimates. |

## Observability & Quality

| Tech | Why |
|------|-----|
| **LangSmith** | Trace every agent, retrieval, and LLM call. |
| **pytest** | Unit tests for agents, rules, retrieval. |
| **Python logging** | Structured application logs. |

## Deployment

| Tech | Why |
|------|-----|
| **Docker** | Reproducible environment. |
| **Docker Compose** | Local multi-service (app + Postgres). |
| **Render** (free tier) | Host FastAPI backend. |
| **Streamlit Cloud** (free) | Host UI. |
| **Neon** (free tier) | Serverless PostgreSQL. |

**Total hosting cost: $0/month.**

## Out of Scope (Future Roadmap)

- CNN / BiLSTM for deep document classification
- OCR for scanned documents
- Voice interface
- Power BI dashboards
- CI/CD pipeline
- Direct application submission
- Mobile app

## Technology Philosophy

Every tech above exists because it solves a specific problem:

**Problem → Requirement → Technology**

Not: "I used X because it's popular."

If a technology isn't solving a real problem, it's not here.