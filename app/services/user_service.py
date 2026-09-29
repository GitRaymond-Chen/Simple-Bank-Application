from app.models import User
from app.repositories.user_repository import UserRepository
from app.exceptions import NotFoundError


class UserService:
    """
    Contains business logic for user operations.
    Calls the repository for database access.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, name: str, email: str) -> tuple[User, bool]:
        """
        Create a new user, or return the existing one if the email is taken.
        Returns (user, created) so the router can answer 201 vs 200.
        """
        existing = self.user_repo.get_by_email(email)
        if existing is not None:
            return existing, False
        return self.user_repo.create(name=name, email=email), True

    def get_user(self, user_id: int) -> User:
        """
        Retrieve a user by ID.
        Raises NotFoundError if the user does not exist.
        """
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User with id {user_id} not found")
        return user
