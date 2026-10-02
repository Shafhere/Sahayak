# Sahayak — Risk Assessment

Every project has risks. Pretending they don't exist is the biggest risk of all.

---

## Risk Categories

1. **Technical Risks** — things that could break
2. **Data Risks** — things that could go missing or wrong
3. **Timeline Risks** — things that could make us late
4. **Quality Risks** — things that could make it worse
5. **Scope Risks** — things that could make it too big

---

## 1. Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| LLM hallucination (invents schemes) | High | High | RAG + critic + citations + strict prompt rules |
| myScheme API rate limits | Medium | Medium | Cache responses; fallback to local KB only |
| ChromaDB setup issues | Low | Medium | Local install; test early in Week 2 |
| LangGraph loop running forever | Medium | High | Max iterations = 3, hard-coded guard |
| Embedding cost overrun | Low | Low | Cache embeddings; use small model |
| Multilingual handling fails | Medium | Medium | Fall back to English; test with 3 languages |

---

## 2. Data Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Downloaded PDFs are scans (no text) | Medium | High | Verify each has extractable text; re-download if needed |
| Scheme documents outdated | Medium | Medium | Store `last_checked` date; use live API for freshness |
| Metadata missing or wrong | Medium | High | Manually tag key fields; verify with sample queries |
| Government portals block scraping | Low | Low | Already downloaded 35 docs; only need API as fallback |
| File rename errors | Low | Low | Verify log matches actual filenames after rename |

---

## 3. Timeline Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Underestimating Week 2 build time | High | High | Start with smallest components first; test as you go |
| Getting stuck on one bug | Medium | High | Time-box debugging to 2 hours; ask for help after |
| LLM API issues delay work | Low | Medium | Have 2 providers configured (OpenAI + Groq fallback) |
| Personal interruptions | Medium | Medium | Plan buffer days in Week 4; document progress daily |
| Scope creep (adding features) | High | High | Lock V1 scope; new ideas go to Future Roadmap file |

---

## 4. Quality Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| UI is confusing | Medium | Medium | Use simple Streamlit components; test with a friend |
| Wrong schemes recommended | Medium | High | Rule-based critic catches eligibility errors |
| Report is not user-friendly | Medium | Medium | Test report with a non-technical person |
| Multilingual output is unnatural | Medium | Medium | Use LLM translation, verify with native speakers |

---

## 5. Scope Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Trying to match bigger projects | High | High | Focus on story + finishability, not tech volume |
| Adding CNN/BiLSTM too early | Medium | High | Keep XGBoost only; CNN/BiLSTM to Future Roadmap |
| Adding MCP, Power BI, voice, OCR | Medium | High | All in Future Roadmap; not in V1 |
| Rebuilding architecture midway | Low | High | Lock architecture; adjust only if truly broken |

---

## Top 3 Risks (Watch These Daily)

1. **LLM hallucination** — the biggest threat to credibility
   - *Mitigation:* RAG grounding + Critic validation + strict "do not invent" prompt rule
   
2. **Timeline overrun in Week 3** — the demo week
   - *Mitigation:* cut non-core features first; never sacrifice the agent loop
   
3. **Scope creep** — the silent killer
   - *Mitigation:* every new idea goes to `docs/future_roadmap.md`, never into current work

---

## Weekly Risk Review

Every Sunday (end of week):
- Review this document
- Update likelihood and impact
- Add new risks discovered during the week
- Note mitigation that worked or failed

---

## Contingency Plans

### If LLM costs exceed budget
Use Groq free tier (Llama 3.1 70B) as primary; OpenAI for embeddings only.

### If deployment fails on Render
Fallback: Railway.app or Fly.io (both free tiers).

### If 4 weeks is not enough
- Cut: multilingual, report gen, ML model
- Keep: 5 agents, RAG, Critic, Replanner
- Add Week 5 buffer

### If a core component breaks badly
- Revert to last known working commit (Git history)
- Simplify the component (fewer features, same purpose)
- Document the trade-off in steps.md