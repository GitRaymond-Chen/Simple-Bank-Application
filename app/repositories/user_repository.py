from sqlalchemy.orm import Session
from app.models import User


class UserRepository:
    """
    Handles all database operations for the User model.
    The repository pattern keeps SQL/ORM logic in one place,
    separate from business logic.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str) -> User:
        """Insert a new user row and return it."""
        user = User(name=name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)  # reload to get auto-generated fields (user_id, created_at)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Look up a user by primary key. Returns None if not found."""
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Look up a user by their unique email address."""
        return self.db.query(User).filter(User.email == email).first()
