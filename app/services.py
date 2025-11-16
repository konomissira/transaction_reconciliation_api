from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import ReconciliationSession, Transaction, SystemType
from app.schemas import (
    ReconciliationSessionCreate, TransactionCreate, ReconciliationResult,
    AmountDiscrepancyResult, AmountDiscrepancyDetail, ReconciliationSummary
)
from typing import List, Optional, Dict


class ReconciliationSessionService:
    """Service class for reconciliation session operations"""

    @staticmethod
    def create_session(db: Session, session_data: ReconciliationSessionCreate) -> ReconciliationSession:
        """Create a new reconciliation session"""
        session = ReconciliationSession(
            session_name=session_data.session_name,
            system_a_name=session_data.system_a_name,
            system_b_name=session_data.system_b_name,
            description=session_data.description
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_by_id(db: Session, session_id: int) -> Optional[ReconciliationSession]:
        """Get session by ID"""
        return db.query(ReconciliationSession).filter(ReconciliationSession.id == session_id).first()

    @staticmethod
    def get_session_by_name(db: Session, session_name: str) -> Optional[ReconciliationSession]:
        """Get session by name"""
        return db.query(ReconciliationSession).filter(ReconciliationSession.session_name == session_name).first()

    @staticmethod
    def get_all_sessions(db: Session) -> List[ReconciliationSession]:
        """Get all reconciliation sessions"""
        return db.query(ReconciliationSession).all()

    @staticmethod
    def delete_session(db: Session, session_id: int) -> bool:
        """Delete a session and all its transactions"""
        session = db.query(ReconciliationSession).filter(ReconciliationSession.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False


class TransactionService:
    """Service class for transaction operations and reconciliation logic"""

    @staticmethod
    def create_transaction(db: Session, session_id: int, transaction_data: TransactionCreate) -> Transaction:
        """Create a single transaction"""
        transaction = Transaction(
            transaction_id=transaction_data.transaction_id,
            session_id=session_id,
            system=transaction_data.system,
            amount=transaction_data.amount,
            transaction_metadata=transaction_data.transaction_metadata
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def bulk_create_transactions(db: Session, session_id: int, transactions_data: List[TransactionCreate]) -> List[Transaction]:
        """Bulk create transactions"""
        transactions = [
            Transaction(
                transaction_id=trans_data.transaction_id,
                session_id=session_id,
                system=trans_data.system,
                amount=trans_data.amount,
                transaction_metadata=trans_data.transaction_metadata
            )
            for trans_data in transactions_data
        ]
        db.add_all(transactions)
        db.commit()
        return transactions

    @staticmethod
    def get_transactions_by_session(db: Session, session_id: int) -> List[Transaction]:
        """Get all transactions for a session"""
        return db.query(Transaction).filter(Transaction.session_id == session_id).all()

    @staticmethod
    def get_transactions_by_system(db: Session, session_id: int, system: SystemType) -> List[Transaction]:
        """Get transactions by system for a specific session"""
        return db.query(Transaction).filter(
            Transaction.session_id == session_id,
            Transaction.system == system
        ).all()

    @staticmethod
    def reconcile_transactions(db: Session, session_id: int) -> ReconciliationResult:
        """
        Reconcile transactions between two systems using SET operations
        
        Returns:
        - Matched transactions (INTERSECTION)
        - Transactions only in system A (DIFFERENCE)
        - Transactions only in system B (DIFFERENCE)
        """
        # Get the session
        session = db.query(ReconciliationSession).filter(ReconciliationSession.id == session_id).first()
        if not session:
            raise ValueError(f"Reconciliation session with id {session_id} not found")

        # Get transactions from system A
        system_a_transactions = db.query(Transaction.transaction_id).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_A
        ).all()
        system_a_ids = set([t.transaction_id for t in system_a_transactions])

        # Get transactions from system B
        system_b_transactions = db.query(Transaction.transaction_id).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_B
        ).all()
        system_b_ids = set([t.transaction_id for t in system_b_transactions])

        # SET OPERATIONS FOR RECONCILIATION
        # Intersection: Transactions in BOTH systems (matched)
        matched = system_a_ids & system_b_ids
        
        # Difference: Transactions only in system A (missing from system B)
        only_in_a = system_a_ids - system_b_ids
        
        # Difference: Transactions only in system B (missing from system A)
        only_in_b = system_b_ids - system_a_ids

        # Calculate match rate
        total_unique = len(system_a_ids | system_b_ids)  # Union for total unique
        if total_unique > 0:
            match_rate = (len(matched) / total_unique) * 100
        else:
            match_rate = 0.0

        return ReconciliationResult(
            session_id=session_id,
            session_name=session.session_name,
            system_a_name=session.system_a_name,
            system_b_name=session.system_b_name,
            total_system_a=len(system_a_ids),
            total_system_b=len(system_b_ids),
            matched_count=len(matched),
            matched_transactions=sorted(list(matched)),
            only_in_system_a_count=len(only_in_a),
            only_in_system_a=sorted(list(only_in_a)),
            only_in_system_b_count=len(only_in_b),
            only_in_system_b=sorted(list(only_in_b)),
            match_rate=round(match_rate, 2)
        )

    @staticmethod
    def find_amount_discrepancies(db: Session, session_id: int) -> AmountDiscrepancyResult:
        """
        Find transactions where the same transaction_id exists in both systems
        but with different amounts
        """
        session = db.query(ReconciliationSession).filter(ReconciliationSession.id == session_id).first()
        if not session:
            raise ValueError(f"Reconciliation session with id {session_id} not found")

        # Get all transactions from both systems
        system_a_trans = db.query(Transaction).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_A
        ).all()
        
        system_b_trans = db.query(Transaction).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_B
        ).all()

        # Create dictionaries for easy lookup
        system_a_amounts = {t.transaction_id: t.amount for t in system_a_trans}
        system_b_amounts = {t.transaction_id: t.amount for t in system_b_trans}

        # Find transactions in both systems (intersection)
        common_ids = set(system_a_amounts.keys()) & set(system_b_amounts.keys())

        # Check for amount discrepancies
        discrepancies = []
        total_discrepancy = 0.0

        for trans_id in common_ids:
            amount_a = system_a_amounts[trans_id]
            amount_b = system_b_amounts[trans_id]
            
            if amount_a != amount_b:
                difference = abs(amount_a - amount_b)
                discrepancies.append(
                    AmountDiscrepancyDetail(
                        transaction_id=trans_id,
                        system_a_amount=amount_a,
                        system_b_amount=amount_b,
                        difference=difference
                    )
                )
                total_discrepancy += difference

        return AmountDiscrepancyResult(
            session_id=session_id,
            session_name=session.session_name,
            transactions_with_discrepancies=len(discrepancies),
            discrepancies=sorted(discrepancies, key=lambda x: x.difference, reverse=True),
            total_discrepancy_amount=round(total_discrepancy, 2)
        )

    @staticmethod
    def get_reconciliation_summary(db: Session, session_id: int) -> ReconciliationSummary:
        """Get summary statistics for a reconciliation session"""
        session = db.query(ReconciliationSession).filter(ReconciliationSession.id == session_id).first()
        if not session:
            raise ValueError(f"Reconciliation session with id {session_id} not found")

        # Count transactions by system
        system_a_count = db.query(func.count(Transaction.id)).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_A
        ).scalar()

        system_b_count = db.query(func.count(Transaction.id)).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_B
        ).scalar()

        # Get transaction IDs for set operations
        system_a_ids = set([
            t.transaction_id for t in db.query(Transaction.transaction_id).filter(
                Transaction.session_id == session_id,
                Transaction.system == SystemType.SYSTEM_A
            ).all()
        ])

        system_b_ids = set([
            t.transaction_id for t in db.query(Transaction.transaction_id).filter(
                Transaction.session_id == session_id,
                Transaction.system == SystemType.SYSTEM_B
            ).all()
        ])

        # Calculate matches and discrepancies
        matched = len(system_a_ids & system_b_ids)
        discrepancy = len((system_a_ids - system_b_ids) | (system_b_ids - system_a_ids))

        # Calculate match rate
        total_unique = len(system_a_ids | system_b_ids)
        if total_unique > 0:
            match_rate = (matched / total_unique) * 100
        else:
            match_rate = 0.0

        # Calculate total amounts
        system_a_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_A
        ).scalar() or 0.0

        system_b_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.session_id == session_id,
            Transaction.system == SystemType.SYSTEM_B
        ).scalar() or 0.0

        return ReconciliationSummary(
            session_id=session_id,
            session_name=session.session_name,
            system_a_name=session.system_a_name,
            system_b_name=session.system_b_name,
            system_a_count=system_a_count,
            system_b_count=system_b_count,
            matched_count=matched,
            discrepancy_count=discrepancy,
            match_rate=round(match_rate, 2),
            system_a_total_amount=round(system_a_total, 2),
            system_b_total_amount=round(system_b_total, 2),
            amount_difference=round(abs(system_a_total - system_b_total), 2)
        )

    @staticmethod
    def clear_all_transactions(db: Session, session_id: int) -> int:
        """Delete all transactions for a session"""
        count = db.query(Transaction).filter(Transaction.session_id == session_id).delete()
        db.commit()
        return count