from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_user_service
from app.schemas import CreateUserRequest, ErrorResponse, UserResponse
from app.services import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])
UserSvc = Annotated[UserService, Depends(get_user_service)]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={200: {"description": "Email already registered; existing user returned"}},
)
def create_user(body: CreateUserRequest, response: Response, svc: UserSvc):
    """Create a user, or return the existing one if the email is already registered."""
    user, created = svc.create_or_get_user(body.name, body.email)
    if not created:
        response.status_code = status.HTTP_200_OK
    return UserResponse(
        user_id=user.user_id, name=user.name, email=user.email, created_at=user.created_at
    )


@router.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def get_user(user_id: int, svc: UserSvc):
    user = svc.get_user(user_id)
    return UserResponse(
        user_id=user.user_id, name=user.name, email=user.email, created_at=user.created_at
    )

