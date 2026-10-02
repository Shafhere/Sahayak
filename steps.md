# Sahayak — Development Log

Day-by-day record of what was done.

---

## Day 0 — Fresh Setup


**Date:** [01/10]

**Goal:** Create clean project structure and push to GitHub.

**Actions:**
- Deleted old Project VOLT folder
- Deleted old GitHub repo
- Created fresh GitHub repo: https://github.com/Shafhere/VOLT
- Created minimal folder structure
- Created .gitignore, .env.example, README.md, steps.md
- Initialized git and pushed

**Git commands used:**
```cmd

git init

git add .

git commit -m "chore: initial clean setup"

git branch -M main

git remote add origin https://github.com/Shafhere/VOLT.git

git push -u origin main

## Day 2 — Project Rebrand & Topic Lock

**Date:** [02/10]

**Decision:** Changed project from VOLT (travel) to Sahayak (government scheme finder).

**Reason:** Stronger story (personal — grandmother's missed pension), stronger social impact, native multilingual, native document verification, deeper ML, more unique.

**Actions:**
- Renamed GitHub repo to `Sahayak`
- Updated local folder name
- Updated remote URL
- Updated README and .env.example

**Git commands:**
```cmd
git remote set-url origin https://github.com/Shafhere/Sahayak.git
git add .
git commit -m "chore: rebrand to Sahayak — government scheme finder"
git push


**Files added:**
- docs/arch_system.jpeg
- docs/arch_workflow.jpeg
- docs/arch_state.jpeg


## Day 3 — Technology Selection & Requirements


**Goal:** Document tech choices and system requirements.

**Files added:**
- docs/06_technology_selection.md
- docs/07_requirements.md

**Key decisions:**
- 5-agent architecture locked
- ChromaDB + BM25 + RRF + rerank for RAG
- XGBoost for eligibility (CNN/BiLSTM to Future Roadmap)
- myScheme API + MCP for live data
- Free-tier deployment only

**End of day status:**
- [x] Tech selection documented
- [x] Requirements documented

---


## Day 4 — State Design, Schemas, ER Diagram

**Date:** [fill in]

**Goal:** Define data contracts, state flow, and database schema.

**Files added:**
- app/schemas/citizen.py       (CitizenProfile)
- app/schemas/scheme.py        (Scheme, Eligibility)
- app/schemas/plan.py          (ActionPlan, CriticVerdict)
- app/workflows/state.py       (SahayakState)

**Drawn in notebook:**
- SahayakState — the baton (8 compartments)
- ER diagram (6 tables)
- Agent flow (6 nodes, 1 loop)

**Key decisions:**
- State is a TypedDict — LangGraph standard
- Schemas are Pydantic v2 — structured output validation
- 6 tables: citizens, sessions, agent_runs, retrieval_logs, schemes, action_plans
- Max 3 replan iterations

**End of day status:**
- [x] Pydantic schemas defined
- [x] LangGraph state defined
- [x] ER diagram drawn
- [x] State flow diagram drawn