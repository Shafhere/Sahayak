"""Verify the Research Agent returns relevant results for scheme queries."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand
from app.agents.research import research


TESTS = [
    ("Widow pension",
     "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ"),
    ("OBC scholarship",
     "I'm 17 and finished 12th, I need OBC scholarship"),
    ("Old age pension",
     "My father is 65 and retired, what pension can he get?"),
]


def main():
    start = time.time()

    for label, text in TESTS:
        print(f"\n{'='*70}")
        print(f"TEST: {label}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")

        profile = understand(text)
        print(f"Mode: {profile.mode}")
        print(f"Age: {profile.age}")
        print(f"Gender: {profile.gender}")
        print(f"Category: {profile.category}")

        result = research(profile)
        print(f"Query: {result.query}")
        print(f"Found: {result.num_results} chunks")
        print()

        for i, c in enumerate(result.chunks, 1):
            print(f"  [{i}] {c.name}")
            print(f"      score: {c.rerank_score:.3f}")
            print(f"      text: {c.text[:100]}...")
            print()

    print(f"\nTotal time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()