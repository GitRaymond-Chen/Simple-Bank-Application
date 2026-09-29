from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Transaction


class TransactionRepository:
    """Handles all database operations for the Transaction model."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, account_id: int, txn_type: str, amount: Decimal) -> Transaction:
        """
        Stage a new transaction (deposit or withdrawal) WITHOUT committing.
        The caller commits it together with the balance change so both
        succeed or fail as one unit.
        """
        txn = Transaction(account_id=account_id, txn_type=txn_type, amount=amount)
        self.db.add(txn)
        return txn

    def get_by_account_id(self, account_id: int) -> list[Transaction]:
        """Return all transactions for a given account, newest first."""
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.txn_id.desc())  # created_at has only 1-second precision in MySQL
            .all()
        )
