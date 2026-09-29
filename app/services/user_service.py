from app.exceptions import NotFoundError
from app.models import User
from app.repositories import UserRepository


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def create_or_get_user(self, name: str, email: str) -> tuple[User, bool]:
        """Return (user, created). An existing email returns the existing user."""
        existing = self.users.find_by_email(email)
        if existing:
            return existing, False
        return self.users.save(User(name=name.strip(), email=email)), True

    def get_user(self, user_id: int) -> User:
        user = self.users.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user
