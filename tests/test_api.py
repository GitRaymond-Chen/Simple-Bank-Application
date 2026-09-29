import pytest


def create_account(client, email="john@example.com", account_type="savings"):
    user = client.post("/api/users", json={"name": "John Doe", "email": email}).json()
    r = client.post("/api/accounts", json={"userId": user["userId"], "accountType": account_type})
    assert r.status_code == 201, r.text
    return r.json()["accountId"]


# ── Users ──────────────────────────────────────────────────────

def test_create_user_returns_camel_case(client):
    r = client.post("/api/users", json={"name": "John Doe", "email": "john@example.com"})
    assert r.status_code == 201
    assert set(r.json()) == {"userId", "name", "email", "createdAt"}


def test_duplicate_email_returns_existing_user(client):
    r1 = client.post("/api/users", json={"name": "John Doe", "email": "john@example.com"})
    r2 = client.post("/api/users", json={"name": "John Again", "email": "JOHN@example.com"})
    assert r2.status_code == 200
    assert r2.json()["userId"] == r1.json()["userId"]


def test_invalid_email_gives_readable_error(client):
    r = client.post("/api/users", json={"name": "John", "email": "nope"})
    assert r.status_code == 400
    assert isinstance(r.json()["detail"], str)
    assert "email" in r.json()["detail"]


def test_get_user_not_found(client):
    r = client.get("/api/users/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "User with id 999 not found"}


# ── Accounts ───────────────────────────────────────────────────

def test_create_and_get_account(client):
    acc_id = create_account(client)
    r = client.get(f"/api/accounts/{acc_id}")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"accountId", "userId", "balance", "accountType", "createdAt"}
    assert body["accountType"] == "savings"
    assert body["balance"] == "0.00"


def test_account_type_is_case_insensitive(client):
    acc_id = create_account(client, account_type="CHECKING")
    assert client.get(f"/api/accounts/{acc_id}").json()["accountType"] == "checking"


def test_invalid_account_type_rejected(client):
    user = client.post("/api/users", json={"name": "A", "email": "a@example.com"}).json()
    r = client.post("/api/accounts", json={"userId": user["userId"], "accountType": "banana"})
    assert r.status_code == 400


def test_create_account_for_unknown_user(client):
    r = client.post("/api/accounts", json={"userId": 999, "accountType": "savings"})
    assert r.status_code == 404


def test_snake_case_request_keys_still_accepted(client):
    user = client.post("/api/users", json={"name": "A", "email": "a@example.com"}).json()
    r = client.post("/api/accounts", json={"user_id": user["userId"], "account_type": "savings"})
    assert r.status_code == 201


def test_get_account_not_found(client):
    assert client.get("/api/accounts/999").status_code == 404


# ── Deposit / withdraw ─────────────────────────────────────────

def test_deposit(client):
    acc_id = create_account(client)
    r = client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 500})
    assert r.status_code == 200
    assert r.json()["balance"] == "500.00"


@pytest.mark.parametrize("amount", [0, -10, 1.239, "abc"])
def test_bad_amounts_rejected(client, amount):
    acc_id = create_account(client)
    for action in ("deposit", "withdraw"):
        r = client.post(f"/api/accounts/{acc_id}/{action}", json={"amount": amount})
        assert r.status_code == 400
        assert isinstance(r.json()["detail"], str)
    assert client.get(f"/api/accounts/{acc_id}/transactions").json() == []


def test_withdraw(client):
    acc_id = create_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 500})
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 200})
    assert r.status_code == 200
    assert r.json()["balance"] == "300.00"


def test_withdraw_exact_balance(client):
    acc_id = create_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": "100.00"})
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": "100.00"})
    assert r.json()["balance"] == "0.00"


def test_overdraw_rejected_and_nothing_recorded(client):
    acc_id = create_account(client)
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 100})
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 150})
    assert r.status_code == 400
    assert "Insufficient funds" in r.json()["detail"]
    assert client.get(f"/api/accounts/{acc_id}").json()["balance"] == "100.00"
    assert len(client.get(f"/api/accounts/{acc_id}/transactions").json()) == 1


def test_deposit_unknown_account(client):
    assert client.post("/api/accounts/999/deposit", json={"amount": 5}).status_code == 404


# ── Transactions ───────────────────────────────────────────────

def test_transactions_newest_first(client):
    acc_id = create_account(client)
    # Same-second timestamps: order must still be correct
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 500})
    client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 200})
    client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": 50})
    txns = client.get(f"/api/accounts/{acc_id}/transactions").json()
    assert [t["txnType"] for t in txns] == ["deposit", "withdrawal", "deposit"]
    assert [t["amount"] for t in txns] == ["50.00", "200.00", "500.00"]
    assert set(txns[0]) == {"txnId", "accountId", "txnType", "amount", "createdAt"}


def test_transactions_unknown_account(client):
    assert client.get("/api/accounts/999/transactions").status_code == 404


def test_health(client):
    assert client.get("/").json() == {"status": "ok"}
