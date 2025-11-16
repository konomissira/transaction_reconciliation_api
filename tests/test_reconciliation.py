import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test basic health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"


class TestSessionManagement:
    """Test reconciliation session creation and management"""
    
    def test_create_session(self, client, sample_session):
        """Test creating a new reconciliation session"""
        response = client.post("/api/v1/sessions", json=sample_session)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["session_name"] == sample_session["session_name"]
        assert data["system_a_name"] == sample_session["system_a_name"]
        assert data["system_b_name"] == sample_session["system_b_name"]
        assert "id" in data
    
    def test_create_duplicate_session(self, client, sample_session):
        """Test creating a session with duplicate name fails"""
        # Create first session
        client.post("/api/v1/sessions", json=sample_session)
        
        # Try to create duplicate
        response = client.post("/api/v1/sessions", json=sample_session)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_all_sessions_empty(self, client):
        """Test getting sessions when none exist"""
        response = client.get("/api/v1/sessions")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_sessions(self, client, sample_session):
        """Test getting all sessions"""
        # Create a session
        client.post("/api/v1/sessions", json=sample_session)
        
        # Get all sessions
        response = client.get("/api/v1/sessions")
        assert response.status_code == status.HTTP_200_OK
        sessions = response.json()
        assert len(sessions) == 1
        assert sessions[0]["session_name"] == sample_session["session_name"]
    
    def test_get_session_by_id(self, client, sample_session):
        """Test getting a specific session by ID"""
        # Create session
        create_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = create_response.json()["id"]
        
        # Get session by ID
        response = client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == session_id
    
    def test_get_nonexistent_session(self, client):
        """Test getting a session that doesn't exist"""
        response = client.get("/api/v1/sessions/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_session(self, client, sample_session):
        """Test deleting a session"""
        # Create session
        create_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = create_response.json()["id"]
        
        # Delete session
        response = client.delete(f"/api/v1/sessions/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's gone
        response = client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTransactionManagement:
    """Test transaction creation and management"""
    
    def test_create_single_transaction(self, client, sample_session):
        """Test creating a single transaction"""
        # Create session first
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Create transaction
        transaction_data = {
            "transaction_id": "TXN-999",
            "system": "system_a",
            "amount": 999.99,
            "transaction_metadata": "Test transaction"
        }
        response = client.post(f"/api/v1/transactions?session_id={session_id}", json=transaction_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transaction_id"] == "TXN-999"
        assert data["amount"] == 999.99
    
    def test_bulk_upload_transactions(self, client, sample_session, sample_system_a_transactions):
        """Test bulk uploading transactions"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Bulk upload
        bulk_data = {
            "session_id": session_id,
            "transactions": sample_system_a_transactions["transactions"]
        }
        response = client.post("/api/v1/transactions/bulk", json=bulk_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "Successfully uploaded 5 transactions" in data["message"]
    
    def test_get_transactions_by_session(self, client, sample_session, sample_system_a_transactions):
        """Test getting all transactions for a session"""
        # Create session and transactions
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        bulk_data = {
            "session_id": session_id,
            "transactions": sample_system_a_transactions["transactions"]
        }
        client.post("/api/v1/transactions/bulk", json=bulk_data)
        
        # Get transactions
        response = client.get(f"/api/v1/transactions/session/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 5
    
    def test_get_transactions_by_system(self, client, sample_session, sample_system_a_transactions, sample_system_b_transactions):
        """Test getting transactions by system"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload transactions from both systems
        bulk_a = {"session_id": session_id, "transactions": sample_system_a_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        bulk_b = {"session_id": session_id, "transactions": sample_system_b_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Get System A transactions
        response = client.get(f"/api/v1/transactions/session/{session_id}/system/system_a")
        assert response.status_code == status.HTTP_200_OK
        system_a = response.json()
        assert len(system_a) == 5
        assert all(t["system"] == "system_a" for t in system_a)
        
        # Get System B transactions
        response = client.get(f"/api/v1/transactions/session/{session_id}/system/system_b")
        assert response.status_code == status.HTTP_200_OK
        system_b = response.json()
        assert len(system_b) == 4
        assert all(t["system"] == "system_b" for t in system_b)


class TestReconciliation:
    """Test reconciliation logic using SET operations"""
    
    def test_reconciliation_with_no_data(self, client, sample_session):
        """Test reconciliation when no transactions exist"""
        # Create session with no transactions
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Analyse reconciliation
        response = client.get(f"/api/v1/reconciliation/analyse/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total_system_a"] == 0
        assert data["total_system_b"] == 0
        assert data["matched_count"] == 0
        assert data["matched_transactions"] == []
        assert data["match_rate"] == 0.0
    
    def test_reconciliation_analysis(self, client, sample_session, sample_system_a_transactions, sample_system_b_transactions):
        """Test reconciliation using SET INTERSECTION and DIFFERENCE"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload transactions from both systems
        bulk_a = {"session_id": session_id, "transactions": sample_system_a_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        bulk_b = {"session_id": session_id, "transactions": sample_system_b_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Analyse reconciliation
        response = client.get(f"/api/v1/reconciliation/analyse/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify results
        # System A: TXN-101, 102, 103, 104, 105
        # System B: TXN-101, 102, 103, 106
        # Matched (INTERSECTION): TXN-101, 102, 103
        # Only in A (DIFFERENCE): TXN-104, 105
        # Only in B (DIFFERENCE): TXN-106
        
        assert data["total_system_a"] == 5
        assert data["total_system_b"] == 4
        assert data["matched_count"] == 3
        assert set(data["matched_transactions"]) == {"TXN-101", "TXN-102", "TXN-103"}
        assert data["only_in_system_a_count"] == 2
        assert set(data["only_in_system_a"]) == {"TXN-104", "TXN-105"}
        assert data["only_in_system_b_count"] == 1
        assert set(data["only_in_system_b"]) == {"TXN-106"}
        
        # Match rate: 3 matched / 6 total unique = 50%
        assert data["match_rate"] == 50.0
    
    def test_perfect_reconciliation(self, client, sample_session):
        """Test reconciliation when all transactions match"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload same transactions to both systems
        transactions = [
            {"transaction_id": "TXN-201", "system": "system_a", "amount": 100.00, "transaction_metadata": "Test"},
            {"transaction_id": "TXN-202", "system": "system_a", "amount": 200.00, "transaction_metadata": "Test"}
        ]
        bulk_a = {"session_id": session_id, "transactions": transactions}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        transactions_b = [
            {"transaction_id": "TXN-201", "system": "system_b", "amount": 100.00, "transaction_metadata": "Test"},
            {"transaction_id": "TXN-202", "system": "system_b", "amount": 200.00, "transaction_metadata": "Test"}
        ]
        bulk_b = {"session_id": session_id, "transactions": transactions_b}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Analyse
        response = client.get(f"/api/v1/reconciliation/analyse/{session_id}")
        data = response.json()
        
        assert data["matched_count"] == 2
        assert data["only_in_system_a_count"] == 0
        assert data["only_in_system_b_count"] == 0
        assert data["match_rate"] == 100.0
    
    def test_no_matches_reconciliation(self, client, sample_session):
        """Test reconciliation when no transactions match"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload completely different transactions
        transactions_a = [
            {"transaction_id": "TXN-301", "system": "system_a", "amount": 100.00, "transaction_metadata": "Test"}
        ]
        bulk_a = {"session_id": session_id, "transactions": transactions_a}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        transactions_b = [
            {"transaction_id": "TXN-999", "system": "system_b", "amount": 999.00, "transaction_metadata": "Test"}
        ]
        bulk_b = {"session_id": session_id, "transactions": transactions_b}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Analyse
        response = client.get(f"/api/v1/reconciliation/analyse/{session_id}")
        data = response.json()
        
        assert data["matched_count"] == 0
        assert data["only_in_system_a_count"] == 1
        assert data["only_in_system_b_count"] == 1
        assert data["match_rate"] == 0.0


class TestAmountDiscrepancies:
    """Test amount discrepancy detection"""
    
    def test_find_amount_discrepancies(self, client, sample_session):
        """Test finding transactions with amount discrepancies"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload transactions with same IDs but different amounts
        transactions_a = [
            {"transaction_id": "TXN-401", "system": "system_a", "amount": 100.00, "transaction_metadata": "Test"},
            {"transaction_id": "TXN-402", "system": "system_a", "amount": 200.00, "transaction_metadata": "Test"},
            {"transaction_id": "TXN-403", "system": "system_a", "amount": 300.00, "transaction_metadata": "Test"}
        ]
        bulk_a = {"session_id": session_id, "transactions": transactions_a}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        transactions_b = [
            {"transaction_id": "TXN-401", "system": "system_b", "amount": 100.00, "transaction_metadata": "Match"},
            {"transaction_id": "TXN-402", "system": "system_b", "amount": 250.00, "transaction_metadata": "Different!"},
            {"transaction_id": "TXN-403", "system": "system_b", "amount": 350.00, "transaction_metadata": "Different!"}
        ]
        bulk_b = {"session_id": session_id, "transactions": transactions_b}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Find discrepancies
        response = client.get(f"/api/v1/reconciliation/discrepancies/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["transactions_with_discrepancies"] == 2
        assert len(data["discrepancies"]) == 2
        
        # Check TXN-402 discrepancy (200 vs 250 = 50 difference)
        txn_402 = next(d for d in data["discrepancies"] if d["transaction_id"] == "TXN-402")
        assert txn_402["system_a_amount"] == 200.00
        assert txn_402["system_b_amount"] == 250.00
        assert txn_402["difference"] == 50.00
        
        # Total discrepancy: 50 + 50 = 100
        assert data["total_discrepancy_amount"] == 100.00
    
    def test_no_amount_discrepancies(self, client, sample_session):
        """Test when all amounts match perfectly"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload same amounts
        transactions_a = [
            {"transaction_id": "TXN-501", "system": "system_a", "amount": 100.00, "transaction_metadata": "Test"}
        ]
        bulk_a = {"session_id": session_id, "transactions": transactions_a}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        transactions_b = [
            {"transaction_id": "TXN-501", "system": "system_b", "amount": 100.00, "transaction_metadata": "Test"}
        ]
        bulk_b = {"session_id": session_id, "transactions": transactions_b}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Find discrepancies
        response = client.get(f"/api/v1/reconciliation/discrepancies/{session_id}")
        data = response.json()
        
        assert data["transactions_with_discrepancies"] == 0
        assert data["discrepancies"] == []
        assert data["total_discrepancy_amount"] == 0.0


class TestReconciliationSummary:
    """Test reconciliation summary statistics"""
    
    def test_get_summary(self, client, sample_session, sample_system_a_transactions, sample_system_b_transactions):
        """Test getting reconciliation summary"""
        # Create session
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        # Upload transactions
        bulk_a = {"session_id": session_id, "transactions": sample_system_a_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_a)
        
        bulk_b = {"session_id": session_id, "transactions": sample_system_b_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_b)
        
        # Get summary
        response = client.get(f"/api/v1/reconciliation/summary/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["session_id"] == session_id
        assert data["system_a_count"] == 5
        assert data["system_b_count"] == 4
        assert data["matched_count"] == 3
        assert data["discrepancy_count"] == 3  # 2 in A only + 1 in B only
        assert data["match_rate"] == 50.0
        
        # Check amounts
        # System A: 100 + 200 + 300 + 400 + 500 = 1500
        # System B: 100 + 200 + 300 + 600 = 1200
        assert data["system_a_total_amount"] == 1500.00
        assert data["system_b_total_amount"] == 1200.00
        assert data["amount_difference"] == 300.00


class TestDataCleanup:
    """Test data cleanup functionality"""
    
    def test_clear_session_transactions(self, client, sample_session, sample_system_a_transactions):
        """Test clearing all transactions for a session"""
        # Create session and transactions
        session_response = client.post("/api/v1/sessions", json=sample_session)
        session_id = session_response.json()["id"]
        
        bulk_data = {"session_id": session_id, "transactions": sample_system_a_transactions["transactions"]}
        client.post("/api/v1/transactions/bulk", json=bulk_data)
        
        # Verify transactions exist
        response = client.get(f"/api/v1/transactions/session/{session_id}")
        assert len(response.json()) == 5
        
        # Clear transactions
        response = client.delete(f"/api/v1/transactions/session/{session_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["details"]["deleted_count"] == 5
        
        # Verify transactions are gone
        response = client.get(f"/api/v1/transactions/session/{session_id}")
        assert response.json() == []