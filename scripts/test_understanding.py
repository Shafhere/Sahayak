"""Test the Understanding Agent with 7 diverse inputs — in parallel."""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand


TESTS = [
    ("Malayalam — widow grandmother",
     "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ"),
    ("English — student asking for guidance",
     "I'm 17 and just finished 12th. I like math. What career should I pursue?"),
    ("English — student asking for scholarship",
     "I need a scholarship for OBC students after 12th"),
    ("English — solo travel",
     "I want to travel to Ooty alone for 3 days. Budget-friendly."),
    ("Hindi — scholarship",
     "मैं OBC छात्र हूँ, 12वीं पास किया है, छात्रवृत्ति चाहिए"),
    ("English — emotional distress",
     "I feel so alone. Nobody cares about me."),
    ("Tamil — widow pension",
     "என் அம்மா விதவை, 65 வயது, பென்ஷன் வேண்டும்"),
]


def run_one(item):
    label, text = item
    try:
        profile = understand(text)
        return (label, text, profile, None)
    except Exception as e:
        return (label, text, None, str(e))


def main():
    with ThreadPoolExecutor(max_workers=7) as executor:
        results = list(executor.map(run_one, TESTS))

    for label, text, profile, error in results:
        print(f"\n{'='*70}")
        print(f"TEST: {label}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")
        if error:
            print(f"  ERROR: {error}")
        else:
            print(f"  language:      {profile.language}")
            print(f"  mode:          {profile.mode}")
            print(f"  emotion:       {profile.emotion}")
            print(f"  age:           {profile.age}")
            print(f"  gender:        {profile.gender}")
            print(f"  state:         {profile.state}")
            print(f"  life_events:   {profile.life_events}")
            print(f"  missing:       {profile.missing_fields}")


if __name__ == "__main__":
    import time
    start = time.time()
    main()
    print(f"\n\nTotal time: {time.time() - start:.2f} seconds")