# Sahayak — The Story of How It Was Built

A day-by-day record. Not just what was done, but why.

---

## Prologue — The Wandering

Before Sahayak, there were many ideas: VOLT (travel), e-commerce analytics, neuro research, aviation, healthcare, agriculture, job search, second brain. Twelve ideas. Then four more. Then four more.

Each was strong. None was chosen.

Then one day, a story emerged — not from a list, but from memory.

**My grandmother is 72. She lives in a village near Kochi. For 8 years, she was eligible for a widow pension of ₹2,000 per month. She never received it — not because she didn't qualify, but because nobody told her.**

₹2,000 × 8 years = **₹1.92 lakh she never received.** Not because the system was broken — because information was fragmented, English-only, and buried.

**Sahayak** was born.

---

## Day 0 — The Clean Slate

Fresh GitHub repo. Fresh local folder.

**Set up:**
- Repository: `github.com/Shafhere/Sahayak`
- Folder structure: `app/`, `data/`, `docs/`, `tests/`, `scripts/`, `notebooks/`
- `.gitignore`, `.env.example`, `README.md`, `steps.md`

**First commit pushed.** The project existed in the world.

---

## Day 1 — The Architecture

Three diagrams drawn on paper:
1. **System Architecture** — UI → API → LangGraph → RAG/Tools/ML → DB + LangSmith
2. **Agent Workflow** — Understanding → Research → Planning → Critic → Replanner loop
3. **Journey State** — the "baton" that flows through all agents

Saved as `docs/arch_system.jpeg`, `docs/arch_workflow.jpeg`, `docs/arch_state.jpeg`.

**Why drawing first:** You can't build what you can't see.

---

## Day 2 — Choosing the Tools

Every technology must justify itself.

**The rule:** Problem → Requirement → Technology. Never "I used X because it's popular."

**Decisions:**
- **LangGraph** — the workflow has loops and branches
- **ChromaDB** — metadata-filtered vector search
- **BM25 + RRF + Cross-Encoder reranker** — scheme names need keyword AND semantic search
- **XGBoost** — eligibility is a prediction problem
- **myScheme API + MoSPI MCP** — schemes change, we need live data
- **FastAPI + PostgreSQL + Streamlit** — standard, stable, explainable
- **Docker + free-tier hosting** — deployable at $0

**Documents:** `docs/technology_selection.md`, `docs/requirements.md`

---

## Day 3 — The Contracts

Four Pydantic schemas:
- `app/schemas/citizen.py` — CitizenProfile
- `app/schemas/scheme.py` — Scheme, Eligibility
- `app/schemas/plan.py` — ActionPlan, CriticVerdict
- `app/workflows/state.py` — SahayakState (the baton, 8 compartments)

**ER diagram:** 6 tables — citizens, sessions, agent_runs, retrieval_logs, schemes, action_plans.

---

## Day 4 — The Voice

Five versioned YAML prompts — one for each agent:
- `app/prompts/understanding/v1.yaml`
- `app/prompts/research/v1.yaml`
- `app/prompts/planning/v1.yaml`
- `app/prompts/critic/v1.yaml`
- `app/prompts/replanner/v1.yaml`

**Why YAML not Python:** Prompts live outside code. Easy to version. Easy to A/B test.

---

## Day 5 — The Library

Three data sources designed:
1. Local knowledge base (curated)
2. myScheme API (live)
3. MoSPI MCP server (official stats)

**35 documents collected:** 17 central schemes, 13 Kerala schemes, 5 general guides.

**Pipeline:** Raw PDF → Extract → Clean → Tag → Chunk (500 tokens, 50 overlap) → Embed → Store in ChromaDB.

**Docs written:** `docs/data_sources.md`, `data/raw/COLLECTION_LOG.md`.

---

## Day 6 — Files Renamed

All 35 PDFs renamed to lowercase_with_underscores. Clean filenames = predictable code.

---

## Day 7 — Looking Ahead

Two documents:
- `docs/roadmap.md` — week-by-week plan
- `docs/risk_assessment.md` — 5 risk categories, top 3 risks, contingency plans

**Cut order:** multilingual → report → ML → charts. Never cut agents, RAG, Critic, Replanner.

---

## Day 8 — Sahayak Breathes

**Challenges hit and solved:**
1. Python 3.14 too new → switched venv to Python 3.11
2. Package dependency conflict → removed version pins
3. Wrong database driver → changed URL to `postgresql+psycopg2`
4. Local PostgreSQL on 5432 → moved Docker to 5433
5. Stale Docker volume with old password → `docker compose down -v`
6. Two local Postgres services (v17, v18) → stopped and disabled via admin

**Set up:**
- `.env` with Groq API key, local embeddings, DB URL
- `requirements.txt` (~30 packages)
- `docker-compose.yml` — PostgreSQL 16 on port 5433
- `scripts/test_db.py` — connection verified

**Milestone:** Sahayak runs. Python ↔ PostgreSQL working.

---

## Day 8.9 — Final Feature Set Locked

After exploring many additions, finalized V1 scope:

**Core:**
- 5 agents (Understanding, Research, Planning, Critic, Replanner)
- LangGraph orchestration
- Advanced RAG (ChromaDB + BM25 + RRF + reranker)
- Live data (myScheme API + MCP)
- XGBoost eligibility predictor
- Multilingual (EN, HI, ML, TA)

**Prompt-driven features (no architecture change):**
1. **Life Event Triggers** — "my husband died" → proactively surface widow pension, family benefit, death certificate process
2. **Deadline Dashboard** — schemes sorted by urgency
3. **"Why Not" Explainer** — for rejected schemes, show exactly what's missing

**New tools (Week 4):**
4. **Voice Input** (Groq Whisper) — Malayalam/Hindi/Tamil speech → text
5. **Document OCR** (Groq Llama 3.2 Vision) — document photo → auto-fill profile

**Schema updates applied:**
- CitizenProfile: + `life_events`
- Scheme: + `deadline_date`, `deadline_type`
- Eligibility: + `missing_requirements`

**Deferred (future_roadmap.md):**
Knowledge Graph, Family Mode, Autonomous Monitoring, Multi-Agent Debate, Power BI, Mobile app.

**V1 story:**
> "Sahayak is a multilingual agentic system that listens for life events, speaks your language, reads your documents, and turns them into a grounded, deadline-aware action plan."

---

## Day 9 — The Memory (Upcoming)

**Goal:** Define 6 SQLAlchemy models, create tables in PostgreSQL.

**Files:**
- `app/database.py` — engine + session factory + Base
- `app/models/citizen.py`, `session.py`, `agent_run.py`, `retrieval_log.py`, `scheme.py`, `action_plan.py`
- `app/models/__init__.py` — imports all
- `scripts/init_db.py` — creates tables

**Milestone:** `psql \dt` shows 6 tables.

---

## What's Coming Next

### Week 2 — Core Intelligence
- Day 9: SQLAlchemy models + DB schema
- Day 10: Document ingestion pipeline (35 PDFs → text)
- Day 11: Embeddings into ChromaDB
- Day 12: Hybrid retrieval + reranking
- Day 13: Understanding Agent (with life events)
- Day 14: Research Agent + basic LangGraph

**Milestone:** Enter a citizen profile in any language → receive schemes with citations.

### Week 3 — The Agentic Engine
- Day 15: Planning Agent (with deadline sorting)
- Day 16: Critic Agent (with "why not" logic)
- Day 17: Replanner + full LangGraph loop
- Day 18: XGBoost eligibility predictor
- Day 19: Streamlit UI skeleton
- Day 20: Multilingual support
- Day 21: End-to-end integration

**Milestone:** Full demo with replanning.

### Week 4 (+ Buffer) — Production
- Day 22: LangSmith tracing
- Day 23: Evaluation suite
- Day 24: Error handling + guardrails
- Day 25: HTML report generation
- Day 26: Docker + deployment
- Day 27: Voice + OCR tools
- Day 28: README + demo video
- Day 29–30: Buffer / pitch rehearsal

**Milestone:** Public URL live. Demo video recorded. Story ready.

---

## The Story of Sahayak

Sahayak isn't a chatbot. It's not a RAG demo. It's not a wrapper around an LLM.

**It's a system that treats information access as a design problem.**

Five agents. A stateful workflow. A critic that checks its own work. A replanner that fixes only what's broken. Grounded citations. Multilingual by default. Voice input for those who can't type. OCR for those who can't upload.

And underneath all of it — a story. A grandmother. A pension. ₹1.92 lakh she never received. Not because the system was broken, but because information was hidden.

**Sahayak makes the hidden visible.**

---

## The Rule

Every day:
```cmd
git add .
git commit -m "type: short message"
git push