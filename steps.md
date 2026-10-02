
**Pipeline designed:**
Raw PDF → Extract → Clean → Tag → Chunk (500 tokens, 50 overlap) → Embed → Store in ChromaDB

**Metadata schema:**
Every doc tagged with state, category, income_limit, age range, gender, source_url, reliability, last_checked.

**Document written:** `docs/data_sources.md`

**Collection log created:** `data/raw/COLLECTION_LOG.md`

---

## Day 6 — Files Renamed

Space and special characters in filenames become bugs later.

**All 35 PDFs renamed to lowercase_with_underscores:**
- `Atal Pension Yojana.pdf` → `atal_pension_yojana.pdf`
- `Kerala Widow pension.pdf` → `kerala_widow_pension.pdf`
- etc.

**Duplicate resolved:** Two Karunya Health files kept as one.

**Why:** Clean filenames = predictable code. No quoting issues. No path errors.

---

## Day 7 — Looking Ahead

A project without a roadmap gets lost by Week 3.

**Two documents written:**

### `docs/roadmap.md`
- Week 1: Planning (complete)
- Week 2: Core intelligence (Understanding + Research + RAG)
- Week 3: Agentic engine (Planning + Critic + Replanner + ML + UI)
- Week 4: Production (deploy, evaluate, document)
- Buffer week optional

**Cut order defined:** multilingual → report → ML → charts. Never cut agents, RAG, Critic, Replanner.

### `docs/risk_assessment.md`
- 5 categories: technical, data, timeline, quality, scope
- Top 3 risks to watch daily:
  1. LLM hallucination → mitigated by RAG + Critic + prompt rules
  2. Timeline overrun in Week 3 → mitigated by cut order
  3. Scope creep → every new idea goes to Future Roadmap

**Contingency plans:**
- LLM cost fallback: Groq
- Deployment fallback: Railway / Fly.io
- If behind: cut non-core, add buffer week

---

## The Principles We Follow

1. **One file, one job.** Every agent file does one thing.
2. **Simple, readable code.** No magic abstractions.
3. **Config outside code.** Prompts live in YAML.
4. **Test each piece alone.** Every agent has a `__main__` demo.
5. **Read the flow top-to-bottom.** A new reader understands any file in 2 minutes.

**Total code target: ~800–1000 lines.** Readable in one afternoon.

---

## What's Coming Next

### Week 2 — Core Intelligence
- Day 8: Project scaffold, `.env`, Docker Compose, PostgreSQL up
- Day 9: SQLAlchemy models + DB smoke test
- Day 10: Document ingestion pipeline
- Day 11: Embeddings into ChromaDB
- Day 12: Hybrid retrieval + reranking
- Day 13: Understanding Agent
- Day 14: Research Agent + basic LangGraph

**Milestone:** Enter a citizen profile in any language → receive schemes with citations.

### Week 3 — The Agentic Engine
- Day 15: Planning Agent
- Day 16: Critic Agent
- Day 17: Replanner + full LangGraph loop
- Day 18: XGBoost eligibility predictor
- Day 19: Streamlit UI skeleton
- Day 20: Multilingual support
- Day 21: End-to-end integration

**Milestone:** Full end-to-end demo with replanning.

### Week 4 — Production
- Day 22: LangSmith tracing
- Day 23: Evaluation suite
- Day 24: Error handling + guardrails
- Day 25: HTML report generation
- Day 26: Docker + deployment
- Day 27: README + demo video
- Day 28: Pitch rehearsal

**Milestone:** Public URL live. Demo video recorded. Story ready.

---

## The Story of Sahayak

Sahayak isn't a chatbot. It's not a RAG demo. It's not a wrapper around an LLM.

**It's a system that treats information access as a design problem.**

Five agents. A stateful workflow. A critic that checks its own work. A replanner that fixes only what's broken. Grounded citations. Multilingual by default. Report generation at the end.

And underneath all of it — a story. A grandmother. A pension. ₹1.92 lakh she never received. Not because the system was broken, but because information was hidden.

**Sahayak makes the hidden visible.**

That's what we're building. Not just code. A bridge.

---

---

## Day 8 — Sahayak Breathes (Week 2 Begins)

**Once upon a time**, Sahayak was only a plan. Today, it became running software.

**Challenges hit and solved:**
1. Python 3.14 too new → switched venv to Python 3.11
2. Package dependency conflict → removed version pins, let pip resolve
3. Wrong database driver → changed URL to `postgresql+psycopg2`
4. Local PostgreSQL on 5432 → moved Docker to 5433
5. Stale Docker volume with old password → `docker compose down -v`
6. Two local Postgres services (v17, v18) → stopped and disabled via admin

**What was set up:**
- `.env` with Groq API key, local embeddings, DB URL
- `requirements.txt` with ~30 packages (no pins)
- `docker-compose.yml` — PostgreSQL 16 on port 5433
- `scripts/test_db.py` — connection verified

**End of Day 8:**
- [x] Dependencies installed (Python 3.11 venv)
- [x] PostgreSQL running in Docker
- [x] Python ↔ PostgreSQL connection working
- [x] First real infrastructure debug complete

**Milestone:** Sahayak runs. Tomorrow we build the memory (SQLAlchemy models).

---

## The Rule

Every day:
```cmd
git add .
git commit -m "type: short message"
git push