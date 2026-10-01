<div align="center">

# 🏦 Simple Bank

**A full-stack banking app: FastAPI + MongoDB Atlas on the back, React on the front.**

Open accounts, deposit and withdraw money, and browse transaction history, built step by step with a clean layered architecture.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![MongoDB Atlas](https://img.shields.io/badge/MongoDB_Atlas-47A248?logo=mongodb&logoColor=white)
![PyMongo](https://img.shields.io/badge/PyMongo-4.x-47A248?logo=mongodb&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)

<img src="docs/screenshots/account.jpg" alt="Account dashboard" width="760" />

</div>

---

## Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Quick start](#quick-start)
- [API reference](#api-reference)
- [Business rules](#business-rules)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Tutorial branches](#tutorial-branches)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

## Features

- 👤 **Users & accounts**: create a customer and open checking or savings accounts
- 💸 **Deposits & withdrawals**: validated amounts, and no overdrafts
- 🧾 **Transaction history**: every movement recorded, newest first, with running balance in the UI
- ☁️ **MongoDB Atlas**: cloud database, free tier is plenty
- 🔒 **Safe under concurrency**: atomic conditional updates plus multi-document transactions
- 📖 **Interactive docs**: Swagger UI at `/docs`, plus a ready-made Postman collection
- 🎨 **Polished UI**: responsive React frontend with light/dark mode
- ✅ **Tested**: pytest suite on an in-memory MongoDB, no database server required, plus optional tests against your real Atlas cluster

## Screenshots

| Home | Withdraw |
|---|---|
| ![Home page](docs/screenshots/home.jpg) | ![Withdraw page](docs/screenshots/withdraw.jpg) |
| **Transaction history** | **Dark mode** |
| ![Transaction history](docs/screenshots/history.jpg) | ![Account dashboard in dark mode](docs/screenshots/account-dark.jpg) |

## Architecture

```mermaid
flowchart LR
    UI["React UI<br/>(Vite, :5173)"] -- "/api/* (proxied)" --> R["Routers<br/>app/routers"]
    R --> S["Services<br/>business rules"]
    S --> Repo["Repositories<br/>PyMongo"]
    Repo --> DB[("MongoDB Atlas")]
```

| Layer | Responsibility | Location |
|---|---|---|
| **Router** | HTTP: parse and validate requests, shape responses | [`app/routers/`](app/routers) |
| **Service** | Business rules: positive amounts, no overdrafts, atomic updates | [`app/services/`](app/services) |
| **Repository** | Data access, the only layer that talks to MongoDB | [`app/repositories/`](app/repositories) |
| **Model** | Dataclasses `User`, `Account`, `Transaction` + document mapping | [`app/models.py`](app/models.py) |
| **Schema** | Pydantic request/response DTOs (camelCase JSON) | [`app/schemas.py`](app/schemas.py) |

Dependencies are wired per request in [`app/dependencies.py`](app/dependencies.py). Services get a **unit of work** ([`app/database.py`](app/database.py)) that runs several writes inside one MongoDB transaction, so they commit together or not at all.

> Moving from MySQL to MongoDB touched only the data layer (`database.py`, `models.py`, repositories) and how `AccountService` makes its updates atomic. Routers, schemas, the API contract and the frontend are unchanged.

### Data model

One MongoDB collection per entity, linked by integer ids:

```mermaid
erDiagram
    users ||--o{ accounts : owns
    accounts ||--o{ transactions : records
    users {
        int _id PK
        string name
        string email UK
        date created_at
    }
    accounts {
        int _id PK
        int user_id FK
        string account_type
        long balance_cents
        date created_at
    }
    transactions {
        int _id PK
        int account_id FK
        string txn_type
        long amount_cents
        date created_at
    }
```

A fourth collection, `counters`, hands out ids (`{ _id: "accounts", seq: 2 }`). Design choices:

- **Integer ids instead of ObjectIds**, so the API and the frontend's `#0001` account numbers work unchanged. MongoDB has no `AUTO_INCREMENT`, so `counters` is bumped atomically with `$inc`.
- **Money as integer cents** (`balance_cents: 50025` = $500.25). It's exact, with no floating-point error, and `$inc` can add and subtract it atomically. The API still speaks dollars (`"500.25"`).
- **Indexes**, created on startup: unique `users.email`, `accounts.user_id`, and `transactions (account_id, _id desc)` for the history query.

## Quick start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for the frontend)
- **A MongoDB Atlas account**. The free M0 cluster is enough.

### 1. Set up MongoDB Atlas

1. Sign in at [cloud.mongodb.com](https://cloud.mongodb.com) and **create a free cluster** (M0).
2. **Database Access** → *Add New Database User*: pick a username and password.
3. **Network Access** → *Add IP Address* → *Add Current IP Address*.
4. **Clusters** → *Connect* → *Drivers* → *Python*, then copy the connection string.

### 2. Backend

```bash
# from the project root
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Paste your connection string into `.env`, replacing `<username>` and `<password>`:

```bash
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=SimpleBank
MONGODB_DB=simple_bank
```

> `.env` is git-ignored, so your password never gets committed. If the password contains special characters like `@`, `:` or `/`, [URL-encode](https://www.urlencoder.org/) it.

Start the API. The database, collections and indexes are created automatically:

```bash
uvicorn app.main:app --reload
```

- API → http://localhost:8000
- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The dev server proxies `/api/*` to the backend on port 8000. See the [frontend README](frontend/README.md) for details.

## API reference

Base URL: `http://localhost:8000`. All request and response bodies are JSON, with camelCase keys.

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `GET` | `/` | Health check | `200` |
| `POST` | `/api/users` | Create a user (returns the existing user if the email is taken) | `201` / `200` |
| `GET` | `/api/users/{userId}` | Get a user | `200` |
| `POST` | `/api/accounts` | Open an account | `201` |
| `GET` | `/api/accounts/{accountId}` | Get an account and its balance | `200` |
| `POST` | `/api/accounts/{accountId}/deposit` | Deposit money | `200` |
| `POST` | `/api/accounts/{accountId}/withdraw` | Withdraw money | `200` |
| `GET` | `/api/accounts/{accountId}/transactions` | Transaction history, newest first | `200` |

<details>
<summary><b>Example requests and responses</b></summary>

**Create a user**

```http
POST /api/users
{ "name": "Jordan Lee", "email": "jordan@example.com" }
```
```json
{ "userId": 1, "name": "Jordan Lee", "email": "jordan@example.com", "createdAt": "2026-09-29T17:46:27" }
```

**Open an account** (`accountType` is `checking` or `savings`, case-insensitive)

```http
POST /api/accounts
{ "userId": 1, "accountType": "checking" }
```
```json
{ "accountId": 1, "userId": 1, "balance": "0.00", "accountType": "checking", "createdAt": "2026-09-29T17:46:27" }
```

**Deposit / withdraw** (amount must be > 0 with at most 2 decimal places)

```http
POST /api/accounts/1/deposit
{ "amount": 500 }
```
```json
{ "accountId": 1, "userId": 1, "balance": "500.00", "accountType": "checking", "createdAt": "2026-09-29T17:46:27" }
```

**Transaction history**

```http
GET /api/accounts/1/transactions
```
```json
[
  { "txnId": 2, "accountId": 1, "txnType": "withdrawal", "amount": "120.40", "createdAt": "2026-09-29T17:48:02" },
  { "txnId": 1, "accountId": 1, "txnType": "deposit", "amount": "500.00", "createdAt": "2026-09-29T17:47:10" }
]
```

> Money is serialized as a string (`"500.00"`) so no precision is lost to floating point.

</details>

### Errors

Every error has the same shape:

```json
{ "detail": "Insufficient funds: balance is 500.00, requested 900" }
```

| Status | When |
|---|---|
| `400` | Validation failed (bad email, unknown account type, amount ≤ 0 or > 2 decimals), or insufficient funds |
| `404` | User or account not found |
| `409` | Conflicts with existing data (e.g. two simultaneous sign-ups with the same email) |
| `503` | Database unavailable (Atlas unreachable; see [Troubleshooting](#troubleshooting)) |

### Try it from the terminal

```bash
curl -X POST localhost:8000/api/users -H 'Content-Type: application/json' -d '{"name":"Jordan Lee","email":"jordan@example.com"}'
curl -X POST localhost:8000/api/accounts -H 'Content-Type: application/json' -d '{"userId":1,"accountType":"checking"}'
curl -X POST localhost:8000/api/accounts/1/deposit -H 'Content-Type: application/json' -d '{"amount":500}'
curl -X POST localhost:8000/api/accounts/1/withdraw -H 'Content-Type: application/json' -d '{"amount":120.40}'
curl localhost:8000/api/accounts/1/transactions
```

Or import [`postman_collection.json`](postman_collection.json) into Postman.

## Business rules

Enforced in [`AccountService`](app/services/account_service.py):

1. **Deposits and withdrawals must be positive**, with at most two decimal places.
2. **You can't withdraw more than the balance.** A rejected withdrawal changes nothing.
3. **Every deposit and withdrawal is recorded** as a transaction.
4. **Balance and transaction record are saved together** in one MongoDB transaction, so it's never one without the other.
5. **Concurrent operations can't overdraw.** A withdrawal is a single atomic update whose filter includes the balance check:
   ```python
   accounts.find_one_and_update(
       {"_id": account_id, "balance_cents": {"$gte": amount}},  # only if there's enough
       {"$inc": {"balance_cents": -amount}},
   )
   ```
   If two withdrawals race, MongoDB applies them one at a time, and the second one no longer matches if the money is gone.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The suite ([`tests/`](tests)) runs the real app against [mongomock](https://github.com/mongomock/mongomock), an in-memory MongoDB, so it runs anywhere in well under a second. It covers every endpoint, validation, the business rules above, money conversion, error formats, and the JSON contract the frontend depends on.

To also test against a **real cluster** (real transactions, plus 10 simultaneous withdrawals that must not overdraw), point the integration tests at Atlas. They use a throwaway `simple_bank_test_*` database and drop it afterwards:

```bash
MONGODB_TEST_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/" pytest tests/test_atlas_integration.py
```

## Project structure

```
.
├── app/
│   ├── main.py              # FastAPI app, CORS, lifespan (creates indexes)
│   ├── database.py          # MongoClient, indexes, id counters, unit of work
│   ├── models.py            # dataclasses + document mapping, money helpers
│   ├── schemas.py           # Pydantic request/response models
│   ├── exceptions.py        # domain errors → JSON error responses
│   ├── dependencies.py      # repository / service wiring
│   ├── repositories/        # data access layer
│   ├── services/            # business logic layer
│   └── routers/             # /api/users, /api/accounts
├── frontend/                # React + Vite app (see frontend/README.md)
├── tests/                   # pytest suite (mongomock) + optional Atlas tests
├── docs/screenshots/        # images used in this README
├── postman_collection.json  # all endpoints, ready to import
├── requirements.txt         # runtime dependencies
├── requirements-dev.txt     # + pytest, httpx, mongomock
└── .env.example             # MONGODB_URI / MONGODB_DB template
```

## Tutorial branches

The project is built up one layer at a time. Check out a branch to see the code at that stage:

| Branch | What it adds |
|---|---|
| `step-1-project-setup` | Bare FastAPI app with health check and CORS |
| `step-2-database-models` | SQLAlchemy models and MySQL schema |
| `step-3-repositories` | Data access layer |
| `step-4-services` | Business logic layer |
| `step-5-rest-api` | Routers, dependency injection, Postman collection |
| `step-6-frontend` | React frontend, bug fixes, tests and UI redesign (MySQL) |
| `step-7-mongodb` | Database switched from MySQL to MongoDB Atlas |
| `main` | The finished app |

```bash
git checkout step-3-repositories
```

> Steps 1–6 use MySQL; step 7 swaps in MongoDB Atlas. The bug fixes, tests and redesign were added in step 6, so earlier branches don't include them.

## Troubleshooting

| Problem | Fix |
|---|---|
| Startup fails with `ServerSelectionTimeoutError`, or the API returns `503` | Atlas → **Network Access**: add your current IP (it changes on new Wi-Fi networks). Also check the cluster isn't paused |
| `bad auth : authentication failed` | Wrong username or password in `MONGODB_URI`. These are the *database user's* credentials, not your Atlas login. URL-encode special characters |
| `Transaction numbers are only allowed on a replica set member` | You're on a standalone local `mongod`. Use Atlas, or start a local server as a replica set (`mongod --replSet rs0`, then `rs.initiate()`) |
| UI says *"Can't reach the server"* | Make sure the backend is running on port 8000 |
| Backend is on a different port | `API_URL=http://localhost:8001 npm run dev` |
| `Could not open requirements file` | Run commands from the project root, not `frontend/` |
| `ModuleNotFoundError` | Activate the virtualenv: `source .venv/bin/activate` |

## Roadmap

- [ ] Login and authentication (JWT), with users only seeing their own accounts
- [ ] Transfers between accounts
- [ ] Paginated transaction history
- [ ] Schema validation rules on the MongoDB collections
- [ ] Docker Compose for API + frontend (+ local MongoDB replica set)
