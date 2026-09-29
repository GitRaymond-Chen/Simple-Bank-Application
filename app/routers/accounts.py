from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_account_service
from app.models import Account
from app.schemas import (
    AccountResponse,
    AmountRequest,
    CreateAccountRequest,
    ErrorResponse,
    TransactionResponse,
)
from app.services import AccountService

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])
AccountSvc = Annotated[AccountService, Depends(get_account_service)]

NOT_FOUND = {404: {"model": ErrorResponse}}


def to_response(svc: AccountService, account: Account) -> AccountResponse:
    user = svc.user_service.get_user(account.user_id)
    return AccountResponse(
        account_id=account.account_id,
        user_name=user.name,
        account_type=account.account_type,
        balance=account.balance,
        created_at=account.created_at,
    )


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    responses=NOT_FOUND,
)
def create_account(body: CreateAccountRequest, response: Response, svc: AccountSvc):
    account = svc.create_account(body.user_id, body.account_type)
    response.headers["Location"] = f"/api/accounts/{account.account_id}"
    return to_response(svc, account)


@router.get("/{account_id}", response_model=AccountResponse, responses=NOT_FOUND)
def get_account(account_id: int, svc: AccountSvc):
    return to_response(svc, svc.get_account(account_id))


@router.post("/{account_id}/deposit", response_model=AccountResponse, responses=NOT_FOUND)
def deposit(account_id: int, body: AmountRequest, svc: AccountSvc):
    return to_response(svc, svc.deposit(account_id, body.amount))


@router.post(
    "/{account_id}/withdraw",
    response_model=AccountResponse,
    responses={**NOT_FOUND, 422: {"model": ErrorResponse, "description": "Insufficient funds"}},
)
def withdraw(account_id: int, body: AmountRequest, svc: AccountSvc):
    return to_response(svc, svc.withdraw(account_id, body.amount))


@router.get(
    "/{account_id}/transactions",
    response_model=list[TransactionResponse],
    responses=NOT_FOUND,
)
def get_transactions(account_id: int, svc: AccountSvc):
    return [
        TransactionResponse(
            transaction_id=t.txn_id,
            type=t.txn_type,
            amount=t.amount,
            balance_after=t.balance_after,
            date=t.created_at,
        )
        for t in svc.get_transactions(account_id)
    ]
