"""Domain entities. These mirror the users / accounts / transactions tables in the plan."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"


class TxnType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    name: str
    email: str
    user_id: int = 0  # assigned by the repository
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class Account:
    user_id: int
    account_type: AccountType
    balance: Decimal = Decimal("0.00")
    account_id: int = 0  # assigned by the repository
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class Transaction:
    account_id: int
    txn_type: TxnType
    amount: Decimal
    balance_after: Decimal
    txn_id: int = 0  # assigned by the repository
    created_at: datetime = field(default_factory=utcnow)
