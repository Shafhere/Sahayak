"""Import downloaded official PDFs with page provenance and extraction checks."""
import hashlib
from html import unescape
import json
import re
from datetime import date
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def pieces(text, size=1200, overlap=160):
    text = re.sub(r"\s+", " ", text).strip()
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        yield text[start:end]
        if end == len(text):
            break
        start = max(start + 1, end - overlap)


def main():
    audit = []
    for entry in json.loads((ROOT / "data/source_manifest.json").read_text(encoding="utf8")):
        path = ROOT / entry["path"]
        row = {"id": entry["id"], "source_url": entry["url"]}
        if not path.exists():
            audit.append({**row, "status": "download_unavailable"})
            continue
        if entry.get("extraction_status") == "needs_ocr":
            audit.append({**row, "status": "needs_ocr"})
            continue
        try:
            target = ROOT / "data/knowledge_base" / entry["folder"] / (entry["id"] + ".json")
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if target.exists():
                existing = json.loads(target.read_text(encoding="utf8"))
                if existing.get("metadata", {}).get("sha256") == digest and (entry.get("format") != "html" or existing.get("metadata", {}).get("extraction_version") == 2):
                    existing["metadata"]["source_url"] = entry["url"]
                    target.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf8")
                    audit.append({**row, "status": "text_extracted", "chunks": len(existing["chunks"])})
                    continue
            is_html = entry.get("format") == "html"
            if is_html:
                text = path.read_text(encoding="utf8")
                text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.S|re.I)
                text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", text))).strip()
                end = text.find(entry.get("section_end", "History of Pension"))
                start = text.rfind(entry.get("section_start", "Criteria for Allotting"), 0, end)
                if start < 0 or end <= start:
                    raise ValueError("Expected pension criteria section missing")
                pages = [text[start:end].split("* Special Amount")[0]]
            else:
                reader = PdfReader(path)
                pages = [(p.extract_text() or "").replace("\x00", "") for p in reader.pages]
            useful = [(i + 1, t) for i, t in enumerate(pages) if len(t.strip()) >= 100]
            if len(useful) < max(1, len(pages) * .25):
                audit.append({**row, "status": "needs_ocr", "pages": len(pages)})
                continue
            chunks, page_ids = [], []
            for page, text in useful:
                for part in pieces(text):
                    if len(part) >= 100:
                        chunks.append(part)
                        page_ids.append(0 if is_html else page)
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            doc = {"doc_id": entry["id"], "source_file": entry["path"],
                   "metadata": {"name": entry["name"], "source_url": entry["url"],
                                "publisher": entry["publisher"], "edition": entry["edition"],
                                "retrieved_on": date.today().isoformat(), "sha256": digest,
                                "state": entry.get("state", "central"), "active": True, "extraction_version": 2},
                   "chunks": chunks, "chunk_pages": page_ids, "num_chunks": len(chunks),
                   "char_count": sum(map(len, chunks))}
            target = ROOT / "data/knowledge_base" / entry["folder"] / (entry["id"] + ".json")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf8")
            audit.append({**row, "status": "text_extracted", "pages": len(pages), "chunks": len(chunks)})
            print(entry["id"], len(chunks), "passages", flush=True)
        except Exception as exc:
            audit.append({**row, "status": "extraction_failed", "error_type": type(exc).__name__})
    target = ROOT / "data/eval/source_audit.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(audit, indent=2), encoding="utf8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
