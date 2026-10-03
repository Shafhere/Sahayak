"""Scheme — cached government scheme metadata."""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String(50))
    state = Column(String(50), nullable=True)
    source_url = Column(String)
    deadline_date = Column(String, nullable=True)
    deadline_type = Column(String(20), default="rolling")
    life_events = Column(JSON, default=list)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())