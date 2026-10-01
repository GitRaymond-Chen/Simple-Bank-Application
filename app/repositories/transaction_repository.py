from pymongo import DESCENDING
from pymongo.client_session import ClientSession
from pymongo.database import Database

from app.database import next_id
from app.models import Transaction, utcnow


class TransactionRepository:
    """Handles all database operations for transactions."""

    def __init__(self, db: Database):
        self.transactions = db.transactions
        self.db = db

    def add(
        self, account_id: int, txn_type: str, amount_cents: int,
        session: ClientSession | None = None,
    ) -> Transaction:
        """
        Record a new transaction (deposit or withdrawal).
        Pass the session of the surrounding unit of work so it commits
        (or rolls back) together with the balance change.
        """
        doc = {"_id": next_id(self.db, "transactions"), "account_id": account_id,
               "txn_type": txn_type, "amount_cents": amount_cents, "created_at": utcnow()}
        self.transactions.insert_one(doc, session=session)
        return Transaction.from_doc(doc)

    def get_by_account_id(self, account_id: int) -> list[Transaction]:
        """Return all transactions for a given account, newest first."""
        cursor = self.transactions.find({"account_id": account_id}).sort("_id", DESCENDING)
        return [Transaction.from_doc(d) for d in cursor]
