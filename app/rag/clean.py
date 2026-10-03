"""Clean extracted PDF text."""
import re


# Patterns for website navigation junk that gets captured when saving pages as PDF
JUNK_PATTERNS = [
    r"Check Eligibility",
    r"Sign in to apply",
    r"Sign In",
    r"Back",
    r"Enter scheme name to\s*search\.\.\.",
    r"Details\s*\n\s*Benefits\s*\n\s*\| \|",
    r"News and\s*\n?Updates",
    r"Share",
    r"No new news and\s*\n?updates available",
    r"Was this helpful\?",
    r"Frequently Asked\s*\n?Questions",
    r"Sources And\s*\n?References",
    r"Powered by\s*\n?Digital India Corporation",
    r"Ministry of Electronics & IT",
    r"Government of India\s*\n?Connect on Social",
    r"Quick Links\s+Useful Links\s+Get in touch",
    r"About Us\s*\n?Contact Us\s*\n?Screen Reader",
    r"Accessibility Statement\s*\n?Frequently Asked",
    r"Disclaimer\s*\n?Terms & Conditions\s*\n?Dashboard",
    r"Last Updated On",
    r"©\s*\d{4}",
    r"┬©\s*\d{4}",
    r"┬«",
]


def clean_text(text: str) -> str:
    """Remove common PDF artifacts and website navigation noise."""
    # Remove page numbers like "Page 1 of 10"
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

    # Remove URL lines with timestamps
    text = re.sub(
        r"\d+/\d+/\d+,\s*\d+:\d+\s*(?:AM|PM)\s+.*?https?://\S+\s*\d+/\d+",
        "",
        text,
    )

    # Remove standalone URL lines
    text = re.sub(r"https?://\S+", "", text)

    # Remove the junk patterns
    for pattern in JUNK_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Remove standalone numbers (page numbers, footnote markers)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces into 1
    text = re.sub(r"[ \t]+", " ", text)

    # Remove leading/trailing whitespace on each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Remove empty lines at start/end
    return text.strip()


if __name__ == "__main__":
    sample = """
    Check Eligibility Sign in to apply
    Details
    Benefits
    | |
    Enter scheme name to search...
    Sign In
    10/2/26, 3:12 PM Indira Gandhi National Widow Pension Scheme
    https://www.myscheme.gov.in/schemes/ignwps 1/5
    
    This is the actual content about widow pension.
    A pension of Rs.300/- per month is provided to Widows.
    """
    print("Before:")
    print(repr(sample[:200]))
    print("\nAfter:")
    print(repr(clean_text(sample)[:200]))