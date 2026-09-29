from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# --- Shared config: allows reading from ORM model attributes ---
# Response fields use validation_alias (not alias): they READ snake_case ORM
# attributes but are SERIALIZED under their camelCase field names, which is
# what the frontend expects (userId, accountId, ...).
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"


# Positive, at most 2 decimal places (e.g. 1.239 is rejected, not rounded)
Amount = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


# ── User Schemas ──────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    """Body sent when creating a new user."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=100)


class UserResponse(ORMBase):
    """User data returned by the API (camelCase field names)."""
    userId: int = Field(validation_alias="user_id")
    name: str
    email: str
    createdAt: datetime = Field(validation_alias="created_at")


# ── Account Schemas ───────────────────────────────────────────

class CreateAccountRequest(BaseModel):
    """Body sent when opening a new account. Accepts camelCase or snake_case keys."""
    userId: int = Field(alias="user_id", gt=0)
    accountType: AccountType = Field(alias="account_type")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("accountType", mode="before")
    @classmethod
    def lowercase_type(cls, v):
        # Accept "SAVINGS" / "Savings" as well as "savings"
        return v.lower() if isinstance(v, str) else v


class AccountResponse(ORMBase):
    """Account data returned by the API."""
    accountId: int = Field(validation_alias="account_id")
    userId: int = Field(validation_alias="user_id")
    balance: Decimal
    accountType: str = Field(validation_alias="account_type")
    createdAt: datetime = Field(validation_alias="created_at")


# ── Transaction Schemas ───────────────────────────────────────

class DepositWithdrawRequest(BaseModel):
    """Body sent for a deposit or withdrawal."""
    amount: Amount


class TransactionResponse(ORMBase):
    """Transaction record returned by the API."""
    txnId: int = Field(validation_alias="txn_id")
    accountId: int = Field(validation_alias="account_id")
    txnType: str = Field(validation_alias="txn_type")
    amount: Decimal
    createdAt: datetime = Field(validation_alias="created_at")


# ── Error Schema ──────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error body."""
    detail: str
