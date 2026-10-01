"""
Integration tests against a real MongoDB (e.g. your Atlas cluster).
Skipped unless MONGODB_TEST_URI is set:

    MONGODB_TEST_URI="mongodb+srv://..." pytest tests/test_atlas_integration.py

Each run uses a throwaway database (simple_bank_test_<random>) that is dropped
afterwards, so it never touches your real data. Exercises what mongomock
can't: real multi-document transactions and concurrent withdrawals.
"""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.database import UnitOfWork, get_db, get_uow, init_db
from app.main import app

URI = os.getenv("MONGODB_TEST_URI")
pytestmark = pytest.mark.skipif(not URI, reason="MONGODB_TEST_URI not set")


@pytest.fixture(scope="module")
def client():
    mongo = MongoClient(URI, serverSelectionTimeoutMS=10000)
    db = mongo[f"simple_bank_test_{uuid.uuid4().hex[:8]}"]
    init_db(db)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_uow] = lambda: UnitOfWork(mongo)
    yield TestClient(app)
    app.dependency_overrides.clear()
    mongo.drop_database(db.name)
    mongo.close()


def new_account(client, deposit=None):
    email = f"{uuid.uuid4().hex[:8]}@example.com"
    user = client.post("/api/users", json={"name": "Test User", "email": email}).json()
    acc = client.post("/api/accounts", json={"userId": user["userId"], "accountType": "checking"}).json()
    if deposit is not None:
        client.post(f"/api/accounts/{acc['accountId']}/deposit", json={"amount": deposit})
    return acc["accountId"]


def test_full_flow(client):
    acc_id = new_account(client)
    assert client.post(f"/api/accounts/{acc_id}/deposit", json={"amount": "500.25"}).json()["balance"] == "500.25"
    assert client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 200}).json()["balance"] == "300.25"
    r = client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 1000})
    assert r.status_code == 400
    txns = client.get(f"/api/accounts/{acc_id}/transactions").json()
    assert [t["txnType"] for t in txns] == ["withdrawal", "deposit"]


def test_concurrent_withdrawals_never_overdraw(client):
    acc_id = new_account(client, deposit=100)

    def withdraw(_):
        return client.post(f"/api/accounts/{acc_id}/withdraw", json={"amount": 30}).status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(withdraw, range(10)))

    assert codes.count(200) == 3
    assert codes.count(400) == 7
    assert client.get(f"/api/accounts/{acc_id}").json()["balance"] == "10.00"
    # Exactly one transaction record per successful operation
    assert len(client.get(f"/api/accounts/{acc_id}/transactions").json()) == 1 + 3
