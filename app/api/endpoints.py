from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    ReconciliationSessionCreate, ReconciliationSessionResponse,
    TransactionCreate, TransactionResponse, TransactionBulkUpload,
    ReconciliationResult, AmountDiscrepancyResult, ReconciliationSummary,
    MessageResponse
)
from app.models import SystemType
from app.services import ReconciliationSessionService, TransactionService

router = APIRouter(prefix="/api/v1", tags=["reconciliation"])


# Reconciliation Session endpoints
@router.post("/sessions", response_model=ReconciliationSessionResponse, status_code=status.HTTP_201_CREATED)
def create_reconciliation_session(
    session_data: ReconciliationSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new reconciliation session for comparing two systems
    """
    # Check if session name already exists
    existing = ReconciliationSessionService.get_session_by_name(db, session_data.session_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session with name '{session_data.session_name}' already exists"
        )
    
    try:
        new_session = ReconciliationSessionService.create_session(db, session_data)
        return new_session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions", response_model=List[ReconciliationSessionResponse])
def get_all_sessions(db: Session = Depends(get_db)):
    """
    Get all reconciliation sessions
    """
    sessions = ReconciliationSessionService.get_all_sessions(db)
    return sessions


@router.get("/sessions/{session_id}", response_model=ReconciliationSessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific reconciliation session by ID
    """
    session = ReconciliationSessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    return session


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a reconciliation session and all its transactions
    """
    deleted = ReconciliationSessionService.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    return MessageResponse(
        message=f"Successfully deleted session {session_id}",
        details={"session_id": session_id}
    )


# Transaction endpoints
@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    session_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a single transaction for a reconciliation session
    """
    # Verify session exists
    session = ReconciliationSessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    
    try:
        new_transaction = TransactionService.create_transaction(db, session_id, transaction)
        return new_transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create transaction: {str(e)}"
        )


@router.post("/transactions/bulk", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def bulk_upload_transactions(
    bulk_data: TransactionBulkUpload,
    db: Session = Depends(get_db)
):
    """
    Bulk upload transactions for a reconciliation session
    """
    # Verify session exists
    session = ReconciliationSessionService.get_session_by_id(db, bulk_data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {bulk_data.session_id} not found"
        )
    
    try:
        transactions = TransactionService.bulk_create_transactions(db, bulk_data.session_id, bulk_data.transactions)
        return MessageResponse(
            message=f"Successfully uploaded {len(transactions)} transactions",
            details={"count": len(transactions), "session_id": bulk_data.session_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to bulk upload transactions: {str(e)}"
        )


@router.get("/transactions/session/{session_id}", response_model=List[TransactionResponse])
def get_transactions_by_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific reconciliation session
    """
    # Verify session exists
    session = ReconciliationSessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    
    transactions = TransactionService.get_transactions_by_session(db, session_id)
    return transactions


@router.get("/transactions/session/{session_id}/system/{system}", response_model=List[TransactionResponse])
def get_transactions_by_system(
    session_id: int,
    system: SystemType,
    db: Session = Depends(get_db)
):
    """
    Get transactions by system (system_a or system_b) for a specific session
    """
    # Verify session exists
    session = ReconciliationSessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    
    transactions = TransactionService.get_transactions_by_system(db, session_id, system)
    return transactions


# Reconciliation Analysis endpoints (SET OPERATIONS!)
@router.get("/reconciliation/analyse/{session_id}", response_model=ReconciliationResult)
def analyse_reconciliation(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Reconcile transactions between two systems using SET operations
    
    Set Operations Used:
    - INTERSECTION (&): Find matched transactions in both systems
    - DIFFERENCE (-): Find transactions only in system A
    - DIFFERENCE (-): Find transactions only in system B
    
    This is the core reconciliation using set operations!
    """
    try:
        result = TransactionService.reconcile_transactions(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyse reconciliation: {str(e)}"
        )


@router.get("/reconciliation/discrepancies/{session_id}", response_model=AmountDiscrepancyResult)
def find_amount_discrepancies(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Find transactions where the same transaction ID exists in both systems
    but with different amounts
    
    This helps identify data quality issues beyond just missing transactions
    """
    try:
        result = TransactionService.find_amount_discrepancies(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find amount discrepancies: {str(e)}"
        )


@router.get("/reconciliation/summary/{session_id}", response_model=ReconciliationSummary)
def get_reconciliation_summary(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for a reconciliation session
    """
    try:
        result = TransactionService.get_reconciliation_summary(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reconciliation summary: {str(e)}"
        )


@router.delete("/transactions/session/{session_id}", response_model=MessageResponse)
def clear_session_transactions(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete all transactions for a session (useful for testing/reset)
    """
    # Verify session exists
    session = ReconciliationSessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    
    count = TransactionService.clear_all_transactions(db, session_id)
    return MessageResponse(
        message=f"Successfully deleted all transactions for session {session_id}",
        details={"deleted_count": count, "session_id": session_id}
    )