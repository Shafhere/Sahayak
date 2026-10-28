
"""FastAPI application entry point for Sahayak."""

from fastapi import FastAPI
from app.api import auth

app = FastAPI(
    title="Sahayak API",
    description="Multilingual Citizen Companion",
    version="0.1.0",
)

app.include_router(auth.router)


@app.get("/health", tags=["Health"])
def health():
    """Liveness check: confirms that the API process is responding."""
    return {
        "status": "ok",
        "service": "sahayak",
    }
