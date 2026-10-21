"""Test that SC query falls back instead of returning OBC results."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.citizen import CitizenProfile
from app.agents.research import research


test_profile = CitizenProfile(
    mode="scheme",
    language="en",
    raw_input="SC scholarship for college students",
    state="Kerala",
    category="sc",
    age=18,
)

result = research(test_profile, top_k=3)

print(f"\nSource: {result.source}")
print(f"Expected: web_search (because KB has OBC, not SC)")
if result.source == "web_search":
    print("✅ CORRECT — fell back to web")
else:
    print("❌ WRONG — stayed with OBC data")