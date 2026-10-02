"""Test PostgreSQL connection from Python."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("Connected!")
        print(f"PostgreSQL version: {version}")
except Exception as e:
    print(f"Connection failed: {e}")
    raise