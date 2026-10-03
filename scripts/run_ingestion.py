"""Run ingestion on all PDFs in data/raw/ and save to data/knowledge_base/."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.ingest import ingest_pdf, load_metadata


RAW_DIR = Path("data/raw")
KB_DIR = Path("data/knowledge_base")
CATEGORIES = ["central", "kerala", "general"]


def main():
    all_meta = load_metadata()
    total = 0
    failed = []

    for category in CATEGORIES:
        source_dir = RAW_DIR / category
        target_dir = KB_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)

        if not source_dir.exists():
            print(f"Skipping {category} (no folder)")
            continue

        pdfs = sorted(source_dir.glob("*.pdf"))
        print(f"\n[{category}] Processing {len(pdfs)} PDFs...")

        for pdf in pdfs:
            try:
                result = ingest_pdf(pdf, category, all_meta)
                output_path = target_dir / f"{pdf.stem}.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  OK  {pdf.name} ({result['num_chunks']} chunks)")
                total += 1
            except Exception as e:
                print(f"  FAIL {pdf.name}: {e}")
                failed.append((pdf.name, str(e)))

    print(f"\n{'='*50}")
    print(f"Total ingested: {total}")
    print(f"Failed: {len(failed)}")
    if failed:
        for name, err in failed:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()