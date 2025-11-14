from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class SystemType(str, enum.Enum):
    """Enum for different systems being reconciled"""
    SYSTEM_A = "system_a"
    SYSTEM_B = "system_b"


class ReconciliationSession(Base):
    """ReconciliationSession model representing a reconciliation between two systems"""
    __tablename__ = "reconciliation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String, nullable=False, unique=True, index=True)
    system_a_name = Column(String, nullable=False)  # e.g., "Finance System"
    system_b_name = Column(String, nullable=False)  # e.g., "Stripe"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ReconciliationSession(id={self.id}, name={self.session_name}, {self.system_a_name} vs {self.system_b_name})>"


class Transaction(Base):
    """Transaction model representing individual transactions from either system"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=False, index=True)  # Transaction ID from the source system
    session_id = Column(Integer, ForeignKey("reconciliation_sessions.id"), nullable=False, index=True)
    system = Column(Enum(SystemType), nullable=False)  # Which system this transaction is from
    amount = Column(Float, nullable=False)  # Transaction amount
    transaction_metadata = Column(Text, nullable=True)  # Optional metadata (JSON-like)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to session
    session = relationship("ReconciliationSession", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, system={self.system}, amount={self.amount})>"