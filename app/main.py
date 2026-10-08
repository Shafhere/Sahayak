"""FastAPI application entry point."""
from fastapi import FastAPI
from app.api import auth

app = FastAPI(
    title="Sahayak API",
    description="Multilingual Citizen Companion",
    version="0.1.0",
)

app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "sahayak"}