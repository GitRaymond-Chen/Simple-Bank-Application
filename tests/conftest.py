"""
Test setup: runs the real app against mongomock, an in-memory fake of
MongoDB, so no Atlas cluster is needed. Each test gets a fresh, empty database.
"""
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.database import get_db, get_uow, init_db
from app.main import app


class PassThroughUnitOfWork:
    """mongomock has no sessions/transactions, so just run the work directly."""

    def run(self, work):
        return work(None)


@pytest.fixture
def client():
    db = mongomock.MongoClient()["simple_bank_test"]
    init_db(db)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_uow] = lambda: PassThroughUnitOfWork()
    # Not used as a context manager, so the lifespan (Atlas init_db) doesn't run
    yield TestClient(app)
    app.dependency_overrides.clear()
