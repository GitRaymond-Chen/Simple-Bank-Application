from fastapi import APIRouter, Depends
from app.schemas import (
    CreateAccountRequest,
    AccountResponse,
    DepositWithdrawRequest,
    TransactionResponse,
)
from app.services.account_service import AccountService
from app.dependencies import get_account_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
    body: CreateAccountRequest,
    service: AccountService = Depends(get_account_service),
):
    """
    Open a new bank account for an existing user.

    Request body:
    ```json
    { "userId": 1, "accountType": "checking" }
    ```
    """
    account = service.create_account(
        user_id=body.userId,
        account_type=body.accountType,
    )
    return AccountResponse.model_validate(account)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    service: AccountService = Depends(get_account_service),
):
    """Retrieve an account by its ID. Returns 404 if not found."""
    account = service.get_account(account_id)
    return AccountResponse.model_validate(account)


@router.post("/{account_id}/deposit", response_model=AccountResponse)
def deposit(
    account_id: int,
    body: DepositWithdrawRequest,
    service: AccountService = Depends(get_account_service),
):
    """
    Deposit money into an account.

    Request body:
    ```json
    { "amount": "100.00" }
    ```
    """
    account = service.deposit(account_id=account_id, amount=body.amount)
    return AccountResponse.model_validate(account)


@router.post("/{account_id}/withdraw", response_model=AccountResponse)
def withdraw(
    account_id: int,
    body: DepositWithdrawRequest,
    service: AccountService = Depends(get_account_service),
):
    """
    Withdraw money from an account.
    Returns 400 if the amount exceeds the current balance.
    """
    account = service.withdraw(account_id=account_id, amount=body.amount)
    return AccountResponse.model_validate(account)


@router.get("/{account_id}/transactions", response_model=list[TransactionResponse])
def get_transactions(
    account_id: int,
    service: AccountService = Depends(get_account_service),
):
    """Return all transactions for an account, newest first."""
    transactions = service.get_transactions(account_id)
    return [TransactionResponse.model_validate(t) for t in transactions]
