# EXPLAINER – Playto Payout Engine

This document explains the design decisions, system architecture, and correctness guarantees in the payout engine.

The focus is not features, but correctness under concurrency, idempotency, and financial integrity.



# 1. System Design Overview

Frontend interacts with a Django REST API hosted on Render. The API manages merchant balances, ledger entries, and payout requests.

Payouts are processed asynchronously using Celery with Redis as the broker. PostgreSQL is the source of truth.

Frontend (Next.js)
    ↓
Django REST API (Render)
    ↓
PostgreSQL (Ledger + Payouts) - hosted on Neon Postgres
    ↓
Redis Queue (Upstash)
    ↓
Celery Worker (Async payout processing)

---

# 2. Database Schema Design

Merchant Table: playto_user
- id (BigInt / UUID)
- pt_id (String, public identifier)
- name (String)
- created_at (Timestamp)

Ledger Table: playto_ledger_entries
- id (BigInt)
- merchant_id (FK)
- entry_type (CREDIT / DEBIT)
- amount_paise (BigInteger)
- reference_id (String)
- created_at (Timestamp)

Bank Account Table: playto_account_directory
- id (BigInt)
- merchant_id (FK)
- bank_name (String)
- account_number_hash (String masked)
- bank_branch (String)

Payout Table: playto_payout
- id (BigInt)
- merchant_id (FK)
- bank_account_id (FK)
- amount_paise (BigInteger)
- status (PENDING / PROCESSING / COMPLETED / FAILED)
- idempotency_key (UUID)
- retry_count (Integer)
- failure_reason (Text)
- created_at (Timestamp)

---

# 3. API Contracts

Merchant Profile:
GET /api/v1/merchant/{pt_id}

{
  "pt_id": "M123",
  "name": "Merchant A",
  "bank_accounts": []
}

---

Balance API:
GET /api/v1/merchant/{pt_id}/balance

{
  "available_balance_paise": 100000,
  "held_balance_paise": 20000
}

---

Ledger API (Paginated):
GET /api/v1/merchant/{pt_id}/ledger?page=1

{
  "results": [],
  "total_count": 120,
  "next": "?page=2",
  "previous": null
}

---

Payout Request API:
POST /api/v1/payouts
Headers: Idempotency-Key: uuid

{
  "pt_id": "M123",
  "amount_paise": 5000,
  "bank_account_id": 1
}

Response:
{
  "payout_id": 10,
  "status": "PENDING"
}

---

Payout List API:
GET /api/v1/payouts/{pt_id}

[
  {
    "id": 1,
    "amount_paise": 1000,
    "status": "COMPLETED",
    "failure_reason": null,
    "created_at": "..."
  }
]

---

# 4. Concurrency Handling

- select_for_update() used on merchant row
- transaction.atomic() wraps payout creation + balance update
- prevents double spending when two requests happen at same time

This ensures only one payout succeeds when balance is insufficient.

---

# 5. Idempotency Design

- Idempotency-Key header required
- Stored per merchant
- Duplicate requests return same payout response
- Prevents duplicate payouts under retries or network failures

---

# 6. Why Upstash Redis for Celery Broker

- Fully managed Redis (no infra maintenance)
- Works via HTTP (serverless friendly)
- Free tier available
- Works well with Render + Vercel ecosystem

---

# 7. Celery Design

- Async payout processing via worker
- Simulated outcomes:
  - 70% success
  - 20% failure
  - 10% stuck processing

On failure:
- Funds are reverted atomically
- Status set to FAILED
- Retry logic allows up to 3 attempts

---

# 8. Pagination Strategy

Used in:
- Ledger API
- Payout history API

Reason:
- Ledger grows continuously
- Prevents large payload responses
- Improves frontend performance

---

# 9. Serializer Design

- Separate request and response serializers
- Keeps API contract stable
- Prevents leaking DB structure
- Makes validation explicit

---

# 10. Logging Strategy

Logs added for:
- payout creation
- payout state transitions
- failure scenarios

Used for debugging async flow and production traceability.

---

# 11. Error Handling

- Centralized APIException handling
- Uniform error responses
- Prevents stack trace exposure to frontend

---

# 12. File Structure Decisions

- models → financial entities
- serializers → API contracts
- views → business logic
- tasks → Celery workers
- services → reusable logic layer

Ensures separation of concerns and maintainability.

---

# 13. Testing Approach

Two critical tests:
- Idempotency test (duplicate request safety)
- Concurrency test (race condition prevention)

These validate financial correctness under stress.

---

# Final Note

This system is designed for correctness over features.

Key principles:
- No race conditions in money movement
- Strict idempotent APIs
- Integer-based financial model (paise only)
- Async processing via Celery
- Predictable state transitions in payouts