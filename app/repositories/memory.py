"""In-memory repositories.

Same method names a DB-backed repository would have, so swapping in MySQL later
only touches this layer. Data is lost when the server restarts.
"""

from itertools import count
from threading import Lock

from app.models import Account, Transaction, User


class UserRepository:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._ids = count(1)
        self._lock = Lock()

    def save(self, user: User) -> User:
        with self._lock:
            if not user.user_id:
                user.user_id = next(self._ids)
            self._users[user.user_id] = user
            return user

    def find_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        email = email.lower()
        return next((u for u in self._users.values() if u.email.lower() == email), None)


class AccountRepository:
    def __init__(self) -> None:
        self._accounts: dict[int, Account] = {}
        self._ids = count(1)
        self._lock = Lock()

    def save(self, account: Account) -> Account:
        with self._lock:
            if not account.account_id:
                account.account_id = next(self._ids)
            self._accounts[account.account_id] = account
            return account

    def find_by_id(self, account_id: int) -> Account | None:
        return self._accounts.get(account_id)


class TransactionRepository:
    def __init__(self) -> None:
        self._txns: list[Transaction] = []
        self._ids = count(1)
        self._lock = Lock()

    def save(self, txn: Transaction) -> Transaction:
        with self._lock:
            txn.txn_id = next(self._ids)
            self._txns.append(txn)
            return txn

    def find_by_account_id(self, account_id: int) -> list[Transaction]:
        """Newest first."""
        return sorted(
            (t for t in self._txns if t.account_id == account_id),
            key=lambda t: t.txn_id,
            reverse=True,
        )
