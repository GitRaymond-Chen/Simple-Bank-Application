import os
from typing import Callable, TypeVar

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.database import Database

# Load variables from .env file (MONGODB_URI, MONGODB_DB)
load_dotenv()

# Atlas connection string, e.g.
# mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "simple_bank")

# One client for the whole app: it holds a connection pool and is thread-safe.
# It connects lazily, so importing this module never needs a running database.
client: MongoClient = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,  # fail fast with a clear error instead of hanging 30s
    appname="simple-bank-api",
)


def get_db() -> Database:
    """FastAPI dependency that provides the application database."""
    return client[MONGODB_DB]


def init_db(db: Database) -> None:
    """
    Create indexes (idempotent). Called once at startup.
    MongoDB creates collections on first insert, so there is no schema to create.
    """
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.accounts.create_index([("user_id", ASCENDING)])
    # History query: all transactions for one account, newest first
    db.transactions.create_index([("account_id", ASCENDING), ("_id", DESCENDING)])


def next_id(db: Database, name: str) -> int:
    """
    Return the next integer id for a collection (1, 2, 3, ...).
    MongoDB has no AUTO_INCREMENT, so a "counters" collection holds one
    sequence per collection and $inc bumps it atomically.
    Integer ids keep the API (and the frontend's "#0001" account numbers) unchanged.

    Deliberately runs outside any transaction: a rolled-back operation just
    leaves a gap in the sequence, and concurrent requests don't conflict
    on the counter document.
    """
    doc = db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["seq"]


# ── Unit of work ──────────────────────────────────────────────

T = TypeVar("T")


class UnitOfWork:
    """
    Runs a function inside a MongoDB multi-document transaction, so several
    writes (e.g. balance change + transaction record) succeed or fail together.
    Atlas clusters are replica sets, which is what transactions require.
    """

    def __init__(self, mongo_client: MongoClient):
        self.client = mongo_client

    def run(self, work: Callable[[ClientSession | None], T]) -> T:
        with self.client.start_session() as session:
            # with_transaction commits on success, aborts if `work` raises,
            # and retries automatically on transient errors (e.g. write conflicts)
            return session.with_transaction(work)


def get_uow() -> UnitOfWork:
    """FastAPI dependency that provides the unit of work."""
    return UnitOfWork(client)
