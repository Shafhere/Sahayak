# Sahayak: foundation repair

This is the first repair milestone, not a claim that the complete product is finished.

## Changes

- Replace the misplaced Understanding prompt with a Planning prompt that accepts the variables the caller supplies.
- Include evidence IDs and URLs in the planning request.
- Preserve the selected Scheme/Mentor mode through the workflow.
- Make follow-up questions stop the graph before research; submit answers as structured question/answer pairs on the next invocation.
- Extract mentor interests, strengths and a career goal; any of these can satisfy the direction question.
- Keep pending answers available after an API failure; reject empty submissions and render the result after submission via a Streamlit rerun.
- Hide recommendations and downloads when the critic is missing or fails. This is a display guard, not proof that passing plans are factually correct.
- Show unknown deadlines as Not verified, not Rolling.
- Remove the duplicate ActionPlan schema and the ambiguous two-digit age fallback.

## Verification

Run from the repository root, using the project environment:

```powershell
python -m pytest tests -q
```

These tests use mock model/retrieval responses and real LangGraph routing and Streamlit AppTest reruns. They do not establish live LLM accuracy or multilingual quality.

Verified locally: 12 tests passed, including three Streamlit interaction tests. Test environment: Python 3.14.3; the intended Python 3.11 environment still needs verification.

## Next milestone

Mentor retrieval remains disabled in the original research agent. Next: enable mode-filtered retrieval, preserve adequate evidence, carry sources through plans and reports, and improve factual validation. Then evaluate real examples and redesign the presentation.

A live run requires your local GROQ_API_KEY, the existing retrieval index and installed application dependencies. Keep credentials in your local .env; do not share them in chat.
