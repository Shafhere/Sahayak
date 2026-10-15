# Sahayak — Module Documentation

Every module has one job. No file does two things. This document explains each one.

---

## Module 1 — Configuration & Environment

**Purpose:** Control how the app boots up — secrets, database URL, Docker services, dependencies.

### Files

| File | Purpose |
|------|---------|
| `.env` | Secret keys (Groq API, JWT secret, DATABASE_URL). Never committed to Git. |
| `.env.example` | Template showing required variables. Committed. |
| `.gitignore` | Tells Git to ignore `.env`, `venv/`, `__pycache__/`, `chroma_db/`, `.cache/`. |
| `docker-compose.yml` | Runs PostgreSQL 16 in a container on port 5433. |
| `requirements.txt` | Python dependencies. No version pins for compatibility. |

### Dependencies
None — this is the base layer.

### How It Connects
Every other module reads from `.env`. `docker-compose.yml` provides the database.

### Interview Talking Points
> "Everything configurable lives in `.env`. Secrets never enter Git. Docker Compose runs PostgreSQL in isolation. No version pinning in requirements means pip resolves compatible versions."

---

## Module 2 — Database Layer

**Purpose:** Store and retrieve structured application data — citizens, sessions, plans, logs, users.

### Files

| File | Purpose |
|------|---------|
| `app/database.py` | Creates SQLAlchemy engine, session factory, and Base class. |
| `app/models/citizen.py` | Citizens table — profile (age, gender, income, state, category, life_events). |
| `app/models/session.py` | Sessions table — one row per planning run. |
| `app/models/agent_run.py` | Logs every agent call (input, output, tokens, time). |
| `app/models/retrieval_log.py` | Logs every RAG query (query, retrieved, reranked). |
| `app/models/scheme.py` | Cached scheme data (name, category, deadline, life_events). |
| `app/models/action_plan.py` | Generated plans as JSON. |
| `app/models/user.py` | Users table (email, hashed_password, role). |
| `app/models/__init__.py` | Imports all 7 models so Base.metadata knows about them. |

### Dependencies
- Reads `DATABASE_URL` from `.env`
- No other module dependencies

### Key Concepts

**SQLAlchemy ORM** — Python classes map to database tables. No raw SQL.

**Engine** — the connection pool to PostgreSQL.
**SessionLocal** — factory that opens/closes DB sessions.
**Base** — parent class of all models. Used by `Base.metadata.create_all()`.

**Foreign keys** — sessions belong to citizens; agent_runs and retrieval_logs belong to sessions.

### How It Connects
- RAG pipeline writes to `retrieval_logs`
- Agents write to `agent_runs`
- Every user query becomes a `session` row
- Generated plans saved to `action_plans`

### Interview Talking Points
> "Seven tables around three concerns: memory (citizens, sessions, action_plans), observability (agent_runs, retrieval_logs), and caching (schemes, users). SQLAlchemy maps Python classes to PostgreSQL. When I call `Base.metadata.create_all()`, it creates all seven tables."

---

## Module 3 — RAG Pipeline (The Star Module)

**Purpose:** Turn raw government PDFs into a searchable, cited knowledge base.

This is the heart of Sahayak. Nine files, each with one job.

### Files

| File | Purpose |
|------|---------|
| `app/rag/extract.py` | Reads text from PDFs using pypdf. |
| `app/rag/clean.py` | Removes 20+ junk patterns (page numbers, URLs, navigation). |
| `app/rag/chunk.py` | Splits into 2,000-char chunks with 200-char overlap. |
| `app/rag/ingest.py` | Orchestrates the full pipeline for one PDF. |
| `app/rag/embed.py` | Loads BAAI/bge-small-en-v1.5, converts text → 384-dim vectors. |
| `app/rag/vector_store.py` | ChromaDB wrapper (add, search, count, reset). |
| `app/rag/bm25.py` | Keyword search with singleton index. |
| `app/rag/rrf.py` | Reciprocal Rank Fusion — merges vector + BM25 rankings. |
| `app/rag/rerank.py` | Cross-Encoder re-scores top candidates. |

### Dependencies
- Reads from `data/raw/` (PDFs)
- Writes to `data/knowledge_base/` (JSON)
- Writes to `chroma_db/` (embeddings)
- Read by Research Agent

### The 6-Stage Pipeline (In Order)
Raw PDF
│
▼

EXTRACT → pypdf reads text
│
▼

CLEAN → 20+ regex patterns remove junk
│
▼

CHUNK → 2000 chars, 200 overlap
│
▼

EMBED → BAAI/bge-small-en-v1.5 → 384-dim vector
│
▼

STORE → ChromaDB with metadata
│
▼

RETRIEVE → hybrid: vector + BM25 → RRF → rerank




### Why Hybrid Retrieval

| Layer | What It Does |
|-------|-------------|
| Vector search | Finds meaning (similar topics) |
| BM25 | Finds exact keywords (scheme names) |
| RRF | Merges rankings by rank position |
| Cross-Encoder | Reads (query, chunk) pairs together for true relevance |

**Result:** Top-1 accuracy improved from 33% (vector-only) to 100% (hybrid + rerank).

### Metadata

Every chunk gets tagged:
- `doc_id`, `name`, `category`, `state`
- `life_events`, `source_url`, `deadline_date`
- `doc_version` (Week 3)

Metadata enables filtering (only Kerala schemes), boosting (state-specific), and citations.

### Technology Comparison

| Choice | Alternative | Why We Chose It |
|--------|-------------|-----------------|
| ChromaDB | Qdrant, Weaviate, pgvector | Local, metadata filter, free |
| BAAI/bge-small-en-v1.5 | OpenAI, Cohere | Local, no cost, fast |
| rank-bm25 | Elasticsearch | Lightweight, embedded |
| Cross-Encoder (ms-marco) | Cohere Rerank | Free, local, fast |
| pypdf | Docling, PyMuPDF | Simple, works on most PDFs |

### Interview Talking Points
> "My RAG is not one-step. It's extract → clean → chunk → embed → store → hybrid retrieve → rerank. Vector search alone gets 33% top-1 accuracy. Adding BM25 keyword search, RRF fusion, and cross-encoder reranking takes it to 100% on my test set. That's production-grade retrieval."

---

## Module 4 — Data (PDFs + JSON)

**Purpose:** The actual knowledge. 34 government scheme documents.

### Structure
data/
├── raw/
│ ├── central/ (17 PDFs)
│ ├── kerala/ (12 PDFs)
│ ├── general/ (5 PDFs)
│ ├── metadata.yaml (manual metadata per scheme)
│ └── COLLECTION_LOG.md
│
├── knowledge_base/
│ ├── central/ (17 JSONs — clean text + metadata + chunks)
│ ├── kerala/ (12 JSONs)
│ └── general/ (5 JSONs)
│
└── processed/ (empty — for intermediate files)


### Sources

- myscheme.gov.in (central schemes)
- swd.kerala.gov.in (Kerala state schemes)
- india.gov.in, pib.gov.in (general guides)

### Why This Structure

- **raw/** — original PDFs, never touched
- **knowledge_base/** — processed JSON, ready for embedding
- **metadata.yaml** — manual tagging per scheme

### Interview Talking Points
> "34 documents from official government portals. Raw PDFs stay untouched. Processed JSON files contain clean text, metadata, and chunks. Metadata is manual — I tagged each scheme with state, category, life_events, income_limit, source URL."

---

## Module 5 — Authentication

**Purpose:** Secure user identity and access control.

### Files

| File | Purpose |
|------|---------|
| `app/auth/passwords.py` | bcrypt password hashing. |
| `app/auth/jwt.py` | JWT token creation + verification. |
| `app/auth/dependencies.py` | FastAPI dependencies: `get_current_user`, `require_role`. |
| `app/api/auth.py` | Signup, login, /me endpoints. |

### Dependencies
- Reads `JWT_SECRET_KEY` from `.env`
- Uses User model from `app/models/user.py`

### Key Concepts

**Authentication** — who are you? (JWT token)
**Authorization** — what can you do? (3 roles)

**bcrypt** — slow by design. Prevents brute-force.
**JWT** — stateless token with user_id, email, role, expiry.

### Three Roles

| Role | Can Do |
|------|--------|
| Citizen | Query, see own history |
| Social Worker | Help multiple citizens |
| Admin | Analytics, manage schemes |

### Endpoints

- `POST /auth/signup` — creates user
- `POST /auth/login` — returns JWT
- `GET /auth/me` — returns current user (protected)

### Why HTTPBearer over OAuth2PasswordBearer

OAuth2PasswordBearer asks for username/password/client_id. HTTPBearer just asks for a token. Cleaner for API-first apps.

### Interview Talking Points
> "JWT authentication with bcrypt hashing. Three roles: citizen, social worker, admin. Every protected endpoint reads the JWT from the Authorization header, verifies signature, loads user. Without a token: 401. With wrong password: 401. Duplicate email: 400. All tested via Swagger UI."

---

## Module 6 — Schemas (Data Contracts)

**Purpose:** Define the exact shape of data flowing between components. Pydantic enforces it.

### Files

| File | Defines |
|------|---------|
| `app/schemas/citizen.py` | CitizenProfile (language, mode, emotion, age, gender, income, state, category, family_size, life_events, missing_fields, raw_input). |
| `app/schemas/research.py` | ResearchResult, RetrievedChunk. |
| `app/schemas/scheme.py` | Scheme, Eligibility. |
| `app/schemas/plan.py` | ActionPlan, CriticVerdict. |
| `app/schemas/user.py` | UserSignup, UserLogin, UserResponse, TokenResponse. |

### Dependencies
None. This is the contract layer.

### Key Concepts

**Pydantic v2** — validates LLM output. If the LLM returns "OBC" (uppercase) but the schema expects "obc", it fails.

**Null-safe validators** — `@field_validator` converts `None` → `[]` for list fields.

### Interview Talking Points
> "Every LLM response flows through Pydantic. If the shape is wrong, the schema catches it before it reaches the database. This is why my system is reliable — LLMs are probabilistic, but Pydantic is deterministic."

---

## Module 7 — Agents (Understanding + Research)

**Purpose:** The intelligence layer. Each agent has one job.

### Files

| File | Purpose |
|------|---------|
| `app/agents/understanding.py` | Reads natural language → structured profile + mode + emotion. |
| `app/agents/research.py` | Takes profile → grounded chunks with citations. |
| `app/agents/cache.py` | Disk cache for LLM responses (same input → cached output). |

### Dependencies
- Understanding uses Groq API, prompts, Pydantic
- Research uses RAG pipeline (`app/rag/`)

### Understanding Agent — 4 Steps

1. Load prompt from `app/prompts/understanding/v1.yaml`
2. Call Groq Llama with JSON output mode
3. Post-process (deterministic rules): category lowercase, gender inference, age regex
4. Validate with Pydantic

**Detects:** language (en/hi/ml/ta), mode (scheme/mentor/journey/care/companion), emotion (grief/confusion/hope/urgency/neutral), and profile fields.

### Research Agent — 6 Steps

1. Build mode-aware query from profile
2. Guard: skip if no data for this mode
3. Vector search (ChromaDB)
4. BM25 keyword search
5. RRF fusion
6. Cross-Encoder rerank
7. Filter + state boost + dedupe

### Why 2 Layers of Validation

LLM is probabilistic. Code is deterministic. Combine both:
- LLM extracts flexibly
- Post-processing fixes known issues
- Pydantic rejects invalid output

### Interview Talking Points
> "The Understanding Agent went through 4 prompt iterations. It extracts language, mode, emotion. The post-processing catches what the LLM misses — like 'widow' implies female. The Research Agent uses hybrid retrieval over 149 chunks with state-boost. Together they turn any sentence in 4 languages into grounded, cited answers."

---

## Module 8 — Prompts (Versioned)

**Purpose:** Instructions for each agent, stored as versioned YAML.

### Files

| Folder | Version | Agent |
|--------|:-------:|-------|
| `app/prompts/understanding/v1.yaml` | v3.1 (current) | Understanding Agent |
| `app/prompts/research/v1.yaml` | v1 | Research Agent |
| `app/prompts/planning/v1.yaml` | v1 (draft) | Planning Agent (Week 3) |
| `app/prompts/critic/v1.yaml` | v1 (draft) | Critic Agent (Week 3) |
| `app/prompts/replanner/v1.yaml` | v1 (draft) | Replanner Agent (Week 3) |

### Why YAML Not Python

- Prompts live outside code
- Versioned easily (v1, v2, v3)
- Non-programmers can improve wording
- Easy to A/B test

### Why Versioning Matters

When prompts change, results change. Version tracking lets us:
- Compare v2 vs v3 performance
- Roll back if worse
- Document which version produced which output

### Interview Talking Points
> "Every prompt is a versioned YAML file. When I improved the Understanding Agent's prompt, I created v2, v3, v3.1. Each version's results are traceable. This is prompt engineering as engineering — not ad-hoc tuning."

---

## Module 9 — API Layer

**Purpose:** HTTP endpoints that expose Sahayak's intelligence.

### Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app instance, registers routers, defines `/health`. |
| `app/api/auth.py` | `/signup`, `/login`, `/me` endpoints. |

### Dependencies
- Uses auth module
- Uses schemas
- Will use agents in Week 3

### Key Concepts

**FastAPI** — async web framework. Auto-generates Swagger docs.
**Uvicorn** — ASGI server that runs FastAPI.
**Swagger UI** — interactive API documentation at `/docs`.

### Planned Endpoints (Week 3)

- `POST /query` — main Sahayak query
- `GET /history` — user's past queries
- `GET /schemes` — browse schemes

### Interview Talking Points
> "FastAPI auto-generates interactive documentation from my code. I can test every endpoint live in Swagger UI. This is production-grade API design — typed, async, with auto-docs."

---

## Module 10 — Scripts

**Purpose:** Utility scripts for setup, ingestion, testing.

### Files

| File | Purpose |
|------|---------|
| `scripts/init_db.py` | Creates all 7 tables. |
| `scripts/test_db.py` | Verifies database connection. |
| `scripts/run_ingestion.py` | Runs PDF → JSON pipeline on all files. |
| `scripts/build_index.py` | Embeds all chunks into ChromaDB. |
| `scripts/test_search.py` | Tests hybrid retrieval (5 queries). |
| `scripts/test_understanding.py` | Tests Understanding Agent (7 cases). |
| `scripts/verify_research.py` | Tests Research Agent (3 cases). |
| `scripts/show_tree.py` | Prints project tree. |

### Interview Talking Points
> "Every script has one job. init_db creates tables. run_ingestion processes 34 PDFs into 149 chunks. build_index embeds them into ChromaDB. test_understanding tests 7 cases across 4 languages. The system is fully reproducible."

---

## Module 11 — Follow-Up Conversation Loop (Slot-Filling)

**Purpose:** Ensure the system has enough information to give personalized answers.

### How It Works
User Input
↓
Understanding Agent extracts what's there
↓
Check critical fields for the detected mode
↓
If missing → generate follow-up questions (max 3 at a time)
↓
User answers
↓
Merge into profile, re-run Understanding
↓
Loop up to 5 rounds
↓
Stop when: all critical fields filled OR user says "that's enough"
↓
Proceed with Research → Planning → Critic → Response



### Critical Fields per Mode

| Mode | Critical Fields |
|------|-----------------|
| Scheme | state, category, annual_income |
| Mentor | interests, career_goal, annual_income, category, state |
| Journey | origin, destination, duration, budget |
| Care | (none — empathy first) |

### Non-Critical Fields
Gender, family_size, occupation — recorded if given, but not asked.

### User Control
If user says "that's all", "just help", "proceed", or similar — the system
stops asking and works with available data. It notes assumptions in the response.

### Where It Lives
- Logic: `app/agents/understanding.py`
- Prompt: `app/prompts/understanding/v1.yaml`
- State: `SahayakState` will gain `needs_followup`, `followup_questions`
- UI: Streamlit (Week 3) shows questions as a chat flow

### Example Flows

**Scheme mode — short input:**
User: "I'm 17, I need a scholarship."
→ System asks: state, category, income
→ User provides partial
→ System proceeds with what it has

**Mentor mode — deeper questions:**
User: "I'm 17, finished Plus Two. Please guide me."
→ System asks: interests, strengths, career goal, income, category, abroad interest
→ User answers 4 of 6
→ System asks 1 final question
→ Full 5-year roadmap generated

### Interview Talking Points
> "The Understanding Agent doesn't just extract — it detects gaps and asks. For schemes, it asks state, category, income. For mentor mode, it asks about interests, passions, career goals. It asks until it has enough, or until the user says 'that's all'. This is what makes Sahayak conversational, not transactional."





