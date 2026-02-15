# MCP Server — Transaction Reconciliation API

This MCP (Model Context Protocol) server exposes the Transaction Reconciliation API as governed, auditable tools using the MCP Python SDK (FastMCP).

## Purpose

Allow MCP clients (e.g. Claude Desktop) to interact with the reconciliation system through structured tool calls with policy enforcement and audit logging on every action.

## Tools

### READ Tools

| Tool                | Description                                  |
| ------------------- | -------------------------------------------- |
| `health`            | Check API health                             |
| `list_sessions`     | List all reconciliation sessions             |
| `get_session`       | Get a specific session by ID                 |
| `list_transactions` | List transactions for a session              |
| `reconcile`         | Run reconciliation analysis (set operations) |
| `get_discrepancies` | Find amount mismatches between systems       |
| `get_summary`       | Get reconciliation summary with match rate   |

### WRITE Tools

| Tool                 | Description                           |
| -------------------- | ------------------------------------- |
| `create_session`     | Create a new reconciliation session   |
| `delete_session`     | Delete a session and its transactions |
| `clear_transactions` | Delete all transactions for a session |

## Governance

- All tool calls are validated against policies before execution
- Write tools can be disabled via `ALLOW_WRITE_TOOLS` flag
- Input constraints enforced (name lengths, transaction limits)
- Every tool call is audit logged (success and failure)

## Running

```bash
./scripts/run_mcp.sh
```

## Audit Logs

All tool calls are logged to `logs/mcp_audit.log` in JSONL format.
