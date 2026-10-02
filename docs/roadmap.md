# Sahayak — Development Roadmap

## Overview

**Total duration:** 4 weeks
**Week 1:** Planning and design (current)
**Weeks 2–4:** Build, deploy, evaluate

**Can add a buffer week** if needed (making it 5 weeks total).

---

## Week 1 — Planning (Days 1–7)

**Goal:** Design the full system before writing production code.

**Completed:**
- Project vision, problem statement, user story
- System architecture, agent workflow, state diagrams
- Technology selection document
- Requirements document (functional + non-functional)
- Pydantic schemas (4 files)
- LangGraph state definition
- ER diagram (6 tables)
- Versioned prompts (5 YAML files)
- Data sources plan
- 35 documents collected for the knowledge base
- Collection log

**End of Week 1 milestone:**
A complete architectural blueprint that can be explained in an interview without any code.

---

## Week 2 — Core Intelligence (Days 8–14)

**Goal:** Natural language → Understanding → Research → Grounded schemes with citations.

**Day 8:** Project scaffold, `.env`, Docker Compose, Postgres running
**Day 9:** SQLAlchemy models + DB smoke test
**Day 10:** Document ingestion pipeline (LlamaIndex, chunking, metadata)
**Day 11:** Embeddings into ChromaDB + retrieval smoke test
**Day 12:** Hybrid retrieval (dense + BM25 + RRF) + reranking
**Day 13:** LLM integration + structured outputs + Understanding Agent
**Day 14:** Research Agent + basic LangGraph (Understanding → Research)

**End of Week 2 milestone:**
Enter a citizen profile in any language → receive a list of applicable schemes with citations.

**Do NOT build in Week 2:**
- Planning agent
- Critic
- Replanner
- UI polish
- Deployment
- ML model

---

## Week 3 — Agentic Engine (Days 15–21)

**Goal:** Complete plan → validate → replan loop with ML + UI.

**Day 15:** Planning Agent (builds action plan)
**Day 16:** Critic Agent (rules + LLM coherence)
**Day 17:** Replanner (differential fixing) + LangGraph full loop
**Day 18:** XGBoost eligibility predictor — train, save, wire as tool
**Day 19:** Streamlit UI skeleton + report generation
**Day 20:** Multilingual support (detect → reason → respond)
**Day 21:** End-to-end integration + bug fixes

**End of Week 3 milestone:**
Full end-to-end demo: citizen profile → complete action plan → user changes constraint → system replans intelligently.

**This is the main demo. Protect this week.**

---

## Week 4 — Production & Polish (Days 22–28)

**Goal:** Deployed, observable, evaluated V1.

**Day 22:** LangSmith tracing across all agents
**Day 23:** Evaluation suite (10–15 test scenarios)
**Day 24:** Error handling, retries, guardrails
**Day 25:** HTML report generation (final output for citizen)
**Day 26:** Docker polish + deployment (Render + Streamlit Cloud + Neon)
**Day 27:** Final README, architecture diagrams, demo video
**Day 28:** Buffer: bug fixes, edge cases, interview pitch rehearsal

**End of Week 4 milestone:**
Public URL live. Demo video recorded. Docs complete. Interview pitch rehearsed.

---

## Buffer Week (Optional)

If 4 weeks feels tight, add a Week 5 for:
- Better evaluation
- More test cases
- UI improvements
- Non-critical features

**Rule:** Never sacrifice core functionality for polish. Ship a working simple system, not a broken complex one.

---

## Cut Order (If Behind Schedule)

If Week 4 arrives and core isn't done, cut in this order:
1. Multilingual (drop to English only)
2. Report generation (drop to JSON output)
3. XGBoost ML model (drop to rule-based only)
4. Streamlit charts (drop to plain text)
5. **NEVER cut:** agents, RAG, Critic, Replanner

**Core is sacred. Everything else is negotiable.**