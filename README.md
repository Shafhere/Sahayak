\# VOLT



\*\*Agentic Journey Intelligence System\*\*



A stateful multi-agent system that turns natural-language travel goals into grounded, feasible, and adaptable journey plans.



\## Canonical Demo

10-day motorcycle trip from Delhi through Kashmir — mountains, adventure, budget-friendly, moderate pace.



\## Architecture

\- \*\*5 Agents:\*\* Understanding · Research · Planning · Critic · Replanner

\- \*\*Orchestration:\*\* LangGraph

\- \*\*RAG:\*\* ChromaDB + hybrid retrieval + reranking

\- \*\*ML:\*\* XGBoost cost estimator

\- \*\*Backend:\*\* FastAPI + PostgreSQL

\- \*\*UI:\*\* Streamlit + Folium map

\- \*\*Observability:\*\* LangSmith



\## Status

🚧 Week 1 — Planning



\## Project Structure

VOLT/

├── app/ # application code

├── data/ # knowledge base

├── docs/ # diagrams

├── notebooks/ # experiments

├── tests/ # tests

├── steps.md # development log

└── README.md



\## Development Log

See \[steps.md](steps.md) for day-by-day progress.



\## License

MIT

