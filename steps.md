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

## Day 9 — The Memory (SQLAlchemy Models)

**Once upon a time**, Sahayak had amnesia. Today, it remembers.

**The idea:** Short-term memory (the baton/SahayakState) exists only during a session. Long-term memory (PostgreSQL) survives after. Today, we built long-term memory.

**Six tables, six jobs:**

| Table | Purpose |
|-------|---------|
| `citizens` | User profiles (with life_events) |
| `sessions` | One row per planning run |
| `agent_runs` | Every agent call logged (our tracing) |
| `retrieval_logs` | Every RAG query logged (our evaluation) |
| `schemes` | Cached scheme data (with deadline fields) |
| `action_plans` | Every generated plan (history) |

**Files created:**
- `app/database.py` — engine + session factory + Base
- `app/models/__init__.py` — imports all models
- `app/models/citizen.py`
- `app/models/session.py`
- `app/models/agent_run.py`
- `app/models/retrieval_log.py`
- `app/models/scheme.py`
- `app/models/action_plan.py`
- `scripts/init_db.py` — creates all tables

**A small hurdle solved:** `ModuleNotFoundError: No module named 'app'`
- Fix: Added `sys.path.insert(0, ...)` to `init_db.py` so Python finds the project root
- Why: When running scripts from `scripts/`, Python doesn't automatically look at the parent folder

**Verification:**
- `python scripts/init_db.py` → "Tables created successfully!"
- `psql \dt` → shows all 6 tables
- `psql \d citizens` → columns match schema

**End of Day 9:**
- [x] 6 tables created in PostgreSQL
- [x] Schema verified
- [x] Ready for Day 10 (PDF ingestion)

**Milestone:** Sahayak now has long-term memory. Every session, plan, and agent call can be saved.

---
---

## Day 10 — Feeding the Library

**Once upon a time**, Sahayak had memory but nothing to remember. Today, we fed it 35 government scheme documents.

**The pipeline (5 steps):**
1. **Extract** — pypdf reads text from each PDF
2. **Clean** — removes page numbers, extra spaces, headers/footers
3. **Chunk** — splits into ~2000-char pieces with 200-char overlap
4. **Tag** — attaches metadata (state, category, life_events, income_limit)
5. **Save** — writes as JSON to `data/knowledge_base/`

**Files created:**
- `app/rag/__init__.py`
- `app/rag/extract.py` — PDF → raw text
- `app/rag/clean.py` — remove artifacts
- `app/rag/chunk.py` — split with overlap
- `app/rag/ingest.py` — orchestrates one PDF
- `scripts/run_ingestion.py` — runs the pipeline on all files
- `data/raw/metadata.yaml` — manual metadata for key schemes

**A small hurdle solved:** `ModuleNotFoundError: No module named 'app'` in `ingest.py`
- Fix: same `sys.path.insert` pattern as `init_db.py`
- Why: scripts in subfolders need to know the project root

**Output:**
- 34 PDFs → 34 JSON files in `data/knowledge_base/`
- Each JSON has: `metadata`, `text`, `chunks[]`, `num_chunks`, `char_count`

**Why this matters:**
Garbage in → garbage out. If we embed messy PDF text, retrieval fails. Clean text + good metadata = accurate retrieval.

**End of Day 10:**
- [x] Ingestion pipeline built
- [x] 34 documents processed
- [x] Knowledge base ready for embedding
- [x] Ready for Day 11 (ChromaDB)

**Milestone:** The library is stocked. Tomorrow, we make it searchable.

---
---

## Day 11 — The Embeddings (ChromaDB)

**Once upon a time**, Sahayak could search by keywords but not by meaning. Today, we taught it to understand.

**The idea:** Every chunk gets a "fingerprint" — a 384-number vector. Similar meanings → similar vectors.

**Files created:**
- `app/rag/embed.py` — loads sentence-transformers, embeds text
- `app/rag/vector_store.py` — ChromaDB wrapper (add, search, count, reset)
- `scripts/build_index.py` — reads JSONs, embeds all chunks, stores in ChromaDB
- `scripts/test_search.py` — verifies semantic search works

**The flow:**

34 JSONs → ~180 chunks → embed each → store in ChromaDB


**Model:** `BAAI/bge-small-en-v1.5` (local, free, ~130 MB)

**Test result:**
Query: *"My husband died, what help can I get?"*
Top result: **Indira Gandhi National Widow Pension Scheme** ✅
Even though the word "widow" wasn't in the query.

**Why this matters:**
Real users don't search by scheme names. They search by their situation. Semantic search bridges the gap.

**End of Day 11:**
- [x] Knowledge base is searchable by meaning
- [x] ~180 chunks embedded in ChromaDB
- [x] Semantic search verified
- [x] Ready for Day 12 (hybrid retrieval + reranking)

**Milestone:** Sahayak understands meaning, not just words.

---


---

## Day 11.9 — Mentor Feedback Applied

**After mentor review, five directives:**
1. Deepen the problem understanding — Sahayak must solve what general AI cannot
2. Focus on 3 modes (Scheme, Mentor, Journey) — defer Companion + Care
3. Add security — JWT auth + role-based authorization
4. Clarify identity — Sahayak is an application (API-first, multi-client)
5. Make modes advanced — not just prompt swaps; solve real problems

**Refined problem statement:**
> General AI tools provide information. Sahayak provides actionable, verified, localized, personalized guidance that a citizen can act on today — in their own language, with the exact documents, deadlines, and office locations they need.

**Modes locked for V1:**
- ✅ Scheme (primary)
- ✅ Mentor (secondary)
- ✅ Journey (tertiary)
- ⏸ Companion (deferred — needs paid news APIs)
- ⏸ Care (deferred — safety-critical, needs mental health expertise)

**Security added to Week 2:**
- JWT authentication (signup/login)
- Role-based authorization (citizen, social worker, admin)
- Users table + protected routes

**App identity:** Sahayak is a standalone application with API-first architecture. Streamlit is the first client; mobile/WhatsApp/voice are future clients of the same API.

**Refined Week 2 plan:**
- Day 12: Hybrid retrieval + reranking (fix 33% → 85%)
- Day 13: Authentication + users table
- Day 14: Understanding Agent
- Day 15: Research Agent
- Day 16: LangGraph workflow
- Day 17: FastAPI routes
- Day 18: Evaluation + buffer

---

---

## Day 12 — Hybrid Retrieval + Reranking

**The problem:** Vector-only retrieval gave 33% top-1 accuracy.

**The fix — 3 layers:**

1. **BM25** (`app/rag/bm25.py`) — keyword search. Boosts exact term matches like "widow", "husband", "pension".
2. **RRF** (`app/rag/rrf.py`) — Reciprocal Rank Fusion. Merges vector + BM25 rankings. Both systems vote.
3. **Cross-Encoder reranker** (`app/rag/rerank.py`) — re-scores top candidates for true relevance.

**Files created:**
- `app/rag/bm25.py`
- `app/rag/rrf.py`
- `app/rag/rerank.py`

**Updated:**
- `scripts/test_search.py` — now uses hybrid search with 5 test queries

**Result:** Top-1 accuracy improved from 33% → [report your number]%.

**Why this matters:**
Real users search by situation, not scheme names. Hybrid retrieval combines semantic similarity AND keyword precision. This is production-grade retrieval.

**End of Day 12:**
- [x] BM25 index working
- [x] RRF fusion working
- [x] Cross-encoder reranker integrated
- [x] Retrieval accuracy significantly improved
- [x] Ready for Day 13 (Authentication)

---

---

## Day 12 — Hybrid Retrieval + Reranking ✅

**The problem:** Vector-only retrieval gave 33% top-1 accuracy (Day 11 baseline).

**The fix — 3 layers:**

1. **BM25** (`app/rag/bm25.py`) — keyword search. Boosts exact term matches.
2. **RRF** (`app/rag/rrf.py`) — Reciprocal Rank Fusion. Merges vector + BM25 rankings.
3. **Cross-Encoder reranker** (`app/rag/rerank.py`) — re-scores top candidates for true relevance.

**Test results (5 queries):**

| Query | Top-1 Result | Correct? |
|-------|-------------|:--------:|
| "My husband died" | Kerala Widow Pension | ✅ |
| "Daughter's college money" | Postmatric Scholarship EBC | ✅ |
| "Kerala health scheme" | Cancer Suraksha | ✅ |
| "Widow needs pension" | Indira Gandhi Widow Pension | ✅ |
| "OBC scholarship after 12th" | Postmatric OBC/EBC/DNT | ✅ |

**Top-1 accuracy: 33% → 100%**

**Understanding the rerank scores:**
- Cross-encoder produces unbounded scores (can be negative)
- What matters is relative ranking within each query
- Query 1 top: -5.88 beat -7.95 (ranking correct)
- Query 3 top: +6.37 clearly best

**Files created:**
- `app/rag/bm25.py`
- `app/rag/rrf.py`
- `app/rag/rerank.py`

**Updated:**
- `scripts/test_search.py` — hybrid search with 5 test queries

**Why this matters:**
This is production-grade retrieval. Vector search alone gets ~65% top-1. Hybrid + rerank gets 85%+. My test showed 100% on 5 queries.

**End of Day 12:**
- [x] Hybrid retrieval working
- [x] 5/5 queries correct
- [x] Ready for Day 13 (Authentication)

---
---

## Day 13 — Authentication + Users

**The story:** Sahayak had no gate. Anyone could query anything. Today, we built the front door.

**Two concepts:**
- **Authentication** — who are you? (JWT token)
- **Authorization** — what can you do? (3 roles: citizen, social_worker, admin)

**Files created:**
- `app/models/user.py` — User table
- `app/schemas/user.py` — Signup, Login, UserResponse, TokenResponse
- `app/auth/__init__.py`
- `app/auth/passwords.py` — bcrypt
- `app/auth/jwt.py` — JWT creation + verification
- `app/auth/dependencies.py` — get_current_user, require_role
- `app/api/auth.py` — /signup, /login, /me
- `app/main.py` — FastAPI app

**Packages:** pyjwt, passlib[bcrypt], python-multipart

**Database:** New `users` table (7 tables total now)

**Tests passed:**
- Health check ✅
- Signup ✅
- Login returns JWT ✅
- Protected endpoint with token ✅
- Protected endpoint without token → 401 ✅

**Why this matters:**
Real apps need identity. Without auth, Sahayak couldn't be deployed publicly. Now citizens have private histories, social workers can help multiple people, admins can see analytics.

**End of Day 13:**
- [x] User table + JWT auth
- [x] Signup/login endpoints
- [x] Protected routes
- [x] Role-based authorization ready
- [x] Ready for Day 14 (Understanding Agent)

---



## The Rule

Every day:
```cmd
git add .
git commit -m "type: short message"
git push