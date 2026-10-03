"""Ingest a single PDF: extract, clean, chunk, tag, structure."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import yaml
from app.rag.extract import extract_text
from app.rag.clean import clean_text
from app.rag.chunk import chunk_text


METADATA_PATH = Path("data/raw/metadata.yaml")


def load_metadata() -> dict:
    """Load the metadata YAML file."""
    if not METADATA_PATH.exists():
        return {}
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_file_metadata(category: str, filename_stem: str, all_meta: dict) -> dict:
    """Look up metadata for a specific file. Return defaults if missing."""
    defaults = {
        "name": filename_stem.replace("_", " ").title(),
        "category": "unknown",
        "state": None,
        "life_events": [],
        "target_gender": "any",
        "target_age_min": 0,
        "income_limit": None,
        "source_url": "",
    }
    category_meta = all_meta.get(category, {})
    file_meta = category_meta.get(filename_stem, {})
    return {**defaults, **file_meta}


def ingest_pdf(pdf_path: Path, category: str, all_meta: dict) -> dict:
    """Run the full pipeline on one PDF. Return a structured dict."""
    raw = extract_text(pdf_path)
    clean = clean_text(raw)
    chunks = chunk_text(clean)
    metadata = get_file_metadata(category, pdf_path.stem, all_meta)

    return {
        "doc_id": pdf_path.stem,
        "source_file": str(pdf_path),
        "category_folder": category,
        "metadata": metadata,
        "text": clean,
        "chunks": chunks,
        "num_chunks": len(chunks),
        "char_count": len(clean),
    }


if __name__ == "__main__":
    import json

    pdf = Path(sys.argv[1])
    category = sys.argv[2] if len(sys.argv) > 2 else "central"
    all_meta = load_metadata()
    result = ingest_pdf(pdf, category, all_meta)

    print(f"File: {pdf.name}")
    print(f"Category: {category}")
    print(f"Characters: {result['char_count']}")
    print(f"Chunks: {result['num_chunks']}")
    print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")