# Sahayak — Data Sources Plan

## Overview

Sahayak uses three sources of scheme information:
1. **Local knowledge base** — 50 curated documents (central + Kerala)
2. **myScheme API** — live scheme search
3. **MoSPI MCP server** — official statistics (optional for V1)

## Knowledge Base Coverage

| Category | Documents | Source |
|----------|-----------|--------|
| Central schemes | 15 | myscheme.gov.in, india.gov.in |
| Kerala state schemes | 15 | swd.kerala.gov.in, edistrict.kerala.gov.in |
| General guides | 10 | india.gov.in, state portals |
| Reference/context | 10 | PIB, India Code, state circulars |
| **Total** | **50** | All public, all free |

## Document Metadata Schema

Every document is tagged with:
- doc_id, name, category, state, scheme_type
- target_gender, target_age_min, target_age_max
- income_limit, category_eligibility
- source_url, source_type, reliability
- last_checked, language, text

## Ingestion Pipeline
Raw PDF → Extract → Clean → Tag → Chunk (500 tokens) → Embed → Store in ChromaDB


## Storage Structure

- `data/raw/` — original PDFs (unprocessed)
- `data/processed/` — cleaned markdown
- `data/knowledge_base/` — JSON with text + metadata

## Live APIs

| API | Purpose | Access |
|-----|---------|--------|
| myScheme API | Live scheme search | Free with registration |
| MoSPI MCP | Official statistics | Free |

## Retrieval Strategy

1. Metadata filter (state, gender, age, income)
2. Dense vector search (semantic)
3. BM25 sparse search (keyword)
4. RRF merge (combine rankings)
5. Cross-encoder rerank (top-K refinement)
6. Return top 5 with citations

## Freshness Strategy (V1)

- Documents re-checked monthly (manual)
- myScheme API provides fresh data on every query
- Source URLs stored so users can verify

## Out of Scope for V1

- Automated freshness monitoring
- Scraping every state portal
- Non-English scheme documents
- Real-time scheme change notifications

## Cost

$0. All sources are publicly accessible.