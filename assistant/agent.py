import re
from typing import Any, Dict, Optional, Tuple

import httpx

from assistant.config import ASSISTANT_API_BASE_URL, ASSISTANT_HTTP_TIMEOUT


def _extract_ints(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"\b\d+\b", text)]


def _infer_action(message: str) -> Tuple[str, Dict[str, Any]]:
    """Rule-based intent router (v1)."""
    msg = message.strip().lower()

    # Health
    if "health" in msg or "status" in msg:
        return "health", {}

    # List sessions
    if "list sessions" in msg or ("sessions" in msg and ("list" in msg or "show" in msg or "all" in msg)):
        return "list_sessions", {}

    # Get specific session
    if "get session" in msg or "session details" in msg:
        ints = _extract_ints(msg)
        if ints:
            return "get_session", {"session_id": ints[0]}
        return "help", {"reason": "missing_session_id"}

    # Reconciliation summary
    if "summary" in msg:
        ints = _extract_ints(msg)
        if ints:
            return "get_summary", {"session_id": ints[0]}
        return "help", {"reason": "missing_session_id"}

    # Amount discrepancies
    if "discrepanc" in msg or "mismatch" in msg:
        ints = _extract_ints(msg)
        if ints:
            return "get_discrepancies", {"session_id": ints[0]}
        return "help", {"reason": "missing_session_id"}

    # Reconcile / analyse
    if "reconcil" in msg or "analyse" in msg or "analyze" in msg or "compare" in msg or "match" in msg:
        ints = _extract_ints(msg)
        if ints:
            return "reconcile", {"session_id": ints[0]}
        return "help", {"reason": "missing_session_id"}

    # Show transactions for a session
    if "transaction" in msg:
        ints = _extract_ints(msg)
        if ints:
            return "list_transactions", {"session_id": ints[0]}
        return "help", {"reason": "missing_session_id"}

    return "help", {"reason": "unknown_intent"}


async def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{ASSISTANT_API_BASE_URL}{path}"
    timeout = ASSISTANT_HTTP_TIMEOUT

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, json=json)
        if resp.status_code >= 400:
            detail = resp.text
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                pass
            raise ValueError(f"API error ({resp.status_code}): {detail}")
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return {"raw": resp.text}


async def run_assistant(message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Returns dict with:
      - action
      - result
      - explanation
    """
    action, params = _infer_action(message)

    # Allow deterministic overrides via metadata
    if metadata and isinstance(metadata, dict) and "action" in metadata:
        action = str(metadata["action"])
        params = dict(metadata.get("params", {}))

    if action == "health":
        data = await _request("GET", "/health")
        return {
            "action": "health",
            "result": data if isinstance(data, dict) else {"data": data},
            "explanation": "Health check completed successfully.",
        }

    if action == "list_sessions":
        data = await _request("GET", "/api/v1/sessions")
        count = len(data) if isinstance(data, list) else None
        return {
            "action": "list_sessions",
            "result": {"count": count, "sessions": data},
            "explanation": f"Found {count} reconciliation session(s).",
        }

    if action == "get_session":
        session_id = int(params["session_id"])
        data = await _request("GET", f"/api/v1/sessions/{session_id}")
        return {
            "action": "get_session",
            "result": {"session": data},
            "explanation": f"Fetched details for session #{session_id}.",
        }

    if action == "reconcile":
        session_id = int(params["session_id"])
        data = await _request("GET", f"/api/v1/reconciliation/analyse/{session_id}")
        explanation = "Reconciliation analysis completed."
        if isinstance(data, dict):
            matched = data.get("matched_count")
            only_a = data.get("only_in_system_a_count")
            only_b = data.get("only_in_system_b_count")
            match_rate = data.get("match_rate")
            if matched is not None:
                explanation = (
                    f"Reconciliation complete: {matched} matched transactions, "
                    f"{only_a} only in System A, {only_b} only in System B. "
                    f"Match rate: {match_rate}%."
                )
        return {
            "action": "reconcile",
            "result": {"analysis": data},
            "explanation": explanation,
        }

    if action == "get_discrepancies":
        session_id = int(params["session_id"])
        data = await _request("GET", f"/api/v1/reconciliation/discrepancies/{session_id}")
        explanation = "Discrepancy analysis completed."
        if isinstance(data, dict):
            count = data.get("discrepancy_count")
            total = data.get("total_discrepancy_amount")
            if count is not None:
                explanation = (
                    f"Found {count} amount discrepancies "
                    f"with a total difference of ${total}."
                )
        return {
            "action": "get_discrepancies",
            "result": {"discrepancies": data},
            "explanation": explanation,
        }

    if action == "get_summary":
        session_id = int(params["session_id"])
        data = await _request("GET", f"/api/v1/reconciliation/summary/{session_id}")
        explanation = "Reconciliation summary retrieved."
        if isinstance(data, dict):
            match_rate = data.get("match_rate")
            total_a = data.get("system_a_total")
            total_b = data.get("system_b_total")
            if match_rate is not None:
                explanation = (
                    f"Session summary: match rate is {match_rate}%, "
                    f"System A total: ${total_a}, System B total: ${total_b}."
                )
        return {
            "action": "get_summary",
            "result": {"summary": data},
            "explanation": explanation,
        }

    if action == "list_transactions":
        session_id = int(params["session_id"])
        data = await _request("GET", f"/api/v1/transactions/session/{session_id}")
        count = len(data) if isinstance(data, list) else None
        return {
            "action": "list_transactions",
            "result": {"count": count, "transactions": data},
            "explanation": f"Found {count} transaction(s) for session #{session_id}.",
        }

    # Help / fallback
    return {
        "action": "help",
        "result": {
            "examples": [
                "health",
                "list sessions",
                "get session 1",
                "reconcile session 1",
                "show discrepancies for session 1",
                "summary for session 1",
                "show transactions for session 1",
            ],
            "hint": "Include a session ID for reconciliation commands, e.g. 'reconcile session 1'.",
            "reason": params.get("reason"),
        },
        "explanation": "I couldn't confidently infer the action from your message. Try one of the examples.",
    }