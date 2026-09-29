from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())  # fresh in-memory store per test


def make_account(client: TestClient, email: str = "john@example.com") -> int:
    user = client.post("/api/users", json={"name": "John Doe", "email": email}).json()
    acc = client.post("/api/accounts", json={"userId": user["userId"], "accountType": "SAVINGS"})
    assert acc.status_code == 201
    return acc.json()["accountId"]


# ---- Users ----

def test_create_user_then_same_email_returns_existing(client):
    r1 = client.post("/api/users", json={"name": "John Doe", "email": "john@example.com"})
    r2 = client.post("/api/users", json={"name": "Other", "email": "JOHN@example.com"})
    assert r1.status_code == 201
    assert r2.status_code == 200
    assert r2.json()["userId"] == r1.json()["userId"]


def test_create_user_invalid_email(client):
    r = client.post("/api/users", json={"name": "John", "email": "not-an-email"})
    assert r.status_code == 400
    assert r.json()["error"] == "VALIDATION_ERROR"


# ---- Accounts ----

def test_create_and_get_account(client):
    acc_id = make_account(client)
    r = client.get(f"/api/accounts/{acc_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["userName"] == "John Doe"
    assert body["accountType"] == "SAVINGS"
    assert body["balance"] == 0


def test_create_account_unknown_user(client):
    r = client.post("/api/accounts", json={"userId": 999, "accountType": "SAVINGS"})
    assert r.status_code == 404


def test_create_account_invalid_type(client):
    r = client.post("/api/accounts", json={"userId": 1, "accountType": "GOLD"})
    assert r.status_code == 400


def test_get_unknown_account(client):
    r = client.get("/api/accounts/999")
    assert r.status_code == 404
    assert r.json()["error"] == "NOT_FOUND"


# ---- Deposit / withdraw ----

def test_deposit_increases_balance(client):
    acc_id = make_account(client)
    r = client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 500})
    assert r.status_code == 200
    assert r.json()["balance"] == 500


@pytest.mark.parametrize("amount", [0, -10, 1.234])
def test_deposit_rejects_bad_amounts(client, amount):
    acc_id = make_account(client)
    r = client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": amount})
    assert r.status_code == 400


def test_withdraw_decreases_balance(client):
    acc_id = make_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 500})
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 200})
    assert r.status_code == 200
    assert r.json()["balance"] == 300


def test_withdraw_exact_balance(client):
    acc_id = make_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 100})
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 100})
    assert r.json()["balance"] == 0


def test_withdraw_more_than_balance_fails_and_records_nothing(client):
    acc_id = make_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 100})
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 150})
    assert r.status_code == 422
    assert r.json()["error"] == "INSUFFICIENT_FUNDS"
    assert client.get(f"/api/accounts/{acc_id}").json()["balance"] == 100
    assert len(client.get(f"/api/accounts/{acc_id}/transactions").json()) == 1


def test_decimal_precision(client):
    acc_id = make_account(client)
    for _ in range(3):
        client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 0.1})
    assert client.get(f"/api/accounts/{acc_id}").json()["balance"] == 0.3


# ---- Transactions ----

def test_transaction_history_newest_first(client):
    acc_id = make_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 500})
    client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 200})
    txns = client.get(f"/api/accounts/{acc_id}/transactions").json()
    assert [t["type"] for t in txns] == ["WITHDRAW", "DEPOSIT"]
    assert txns[0]["amount"] == 200
    assert txns[0]["balanceAfter"] == 300
    assert {"transactionId", "type", "amount", "balanceAfter", "date"} <= txns[0].keys()


def test_transactions_unknown_account(client):
    assert client.get("/api/accounts/999/transactions").status_code == 404


# ---- Concurrency ----

def test_concurrent_withdrawals_never_overdraw(client):
    acc_id = make_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 100})

    def withdraw(_):
        return client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 30}).status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(withdraw, range(10)))

    assert codes.count(200) == 3
    assert codes.count(422) == 7
    assert client.get(f"/api/accounts/{acc_id}").json()["balance"] == 10
