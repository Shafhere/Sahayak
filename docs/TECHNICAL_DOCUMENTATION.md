# Sahayak Technical Documentation

This document explains Sahayak's purpose, architecture, development sequence, core technologies, deployment, trade-offs, and interview talking points. It intentionally distinguishes known implementation details from recommendations that would require further work.

## 1. Project summary

Sahayak is a multilingual citizen companion intended to help users explore government schemes and receive mentorship-style guidance. The current deployed interface provides two modes:

- **Scheme mode:** retrieves information relevant to a user's government-scheme question and provides a cautious fallback when the verified knowledge base does not support a specific answer.
- **Mentor mode:** supports learning and career guidance, including roadmap-style questions.

The public demo is available at https://sahayaka.streamlit.app/. The backend's OpenAPI documentation is available at https://sahayak-api-kfuk.onrender.com/docs.

The project is currently best described as a **deployed portfolio demo**, not as a production government service. It should not be presented as an official source of eligibility decisions.

## 2. Problem statement and design goals

### Problem

People may not know which government schemes or support programs could apply to their circumstances, what information they need to check, or where to start. Separately, learners often need structured guidance for educational and career goals.

### Goals

1. Offer a straightforward interface for two distinct types of questions.
2. Use retrieval and language-model generation to produce more context-aware responses than a bare prompt alone.
3. Prefer a safe fallback over inventing scheme details when the knowledge base does not support the answer.
4. Keep the UI and API separate so they can be deployed and developed independently.
5. Use automated tests and CI to catch regressions.
6. Make the application accessible through a public demo link for reviewers.

### Non-goals for the current version

The current demo should not be represented as:
- An official government portal.
- A guaranteed eligibility checker.
- A system with guaranteed up-to-date coverage of every scheme.
- A high-availability, horizontally scalable production service.
- A substitute for checking official government sources.

## 3. System architecture

### Deployed topology

```text
Recruiter / User Browser
        |
        v
Streamlit Community Cloud
(app/ui/streamlit_app.py)
        |
        | HTTP request
        v
Render FastAPI service
(app/api/main.py)
        |
        +--> API routes / authentication endpoints
        |
        +--> Research orchestration
                 |
                 +--> Embedding model
                 +--> Vector retrieval
                 +--> BM25 keyword retrieval
                 +--> Reciprocal Rank Fusion
                 +--> Optional cross-encoder reranking
                 +--> LLM response generation
                 +--> Answer / fallback
        |
        v
JSON response
        |
        v
Streamlit renders the result
```

This is a logical architecture based on the project structure and code excerpts reviewed during development. Check the current branch for any changed entry points or added services before treating this as a complete deployment diagram.

### Why separate frontend and backend?

**Benefits**
- UI and API can be changed independently.
- The API can be tested without clicking through the UI.
- FastAPI exposes an OpenAPI schema and interactive documentation.
- Multiple clients could use the same API in the future.

**Costs**
- Requires correct API URL configuration.
- Introduces network failures, CORS/configuration concerns, and two sets of logs.
- The backend may cold-start independently of the frontend.
- The backend needs its own resource budget and deployment configuration.

## 4. User request lifecycle

A typical request follows this conceptual path:

1. The user chooses Scheme or Mentor mode.
2. The user submits a question and any additional context collected by the UI.
3. The frontend sends the request to the configured backend.
4. The backend validates the request and routes it to the relevant application logic.
5. For modes that use the knowledge base, the research workflow builds a retrieval query.
6. The embedding model turns the query into a vector.
7. Semantic retrieval finds candidates by vector similarity.
8. BM25 retrieves candidates based on lexical term matching.
9. Reciprocal Rank Fusion combines ranked results.
10. If enabled, the cross-encoder reranks a candidate subset.
11. Mode-specific filters and score thresholds select useful context.
12. The relevant context is passed into the downstream response-generation flow.
13. If relevant verified context is insufficient, the app can return a fallback asking the user to narrow the search or consult official sources.
14. The API returns a response and the UI renders it.

The exact sequence may vary by mode. The numbered steps describe the observed research pipeline and expected request flow; verify each call site in the current code before presenting every step as a guaranteed path for every request.

## 5. Retrieval-Augmented Generation (RAG)

### Why RAG?

A general language model may answer from its training data and can confidently invent details. RAG attempts to ground generation in retrieved material relevant to the user's question.

A simplified pattern is:

```text
Question
  -> Retrieve relevant passages
  -> Build context
  -> Generate answer from context
  -> Return answer or fallback
```

RAG does not automatically guarantee truth. The quality of the answer depends on source coverage, document freshness, retrieval quality, prompts, and model behaviour. Scheme answers still need verification against official government sources.

### 5.1 Embeddings

**Implementation detail:** `app/rag/embed.py` identifies `BAAI/bge-small-en-v1.5` as the embedding model and uses Sentence Transformers.

An embedding is a numeric vector representing text. Texts with related meaning may have vectors that are close in the embedding space.

**Why it is used**
- Supports semantic matching when the user and source use different wording.
- Converts the query into a representation usable by vector search.

**Limitations**
- The model is English-oriented; multilingual retrieval quality should be evaluated rather than assumed.
- Model loading consumes RAM and CPU.
- Embedding model changes may require re-embedding the stored corpus to keep vector dimensions and representation consistent.

**Production options**
- Use a smaller model when resource constraints dominate, after evaluating quality.
- Use a multilingual embedding model if the source corpus and user queries require multilingual support.
- Serve embeddings through a managed inference endpoint when hosting resources are limited.
- Cache model instances and batch requests where appropriate.

### 5.2 Vector retrieval

The research workflow imports a vector-search interface from `app/rag/vector_store.py`. Vector retrieval compares query embeddings with stored embeddings to return semantically similar items.

**Why it is used:** semantic search can find relevant content without requiring an exact keyword match.

**Production options:** a managed vector database or a persistent self-hosted database can provide indexing, access control, backups, and scaling. The exact vector-store implementation and persistence settings should be verified in the current `vector_store.py` before naming the underlying engine in an interview.

### 5.3 BM25 keyword retrieval

The research workflow imports `get_bm25_index` from `app/rag/bm25.py`.

BM25 is a lexical ranking method. It scores documents based on query-term matches and term frequency, with normalization for document length and term rarity.

**Why use it alongside embeddings?**
- Exact names, scheme titles, identifiers, and phrases may be better captured by keyword retrieval.
- Semantic retrieval and lexical retrieval fail in different ways.

**Production options:** depending on scale, use an established search engine such as OpenSearch or Elasticsearch, or keep BM25 for a small corpus if evaluation shows that it performs well.

### 5.4 Reciprocal Rank Fusion (RRF)

The project has `app/rag/rrf.py`; the research workflow combines vector and BM25 results using `reciprocal_rank_fusion`.

RRF combines rankings from different retrievers without requiring their raw scores to be directly comparable. A common form is:

\[
\operatorname{RRF}(d)=\sum_i \frac{1}{k+\operatorname{rank}_i(d)}
\]

Here, \(d\) is a candidate document, \(i\) is a retriever, and \(k\) is a smoothing constant.

**Why it is useful:** it provides a straightforward way to combine lexical and semantic ranking signals.

**What to evaluate:** compare vector-only, BM25-only, and hybrid retrieval using a labeled set of realistic questions and relevant source passages.

### 5.5 Cross-encoder reranking

The project has `app/rag/rerank.py`, which identifies `cross-encoder/ms-marco-MiniLM-L-6-v2`.

A cross-encoder evaluates a query and candidate passage together. It is typically more computationally expensive than embedding search but can improve the ordering of a relatively small candidate set.

The research workflow reranks up to 35 fused candidates in the reviewed implementation.

**Resource trade-off:** loading a cross-encoder can increase memory use and cold-start time. The project has been adapted to support a `SAHAYAK_USE_RERANKER` configuration flag in the research workflow. When disabled, the workflow can retain fused retrieval order. Verify that the deployed commit contains this change before relying on the setting.

**Important quality trade-off:** disabling the reranker may reduce retrieval precision. If the fallback path assigns synthetic ranking values, those values must not be interpreted as calibrated relevance probabilities. Production evaluation should compare answer quality with and without reranking.

**Production options**
- Use a smaller cross-encoder.
- Rerank fewer candidates.
- Run reranking in a separate service.
- Keep reranking disabled for low-risk or low-resource demo scenarios only after evaluating the quality impact.

## 6. LLM generation and fallback behaviour

The application has used Groq as an LLM provider, but the exact model and call configuration should be checked in the current source and service environment.

A hosted LLM API can reduce the memory required on the web server because the generative model does not need to run inside the same process. It introduces API key management, rate limits, network latency, provider availability, and possible per-request costs.

### Fallback behaviour

The deployed UI has displayed a message explaining that the verified knowledge base does not contain the specific scheme information and asking the user to narrow the search or consult official sources.

This is a useful safety behaviour: the application acknowledges retrieval limitations rather than pretending that the knowledge base supports the answer.

### Improvements to consider

- Attach source titles, URLs, and last-verified dates to scheme claims.
- Separate “no relevant retrieval” from “LLM provider failure” and “backend failure”.
- Log retrieval identifiers and scores without logging unnecessary personal information.
- Evaluate whether a fallback is appropriate using labeled test questions.
- Keep the user-facing response clear about what was verified and what remains uncertain.

## 7. Backend API: FastAPI

**Known deployment:** FastAPI is hosted on Render, and the public API documentation is at https://sahayak-api-kfuk.onrender.com/docs.

The docs currently expose authentication routes:
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`

They also expose:
- `GET /health`

FastAPI builds an OpenAPI schema from route declarations and request/response models. Swagger UI at `/docs` makes endpoints easy to inspect and manually test.

### Why FastAPI?

- Request and response schemas can be validated.
- OpenAPI documentation is generated.
- It supports asynchronous endpoints where appropriate.
- It works well for separating the API layer from the UI.

### Production improvements

- Add API-level integration tests for successful and invalid requests.
- Validate authentication, authorization, token expiry, and error responses.
- Configure CORS to allow only required origins.
- Add rate limits and request-size limits.
- Use structured logs, health/readiness checks, metrics, and alerts.
- Add API versioning if breaking changes are expected.
- Do not expose stack traces or secrets in public responses.

## 8. Streamlit frontend

The main UI entry point reviewed in development is `app/ui/streamlit_app.py`. The app is deployed at https://sahayaka.streamlit.app/.

Streamlit is useful for a Python-first project because interactive UI controls can be built without creating a separate JavaScript frontend.

**Benefits**
- Fast development and iteration.
- UI logic can remain close to the Python AI workflow.
- Straightforward deployment for portfolio demos.

**Trade-offs**
- Less control over complex frontend state and visual behaviour than a dedicated frontend framework.
- Community hosting has resource and availability limits.
- The UI depends on the backend being reachable.

**Production alternative:** a React/Next.js frontend can provide more custom interaction and design control, but it adds a separate frontend codebase, build process, and maintenance burden. For a portfolio project, Streamlit is a reasonable choice when the primary goal is demonstrating AI functionality.

## 9. Authentication and data storage

The API documentation exposes signup, login, and current-user endpoints. That confirms the routes are present, but does not by itself prove that every security and persistence requirement is production-ready.

The development deployment has used SQLite for quick testing. SQLite is convenient for local development and small demos, but a local file on ephemeral hosting may be lost when an instance is replaced or restarted.

**Production direction**
- Use managed PostgreSQL for multi-user persistent account data.
- Use migrations and backups.
- Store passwords only as strong salted password hashes using a maintained password-hashing library.
- Use short-lived access tokens and carefully managed signing secrets if JWT is used.
- Apply least-privilege access controls.
- Avoid storing sensitive user documents unless required and explicitly disclosed.

Confirm the actual database, password-hashing method, token implementation, and persistence settings in source code before describing them as implemented features.

## 10. CI and testing

The repository has a GitHub Actions CI workflow. A prior local test run reported 38 passing tests, but this is a historical result; run tests again after any changes.

### Local test command

```cmd
python -m pytest -q
```

### Check CI

1. Open https://github.com/Shafhere/Sahayak.
2. Select **Actions**.
3. Open the latest run for the branch or commit you intend to deploy.
4. Confirm that required jobs passed.

### Recommended testing layers

- **Unit tests:** utility functions, scoring, fusion, request validation.
- **Retrieval tests:** known queries should retrieve expected source passages.
- **API integration tests:** health, signup/login validation, authorization, error paths.
- **End-to-end tests:** one representative Scheme request and one Mentor request.
- **Regression set:** a fixed set of queries with expected sources and quality criteria.
- **Deployment smoke tests:** public frontend loads, API health responds, and a request returns a valid result.

A green CI run is valuable, but it does not by itself prove that cloud secrets, memory limits, model downloads, or live API connectivity are configured correctly.

## 11. Deployment runbook

### Public links

- Frontend: https://sahayaka.streamlit.app/
- Backend docs: https://sahayak-api-kfuk.onrender.com/docs
- Backend health: https://sahayak-api-kfuk.onrender.com/health
- GitHub: https://github.com/Shafhere/Sahayak

### To demo Sahayak in an interview

1. Open the frontend link first.
2. If it is slow, allow time for the backend to wake up.
3. Test Mentor mode with a roadmap question.
4. Test Scheme mode with a question that includes a state and relevant personal context.
5. Explain the fallback if the verified knowledge base lacks relevant information.
6. Open `/docs` only if the interviewer wants to inspect the API.
7. Open GitHub Actions to show CI status.
8. Explain the architecture and the resource trade-off between reranking quality and memory use.

### Troubleshooting

**Frontend loads, but a request fails**
- Check Streamlit Cloud logs at the request timestamp.
- Check Render logs at the same timestamp.
- Confirm the frontend is configured with the correct backend URL.
- Confirm the backend health route responds.
- Verify the required LLM credentials are configured in the service that makes the LLM call.

**Backend is slow**
- Free hosting may sleep or cold-start.
- Check whether model loading occurs on the first request.
- Inspect memory usage and restarts before changing platforms.

**Scheme mode returns the knowledge-base fallback**
- This may be expected when relevant verified material is not indexed or retrieval scores are below the configured threshold.
- Test with a narrower query and relevant context.
- Inspect retrieved candidates, source coverage, and thresholds.
- Do not remove fallback behaviour merely to make every query produce an answer.

**Reranker-related memory problems**
- Check whether `SAHAYAK_USE_RERANKER` is supported by the deployed commit.
- Disable it only as a controlled demo workaround.
- Compare retrieval quality before and after disabling it.

## 12. Security and privacy checklist

Before sharing the public demo:

- [ ] No `.env` or API keys committed to GitHub.
- [ ] Any previously exposed key has been revoked and replaced.
- [ ] Cloud secrets are configured only in the relevant provider's secret settings.
- [ ] Error messages do not expose stack traces, tokens, or environment values.
- [ ] CORS and authentication are configured for the actual deployment.
- [ ] Public users are warned not to submit sensitive personal data.
- [ ] Scheme answers direct users to official sources for final verification.
- [ ] Persistent data has an intentional retention and backup policy if real users are involved.

## 13. Production architecture: what would change?

| Area | Current portfolio approach | Production direction |
|---|---|---|
| Frontend | Streamlit Community Cloud | Streamlit on managed infrastructure or a dedicated web frontend |
| API | FastAPI on Render | Managed/containerized API with scaling, monitoring, and availability targets |
| LLM | Hosted provider when configured | Provider abstraction, quota management, retries, cost tracking, and fallback policy |
| Embeddings | Local Sentence Transformers model | Smaller/multilingual model, managed inference, or dedicated embedding service |
| Vector retrieval | Project vector-store abstraction | Persistent managed vector database or evaluated self-hosted service |
| Keyword retrieval | BM25 | BM25 or search-engine service based on corpus size and evaluation |
| Reranking | Local cross-encoder, optionally disabled | Benchmark and serve with sufficient memory; tune candidate count |
| Database | SQLite used in development/testing | Managed PostgreSQL with migrations, backups, and connection management |
| Observability | Provider logs and basic health endpoint | Structured logs, metrics, tracing, alerts, and dashboards |
| CI/CD | GitHub Actions CI | CI plus deployment gates, staged environment, rollback, and smoke tests |
| Evaluation | Existing tests and manual scenario checks | Versioned evaluation dataset, retrieval metrics, faithfulness checks, and regression thresholds |
| Security | Project-level configuration | Threat model, rate limiting, secret rotation, least privilege, privacy and retention controls |

“Production” is not just a more powerful host. It requires defined reliability targets, observability, data protection, evaluation, and an operational process.

## 14. Suggested development timeline (reconstruct and verify)

The following is a conceptual chronology for explaining the project. It is not a verified commit-by-commit history. Use Git history and pull requests to replace it with exact dates and commits.

1. **Problem definition:** decide to help citizens explore schemes and users receive mentorship guidance.
2. **Application skeleton:** organize the Python project and establish the UI/API boundary.
3. **Backend API:** create FastAPI app and expose health and authentication endpoints.
4. **Frontend:** build the Streamlit interface and connect it to the backend.
5. **Retrieval components:** implement embeddings, vector retrieval, BM25, and rank fusion.
6. **Reranking:** add a cross-encoder stage to refine candidates.
7. **Mode-specific research logic:** filter results and apply mode-specific thresholds and fallbacks.
8. **Testing:** add pytest tests and run local checks.
9. **CI:** configure GitHub Actions to run automated checks on changes.
10. **First deployment:** deploy backend to Render and configure its runtime environment.
11. **Frontend deployment:** deploy Streamlit through Community Cloud and connect it to the backend.
12. **Cloud troubleshooting:** inspect service logs, correct configuration, and address resource limits.
13. **Portfolio validation:** test both modes from the public URL and document limitations.

To make this chronology precise, review `git log --oneline --decorate`, pull requests, and GitHub Actions history. Do not invent week numbers or dates without evidence.

## 15. Interview questions and suggested answers

### Why did you choose RAG instead of sending the question directly to an LLM?

RAG lets the application retrieve context from its knowledge base before generating a response. This can improve relevance and gives the system a way to abstain when the available material does not support an answer. It does not eliminate hallucinations, so source coverage and evaluation remain important.

### Why combine embeddings and BM25?

Embeddings help with semantic similarity, while BM25 is useful for exact terms and names. Combining their ranked results can improve coverage across different query types.

### What does Reciprocal Rank Fusion do?

RRF combines rankings from multiple retrieval systems using their rank positions, avoiding the need to directly compare incompatible raw score scales.

### Why add a cross-encoder?

It scores the query and candidate passage together, which can improve ordering of a shortlist. It costs more memory and compute than simple vector retrieval, so candidate count and measured quality matter.

### Why can the app return a fallback instead of an answer?

A scheme assistant should not invent eligibility details when relevant verified material is missing. The fallback tells users that the current knowledge base is insufficient and directs them toward a narrower search or official sources.

### Why separate Streamlit and FastAPI?

The frontend and backend can evolve independently, the API can be tested directly, and the same backend could support additional clients. The cost is more deployment configuration and another network boundary to debug.

### Is the current deployment production-ready?

It is a public portfolio demo. A production deployment would require stronger availability guarantees, persistent storage, observability, security hardening, rate limiting, data-retention policy, and systematic retrieval/answer evaluation.

### What was a real deployment challenge?

Local embedding and reranking models can consume significant memory and slow cold starts. I inspected service logs and made reranking configurable so I could trade off resource use against retrieval quality. I would validate the trade-off with a repeatable evaluation set rather than assume disabling reranking is always better.

### What would you improve next?

I would build a labeled retrieval evaluation set, add source-level citations and update dates for scheme information, test both modes end-to-end in CI, improve observability, and use persistent managed storage for any data that must survive service restarts.

## 16. Claims to verify before an interview

Check these in the current repository and cloud settings before stating them as facts:

- Exact LLM model name and provider configuration.
- Exact vector-store implementation and whether data persists across restarts.
- Whether the knowledge base contains only official and up-to-date sources.
- Exact authentication implementation and password hashing.
- Whether all user-facing modes use the same RAG pipeline.
- Whether the reranker-disable flag is present in the deployed commit.
- Current test count and latest CI result.
- Whether the cloud backend URL is read from Streamlit secrets or another configuration mechanism.

This verification habit is itself a good engineering practice: describe what you can demonstrate, and label proposed improvements as future work.
