"""
Domain models and their MongoDB document mapping.

Collections (one document per object):
  users         { _id: int, name, email, created_at }
  accounts      { _id: int, user_id, account_type, balance_cents: int, created_at }
  transactions  { _id: int, account_id, txn_type, amount_cents: int, created_at }
  counters      { _id: "<collection>", seq: int }   -- integer id sequences

Money is stored as integer cents: exact (no floating point), and MongoDB can
add/subtract it atomically with $inc. The models expose Decimal dollars.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

CENT = Decimal("0.01")


def utcnow() -> datetime:
    """
    Current UTC time as a naive datetime. MongoDB stores UTC with millisecond
    precision, and PyMongo returns naive UTC datetimes by default.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


def to_cents(amount: Decimal) -> int:
    """Decimal dollars -> integer cents (amounts are validated to 2 decimal places)."""
    return int((amount / CENT).to_integral_value())


def from_cents(cents: int) -> Decimal:
    """Integer cents -> Decimal dollars, e.g. 50025 -> Decimal('500.25')."""
    return (Decimal(cents) * CENT).quantize(CENT)


@dataclass
class User:
    """A bank customer."""
    user_id: int
    name: str
    email: str
    created_at: datetime

    @classmethod
    def from_doc(cls, doc: dict) -> "User":
        return cls(user_id=doc["_id"], name=doc["name"], email=doc["email"],
                   created_at=doc["created_at"])


@dataclass
class Account:
    """A bank account (checking or savings)."""
    account_id: int
    user_id: int
    account_type: str
    balance: Decimal
    created_at: datetime

    @classmethod
    def from_doc(cls, doc: dict) -> "Account":
        return cls(account_id=doc["_id"], user_id=doc["user_id"],
                   account_type=doc["account_type"],
                   balance=from_cents(doc["balance_cents"]),
                   created_at=doc["created_at"])


@dataclass
class Transaction:
    """A single deposit or withdrawal on an account."""
    txn_id: int
    account_id: int
    txn_type: str  # "deposit" or "withdrawal"
    amount: Decimal
    created_at: datetime

    @classmethod
    def from_doc(cls, doc: dict) -> "Transaction":
        return cls(txn_id=doc["_id"], account_id=doc["account_id"], txn_type=doc["txn_type"],
                   amount=from_cents(doc["amount_cents"]), created_at=doc["created_at"])
