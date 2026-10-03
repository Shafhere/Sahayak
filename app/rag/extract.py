"""Extract text from a PDF using pypdf."""
from pathlib import Path
from pypdf import PdfReader


def extract_text(pdf_path: Path) -> str:
    """Read a PDF and return its full text as a single string."""
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1])
    text = extract_text(path)
    print(f"Extracted {len(text)} characters from {path.name}")
    print("First 500 chars:")
    print(text[:500])