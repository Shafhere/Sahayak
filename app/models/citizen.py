"""Citizen — user profile stored for reuse."""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    annual_income = Column(Integer, nullable=False)
    state = Column(String(50), nullable=False)
    occupation = Column(String(100))
    category = Column(String(20), default="general")
    family_size = Column(Integer, default=1)
    language = Column(String(5), default="en")
    life_events = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())