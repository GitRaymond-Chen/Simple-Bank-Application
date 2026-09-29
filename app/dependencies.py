from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.user_service import UserService
from app.services.account_service import AccountService


# ── Repository dependencies ───────────────────────────────────

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_account_repo(db: Session = Depends(get_db)) -> AccountRepository:
    return AccountRepository(db)


def get_transaction_repo(db: Session = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)


# ── Service dependencies ──────────────────────────────────────

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repo)


def get_account_service(
    account_repo: AccountRepository = Depends(get_account_repo),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> AccountService:
    return AccountService(account_repo, transaction_repo, user_repo)
