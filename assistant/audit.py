import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from assistant.config import ASSISTANT_AUDIT_DIR, ASSISTANT_AUDIT_FILE


def _ensure_dir() -> None:
    ASSISTANT_AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def log_assistant_action(
    *,
    action: str,
    arguments: Dict[str, Any],
    success: bool,
    error: Optional[str] = None,
) -> None:
    _ensure_dir()

    record = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "action": action,
        "arguments": arguments,
        "success": success,
        "error": error,
    }

    with ASSISTANT_AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")