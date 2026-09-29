"""Business logic for accounts. All balance rules live here, not in the routers."""

from decimal import Decimal
from threading import Lock

from app.exceptions import InsufficientFundsError, InvalidAmountError, NotFoundError
from app.models import Account, AccountType, Transaction, TxnType
from app.repositories import AccountRepository, TransactionRepository
from app.services.user_service import UserService

CENTS = Decimal("0.01")


class AccountService:
    def __init__(
        self,
        accounts: AccountRepository,
        transactions: TransactionRepository,
        user_service: UserService,
    ) -> None:
        self.accounts = accounts
        self.transactions = transactions
        self.user_service = user_service
        # One lock per account: the in-memory stand-in for SELECT ... FOR UPDATE.
        # Stops two concurrent withdrawals from both passing the balance check.
        self._account_locks: dict[int, Lock] = {}

    def create_account(self, user_id: int, account_type: AccountType) -> Account:
        self.user_service.get_user(user_id)  # 404 if missing
        return self.accounts.save(Account(user_id=user_id, account_type=account_type))

    def get_account(self, account_id: int) -> Account:
        account = self.accounts.find_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")
        return account

    def deposit(self, account_id: int, amount: Decimal) -> Account:
        amount = self._validate_amount(amount)
        with self._lock_for(account_id):
            account = self.get_account(account_id)
            account.balance += amount
            self._record(account, TxnType.DEPOSIT, amount)
            return self.accounts.save(account)

    def withdraw(self, account_id: int, amount: Decimal) -> Account:
        amount = self._validate_amount(amount)
        with self._lock_for(account_id):
            account = self.get_account(account_id)
            if amount > account.balance:
                raise InsufficientFundsError(
                    f"Withdrawal of {amount} exceeds balance of {account.balance}"
                )
            account.balance -= amount
            self._record(account, TxnType.WITHDRAW, amount)
            return self.accounts.save(account)

    def get_transactions(self, account_id: int) -> list[Transaction]:
        self.get_account(account_id)  # 404 if missing
        return self.transactions.find_by_account_id(account_id)

    def _lock_for(self, account_id: int) -> Lock:
        # dict.setdefault is atomic, so two threads always get the same lock.
        return self._account_locks.setdefault(account_id, Lock())

    def _record(self, account: Account, txn_type: TxnType, amount: Decimal) -> None:
        self.transactions.save(
            Transaction(
                account_id=account.account_id,
                txn_type=txn_type,
                amount=amount,
                balance_after=account.balance,
            )
        )

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        # The API layer validates too; this guards callers that bypass it.
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive")
        return amount.quantize(CENTS)
