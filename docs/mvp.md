# Sahayak — MVP Documentation

## 1. Executive Summary

**Sahayak** (Hindi: "helper") is a multilingual agentic AI system that helps Indian citizens access government schemes, career guidance, and travel planning — in their own language.

**Core problem:** Millions of Indians miss benefits they qualify for because information is fragmented, English-only, and buried in bureaucratic language.

**Solution:** A stateful 5-agent system (Understanding, Research, Planning, Critic, Replanner) that extracts intent, retrieves grounded information with citations, builds actionable plans, validates them deterministically, and replans intelligently when constraints change.

**Canonical story:** My grandmother, 72, missed ₹1.92 lakh in widow pension over 8 years — not because she didn't qualify, but because nobody told her.

## 2. The Three Modes

### Mode 1 — Scheme
Government benefits. Finds schemes a citizen qualifies for — with documents, deadlines, local office addresses, and citations. Example: Kerala widow gets Kerala Widow Pension first (state boost).

### Mode 2 — Mentor
Career and education guidance. Builds a 5-year roadmap for students — which exams, which colleges, which certifications, which visa processes, which embassy to contact. Example: A 17-year-old wanting to work in Saudi Arabia gets a step-by-step plan.

### Mode 3 — Journey
Travel planning with safe stays, budgets, and emergency contacts for solo travelers.

## 3. The 5 Agents

| Agent | Role | Input | Output | Tech |
|-------|------|-------|--------|------|
| Understanding | Extract profile, mode, emotion | Natural language | CitizenProfile | Groq Llama + Pydantic + post-processing |
| Research | Retrieve grounded info | Profile | ResearchResult (chunks + citations) | ChromaDB + BM25 + RRF + Cross-Encoder |
| Planning | Build action plan | Profile + research | ActionPlan | Groq Llama + XGBoost |
| Critic | Validate with rules | Plan + profile | CriticVerdict (pass/fail + issues) | Pure Python rules |
| Replanner | Fix affected parts | Plan + issues | Updated plan | Groq Llama |

## 4. The RAG Pipeline (6 Stages)

1. **Extract** — pypdf reads PDFs
2. **Clean** — 20+ regex patterns remove junk
3. **Chunk** — 2,000-char pieces with 200-char overlap
4. **Embed** — BAAI/bge-small-en-v1.5 → 384-dim vectors
5. **Store** — ChromaDB with metadata
6. **Retrieve** — hybrid: vector + BM25 → RRF → Cross-Encoder rerank

**Accuracy:** 33% (vector-only) → 100% (hybrid + rerank).

## 5. The Follow-Up Conversation Loop

If critical fields are missing, the system asks follow-up questions.

**Critical fields:**
- Scheme: state, category, income
- Mentor: interests, career goal, income, category, state

**Stop conditions:**
- All critical fields filled
- User says "that's all I can give"
- Max 5 rounds

## 6. Technology Stack (Every Tech + Why)

| Tech | What | Why |
|------|------|-----|
| Python 3.11 | Language | Stable AI/ML support |
| LangGraph | Orchestration | Stateful workflows, loops |
| Groq Llama | LLM | Free, fast |
| BAAI/bge-small-en-v1.5 | Embeddings | Local, free |
| ChromaDB | Vector DB | Local, metadata filter |
| rank-bm25 | Keyword search | Exact matches |
| RRF | Fusion | Rank-based, scale-free |
| Cross-Encoder | Reranker | True relevance |
| FastAPI | API | Async, typed |
| PostgreSQL | Database | 7 tables |
| SQLAlchemy | ORM | Type-safe DB access |
| Pydantic | Validation | Schema enforcement |
| JWT + bcrypt | Auth | Stateless, secure |
| Docker | Containers | Reproducibility |
| Streamlit | UI | Fast dev |

**Total hosting cost:** $0/month (free-tier).

## 7. Folder Structure
Sahayak/
├── app/
│ ├── agents/ (understanding, research, cache)
│ ├── api/ (auth)
│ ├── auth/ (passwords, jwt, dependencies)
│ ├── models/ (7 SQLAlchemy tables)
│ ├── prompts/ (5 versioned YAML)
│ ├── rag/ (9 files)
│ ├── schemas/ (5 Pydantic)
│ ├── workflows/ (state)
│ ├── database.py
│ └── main.py
├── data/
│ ├── raw/ (34 PDFs + metadata)
│ └── knowledge_base/ (34 JSONs, 149 chunks)
├── docs/ (all documentation)
├── scripts/ (10 utility scripts)
└── docker-compose.yml

text

## 8. From User Input to Final Output (Full Internal Flow)
User types: "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ"

Streamlit UI sends to FastAPI via HTTP

FastAPI → Understanding Agent

Understanding Agent extracts: mode=scheme, language=ml, emotion=grief, age=68, gender=female, state=Kerala, life_events=[spouse_death]

Critical fields check → missing "category", "annual_income"

Follow-up loop asks: "What's the category? What's the income?"

User answers → profile complete

Research Agent runs:

Builds query: "widow pension senior citizen scheme government scheme"

Vector search: 15 chunks from ChromaDB

BM25 search: 15 chunks by keyword

RRF fusion: merged ranking

Cross-Encoder: top 20 reranked

Filter + boost: Kerala chunks +5.0, drop score < 0.5

Dedupe by document → top 3

Planning Agent builds action plan: schemes, documents, timeline, next steps

Critic validates: age ≥ 60 ✅, income ≤ limit ✅, documents ✅

If passed → Final response

If failed → Replanner fixes affected parts → back to Critic (max 3 loops)

Response rendered in Malayalam with citations

Everything saved to 7 PostgreSQL tables

text

## 9. Validation Framework

**Retrieval:**
- Top-1 accuracy: 33% → 100% on 5 queries
- Precision@3: measured

**Generation:**
- Citation coverage: 100%
- Groundedness: every claim traced

**Planning:**
- Constraint satisfaction: budget, deadlines
- Eligibility: deterministic rules

**System:**
- End-to-end latency: <30s target
- Cost: $0/month

## 10. What Makes Sahayak Different

| Feature | ChatGPT | myScheme | Sahayak |
|---------|:-------:|:--------:|:-------:|
| Grounded with citations | ❌ | 🟡 | ✅ |
| Multilingual | 🟡 | ❌ | ✅ |
| Multi-modal (scheme/mentor/journey) | ❌ | ❌ | ✅ |
| Deterministic validation | ❌ | ❌ | ✅ |
| Differential replanning | ❌ | ❌ | ✅ |
| Follow-up conversation | ❌ | ❌ | ✅ |
| Empathetic responses | ❌ | ❌ | ✅ |
| Role-based access | ❌ | ❌ | ✅ |
| Free-tier deployment | ✅ | ✅ | ✅ |

## 11. Future Roadmap

- Companion mode (news + weather)
- Care mode (emotional support + escalation)
- Knowledge Graph (GraphRAG)
- Voice input (Groq Whisper)
- Document OCR (Groq Vision)
- Microservices architecture
- Qdrant for scale
- Mobile app
- WhatsApp bot

## 12. Interview-Ready Story

> "Sahayak takes a citizen's question in their language, extracts a structured profile with emotion and mode, asks follow-up questions if critical info is missing, retrieves grounded information with hybrid RAG, builds an action plan, validates it with deterministic rules, and returns a cited, empathetic response — all stateful, all production-ready, all free-tier."
PART 6 — Auth Deep Dive
What Is Authentication vs Authorization
Term	Question	Example
Authentication	Who are you?	"I'm Lakshmi, here's my JWT"
Authorization	What can you do?	"You're a citizen — you see only your own data"
The Flow
Signup
POST /auth/signup with email + password + name

Server validates email format (Pydantic EmailStr)

Server checks email not already used

Password hashed with bcrypt

User row created in users table

Response returns user info (no password)

Login
POST /auth/login with email + password

Server finds user by email

verify_password(plain, hashed) compares

If match: JWT created with user_id, email, role, expiry

Response returns access_token + user info

Protected Endpoint
Request arrives with Authorization: Bearer <token> header

FastAPI dependency get_current_user() reads token

decode_access_token() verifies signature + expiry

Loads user from DB

Returns User object to endpoint

If invalid → 401

Why JWT Over Sessions
Stateless: Server doesn't store sessions

Scales horizontally: Any server can verify a token

No shared state: No Redis needed for sessions

Why bcrypt Over SHA-256
SHA-256: 10 billion hashes/sec → brute-force easy

bcrypt: 10 hashes/sec → brute-force infeasible

Slow by design is the point

Why HTTPBearer Not OAuth2PasswordBearer
OAuth2PasswordBearer is for full OAuth2 flows

HTTPBearer is cleaner for API-first apps

Swagger UI asks for token only, not username/password/client_id

3 Roles
Role	Can Do
Citizen	Query, see own history
Social Worker	Help multiple citizens
Admin	Analytics, manage schemes
Files
File	Purpose
app/auth/passwords.py	bcrypt hashing
app/auth/jwt.py	Token creation + verification
app/auth/dependencies.py	get_current_user, require_role
app/api/auth.py	Signup, login, /me
app/models/user.py	Users table