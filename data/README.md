# Sample Data

This directory contains sample transaction data for testing and demonstrating the reconciliation API.

## Files

### `sample_transactions.json`

JSON format sample data representing a month-end reconciliation between:

-   **System A (Internal Finance System)**: 10 transactions
-   **System B (Stripe Payment Processor)**: 9 transactions

### `sample_transactions.csv`

Same data in CSV format for alternative loading methods.

### `seed_data.py`

Python script to automatically load sample data into the database.

## Data Overview

The sample data demonstrates a realistic **Finance vs Payment Processor** reconciliation scenario for November 2025.

### System A: Internal Finance System (10 transactions)

Finance team records for payments that should have been processed:

| Transaction ID | Amount  | Status                     |
| -------------- | ------- | -------------------------- |
| PAY-10001      | $150.00 | ✅ Matched                 |
| PAY-10002      | $225.50 | ✅ Matched                 |
| PAY-10003      | $89.99  | ✅ Matched                 |
| PAY-10004      | $320.00 | ⚠️ **Missing from Stripe** |
| PAY-10005      | $175.25 | ✅ Matched                 |
| PAY-10006      | $450.00 | ⚠️ **Missing from Stripe** |
| PAY-10007      | $99.99  | ✅ Matched                 |
| PAY-10008      | $275.80 | ✅ Matched                 |
| PAY-10009      | $500.00 | ⚠️ **Missing from Stripe** |
| PAY-10010      | $399.99 | ✅ Matched                 |

**Total:** $2,686.52

### System B: Stripe Payment Processor (9 transactions)

Stripe records for payments that were actually processed:

| Transaction ID | Amount  | Status                      |
| -------------- | ------- | --------------------------- |
| PAY-10001      | $150.00 | ✅ Matched                  |
| PAY-10002      | $225.50 | ✅ Matched                  |
| PAY-10003      | $89.99  | ✅ Matched                  |
| PAY-10005      | $175.25 | ✅ Matched                  |
| PAY-10007      | $99.99  | ✅ Matched                  |
| PAY-10008      | $275.80 | ✅ Matched                  |
| PAY-10010      | $399.99 | ✅ Matched                  |
| PAY-10011      | $650.00 | ⚠️ **Missing from Finance** |
| PAY-10012      | $125.75 | ⚠️ **Missing from Finance** |

**Total:** $2,192.27

## Expected Reconciliation Results

When analysing this data using SET operations:

### Matched Transactions (INTERSECTION)

```python
system_a = {PAY-10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010}
system_b = {PAY-10001, 10002, 10003, 10005, 10007, 10008, 10010, 10011, 10012}

# SET INTERSECTION: Find matched transactions
matched = system_a & system_b  # {PAY-10001, 10002, 10003, 10005, 10007, 10008, 10010}
```

**Result:** 7 matched transactions ✅

### Transactions Only in Finance (DIFFERENCE)

```python
# SET DIFFERENCE: Find transactions in Finance but not Stripe
only_in_finance = system_a - system_b  # {PAY-10004, 10006, 10009}
```

**Result:** 3 transactions missing from Stripe ⚠️

-   PAY-10004 ($320.00) - Payment failed
-   PAY-10006 ($450.00) - Gateway timeout
-   PAY-10009 ($500.00) - Card declined

**Revenue at risk:** $1,270.00

### Transactions Only in Stripe (DIFFERENCE)

```python
# SET DIFFERENCE: Find transactions in Stripe but not Finance
only_in_stripe = system_b - system_a  # {PAY-10011, 10012}
```

**Result:** 2 transactions missing from Finance ⚠️

-   PAY-10011 ($650.00) - Manual refund not recorded
-   PAY-10012 ($125.75) - Chargeback not recorded

**Missing records:** $775.75

### Overall Statistics

-   **Total unique transactions:** 12 (using SET UNION)
-   **Matched:** 7 transactions (58.3% match rate)
-   **Discrepancies:** 5 transactions (41.7%)
-   **Finance total:** $2,686.52
-   **Stripe total:** $2,192.27
-   **Amount difference:** $494.25

## Usage

### Load Sample Data into Database

**From outside the Docker container:**

```bash
docker-compose exec app python data/seed_data.py
```

**From inside the Docker container:**

```bash
docker-compose exec app bash
python data/seed_data.py
```

**Running locally (without Docker):**

```bash
python data/seed_data.py
```

### Expected Output

```
======================================================================
Transaction Reconciliation API - Data Seeding
======================================================================

Cleared 0 existing sessions and 0 existing transactions
Created reconciliation session: finance_vs_stripe_nov_2025 (ID: 1)
  System A: Internal Finance System
  System B: Stripe Payment Processor

Loaded 10 transactions from Internal Finance System
Loaded 9 transactions from Stripe Payment Processor

--- Reconciliation Analysis ---

✅ Matched transactions: 7
   Transaction IDs: ['PAY-10001', 'PAY-10002', 'PAY-10003', 'PAY-10005', 'PAY-10007', 'PAY-10008', 'PAY-10010']

⚠️  Only in Internal Finance System: 3
   Transaction IDs: ['PAY-10004', 'PAY-10006', 'PAY-10009']

⚠️  Only in Stripe Payment Processor: 2
   Transaction IDs: ['PAY-10011', 'PAY-10012']

📊 Match Rate: 58.3% (7 out of 12 unique transactions)

💰 Financial Summary:
   Internal Finance System total: $2,686.52
   Stripe Payment Processor total: $2,192.27
   Difference: $494.25

======================================================================
✅ Database seeded successfully!
======================================================================

Session ID: 1

You can now:
1. Visit http://localhost:8002/docs to test the API
2. Try GET /api/v1/reconciliation/analyse/1
3. Try GET /api/v1/reconciliation/summary/1
4. Try GET /api/v1/reconciliation/discrepancies/1
```

## Using the API with Sample Data

After seeding, try these endpoints:

### 1. **Analyse Reconciliation** ⭐

```bash
GET http://localhost:8002/api/v1/reconciliation/analyse/1
```

Expected response:

```json
{
    "session_id": 1,
    "session_name": "finance_vs_stripe_nov_2025",
    "system_a_name": "Internal Finance System",
    "system_b_name": "Stripe Payment Processor",
    "total_system_a": 10,
    "total_system_b": 9,
    "matched_count": 7,
    "matched_transactions": [
        "PAY-10001",
        "PAY-10002",
        "PAY-10003",
        "PAY-10005",
        "PAY-10007",
        "PAY-10008",
        "PAY-10010"
    ],
    "only_in_system_a_count": 3,
    "only_in_system_a": ["PAY-10004", "PAY-10006", "PAY-10009"],
    "only_in_system_b_count": 2,
    "only_in_system_b": ["PAY-10011", "PAY-10012"],
    "match_rate": 58.33
}
```

### 2. **Get Reconciliation Summary**

```bash
GET http://localhost:8002/api/v1/reconciliation/summary/1
```

Shows overall statistics including total amounts and match rate.

### 3. **Find Amount Discrepancies**

```bash
GET http://localhost:8002/api/v1/reconciliation/discrepancies/1
```

In this sample data, all matched transactions have the same amounts (no discrepancies).

### 4. **View Transactions by System**

```bash
# Finance system transactions
GET http://localhost:8002/api/v1/transactions/session/1/system/system_a

# Stripe transactions
GET http://localhost:8002/api/v1/transactions/session/1/system/system_b
```

### 5. **View All Transactions**

```bash
GET http://localhost:8002/api/v1/transactions/session/1
```

Shows all 19 transactions (10 from Finance + 9 from Stripe).

## Real-World Application

This sample data represents common reconciliation challenges:

### Why Transactions Are Missing

**Missing from Stripe (System B):**

-   PAY-10004: Payment gateway timeout
-   PAY-10006: API failure during high traffic
-   PAY-10009: Card declined but recorded in Finance

**Missing from Finance (System A):**

-   PAY-10011: Manual refund processed in Stripe
-   PAY-10012: Chargeback not yet recorded

### Business Impact

-   **Revenue at risk:** $1,270.00 (payments in Finance but not in Stripe)
-   **Unrecorded adjustments:** $775.75 (transactions in Stripe but not in Finance)
-   **Net discrepancy:** $494.25
-   **Match rate:** 58.3% (needs investigation!)

This is exactly what the API helps you identify and resolve! 🔍

## Use Cases

This reconciliation pattern applies to:

-   💳 **Payment processors** (Stripe, PayPal) vs internal accounting
-   🏦 **Banking** vs accounting systems
-   📦 **Inventory** across warehouses
-   📊 **Data warehouse** vs source systems
-   🔄 **API integrations** validation
-   📧 **Email delivery** (sent vs delivered)
-   🎫 **Ticket sales** across platforms
