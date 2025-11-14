from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from app.models import SystemType


# Reconciliation Session schemas
class ReconciliationSessionCreate(BaseModel):
    """Schema for creating a new reconciliation session"""
    session_name: str = Field(..., min_length=1, max_length=255, description="Unique session name")
    system_a_name: str = Field(..., min_length=1, max_length=255, description="Name of system A (e.g., Finance System)")
    system_b_name: str = Field(..., min_length=1, max_length=255, description="Name of system B (e.g., Stripe)")
    description: Optional[str] = Field(None, description="Optional session description")


class ReconciliationSessionResponse(BaseModel):
    """Schema for reconciliation session response"""
    id: int
    session_name: str
    system_a_name: str
    system_b_name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionCreate(BaseModel):
    """Schema for creating a single transaction"""
    transaction_id: str = Field(..., description="Transaction ID from source system")
    system: SystemType = Field(..., description="Which system this transaction is from")
    amount: float = Field(..., description="Transaction amount")
    transaction_metadata: Optional[str] = Field(None, description="Optional metadata")


class TransactionBulkUpload(BaseModel):
    """Schema for bulk uploading transactions"""
    session_id: int = Field(..., description="Reconciliation session ID")
    transactions: List[TransactionCreate]


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    transaction_id: str
    session_id: int
    system: SystemType
    amount: float
    transaction_metadata: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Reconciliation Analysis schemas
class ReconciliationResult(BaseModel):
    """Schema for reconciliation analysis using SET operations"""
    session_id: int
    session_name: str
    system_a_name: str
    system_b_name: str
    total_system_a: int
    total_system_b: int
    matched_count: int
    matched_transactions: List[str]
    only_in_system_a_count: int
    only_in_system_a: List[str]
    only_in_system_b_count: int
    only_in_system_b: List[str]
    match_rate: float


class AmountDiscrepancyDetail(BaseModel):
    """Schema for transactions with amount discrepancies"""
    transaction_id: str
    system_a_amount: Optional[float]
    system_b_amount: Optional[float]
    difference: float


class AmountDiscrepancyResult(BaseModel):
    """Schema for amount discrepancy analysis"""
    session_id: int
    session_name: str
    transactions_with_discrepancies: int
    discrepancies: List[AmountDiscrepancyDetail]
    total_discrepancy_amount: float


class ReconciliationSummary(BaseModel):
    """Schema for reconciliation summary statistics"""
    session_id: int
    session_name: str
    system_a_name: str
    system_b_name: str
    system_a_count: int
    system_b_count: int
    matched_count: int
    discrepancy_count: int
    match_rate: float
    system_a_total_amount: float
    system_b_total_amount: float
    amount_difference: float


class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str
    details: Optional[dict] = None