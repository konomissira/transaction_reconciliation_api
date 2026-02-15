from pathlib import Path

# -------------------------
# Tool execution limits
# -------------------------

MAX_SESSION_NAME_LENGTH = 255
MAX_TRANSACTIONS_PER_UPLOAD = 10_000

# -------------------------
# Governance flags
# -------------------------

ALLOW_WRITE_TOOLS = True

# -------------------------
# Audit logging
# -------------------------

AUDIT_LOG_DIR = Path("logs")
AUDIT_LOG_FILE = AUDIT_LOG_DIR / "mcp_audit.log"