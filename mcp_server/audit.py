import json
from datetime import datetime, timezone
from typing import Any, Dict

from mcp_server.config import AUDIT_LOG_DIR, AUDIT_LOG_FILE


def _ensure_log_dir() -> None:
    AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_tool_call(
    *,
    tool_name: str,
    arguments: Dict[str, Any],
    success: bool,
    error: str | None = None,
) -> None:
    """
    Write a structured audit log entry (JSONL).
    """
    _ensure_log_dir()

    record = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "tool": tool_name,
        "arguments": arguments,
        "success": success,
        "error": error,
    }

    with AUDIT_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")