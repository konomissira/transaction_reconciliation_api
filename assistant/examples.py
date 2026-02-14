from fastapi import APIRouter

router = APIRouter()


@router.get("/examples")
def examples():
    return {
        "examples": [
            {"prompt": "health", "description": "Check if the API is running"},
            {"prompt": "list sessions", "description": "List all reconciliation sessions"},
            {"prompt": "get session 1", "description": "Get details of a specific session"},
            {"prompt": "reconcile session 1", "description": "Run reconciliation analysis using set operations"},
            {"prompt": "show discrepancies for session 1", "description": "Find amount mismatches between systems"},
            {"prompt": "summary for session 1", "description": "Get reconciliation summary with match rate"},
            {"prompt": "show transactions for session 1", "description": "List all transactions in a session"},
        ]
    }