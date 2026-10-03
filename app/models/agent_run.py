"""AgentRun — logs every agent call for debugging and tracing."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    agent_name = Column(String(50), nullable=False)
    input_json = Column(JSON)
    output_json = Column(JSON)
    tokens_used = Column(Integer, default=0)
    time_ms = Column(Float, default=0.0)
    status = Column(String(20), default="success")
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())