
"""Non-sensitive run metrics; no prompts, profiles, answers or documents are recorded."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_LOCK = Lock()

PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "eval"
    / "runtime_metrics.jsonl"
)


def record_run(result, seconds, failed=False):
    """Record aggregate run metadata without disrupting the pipeline."""
    if os.getenv("SAHAYAK_METRICS", "true").strip().lower() != "true":
        return

    try:
        if not isinstance(result, dict):
            result = {}

        profile = result.get("profile")
        research = result.get("research")
        verdict = result.get("verdict")

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": getattr(profile, "mode", "unknown"),
            "language": getattr(profile, "language", "unknown"),
            "seconds": round(max(0.0, float(seconds)), 3),
            "error": bool(failed),
            "followup": bool(result.get("needs_followup")),
            "retrieved_chunks": getattr(research, "num_results", 0),
            "validation_passed": getattr(verdict, "passed", None),
            "iterations": result.get("iterations", 0),
        }

        with _LOCK:
            PATH.parent.mkdir(parents=True, exist_ok=True)
            with PATH.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")

    except Exception:
        # Metrics must never prevent a citizen from receiving a result.
        pass
