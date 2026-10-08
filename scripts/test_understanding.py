"""Test the Understanding Agent with 5 diverse inputs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand


TESTS = [
    ("Malayalam — widow grandmother",
     "എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ"),
    ("English — student career",
     "I'm 17 and just finished 12th. I like math. What should I do next?"),
    ("English — solo travel",
     "I want to travel to Ooty alone for 3 days. Budget-friendly."),
    ("Hindi — scholarship",
     "मैं OBC छात्र हूँ, 12वीं पास किया है, छात्रवृत्ति चाहिए"),
    ("English — emotional distress",
     "I feel so alone. Nobody cares about me."),
]


def main():
    for label, text in TESTS:
        print(f"\n{'='*70}")
        print(f"TEST: {label}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")
        try:
            profile = understand(text)
            print(f"  language:      {profile.language}")
            print(f"  mode:          {profile.mode}")
            print(f"  emotion:       {profile.emotion}")
            print(f"  age:           {profile.age}")
            print(f"  gender:        {profile.gender}")
            print(f"  state:         {profile.state}")
            print(f"  life_events:   {profile.life_events}")
            print(f"  missing:       {profile.missing_fields}")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()