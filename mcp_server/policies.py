from typing import Any, Dict

from mcp_server.config import (
    ALLOW_WRITE_TOOLS,
    MAX_SESSION_NAME_LENGTH,
    MAX_TRANSACTIONS_PER_UPLOAD,
)

# -------------------------
# Tool classification
# -------------------------

READ_TOOLS = {
    "health",
    "list_sessions",
    "get_session",
    "list_transactions",
    "reconcile",
    "get_discrepancies",
    "get_summary",
}

WRITE_TOOLS = {
    "create_session",
    "bulk_upload_transactions",
    "delete_session",
    "clear_transactions",
}


def validate_tool_allowed(tool_name: str) -> None:
    if tool_name in WRITE_TOOLS and not ALLOW_WRITE_TOOLS:
        raise PermissionError(f"Write tool '{tool_name}' is disabled")


def validate_tool_inputs(tool_name: str, args: Dict[str, Any]) -> None:
    """
    Enforce per-tool input constraints.
    """
    if tool_name == "create_session":
        name = args.get("session_name", "")
        if len(name) > MAX_SESSION_NAME_LENGTH:
            raise ValueError("session_name too long")

    if tool_name == "bulk_upload_transactions":
        transactions = args.get("transactions", [])
        if len(transactions) > MAX_TRANSACTIONS_PER_UPLOAD:
            raise ValueError(f"transactions exceeds limit ({MAX_TRANSACTIONS_PER_UPLOAD})")