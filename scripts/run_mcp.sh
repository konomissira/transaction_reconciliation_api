#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/mahamadoucamara/2026_projects/personal_project/transaction_reconciliation_api"
PYTHON="$REPO_DIR/.venv/bin/python"

export RECONCILIATION_API_BASE_URL="http://localhost:8000"
export MCP_HTTP_TIMEOUT="5"
export PYTHONPATH="$REPO_DIR"

mkdir -p "$REPO_DIR/logs"

cd "$REPO_DIR"

exec 2>>"$REPO_DIR/logs/mcp_server.stderr.log"

exec "$PYTHON" -m mcp_server.server