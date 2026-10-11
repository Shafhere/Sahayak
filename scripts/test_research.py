"""Test the Research Agent with scheme-mode inputs only."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand
from app.agents.research import research


TESTS = [
    "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ",
    "I'm 17 and finished 12th, I need OBC scholarship",
    "My father is 65 and retired, what pension can he get?",
]


def main():
    start = time.time()
    for text in TESTS:
        print(f"\n{'='*70}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")

        profile = understand(text)
        result = research(profile)

        print(f"Mode: {profile.mode}")
        print(f"Query: {result.query}")
        print(f"Found: {result.num_results} chunks\n")

        if result.num_results == 0:
            print(f"  (No data for mode '{profile.mode}' yet)")
        for i, c in enumerate(result.chunks, 1):
            print(f"[{i}] {c.name} (score: {c.rerank_score:.3f})")
            print(f"    {c.text[:120]}...")

    print(f"\n\nTotal time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()