import os
import httpx
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_server.audit import log_tool_call
from mcp_server.policies import validate_tool_allowed, validate_tool_inputs


mcp = FastMCP("Transaction Reconciliation API - MCP Tools")

BASE_URL = os.getenv("RECONCILIATION_API_BASE_URL", "http://localhost:8000").rstrip("/")
DEFAULT_TIMEOUT = float(os.getenv("MCP_HTTP_TIMEOUT", "15"))


async def _request(method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{BASE_URL}{path}"

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.request(method, url, json=json)
        resp.raise_for_status()
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.text


# -------------------------
# READ tools
# -------------------------

@mcp.tool()
async def health() -> Dict[str, Any]:
    """Check the API health (calls GET /health)."""
    tool_name = "health"
    audit_args: Dict[str, Any] = {}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, {})

        result = await _request("GET", "/health")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def list_sessions() -> List[Dict[str, Any]]:
    """List all reconciliation sessions (calls GET /api/v1/sessions)."""
    tool_name = "list_sessions"
    audit_args: Dict[str, Any] = {}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, {})

        result = await _request("GET", "/api/v1/sessions")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def get_session(session_id: int) -> Dict[str, Any]:
    """Get a specific reconciliation session (calls GET /api/v1/sessions/{id})."""
    tool_name = "get_session"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("GET", f"/api/v1/sessions/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def list_transactions(session_id: int) -> List[Dict[str, Any]]:
    """List all transactions for a session (calls GET /api/v1/transactions/session/{id})."""
    tool_name = "list_transactions"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("GET", f"/api/v1/transactions/session/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def reconcile(session_id: int) -> Dict[str, Any]:
    """Run reconciliation analysis using set operations (calls GET /api/v1/reconciliation/analyse/{id})."""
    tool_name = "reconcile"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("GET", f"/api/v1/reconciliation/analyse/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def get_discrepancies(session_id: int) -> Dict[str, Any]:
    """Find amount discrepancies between systems (calls GET /api/v1/reconciliation/discrepancies/{id})."""
    tool_name = "get_discrepancies"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("GET", f"/api/v1/reconciliation/discrepancies/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def get_summary(session_id: int) -> Dict[str, Any]:
    """Get reconciliation summary with match rate (calls GET /api/v1/reconciliation/summary/{id})."""
    tool_name = "get_summary"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("GET", f"/api/v1/reconciliation/summary/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


# -------------------------
# WRITE tools
# -------------------------

@mcp.tool()
async def create_session(
    session_name: str,
    system_a_name: str,
    system_b_name: str,
) -> Dict[str, Any]:
    """Create a new reconciliation session (calls POST /api/v1/sessions)."""
    tool_name = "create_session"

    payload = {
        "session_name": session_name,
        "system_a_name": system_a_name,
        "system_b_name": system_b_name,
    }

    audit_args = {
        "session_name": session_name,
        "system_a_name": system_a_name,
        "system_b_name": system_b_name,
    }

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, payload)

        result = await _request("POST", "/api/v1/sessions", json=payload)

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def delete_session(session_id: int) -> Dict[str, Any]:
    """Delete a reconciliation session and all its transactions (calls DELETE /api/v1/sessions/{id})."""
    tool_name = "delete_session"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("DELETE", f"/api/v1/sessions/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


@mcp.tool()
async def clear_transactions(session_id: int) -> Dict[str, Any]:
    """Delete all transactions for a session (calls DELETE /api/v1/transactions/session/{id})."""
    tool_name = "clear_transactions"
    audit_args = {"session_id": session_id}

    try:
        validate_tool_allowed(tool_name)
        validate_tool_inputs(tool_name, audit_args)

        result = await _request("DELETE", f"/api/v1/transactions/session/{session_id}")

        log_tool_call(tool_name=tool_name, arguments=audit_args, success=True)
        return result

    except Exception as exc:
        log_tool_call(tool_name=tool_name, arguments=audit_args, success=False, error=str(exc))
        raise


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()