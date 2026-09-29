"""Request/response DTOs (the API contract). Kept separate from domain models."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PlainSerializer
from pydantic.alias_generators import to_camel

from app.models import AccountType, TxnType

# Serialize money as a JSON number (Pydantic defaults Decimal to a string).
Money = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
PositiveAmount = Annotated[
    Decimal, Field(gt=0, max_digits=12, decimal_places=2, examples=[500])
]


class CamelModel(BaseModel):
    """Accept and emit camelCase JSON (userId, accountType, ...)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---- Requests ----

class CreateUserRequest(CamelModel):
    name: str = Field(min_length=1, max_length=100, examples=["John Doe"])
    email: EmailStr = Field(max_length=100, examples=["john@example.com"])


class CreateAccountRequest(CamelModel):
    user_id: int = Field(gt=0, examples=[1])
    account_type: AccountType = Field(examples=["SAVINGS"])


class AmountRequest(CamelModel):
    amount: PositiveAmount


# ---- Responses ----

class UserResponse(CamelModel):
    user_id: int
    name: str
    email: str
    created_at: datetime


class AccountResponse(CamelModel):
    account_id: int
    user_name: str
    account_type: AccountType
    balance: Money
    created_at: datetime


class TransactionResponse(CamelModel):
    transaction_id: int
    type: TxnType
    amount: Money
    balance_after: Money
    date: datetime


class ErrorResponse(BaseModel):
    status: int
    error: str
    message: str
    timestamp: datetime
    details: list[dict] | None = None
