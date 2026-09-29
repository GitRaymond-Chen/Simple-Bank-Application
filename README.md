# Simple Bank Application

A simple banking REST API: create accounts, deposit, withdraw and view transaction history.

**Phase 1 (current):** Python + FastAPI backend with **in-memory storage** (no database yet; data resets when the server restarts).
Coming later: MySQL persistence and a React frontend.

## Architecture

```
Router (REST) → Service (business rules) → Repository (in-memory) → dict/list storage
```

```
app/
├── main.py            # app factory, CORS, router registration
├── models.py          # domain entities: User, Account, Transaction
├── schemas.py         # request/response DTOs (camelCase JSON)
├── exceptions.py      # domain errors + consistent JSON error handler
├── dependencies.py    # wires repositories → services
├── repositories/      # in-memory repos (swap for MySQL later)
├── services/          # UserService, AccountService
└── routers/           # /api/users, /api/accounts
tests/test_api.py      # API + business rule + concurrency tests
```

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Run tests:

```bash
pytest
```

## API

| Method | Path | Body | Success |
|---|---|---|---|
| POST | `/api/users` | `{"name": "John Doe", "email": "john@example.com"}` | 201 (or 200 if email exists) |
| GET | `/api/users/{id}` | | 200 |
| POST | `/api/accounts` | `{"userId": 1, "accountType": "SAVINGS"}` | 201 |
| GET | `/api/accounts/{id}` | | 200 |
| POST | `/api/accounts/{id}/deposit` | `{"amount": 500}` | 200 |
| POST | `/api/accounts/{id}/withdraw` | `{"amount": 200}` | 200 |
| GET | `/api/accounts/{id}/transactions` | | 200 |

`accountType`: `SAVINGS` or `CHECKING`.

**Account response**
```json
{ "accountId": 1, "userName": "John Doe", "accountType": "SAVINGS", "balance": 300.0, "createdAt": "2026-09-29T16:45:50Z" }
```

**Transaction response** (newest first)
```json
[ { "transactionId": 2, "type": "WITHDRAW", "amount": 200.0, "balanceAfter": 300.0, "date": "2026-09-29T16:45:50Z" } ]
```

**Error response**
```json
{ "status": 422, "error": "INSUFFICIENT_FUNDS", "message": "Withdrawal of 900.00 exceeds balance of 500.00", "timestamp": "..." }
```

| Status | error | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | bad body (amount ≤ 0, >2 decimals, bad email, unknown account type) |
| 404 | `NOT_FOUND` | user/account doesn't exist |
| 422 | `INSUFFICIENT_FUNDS` | withdraw more than balance |

## Business rules

- Deposit/withdraw amount must be positive, max 2 decimal places.
- Cannot withdraw more than the balance.
- Every successful deposit/withdraw records a transaction (with the resulting balance).
- Money uses `Decimal`, never `float`.
- Deposits/withdrawals on the same account are serialized with a per-account lock, so concurrent withdrawals can't overdraw.

## Quick test with curl

```bash
curl -X POST localhost:8000/api/users -H 'Content-Type: application/json' -d '{"name":"John Doe","email":"john@example.com"}'
curl -X POST localhost:8000/api/accounts -H 'Content-Type: application/json' -d '{"userId":1,"accountType":"SAVINGS"}'
curl -X POST localhost:8000/api/accounts/1/deposit -H 'Content-Type: application/json' -d '{"amount":500}'
curl -X POST localhost:8000/api/accounts/1/withdraw -H 'Content-Type: application/json' -d '{"amount":200}'
curl localhost:8000/api/accounts/1/transactions
```
