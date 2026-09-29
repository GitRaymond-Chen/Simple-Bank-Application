"""Wires repositories -> services. Routers get services via FastAPI Depends."""

from dataclasses import dataclass

from fastapi import Request

from app.repositories import AccountRepository, TransactionRepository, UserRepository
from app.services import AccountService, UserService


@dataclass
class Container:
    user_service: UserService
    account_service: AccountService


def build_container() -> Container:
    user_service = UserService(UserRepository())
    account_service = AccountService(AccountRepository(), TransactionRepository(), user_service)
    return Container(user_service=user_service, account_service=account_service)


def get_user_service(request: Request) -> UserService:
    return request.app.state.container.user_service


def get_account_service(request: Request) -> AccountService:
    return request.app.state.container.account_service
