"""RetrievalLog — logs every RAG query for evaluation."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    query = Column(String, nullable=False)
    retrieved_docs = Column(JSON)
    reranked_docs = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())