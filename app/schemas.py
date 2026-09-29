from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# --- Shared config: allows reading from ORM model attributes ---
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── User Schemas ──────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    """Body sent when creating a new user."""
    name: str
    email: EmailStr


class UserResponse(ORMBase):
    """User data returned by the API (camelCase field names)."""
    userId: int = Field(alias="user_id")
    name: str
    email: str
    createdAt: datetime = Field(alias="created_at")


# ── Account Schemas ───────────────────────────────────────────

class CreateAccountRequest(BaseModel):
    """Body sent when opening a new account."""
    userId: int = Field(alias="user_id")
    accountType: str = Field(alias="account_type")

    model_config = ConfigDict(populate_by_name=True)


class AccountResponse(ORMBase):
    """Account data returned by the API."""
    accountId: int = Field(alias="account_id")
    userId: int = Field(alias="user_id")
    balance: Decimal
    accountType: str = Field(alias="account_type")
    createdAt: datetime = Field(alias="created_at")


# ── Transaction Schemas ───────────────────────────────────────

class DepositWithdrawRequest(BaseModel):
    """Body sent for a deposit or withdrawal."""
    amount: Decimal


class TransactionResponse(ORMBase):
    """Transaction record returned by the API."""
    txnId: int = Field(alias="txn_id")
    accountId: int = Field(alias="account_id")
    txnType: str = Field(alias="txn_type")
    amount: Decimal
    createdAt: datetime = Field(alias="created_at")


# ── Error Schema ──────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error body."""
    detail: str
