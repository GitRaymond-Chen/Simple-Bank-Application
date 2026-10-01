from decimal import Decimal

from app.database import UnitOfWork
from app.exceptions import InsufficientFundsError, InvalidAmountError, NotFoundError
from app.models import Account, Transaction, to_cents
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository


class AccountService:
    """
    Contains business logic for account operations.
    Enforces rules like: amount must be positive, balance cannot go negative.
    """

    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        uow: UnitOfWork,
    ):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.user_repo = user_repo
        self.uow = uow

    def create_account(self, user_id: int, account_type: str) -> Account:
        """Open a new bank account for an existing user."""
        # Make sure the user exists before creating an account for them
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User with id {user_id} not found")

        return self.account_repo.create(user_id=user_id, account_type=account_type)

    def get_account(self, account_id: int) -> Account:
        """Retrieve an account by ID. Raises NotFoundError if missing."""
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account with id {account_id} not found")
        return account

    def deposit(self, account_id: int, amount: Decimal) -> Account:
        """
        Add money to an account.
        Business rule: amount must be greater than zero.
        """
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be greater than zero")
        cents = to_cents(amount)

        def work(session):
            account = self.account_repo.change_balance(account_id, cents, session=session)
            if account is None:
                raise NotFoundError(f"Account with id {account_id} not found")
            self.transaction_repo.add(account_id, "deposit", cents, session=session)
            return account

        # Balance change and transaction record commit together (or not at all)
        return self.uow.run(work)

    def withdraw(self, account_id: int, amount: Decimal) -> Account:
        """
        Remove money from an account.
        Business rules: amount must be > 0 and balance must be sufficient.
        """
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero")
        cents = to_cents(amount)

        def work(session):
            # Atomic "subtract only if balance >= amount"; None means it didn't apply
            account = self.account_repo.change_balance(account_id, -cents, session=session)
            if account is None:
                current = self.get_account(account_id)  # raises NotFoundError if missing
                raise InsufficientFundsError(
                    f"Insufficient funds: balance is {current.balance}, requested {amount}"
                )
            self.transaction_repo.add(account_id, "withdrawal", cents, session=session)
            return account

        return self.uow.run(work)

    def get_transactions(self, account_id: int) -> list[Transaction]:
        """Return all transactions for an account (newest first)."""
        # Verify the account exists
        self.get_account(account_id)
        return self.transaction_repo.get_by_account_id(account_id)
