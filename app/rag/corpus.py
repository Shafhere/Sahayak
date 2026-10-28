"""One metadata contract for sparse and dense retrieval."""
import json
from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_base"
CATEGORIES = ("central", "kerala", "general", "mentor")


def load_chunks(kb_dir: Path = KB_DIR) -> list[dict]:
    chunks = []
    for category in CATEGORIES:
        for path in sorted((kb_dir / category).glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            meta = doc.get("metadata", {})
            if meta.get("active") is False:
                continue
            # Existing mentor JSONs have no mode tag. Their folder defines it.
            mode = "mentor" if category == "mentor" else "scheme"
            texts = list(doc.get("chunks", []))
            pages = list(doc.get("chunk_pages") or [0] * len(texts))
            names = [meta.get("name") or doc["doc_id"]] * len(texts)
            for reviewed in doc.get("reviewed_passages", []):
                texts.append(reviewed["text"])
                pages.append(reviewed["page"])
                names.append(reviewed["name"])
            for i, text in enumerate(texts):
                if not text.strip():
                    continue
                chunks.append({
                    "id": f"{doc['doc_id']}__chunk_{i}", "text": text,
                    "doc_id": doc["doc_id"], "name": names[i],
                    "category": meta.get("category") or "unknown",
                    "state": (meta.get("state") or (category if category in ("central", "kerala") else "")).lower(),
                    "mode": mode, "source_url": meta.get("source_url") or "",
                    "chunk_index": i,
                    "page": pages[i],
                    "edition": meta.get("edition", "Date not recorded"),
                    "retrieved_on": meta.get("retrieved_on", ""),
                })
    return chunks
