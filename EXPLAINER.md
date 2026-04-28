# EXPLAINER – Playto Payout Engine

This document explains the design decisions, system architecture, and correctness guarantees in the payout engine.

The focus is not features, but correctness under concurrency, idempotency, and financial integrity.

---

# 1. System Design Overview

Frontend interacts with a Django REST API hosted on Render.

Payouts are processed asynchronously using Celery with Redis (Upstash) as broker. PostgreSQL (Neon) is the source of truth.

Frontend (Next.js)
    ↓
Django REST API (Render)
    ↓
PostgreSQL (Neon)
    ↓
Redis Queue (Upstash)
    ↓
Celery Worker (Async payout processing)

---

# 2. Database Schema (Actual Models)

## playto_user
- id (BigInt)
- pt_id (UUID)
- first_name (String)
- last_name (String)

---

## playto_ledger_entries
- id (BigInt)
- user (FK → playto_user)
- entry_type (CREDIT / DEBIT)
- amount_paise (BigInteger)
- reference_id (String)
- created_at (Timestamp)

---

## playto_account_directory
- id (BigInt)
- user (FK → playto_user)
- bank_name (String)
- bank_branch (String)
- account_number_hash (String masked)

---

## playto_payout
- id (BigInt)
- puid (FK → playto_user)
- bank_account (FK → playto_account_directory)
- amount_paise (BigInteger)
- status (PENDING / PROCESSING / COMPLETED / FAILED)
- idempotency_key (UUID)
- retry_count (Integer)
- failure_reason (Text)
- created_at (Timestamp)

---

# 3. API CONTRACTS (ACTUAL ENDPOINTS)

---

## GET /users/
Returns all users.

Response:
[
  {
    "pt_id": "uuid",
    "first_name": "John",
    "last_name": "Doe"
  }
]

---

## POST /profile/
Request:
{
  "pt_id":<uuid>
}

Response:
{
  "pt_id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "bank_accounts": [
    {
      "id": 1,
      "bank_name": "HDFC",
      "bank_branch": "BLR",
      "account_number_hash": "encrypted"
    }
  ]
}

---

## POST /balance/

Request:
{
  "pt_id":<uuid>
}

Response:
{
  "available_balance": 100000,
  "held_balance": 20000
}

---

## POST /ledger/
Request:
{
  "pt_id":<uuid>
}

Response:
[
  {
    "id": 1,
    "entry_type": "CREDIT",
    "amount_paise": 5000,
    "reference_id": "ref123",
    "created_at": "..."
  }
]

---

## POST /payouts/

Headers:
Idempotency-Key: uuid

Request:
{
  "pt_id": "uuid",
  "amount_paise": 5000,
  "bank_account_id": 1,
  "idempotency_key": "uuid"
}

Response:
{
  "payout_id": 10,
  "status": "PENDING",
  "amount_paise": 5000
}

---

## POST /payouts/list/

Request:
{
  "pt_id":<uuid>
}

Response:
[
  {
    "id": 1,
    "amount_paise": 1000,
    "status": "COMPLETED",
    "bank_name": "HDFC",
    "bank_branch": "BLR",
    "masked_account": "****1234",
    "failure_reason": null,
    "created_at": "..."
  }
]

---

# 4. Concurrency Handling

- select_for_update() used on user balance operations
- All payout operations wrapped in transaction.atomic()
- Prevents race conditions during simultaneous payouts

Guarantee:
→ No double spending under concurrent requests

---

# 5. Idempotency Design

- Idempotency-Key required in payout API
- Stored per user
- Duplicate requests return same payout response
- Prevents duplicate payouts due to retries or network issues

---

# 6. Why Upstash Redis

- Fully managed Redis
- No infra maintenance
- Works over HTTP (serverless compatible)
- Free tier available
- Works seamlessly with Render + Vercel

---

# 7. Celery Worker Design

State machine:
PENDING → PROCESSING → COMPLETED / FAILED

Simulation:
- 70% success
- 20% failure
- 10% stuck (retry case)

On failure:
- funds are reverted atomically
- status set to FAILED
- retry logic up to 3 attempts

---

# 8. Pagination Strategy

Used in:
- Ledger API (page_no)

Reason:
- prevents large payloads
- improves frontend performance
- ensures scalability of ledger history

---

# 9. Serializer Design

- Separate request and response serializers
- Strict validation using DRF
- Prevents DB schema leakage
- Keeps API contracts stable

---

# 10. Logging Strategy

Logs added for:
- payout creation
- payout state transitions
- async worker execution
- failure scenarios

Used for debugging distributed async flows.

---

# 11. Error Handling

- Centralized APIException handling
- Consistent API error structure
- Prevents stack trace exposure to frontend

---

# 12. File Structure Design

- models → database entities
- serializers → API contracts
- views → business logic layer
- tasks → celery workers
- services → reusable logic layer

Keeps financial logic modular and testable.

---

# 13. Frontend Design (Important)

## User Selection Screen
- Calls /users/
- Displays list of merchants
- Clicking user navigates to dashboard

## Dashboard Screen
- Profile (with bank accounts)
- Balance (available + held)
- Ledger table (paginated)
- Payout history modal

## UX Decisions
- INR formatting (₹) directly in UI
- Modal instead of separate page for payouts
- Pagination controls for ledger navigation

---

# 14. Testing Approach

Two critical tests:

1. Idempotency test → duplicate request returns same payout
2. Concurrency test → simultaneous payouts do not overspend balance

---

# FINAL NOTE

This system is designed for correctness over features.

Key principles:
- No race conditions in money movement
- Strict idempotency guarantees
- Integer-based financial model (paise only)
- Async processing via Celery
- Predictable payout state machine