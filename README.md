# Simple Bank Application

A beginner-friendly tutorial project that builds a full-stack banking REST API step by step.

## What This Project Is

A simple bank API that lets you:
- Create users and bank accounts
- Deposit and withdraw money
- View transaction history

Built with **Python + FastAPI** (backend) and **React** (frontend), using **MySQL** for storage.

## Tutorial Steps

| Branch | What You Build |
|--------|---------------|
| `step-1-project-setup` | Bare FastAPI app with health check |
| `step-2-database-models` | SQLAlchemy models + MySQL schema |
| `step-3-repositories` | Data access layer (repositories) |
| `step-4-services` | Business logic layer (services) |
| `step-5-rest-api` | Full REST API with all endpoints |
| `step-6-frontend` | React frontend wired to the API |

## How to Run (This Step)

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

### 4. Test the health check

Open your browser or run:

```bash
curl http://localhost:8000/
# {"status": "ok"}
```

Interactive API docs are available at: http://localhost:8000/docs

### 5. Run the tests

Tests use an in-memory SQLite database, so MySQL doesn't need to be running.

```bash
pip install -r requirements-dev.txt
pytest
```
