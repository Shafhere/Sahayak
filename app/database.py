"""Database engine, session factory, and Base class."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine talks to PostgreSQL
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session factory: opens a new DB session when needed
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class that all our models inherit from
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()