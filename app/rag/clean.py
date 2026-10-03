"""Clean extracted PDF text."""
import re


def clean_text(text: str) -> str:
    """Remove common PDF artifacts and normalize whitespace."""
    # Remove page numbers like "Page 1 of 10"
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

    # Remove standalone numbers (page numbers, footnote markers)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces into 1
    text = re.sub(r"[ \t]+", " ", text)

    # Remove leading/trailing whitespace on each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Final trim
    return text.strip()


if __name__ == "__main__":
    sample = "Page 1 of 10\n\n\n\nHello    world\n\n\n\n  123  \n\nThis is a test."
    print("Before:")
    print(repr(sample))
    print("\nAfter:")
    print(repr(clean_text(sample)))