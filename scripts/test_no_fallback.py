"""Test that fallback does NOT trigger for queries KB can answer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.citizen import CitizenProfile
from app.agents.research import research


test_profile = CitizenProfile(
    mode="scheme",
    language="en",
    raw_input="Kerala widow pension eligibility",
    state="Kerala",
    age=65,
    category="general",
    life_events=["spouse_death"],  # ADDED — tells the query builder this is a widow
)

print("Testing no-fallback (KB should answer)...")
result = research(test_profile, top_k=3)

print(f"\nSource: {result.source}")
print(f"Results: {result.num_results}")
print(f"Expected source: rag")
if result.source == "rag":
    print("✅ CORRECT — no false fallback")
else:
    print("❌ WRONG — fallback triggered on a KB-answerable query")