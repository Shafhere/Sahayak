\## V1 Modes (Locked)



| Mode | Status | User | Example |

|------|:------:|------|---------|

| Scheme | ✅ V1 | Citizens | "My husband died" |

| Mentor | ✅ V1 | Students | "I'm in 12th, what next?" |

| Journey | ✅ V1 | Travelers | "Visit Ooty alone, 3 days" |

| Companion | ⏸ Future | Daily life | "News in Kochi today" |

| Care | ⏸ Future | Emotional | "I feel alone" |



\*\*Why only 3 in V1:\*\* Depth over breadth. Each mode must solve real problems with grounded RAG, deterministic validation, and citations. Two modes deferred to protect quality.



\*\*Security:\*\* JWT auth + role-based authorization (citizen, social worker, admin).



\*\*Architecture:\*\* 5-agent LangGraph workflow. Same code for all modes. Only prompts and tools change.

