"""Create all database tables from SQLAlchemy models."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine, Base
from app import models  # noqa: F401

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
print("\nTables in database:")
print(list(Base.metadata.tables.keys()))