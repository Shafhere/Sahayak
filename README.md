# Sahayak

Sahayak turns a citizen's question into a source-linked action plan. It has two modes: **Scheme** for a curated collection of government support, and **Mentor** for education and career exploration. It accepts English, Hindi, Malayalam and Tamil; it translates the retrieval intent into English to search the current English-language corpus.

## What is implemented

- A LangGraph workflow: Understanding → Research → Planning → deterministic Critic → bounded Replanner. Missing information pauses the graph and returns follow-up questions.
- Hybrid retrieval: local BGE embeddings, Chroma, BM25, reciprocal-rank fusion and an MS MARCO cross-encoder. Mode and state filters apply before retrieval; irrelevant passages can be rejected.
- Source IDs, official URLs, document editions, page numbers and verbatim supporting excerpts. URLs are attached by application code, not trusted from model output.
- Native Streamlit result cards, document checkboxes, a downloadable HTML plan, and browser Print / Save as PDF. Result headings support four languages.
- Groq Whisper voice input; local RapidOCR for printed English document images. Extracted text can be edited before submission.
- FastAPI authentication with bcrypt/JWT and PostgreSQL. Guest mode works without authentication. The guidance workflow currently runs inside Streamlit, not through an authenticated inference API.
- Corpus-quality CSV exports, a separate project evidence dashboard, synthetic live evaluation scripts, and offline regression tests.

## Local setup (PowerShell, Python 3.11)

Run commands from this project folder. Keep your existing `.env`; `.env.example` is a template for a new installation. Never put API keys into chat or Git.

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env  # New installation only; do not overwrite an existing .env.
```

Set `GROQ_API_KEY` and a strong `JWT_SECRET_KEY` locally. `GROQ_MODEL` defaults to `openai/gpt-oss-20b`. Model availability and free-tier limits depend on the provider; operation is not guaranteed to be free. Local embedding and reranker models download on first use, then load from cache.

```powershell
# Optional: authentication database
docker compose up -d postgres
.\venv\Scripts\python.exe scripts/init_db.py
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
.\venv\Scripts\python.exe -m streamlit run app/ui/streamlit_app.py
```

Choose **Continue as guest** to test guidance without the database. In Mentor, enter `I finished 12th, I am confused.` and answer the follow-up questions with your actual subjects and interests. A request without a direction should ask questions before preparing a roadmap.

## Documents and search index

The reviewed source list is `data/source_manifest.json`. Original files stay in `data/raw/`; extracted passages with provenance are in `data/knowledge_base/`. The importer preserves page numbers, normalizes whitespace and reports missing or scanned sources. Eight reviewed CBSE/NTA excerpts preserve exact text and pages while removing surrounding lists; retrieval headings describe their topics. Unverified legacy files remain on disk but are excluded with `metadata.active=false`.

```powershell
.\scripts\download_sources.ps1
.\venv\Scripts\python.exe scripts/import_sources.py
.\venv\Scripts\python.exe scripts/curate_pathways.py
.\venv\Scripts\python.exe scripts/build_index.py
.\venv\Scripts\python.exe scripts/audit_corpus.py
```

Stop/restart the UI after rebuilding so its in-memory BM25 index reloads. The builder reuses unchanged embeddings only when the stored model identity matches. A first CPU build may take many minutes. Do not edit or query the index while it is being replaced.

Coverage is deliberately described as **curated**, not all Indian schemes or every career. Sources include CBSE, NCERT, NTA, selected central schemes and Kerala government portals. Historical guidelines and past admission cycles are labeled; check subsequent amendments and current application windows. One scanned NCERT volume is downloaded but excluded pending reliable OCR. New topics require additional reviewed sources.

## Evaluation and data analysis

```powershell
.\venv\Scripts\python.exe -m pytest tests -q
.\venv\Scripts\python.exe scripts/evaluate_live_retrieval.py
.\venv\Scripts\python.exe scripts/evaluate_live_pipeline.py
.\venv\Scripts\python.exe -m streamlit run app/ui/analytics.py --server.port 8502
```

To retry only failed live cases, run `scripts/evaluate_live_pipeline.py --retry-failed --delay 60`. Attempts are preserved in `data/eval/live_pipeline_attempts.jsonl`; pacing reduces temporary provider rate limits.

The live pipeline script makes Groq calls with synthetic examples and disables external tracing. The retrieval script uses the actual research agent and local models. Read per-case results, not just a pass count. A matching document and valid quotation do **not** prove every generated statement is correct. The small developer-curated set is not a held-out benchmark.

`data/eval/corpus_quality.csv` can be loaded into Power BI. Suggested charts: active versus excluded documents, passages by mode, missing provenance, and document editions. `runtime_metrics.jsonl` contains timing, mode, language and outcome flags only; no prompts or profiles. Disable it with `SAHAYAK_METRICS=false`. LangSmith tracing is separate and can transmit prompts/responses if enabled in your environment.

Older `golden_queries.json` and `baseline_results.json` are historical artifacts for the previous corpus. Their accuracy figures must not be presented as current system performance. Seven database models exist, but citizen/session/plan persistence is not wired into the guidance flow; do not describe unused tables as completed product features.

## Container setup

```powershell
docker compose -f docker-compose.yml -f compose.app.yml up --build -d
```

This layers API/UI services over the existing local PostgreSQL setup. Build the local index first. These files are intended for local demonstration, not public production hosting. Container execution must be validated on a host with access to Docker Engine. Do not expose this development setup publicly without deployment-specific configuration.

## Reliability boundaries

The critic checks source membership, exact quotation presence, selected context rules, and minimum completeness. It cannot establish semantic entailment, current legal eligibility, admission chances, or translation quality. Unsupported plans are hidden; no unverified web-search snippets become evidence. The application does not guarantee three options, award amounts, processing times or a five-year path when the sources do not support them.

The only additional ML components are those that serve the product: embeddings, reranking, speech recognition and OCR. There is no claimed XGBoost eligibility predictor, myScheme API integration, BERT classifier, or microservice architecture.

## Verified local status — 22 October 2026

- 34 offline regression tests passed; Python compilation passed.
- 13/13 retrieval smoke checks passed: 10 supported queries and 3 unrelated-topic rejection checks.
- All 4 synthetic end-to-end flow checks passed (English, Hindi, Tamil, Malayalam), after paced retries of provider quota failures. These check profile language, nonempty options and critic acceptance; they do not certify translation or factual entailment.
- Active index: 10 official documents and 2,016 passages, all with source URLs; 2,008 include PDF page provenance. Forty-four legacy documents are excluded.
- The local Streamlit guest interface and printable HTML were visually inspected. Printed-English OCR and a synthetic English voice transcription were exercised.
- Docker Engine is unavailable on the validation host. Container build/startup and current PostgreSQL-backed login remain pending; in-memory authentication regression tests pass.

Reranker cutoffs are raw model scores (scheme 0.5, mentor -1.0), not probabilities. They were tuned on this small developer set and require broader independent evaluation. Before a public release, review generated instructions and translations with domain/native-language reviewers; source citations alone do not establish correctness.
