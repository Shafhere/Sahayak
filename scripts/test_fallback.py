"""Test live API fallback when KB has no answer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.citizen import CitizenProfile
from app.agents.research import research


# Query about a scheme NOT in our 34 documents
test_profile = CitizenProfile(
    mode="scheme",
    language="en",
    raw_input="Tell me about PM Fasal Bima Yojana crop insurance",
    state="Kerala",
    age=45,
    category="obc",
)

print("Testing fallback...")
print(f"Query: {test_profile.raw_input}\n")

result = research(test_profile, top_k=5)

print(f"\n{'='*60}")
print(f"Source: {result.source}")
print(f"Results: {result.num_results}")
print(f"{'='*60}\n")

for i, c in enumerate(result.chunks, 1):
    print(f"[{i}] {c.name}")
    print(f"    {c.text[:200]}...")
    print(f"    URL: {c.source_url}\n")