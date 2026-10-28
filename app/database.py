
"""Database engine, session factory, and ORM base for Sahayak."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "Set it in your environment or .env file."
    )

# Keep SQLAlchemy's connection pool enabled for normal application use.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Each request or operation gets its own database session.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# All SQLAlchemy ORM models should inherit from this Base.
Base = declarative_base()


def get_db():
    """Yield a database session and always close it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
