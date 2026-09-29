from fastapi import APIRouter, Depends, Response, status
from app.schemas import CreateUserRequest, UserResponse
from app.services.user_service import UserService
from app.dependencies import get_user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    body: CreateUserRequest,
    response: Response,
    service: UserService = Depends(get_user_service),
):
    """
    Create a new bank customer.

    Request body:
    ```json
    { "name": "Alice", "email": "alice@example.com" }
    ```
    If the email is already registered, the existing user is returned with 200.
    """
    user, created = service.create_user(name=body.name, email=body.email.lower())
    if not created:
        response.status_code = status.HTTP_200_OK
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """Retrieve a user by their ID. Returns 404 if not found."""
    user = service.get_user(user_id)
    return UserResponse.model_validate(user)
