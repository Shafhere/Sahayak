"""ActionPlan — every generated plan stored for history."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    plan_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())