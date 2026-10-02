# Sahayak — Requirements

## Functional Requirements

### FR1 — Multilingual Input
The system accepts a citizen profile in English, Hindi, Malayalam, or Tamil.

### FR2 — Profile Understanding
Extract structured profile: age, gender, income, state, occupation, category, family details.

### FR3 — Scheme Research
Retrieve all applicable schemes from:
- Knowledge base (ChromaDB + BM25 hybrid)
- Live myScheme API
- MCP statistics server

### FR4 — Eligibility Validation
Apply deterministic rules per scheme (age ≥ X, income ≤ Y, state = Z). Return pass/fail per scheme.

### FR5 — Action Plan Generation
Generate:
- Eligible scheme list
- Required documents per scheme
- Application order and deadlines
- Next-step instructions

### FR6 — Citations
Every scheme claim must cite its source (official portal, PDF, or API).

### FR7 — Language Response
Return the final action plan in the user's input language.

### FR8 — Replanning
When the user changes their profile or a scheme updates, replan only affected parts.

### FR9 — Report Generation
Generate a downloadable HTML report with scheme list, document checklist, and timeline.

### FR10 — Observability
Every agent run, retrieval, and LLM call is traced in LangSmith.

## Non-Functional Requirements

### NFR1 — Latency
End-to-end response in under 30 seconds for a standard profile.

### NFR2 — Grounding
≥90% of factual claims must have a citation.

### NFR3 — Constraint Satisfaction
≥80% of test profiles must produce a fully valid action plan.

### NFR4 — Language Coverage
Support English, Hindi, Malayalam, Tamil in V1.

### NFR5 — Reproducibility
Docker-based setup works on any machine.

### NFR6 — Cost
Zero monthly hosting cost using free-tier services.

### NFR7 — Explainability
Every agent has a clear input, output, and reason for existing.

### NFR8 — Replanning Efficiency
Changing one field updates only affected plan components, not the entire plan.

### NFR9 — Max Iterations
Critic → Replanner loop capped at 3 iterations to avoid infinite loops.

### NFR10 — Human-in-the-Loop
Significant changes require user approval before final plan.

## Success Criteria

The V1 is successful when:
1. End-to-end pipeline works (Understanding → Research → Plan → Critic → Replan)
2. Deployed on a public URL
3. Evaluated on 10–15 test profiles
4. All metrics in NFR2 and NFR3 are met
5. Fully documented and explainable in an interview

## Out of Scope for V1

- Direct application submission to government portals
- OCR of scanned documents
- Voice input
- Mobile app
- Real-time scheme change notifications
- Integration with Aadhaar or DigiLocker APIs