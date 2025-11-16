#!/usr/bin/env python3
"""
Script to seed the database with sample transaction reconciliation data
Usage: python data/seed_data.py
"""
import json
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import ReconciliationSession, Transaction, SystemType


def clear_existing_data(db):
    """Clear all existing data"""
    transaction_count = db.query(Transaction).delete()
    session_count = db.query(ReconciliationSession).delete()
    db.commit()
    print(f"Cleared {session_count} existing sessions and {transaction_count} existing transactions")


def load_sample_data(db, clear_first=True):
    """Load sample transaction reconciliation data from JSON file"""
    if clear_first:
        clear_existing_data(db)
    
    # Read sample data file
    json_file = os.path.join(os.path.dirname(__file__), 'sample_transactions.json')
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create reconciliation session
    session = ReconciliationSession(
        session_name=data['session']['session_name'],
        system_a_name=data['session']['system_a_name'],
        system_b_name=data['session']['system_b_name'],
        description=data['session']['description']
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    print(f"Created reconciliation session: {session.session_name} (ID: {session.id})")
    print(f"  System A: {session.system_a_name}")
    print(f"  System B: {session.system_b_name}")
    
    # Create System A transactions
    system_a_transactions = []
    for trans_data in data['system_a_transactions']:
        transaction = Transaction(
            transaction_id=trans_data['transaction_id'],
            session_id=session.id,
            system=SystemType(trans_data['system']),
            amount=trans_data['amount'],
            transaction_metadata=trans_data['transaction_metadata']
        )
        system_a_transactions.append(transaction)
    
    db.add_all(system_a_transactions)
    db.commit()
    
    print(f"\nLoaded {len(system_a_transactions)} transactions from {session.system_a_name}")
    
    # Create System B transactions
    system_b_transactions = []
    for trans_data in data['system_b_transactions']:
        transaction = Transaction(
            transaction_id=trans_data['transaction_id'],
            session_id=session.id,
            system=SystemType(trans_data['system']),
            amount=trans_data['amount'],
            transaction_metadata=trans_data['transaction_metadata']
        )
        system_b_transactions.append(transaction)
    
    db.add_all(system_b_transactions)
    db.commit()
    
    print(f"Loaded {len(system_b_transactions)} transactions from {session.system_b_name}")
    
    # Calculate and display reconciliation summary
    print("\n--- Reconciliation Analysis ---")
    
    # Get transaction IDs for set operations
    system_a_ids = set(t.transaction_id for t in system_a_transactions)
    system_b_ids = set(t.transaction_id for t in system_b_transactions)
    
    # SET OPERATIONS
    matched = system_a_ids & system_b_ids  # Intersection
    only_in_a = system_a_ids - system_b_ids  # Difference
    only_in_b = system_b_ids - system_a_ids  # Difference
    
    print(f"\n✅ Matched transactions: {len(matched)}")
    print(f"   Transaction IDs: {sorted(list(matched))}")
    
    print(f"\n⚠️  Only in {session.system_a_name}: {len(only_in_a)}")
    print(f"   Transaction IDs: {sorted(list(only_in_a))}")
    
    print(f"\n⚠️  Only in {session.system_b_name}: {len(only_in_b)}")
    print(f"   Transaction IDs: {sorted(list(only_in_b))}")
    
    # Calculate match rate
    total_unique = len(system_a_ids | system_b_ids)
    if total_unique > 0:
        match_rate = (len(matched) / total_unique) * 100
        print(f"\n📊 Match Rate: {match_rate:.1f}% ({len(matched)} out of {total_unique} unique transactions)")
    
    # Calculate amounts
    system_a_total = sum(t.amount for t in system_a_transactions)
    system_b_total = sum(t.amount for t in system_b_transactions)
    
    print(f"\n💰 Financial Summary:")
    print(f"   {session.system_a_name} total: ${system_a_total:,.2f}")
    print(f"   {session.system_b_name} total: ${system_b_total:,.2f}")
    print(f"   Difference: ${abs(system_a_total - system_b_total):,.2f}")
    
    return session.id


def main():
    """Main function"""
    print("=" * 70)
    print("Transaction Reconciliation API - Data Seeding")
    print("=" * 70)
    print()
    
    # Create database session
    db = SessionLocal()
    
    try:
        session_id = load_sample_data(db, clear_first=True)
        print("\n" + "=" * 70)
        print("✅ Database seeded successfully!")
        print("=" * 70)
        print(f"\nSession ID: {session_id}")
        print("\nYou can now:")
        print("1. Visit http://localhost:8002/docs to test the API")
        print(f"2. Try GET /api/v1/reconciliation/analyse/{session_id}")
        print(f"3. Try GET /api/v1/reconciliation/summary/{session_id}")
        print(f"4. Try GET /api/v1/reconciliation/discrepancies/{session_id}")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()