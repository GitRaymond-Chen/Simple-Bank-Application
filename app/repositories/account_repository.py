from pymongo import ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.database import Database

from app.database import next_id
from app.models import Account, utcnow


class AccountRepository:
    """Handles all database operations for accounts."""

    def __init__(self, db: Database):
        self.accounts = db.accounts
        self.db = db

    def create(self, user_id: int, account_type: str) -> Account:
        """Create a new bank account with a starting balance of 0."""
        doc = {"_id": next_id(self.db, "accounts"), "user_id": user_id,
               "account_type": account_type, "balance_cents": 0, "created_at": utcnow()}
        self.accounts.insert_one(doc)
        return Account.from_doc(doc)

    def get_by_id(self, account_id: int) -> Account | None:
        """Look up an account by id."""
        doc = self.accounts.find_one({"_id": account_id})
        return Account.from_doc(doc) if doc else None

    def get_by_user_id(self, user_id: int) -> list[Account]:
        """Return all accounts belonging to a user."""
        return [Account.from_doc(d) for d in self.accounts.find({"user_id": user_id})]

    def change_balance(
        self, account_id: int, delta_cents: int, session: ClientSession | None = None
    ) -> Account | None:
        """
        Atomically add delta_cents (negative for a withdrawal) to the balance.

        The balance check is part of the update's filter, so MongoDB checks
        and updates in one atomic step: two concurrent withdrawals can't both
        pass the check, and the balance can never go below zero.
        Returns the updated account, or None if the account doesn't exist or
        has insufficient funds.
        """
        query = {"_id": account_id}
        if delta_cents < 0:
            query["balance_cents"] = {"$gte": -delta_cents}
        doc = self.accounts.find_one_and_update(
            query,
            {"$inc": {"balance_cents": delta_cents}},
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        return Account.from_doc(doc) if doc else None
