"""Diagnose exactly where research slows down."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def log(label, start):
    print(f"  [{time.time() - start:.2f}s] {label}")
    return time.time()


def main():
    text = "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ"

    print("=" * 60)
    print("STEP 1: Import modules")
    print("=" * 60)
    t = time.time()
    from app.agents.understanding import understand
    from app.agents.research import research
    log("imports done", t)

    print("\n" + "=" * 60)
    print("STEP 2: Understanding Agent (LLM call)")
    print("=" * 60)
    t = time.time()
    profile = understand(text)
    log(f"understand done — mode={profile.mode}", t)

    print("\n" + "=" * 60)
    print("STEP 3: Research Agent")
    print("=" * 60)
    t = time.time()
    result = research(profile)
    log(f"research done — {result.num_results} chunks", t)

    print("\n" + "=" * 60)
    print(f"TOTAL TIME: {time.time() - t:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()