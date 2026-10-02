# Sahayak — The Story of How It Was Built

A day-by-day record. Not just what was done, but why.

---

## Day 0 — The Beginning (Oct 1)

**Once upon a time**, there was an idea called VOLT — a travel planner for a Kashmir motorcycle trip. A repo was created. Folders were made. The first commit was pushed.

**But a story is not written in one draft.**

---

## Day 1 — The Grandmother's Story (Oct 2)

A new story emerged.

**My grandmother is 72. She lives in a village near Kochi. For 8 years, she was eligible for a widow pension of ₹2,000/month. She never received it — not because she didn't qualify, but because nobody told her.**

That's the problem. Information is fragmented, English-only, and buried.

**The decision:** Change the project from VOLT (travel) to **Sahayak** — a multilingual agentic system that finds government schemes a citizen qualifies for.

**What happened next:**
- GitHub repo renamed from `VOLT` → `Sahayak`
- Local folder renamed
- Remote URL updated
- README rewritten with the new story
- Three architecture diagrams drawn on paper and photographed
  - `docs/arch_system.jpeg` — the 5-layer system
  - `docs/arch_workflow.jpeg` — 5 agents and their loop
  - `docs/arch_state.jpeg` — the baton

**Why:** A stronger, more personal, more unique story than travel.

---

## Day 2 — Choosing the Tools (Oct 2)

The system needs tools. Not because they're popular — because each solves a real problem.

**What was decided:**
- **LangGraph** — because the workflow has branches and loops
- **ChromaDB + BM25 + RRF + reranker** — because scheme names need keyword AND semantic search
- **XGBoost** — to predict eligibility
- **myScheme API + MCP** — for live scheme data
- **FastAPI + PostgreSQL + Streamlit** — the backend + UI
- **Docker + free-tier hosting** — deployable without cost

**The documents written:**
- `docs/technology_selection.md` — every tool and why
- `docs/requirements.md` — what the system must do

**Why this matters:** In an interview, "I chose X because Y" beats "I used X" every time.

---

## Day 3 — The Baton (Oct 2)

Every relay race needs a baton. In Sahayak, the baton is called **`SahayakState`**.

It has 8 compartments. Every agent reads it, writes to it, passes it on.

**The contracts — 4 Pydantic schemas:**

| File | What it defines |
|------|-----------------|
| `app/schemas/citizen.py` | `CitizenProfile` — structured user details |
| `app/schemas/scheme.py` | `Scheme` and `Eligibility` — one scheme, one verdict |
| `app/schemas/plan.py` | `ActionPlan` and `CriticVerdict` — the answer, the judgment |
| `app/workflows/state.py` | `SahayakState` — the baton |

**The drawings:**
- The baton (8 compartments)
- The ER diagram (6 tables)
- The agent flow (6 nodes, 1 loop)

**The 6 database tables:**
- `citizens` — who the user is
- `sessions` — one row per planning run
- `agent_runs` — every agent call logged (our tracing)
- `retrieval_logs` — every RAG query logged (our evaluation)
- `schemes` — cached scheme data
- `action_plans` — every generated plan (history)

**Verification:** All 4 Python files imported successfully. Everything pushed to GitHub.

---

## Coming Next

- **Day 4:** Prompt architecture — how each agent thinks
- **Day 5:** Data sources — where the schemes come from
- **Day 6:** The LangGraph wiring
- **Day 7:** Week 1 review
- **Week 2:** Build the core intelligence
- **Week 3:** Build the agentic engine
- **Week 4:** Deploy and evaluate

---

## The Rule

Every day: **build one thing, log it in this file, commit, push.**

One commit per day. No exceptions.

---

## Git Ritual

Every day:

```cmd
git add .
git commit -m "type: short message"
git push


---

## Day 5 — The Voice of the System (Oct 2)

**Once upon a time**, we had 5 agents with no instructions. Today, we gave each one its manual.

**What we built:**
- `app/prompts/understanding/v1.yaml` — extract structured profile from any language
- `app/prompts/research/v1.yaml` — find schemes with citations, never invent
- `app/prompts/planning/v1.yaml` — build an action plan in simple language
- `app/prompts/critic/v1.yaml` — validate the plan, only flag real issues
- `app/prompts/replanner/v1.yaml` — fix only what the critic flagged

**Why YAML:**
- Prompts live outside code
- Versioning built in (v1, v2, v3)
- Easy to A/B test
- Easy to commit and track changes

**Key design choices:**
- Every prompt has role + task + rules + input + output
- Grounding rule: never invent schemes
- Critic rule: only flag real issues (avoid infinite loops)
- Replanner rule: fix only what's broken (differential replanning)

**End of day status:**
- [x] All 5 prompts written
- [x] Folder structure for prompts created
- [x] Prompts pushed to GitHub