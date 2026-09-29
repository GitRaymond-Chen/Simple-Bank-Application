from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Account


class AccountRepository:
    """Handles all database operations for the Account model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, account_type: str) -> Account:
        """Create a new bank account with a starting balance of 0."""
        account = Account(user_id=user_id, account_type=account_type, balance=Decimal("0.00"))
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def get_by_id(self, account_id: int) -> Account | None:
        """Look up an account by primary key."""
        return self.db.get(Account, account_id)

    def get_by_user_id(self, user_id: int) -> list[Account]:
        """Return all accounts belonging to a user."""
        return self.db.query(Account).filter(Account.user_id == user_id).all()

    def update_balance(self, account: Account, new_balance: Decimal) -> Account:
        """Persist a new balance value for the given account."""
        account.balance = new_balance
        self.db.commit()
        self.db.refresh(account)
        return account
