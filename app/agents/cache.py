"""Simple disk cache for LLM responses."""
import hashlib
import json
from pathlib import Path


CACHE_DIR = Path(".cache/understanding")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def get(text: str) -> dict | None:
    path = CACHE_DIR / f"{_key(text)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def set(text: str, data: dict) -> None:
    path = CACHE_DIR / f"{_key(text)}.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")