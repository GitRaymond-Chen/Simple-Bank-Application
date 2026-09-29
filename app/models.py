from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """Represents a bank customer."""
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # One user can have many accounts
    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")


class Account(Base):
    """Represents a bank account (checking, savings, etc.)."""
    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))
    balance: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.00"))
    account_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="account")


class Transaction(Base):
    """Records every deposit or withdrawal on an account."""
    __tablename__ = "transactions"

    txn_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.account_id"))
    txn_type: Mapped[str] = mapped_column(String(20))   # "deposit" or "withdrawal"
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Each transaction belongs to one account
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
