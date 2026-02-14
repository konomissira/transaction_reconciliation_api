import os
from pathlib import Path

# In Docker, localhost:8002 is the same container.
ASSISTANT_API_BASE_URL = os.getenv("ASSISTANT_API_BASE_URL", "http://localhost:8000").rstrip("/")
ASSISTANT_HTTP_TIMEOUT = float(os.getenv("ASSISTANT_HTTP_TIMEOUT", "15"))

# Assistant audit log
ASSISTANT_AUDIT_DIR = Path("logs")
ASSISTANT_AUDIT_FILE = ASSISTANT_AUDIT_DIR / "assistant_audit.log"