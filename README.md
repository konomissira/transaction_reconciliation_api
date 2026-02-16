# Transaction Reconciliation API

A production-ready REST API for reconciling transactions between different systems using Python set operations now extended with a **governed AI assistant** and **MCP server** for safe, auditable interaction.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-21%20passed-success.svg)](tests/)
[![MCP](https://img.shields.io/badge/MCP-enabled-blueviolet.svg)](mcp_server/)

## 📋 Overview

This project demonstrates efficient transaction reconciliation for matching records between two systems (finance vs payment processor, source vs target database, etc.) using **Python set intersection and difference operations**. Built as a real-world example of how data structures solve practical data engineering problems.

On top of the core API, this project includes:

- **A governed AI assistant** a deterministic, rule-based assistant layer that maps natural language questions to explicit API actions. No LLM, no black-box model. Every interaction is structured, explainable, and auditable.
- **A browser-based chat UI** a plain HTML/JavaScript interface that talks directly to the assistant API running locally.
- **An MCP server** exposes the API as governed tools for Claude Desktop, with policy enforcement and audit logging on every action.

### The Philosophy

> **AI is not the system. AI is the interface.**

The system is still: clean data models, deterministic logic, governance and auditability, clear separation of concerns, and production-friendly deployment (Docker, APIs, tests).

### The Problem

**Real-World Scenario:**

- Finance team: **2,847 payments recorded**
- Stripe: **2,844 payments confirmed**
- **CFO asks: "Which 3 are missing? What's matched?"**

Traditional approaches:

- Manual Excel VLOOKUP (hours of work, error-prone)
- Nested loops checking each record (O(n²) - too slow at scale)
- Complex SQL queries across systems (fragile and hard to maintain)
- Month-end panic when discrepancies are discovered

### The Solution

Using **set intersection and difference operations** to efficiently:

- Find matched transactions in O(n) time (INTERSECTION)
- Identify transactions only in System A (DIFFERENCE)
- Identify transactions only in System B (DIFFERENCE)
- Detect amount discrepancies automatically
- Generate reconciliation reports instantly

## 🚀 Features

### Core API

- **Session-Based Reconciliation**: Create sessions to compare any two systems
- **Matched Transactions**: Find records in both systems using SET INTERSECTION
- **Discrepancy Detection**: Identify missing records using SET DIFFERENCE
- **Amount Validation**: Detect transactions with matching IDs but different amounts
- **Match Rate Calculation**: Automatically calculate reconciliation success rates
- **Financial Summaries**: Track total amounts and discrepancies
- **Auto-generated API Docs**: Interactive Swagger UI and ReDoc
- **Comprehensive Tests**: 21 pytest unit tests covering all functionality
- **Sample Data**: Pre-built Finance vs Stripe scenario for quick demos
- **Modern Python**: Uses pyproject.toml for configuration (PEP 517/518/621)

### Governed AI Assistant

- **Natural Language Interface**: Ask questions like "reconcile session 1" or "show discrepancies for session 1"
- **Deterministic Intent Mapping**: Rule-based router maps user messages to explicit API actions
- **Structured Responses**: Every response includes the action taken, the result data, and a human-readable explanation
- **Audit Logging**: Every interaction is logged to `logs/assistant_audit.log` in JSONL format
- **Example Prompts**: Built-in `/assistant/examples` endpoint for discoverability
- **No External AI**: No LLM, no hosted models entirely local and inspectable

### MCP Server (Claude Desktop Integration)

- **Governed Tools**: API endpoints exposed as MCP tools with policy enforcement
- **Read/Write Classification**: Tools classified as READ or WRITE with configurable permissions
- **Input Validation**: Per-tool constraints (name lengths, transaction limits)
- **Audit Logging**: Every tool call logged to `logs/mcp_audit.log` in JSONL format
- **Write Disable Flag**: Disable all write operations via `ALLOW_WRITE_TOOLS` config

### Browser Chat UI

- **Standalone HTML**: Open `chat.html` directly in any browser no build step, no dependencies
- **Dark Grey & Emerald Green Theme**: Professional banking aesthetic
- **Real-time Interaction**: Talks directly to the assistant API on localhost

## 🛠️ Tech Stack

| Technology                   | Purpose                                      |
| ---------------------------- | -------------------------------------------- |
| **Python 3.11**              | Programming language                         |
| **FastAPI**                  | Modern, high-performance web framework       |
| **PostgreSQL 15**            | Relational database for transaction tracking |
| **SQLAlchemy**               | ORM for database operations                  |
| **Pydantic**                 | Data validation and serialisation            |
| **Docker & Docker-Compose**  | Containerization and orchestration           |
| **pytest**                   | Testing framework                            |
| **Uvicorn**                  | ASGI web server                              |
| **httpx**                    | Async HTTP client (assistant → API calls)    |
| **MCP Python SDK (FastMCP)** | Model Context Protocol server                |
| **pyproject.toml**           | Modern Python project configuration          |

## 📦 Installation

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- [Git](https://git-scm.com/) installed
- Ports 8000 and 5432 available

### Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/konomissira/transaction_reconciliation_api.git
    cd transaction_reconciliation_api
    ```

2. **Create environment file**

    ```bash
    cp .env.example .env
    ```

3. **Build and start containers**

    ```bash
    docker compose up --build
    ```

4. **Load sample data** (optional)

    ```bash
    docker compose exec app python data/seed_data.py
    ```

5. **Access the API**
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - API Root: http://localhost:8000

## 📖 Usage

### Quick Start with Sample Data

```bash
# Start the application
docker compose up -d

# Load sample Finance vs Stripe reconciliation
docker compose exec app python data/seed_data.py

# Access API documentation
open http://localhost:8000/docs
```

**Sample scenario:** 10 Finance records, 9 Stripe records, 7 matched (58.3% match rate), $494.25 discrepancy

### API Workflow

#### 1. Create a Reconciliation Session

**POST** `/api/v1/sessions`

```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "finance_vs_stripe_nov_2025",
    "system_a_name": "Internal Finance System",
    "system_b_name": "Stripe Payment Processor",
    "description": "November 2025 month-end reconciliation"
  }'
```

**Response:**

```json
{
    "id": 1,
    "session_name": "finance_vs_stripe_nov_2025",
    "system_a_name": "Internal Finance System",
    "system_b_name": "Stripe Payment Processor",
    "created_at": "2025-11-30T23:59:00Z"
}
```

#### 2. Upload Transactions from System A (Finance)

**POST** `/api/v1/transactions/bulk`

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "transactions": [
      {"transaction_id": "PAY-501", "system": "system_a", "amount": 150.00, "transaction_metadata": "Invoice #1001"},
      {"transaction_id": "PAY-502", "system": "system_a", "amount": 225.50, "transaction_metadata": "Invoice #1002"},
      {"transaction_id": "PAY-503", "system": "system_a", "amount": 320.00, "transaction_metadata": "Invoice #1003"}
    ]
  }'
```

#### 3. Upload Transactions from System B (Stripe)

**POST** `/api/v1/transactions/bulk`

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "transactions": [
      {"transaction_id": "PAY-501", "system": "system_b", "amount": 150.00, "transaction_metadata": "Stripe confirmed"},
      {"transaction_id": "PAY-502", "system": "system_b", "amount": 225.50, "transaction_metadata": "Stripe confirmed"}
    ]
  }'
```

#### 4. Reconcile Transactions (SET OPERATIONS)

**GET** `/api/v1/reconciliation/analyse/1`

```bash
curl http://localhost:8000/api/v1/reconciliation/analyse/1
```

**Response:**

```json
{
    "session_id": 1,
    "session_name": "finance_vs_stripe_nov_2025",
    "system_a_name": "Internal Finance System",
    "system_b_name": "Stripe Payment Processor",
    "total_system_a": 3,
    "total_system_b": 2,
    "matched_count": 2,
    "matched_transactions": ["PAY-501", "PAY-502"],
    "only_in_system_a_count": 1,
    "only_in_system_a": ["PAY-503"],
    "only_in_system_b_count": 0,
    "only_in_system_b": [],
    "match_rate": 66.67
}
```

**Interpretation:**

- **Matched (INTERSECTION):** PAY-501, PAY-502 ✅
- **Only in Finance:** PAY-503 (missing from Stripe) ⚠️
- **Match rate:** 66.67% (2 out of 3)

#### 5. Check Amount Discrepancies

**GET** `/api/v1/reconciliation/discrepancies/1`

Finds transactions that exist in both systems but with different amounts.

#### 6. Get Reconciliation Summary

**GET** `/api/v1/reconciliation/summary/1`

```bash
curl http://localhost:8000/api/v1/reconciliation/summary/1
```

Shows overall statistics including total amounts, match rate, and financial discrepancies.

## 🤖 Governed AI Assistant

The assistant layer provides a natural language interface to the reconciliation API without using any external AI service.

### How It Works

```
User message → Intent Router (rule-based) → API Call → Structured Response → Audit Log
```

Every interaction returns three things:

- **action**: What action was taken (e.g. `reconcile`, `get_summary`)
- **result**: The structured data from the API
- **explanation**: A human-readable summary

### Assistant Endpoints

| Endpoint              | Method | Description                     |
| --------------------- | ------ | ------------------------------- |
| `/assistant/chat`     | POST   | Send a natural language message |
| `/assistant/examples` | GET    | Get example prompts             |

### Example Prompts

| Prompt                             | Action                           |
| ---------------------------------- | -------------------------------- |
| `health`                           | Check API health                 |
| `list sessions`                    | List all reconciliation sessions |
| `get session 1`                    | Get details of session #1        |
| `reconcile session 1`              | Run reconciliation analysis      |
| `show discrepancies for session 1` | Find amount mismatches           |
| `summary for session 1`            | Get reconciliation summary       |
| `show transactions for session 1`  | List all transactions            |

### Using the Chat UI

1. Make sure Docker containers are running: `docker compose up`
2. Open `chat.html` in your browser (double-click the file)
3. Type a message like "reconcile session 1" and click Send

The chat UI talks directly to `http://localhost:8002/assistant/chat` no external services involved.

### Audit Logging

Every assistant interaction is logged to `logs/assistant_audit.log`:

```json
{
    "timestamp": "2026-02-15T10:30:00Z",
    "action": "reconcile",
    "arguments": { "message_len": 19 },
    "success": true,
    "error": null
}
```

## 🔌 MCP Server (Claude Desktop Integration)

The MCP server exposes the reconciliation API as governed tools using the MCP Python SDK (FastMCP), allowing Claude Desktop to interact with your data system through structured, auditable tool calls.

### Setup

1. **Install MCP SDK in your local virtual environment:**

    ```bash
    .venv/bin/pip install mcp httpx
    ```

2. **Add to Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

    ```json
    {
        "mcpServers": {
            "transaction_reconciliation": {
                "command": "/bin/bash",
                "args": [
                    "/path/to/transaction_reconciliation_api/scripts/run_mcp.sh"
                ]
            }
        }
    }
    ```

3. **Make sure Docker is running**, then restart Claude Desktop.

### Available Tools

#### READ Tools

| Tool                | Description                                  |
| ------------------- | -------------------------------------------- |
| `health`            | Check API health                             |
| `list_sessions`     | List all reconciliation sessions             |
| `get_session`       | Get a specific session by ID                 |
| `list_transactions` | List transactions for a session              |
| `reconcile`         | Run reconciliation analysis (set operations) |
| `get_discrepancies` | Find amount mismatches between systems       |
| `get_summary`       | Get reconciliation summary with match rate   |

#### WRITE Tools

| Tool                 | Description                           |
| -------------------- | ------------------------------------- |
| `create_session`     | Create a new reconciliation session   |
| `delete_session`     | Delete a session and its transactions |
| `clear_transactions` | Delete all transactions for a session |

### Governance

- All tool calls are validated against policies before execution
- Write tools can be disabled via `ALLOW_WRITE_TOOLS` flag in `mcp_server/config.py`
- Input constraints enforced (session name length, transaction upload limits)
- Every tool call is audit logged to `logs/mcp_audit.log`

## 🧮 Set Operations Explained

This project demonstrates three key set operations for reconciliation:

### 1. Intersection (`&`) - Find Matches

```python
finance = {"PAY-501", "PAY-502", "PAY-503"}
stripe = {"PAY-501", "PAY-502", "PAY-504"}

# SET INTERSECTION: Transactions in BOTH systems
matched = finance & stripe  # {"PAY-501", "PAY-502"}
```

**Result:** 2 matched transactions

### 2. Difference (`-`) - Find Missing in System B

```python
# SET DIFFERENCE: In Finance but not in Stripe
missing_from_stripe = finance - stripe  # {"PAY-503"}
```

**Result:** PAY-503 needs investigation

### 3. Difference (`-`) - Find Missing in System A

```python
# SET DIFFERENCE: In Stripe but not in Finance
missing_from_finance = stripe - finance  # {"PAY-504"}
```

**Result:** PAY-504 is unrecorded

### Calculate Match Rate

```python
# Union for total unique transactions
total_unique = finance | stripe  # {"PAY-501", "PAY-502", "PAY-503", "PAY-504"}

# Match rate
match_rate = len(matched) / len(total_unique) * 100  # 50%
```

## 🧪 Testing

Run the test suite with pytest:

```bash
# Run all tests
docker compose exec app pytest

# Run with verbose output
docker compose exec app pytest -v

# Run specific test class
docker compose exec app pytest tests/test_reconciliation.py::TestReconciliation -v

# Run locally (without Docker)
pytest -v
```

**Test Coverage:**

- Health check endpoints
- Session creation and management
- Transaction upload (single and bulk)
- Reconciliation analysis (SET INTERSECTION & DIFFERENCE)
- Amount discrepancy detection
- Reconciliation summary statistics
- Edge cases (no data, perfect matches, no matches)
- Data cleanup operations

**Result:** 21 tests passing ✅

## 📁 Project Structure

```
transaction_reconciliation_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLAlchemy models (ReconciliationSession, Transaction)
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── services.py          # Business logic (set operations)
│   └── api/
│       ├── __init__.py
│       └── endpoints.py     # API route definitions
├── assistant/
│   ├── __init__.py
│   ├── agent.py             # Intent inference + API calls + structured responses
│   ├── audit.py             # Append-only JSONL audit logging
│   ├── config.py            # Environment config (base URL, timeout, log paths)
│   ├── examples.py          # GET /examples endpoint for discoverability
│   ├── router.py            # POST /chat endpoint (orchestrates agent + audit)
│   └── schemas.py           # Pydantic request/response models
├── mcp_server/
│   ├── __init__.py
│   ├── server.py            # FastMCP tools (READ + WRITE)
│   ├── policies.py          # Tool classification + input validation
│   ├── audit.py             # JSONL audit logging for MCP tool calls
│   ├── config.py            # Governance flags + execution limits
│   └── README.md            # MCP server documentation
├── scripts/
│   └── run_mcp.sh           # Shell script to start MCP server locally
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and configuration
│   └── test_reconciliation.py  # Unit tests
├── data/
│   ├── README.md            # Sample data documentation
│   ├── sample_transactions.json
│   ├── sample_transactions.csv
│   └── seed_data.py         # Script to load sample data
├── chat.html                # Browser-based chat UI (standalone)
├── .env.example             # Environment variables template
├── .gitignore
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── pyproject.toml           # Modern Python project configuration
├── requirements.txt         # Python dependencies (for Docker)
└── README.md                # Documentation
```

## 🔧 Development

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Or using pyproject.toml:
pip install -e .

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_USER=reconciliation_user
export POSTGRES_PASSWORD=reconciliation_password
export POSTGRES_DB=reconciliation_db

# Run the application
uvicorn app.main:app --reload --port 8000
```

### Using pyproject.toml

This project uses modern Python packaging with `pyproject.toml`:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code with black
black app/ tests/

# Lint with ruff
ruff check app/ tests/
```

### Stopping the Application

```bash
# Stop containers
docker compose down

# Stop and remove volumes (clears database)
docker compose down -v
```

## 📊 Performance

Set operations provide excellent performance characteristics:

| Operation          | Time Complexity | Space Complexity |
| ------------------ | --------------- | ---------------- |
| Intersection (`&`) | O(min(n, m))    | O(min(n, m))     |
| Difference (`-`)   | O(n)            | O(n)             |
| Union (`\|`)       | O(n + m)        | O(n + m)         |

Where n and m are the sizes of the input sets.

**Example:** Reconciling 1 million transactions between two systems takes ~0.2 seconds using set operations, compared to hours with nested loops or complex SQL queries.

## 🎯 Use Cases

This API is designed for various reconciliation scenarios:

- 💳 **Payment Processing** - Stripe/PayPal vs internal accounting
- 🏦 **Banking** - Core banking vs general ledger
- 📦 **Inventory** - Warehouse management vs ERP
- 📊 **Data Warehousing** - Source systems vs data warehouse
- 🔄 **API Integration** - Third-party APIs vs internal records
- 📧 **Email Marketing** - Sent vs delivered vs opened
- 🎫 **Ticketing** - Sales platforms vs box office
- 🚚 **Logistics** - Shipment tracking across carriers

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/YourFeatureName`)
3. Commit your changes (`git commit -m 'Add some YourFeatureName'`)
4. Push to the branch (`git push origin feature/YourFeatureName`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Built as part of a data engineering portfolio project - Project 3 of 4.

Demonstrating:

- Clean architecture and design patterns
- RESTful API development with FastAPI
- Database modeling with SQLAlchemy
- Docker containerization
- Test-driven development with pytest
- Modern Python packaging (pyproject.toml)
- Professional Git workflow with feature branches
- Comprehensive documentation
- Practical application of set operations
- **Governed AI assistant layer (deterministic, auditable)**
- **MCP server integration (Claude Desktop)**
- **Browser-based chat UI**

## 🔗 Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Set Operations](https://docs.python.org/3/tutorial/datastructures.html#sets)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using Python, FastAPI, PostgreSQL, and MCP**
