\# Sahayak — Project Timeline



Complete timeline: what's done, what's next, and what gets built when.



\---



\## Week 1 — Planning \& Foundation ✅ (Complete)



| Day | Focus | Deliverable |

|:---:|-------|-------------|

| 0 | Repository setup | GitHub repo, folders, README |

| 1 | Architecture diagrams | System, workflow, state |

| 2 | Technology selection | Every tech + reason |

| 3 | Pydantic schemas | CitizenProfile, Scheme, Plan, State |

| 4 | Versioned prompts | 5 YAML prompts |

| 5 | Data collection | 34 PDFs + metadata.yaml |

| 6 | File cleanup | Renamed all files cleanly |

| 7 | Roadmap + risks | timeline.md, risk\_assessment.md |



\*\*End of Week 1 milestone:\*\* Complete architectural blueprint.



\---



\## Week 2 — Core Intelligence ✅ (Complete)



| Day | Focus | Deliverable |

|:---:|-------|-------------|

| 8 | Docker + PostgreSQL | Connection working |

| 9 | 7 SQLAlchemy models | All tables created |

| 10 | PDF ingestion | 34 PDFs → 34 JSONs (149 chunks) |

| 11 | Embeddings | ChromaDB populated, 33% baseline |

| 12 | Hybrid retrieval | BM25 + RRF + Cross-Encoder → 100% |

| 13 | JWT auth | 3 roles, bcrypt, protected routes |

| 14 | Understanding Agent | 4 languages, 7/7 tests pass |

| 15 | Research Agent | Mode-aware retrieval, citations |



\*\*End of Week 2 milestone:\*\* Working pipeline with two agents, hybrid retrieval, and auth.



\---



\## Week 3 — Advanced Intelligence \& Agentic Engine



\### Day 16 — Advanced Chunking



\*\*Focus:\*\* Replace fixed-size chunking with semantic + parent-child chunking using Docling.



\*\*Files to create/update:\*\*

\- `app/rag/extract.py` — add Docling

\- `app/rag/chunk.py` — add semantic + parent-child methods

\- `scripts/run\_ingestion.py` — rerun on all 34 PDFs



\*\*Technologies:\*\* Docling (IBM), LangChain text splitters



\*\*Deliverable:\*\* Better chunks → better retrieval.



\---



\### Day 17 — Metadata \& Prompt Versioning



\*\*Focus:\*\* Version every chunk, every prompt, every model.



\*\*Files to update:\*\*

\- `app/rag/ingest.py` — add `doc\_version`, `model\_used`

\- `app/prompts/understanding/` — keep v1, v2.2, v3.0, v3.1

\- `app/agents/understanding.py` — read version from `.env`

\- `app/models/agent\_run.py` — add `model\_name` column



\*\*Technologies:\*\* Git tags, environment variables



\*\*Deliverable:\*\* Every output traceable to a prompt version and model version.



\---



\### Day 18 — Live API Fallback



\*\*Focus:\*\* When KB has no answer, call live APIs.



\*\*Files to create:\*\*

\- `app/tools/myscheme.py` — myScheme API wrapper

\- `app/tools/web\_search.py` — DuckDuckGo or Tavily

\- Update `app/agents/research.py` — fallback logic



\*\*Technologies:\*\* myScheme API (free), Tavily (free tier)



\*\*Deliverable:\*\* No more "no answer" — always a grounded response.



\---



\### Day 19 — Planning Agent + Critic Agent



\*\*Focus:\*\* Two more agents in the pipeline.



\*\*Files to create:\*\*

\- `app/agents/planning.py` — build action plan

\- `app/agents/critic.py` — validate with rules (no AI)



\*\*Technologies:\*\* Groq Llama, Pydantic, pure Python rules



\*\*Deliverable:\*\* Full pipeline from Understanding → Research → Planning → Critic.



\---



\### Day 20 — Replanner + Full Pipeline Loop



\*\*Focus:\*\* When Critic fails, Replanner fixes only affected parts.



\*\*Files to create:\*\*

\- `app/agents/replanner.py` — differential fixing



\*\*Technologies:\*\* LangGraph (conditional edges, loops)



\*\*Deliverable:\*\* Full 5-agent loop with max 3 iterations.



\---



\### Day 21 — Streamlit UI + 3 Modes



\*\*Focus:\*\* Build the frontend. Wire Scheme, Mentor, Journey modes.



\*\*Files to create:\*\*

\- `app/ui/streamlit\_app.py`

\- Mode tabs, input box, response cards



\*\*Technologies:\*\* Streamlit, Plotly



\*\*Deliverable:\*\* A working UI — user types, gets beautiful cited response.



\---



\## Week 4 — Production, Evaluation \& Deployment



\### Day 22 — LangSmith Tracing + Evaluation



\*\*Focus:\*\* Observe every agent call. Measure everything.



\*\*Files to create:\*\*

\- `app/evaluation/retrieval\_eval.py`

\- `app/evaluation/grounding\_eval.py`

\- `scripts/run\_eval.py`



\*\*Technologies:\*\* LangSmith, pytest



\*\*Deliverable:\*\* Numbered metrics — accuracy, latency, citation coverage.



\---



\### Day 23 — HTML Report Generation



\*\*Focus:\*\* Beautiful downloadable outputs for journey plans and mentor roadmaps.



\*\*Files to create:\*\*

\- `app/reports/journey\_report.py` — Jinja2 template

\- `app/reports/mentor\_report.py`

\- `app/reports/templates/`



\*\*Technologies:\*\* Jinja2, Plotly, Folium (maps)



\*\*Deliverable:\*\* Users download a beautiful HTML report.



\---



\### Day 24 — Mentor \& Journey Document Collection



\*\*Focus:\*\* Add 35 mentor docs + 35 journey docs.



\*\*Files to add:\*\*

\- `data/raw/mentor/` (35 docs)

\- `data/raw/journey/` (35 docs)

\- Update `metadata.yaml`



\*\*Documents:\*\*



| Category | Example |

|----------|---------|

| Entrance exams | JEE Main, NEET, CUET, KCET, CAT, CLAT |

| Indian colleges | IIT Madras, NIT Calicut, CUSAT |

| Career paths | Engineering, medical, commerce, arts, IT |

| Study abroad | Germany, Canada, Saudi Arabia, UAE |

| Skill development | NSDC, ASAP Kerala |

| International jobs | Saudi Vision 2030, Aramco careers |

| Certifications | PMP, Six Sigma, AWS |

| International scholarships | DAAD, Chevening, Fulbright |



\*\*Technologies:\*\* Same ingestion pipeline



\*\*Deliverable:\*\* Three modes fully functional.



\---



\### Day 25 — Microservices Split



\*\*Focus:\*\* Break monolith into 3 services.



\*\*Services:\*\*

\- `services/auth-service/` (port 8001)

\- `services/agent-service/` (port 8002)

\- `services/rag-service/` (port 8003)



\*\*Technologies:\*\* FastAPI, Docker Compose, HTTP client



\*\*Deliverable:\*\* Each service scales independently.



\---



\### Day 26 — Voice + OCR



\*\*Focus:\*\* Add multimodal input.



\*\*Files to create:\*\*

\- `app/tools/voice.py` — Groq Whisper

\- `app/tools/ocr.py` — Groq Llama 3.2 Vision



\*\*Technologies:\*\* Groq Whisper, Groq Vision



\*\*Deliverable:\*\* User can speak or upload document photos.



\---



\### Day 27 — Docker + Deployment



\*\*Focus:\*\* Deploy to free-tier infrastructure.



\*\*Targets:\*\*

\- FastAPI → Render (free tier)

\- PostgreSQL → Neon (free tier)

\- Streamlit → Streamlit Cloud (free tier)



\*\*Technologies:\*\* Docker, Render, Neon, Streamlit Cloud



\*\*Deliverable:\*\* Public URL live. Zero monthly cost.



\---



\### Day 28 — Demo Video + Pitch Rehearsal



\*\*Focus:\*\* Record demo. Practice pitch.



\*\*Deliverables:\*\*

\- 5-minute demo video

\- Slide deck

\- Interview narrative rehearsed



\*\*End of Week 4 milestone:\*\* Public URL live. Demo recorded. Ready for interviews.



\---



\## Technologies by Week



| Week | New Technologies |

|:----:|-----------------|

| 1 | Pydantic, YAML, Git, GitHub |

| 2 | Docker, PostgreSQL, SQLAlchemy, ChromaDB, BM25, RRF, Cross-Encoder, BAAI embeddings, FastAPI, JWT, bcrypt, Groq Llama |

| 3 | Docling, LangChain splitters, myScheme API, LangGraph, Streamlit, Plotly |

| 4 | Qdrant, LangSmith, Jinja2, Folium, Groq Whisper, Groq Vision, Render, Neon |



\---



\## Risks and Mitigation



| Week | Risk | Mitigation |

|:----:|------|-----------|

| 3 | Advanced chunking breaks existing pipeline | Test on 5 PDFs first, then rerun all |

| 3 | Live API rate limits | Cache responses, fallback to web search |

| 3 | Critic rules too strict | Test on 20 sample queries |

| 4 | Microservices break integration | Keep monolith as fallback |

| 4 | Deployment fails | Fall back to Railway or Fly.io |

| 4 | Voice/OCR latency | Groq is fast (<3s per call) |



\---



\## Cut Order (If Behind Schedule)



If Week 4 arrives and core isn't done, cut in this order:



1\. Voice + OCR (Week 4, Day 26)

2\. Microservices (keep monolith)

3\. Qdrant (keep ChromaDB only)

4\. HTML reports (JSON output is fine)



\*\*Never cut:\*\* agents, RAG, Critic, Replanner, auth.



\---



\## Milestones Summary



| Week | Milestone |

|:----:|-----------|

| 1 | Complete architectural blueprint |

| 2 | Working pipeline with 2 agents + hybrid retrieval + auth |

| 3 | Full 5-agent loop + 3 modes + live API fallback |

| 4 | Deployed system on public URL, demo video, pitch ready |



\---



\## Cost Summary



| Service | Cost |

|---------|:----:|

| Groq API (LLM) | $0 (free tier) |

| ChromaDB (vector) | $0 (local) |

| PostgreSQL on Neon | $0 (free tier) |

| FastAPI on Render | $0 (free tier) |

| Streamlit Cloud | $0 (always free) |

| \*\*Total monthly\*\* | \*\*$0\*\* |







